from app.domain.ml.feature_builder import build_feature_row
from app.domain.ml.model_loader import load_feature_schema, load_ml_model
from app.domain.ml.reason_codes import calculate_reason_codes, reason_codes_to_signal_labels
from app.domain.scoring.fallback_scorecard import calculate_fallback_score
from app.domain.scoring.tiering import tier_from_score


def derive_missing_data(farmer: dict) -> list[str]:
    missing = []

    checks = {
        "mobile money consistency": farmer.get("mobile_money_consistency"),
        "cooperative repayment score": farmer.get("cooperative_repayment_score"),
        "peer lending reliability": farmer.get("peer_lending_reliability"),
        "seasonal income pattern": farmer.get("seasonal_income_pattern"),
        "input purchase frequency": farmer.get("input_purchase_frequency"),
        "market payment consistency": farmer.get("market_payment_consistency"),
        "buyer records": farmer.get("has_buyer_records"),
        "sales records": farmer.get("has_sales_records"),
        "formal credit history": farmer.get("has_formal_credit_history"),
    }

    for label, value in checks.items():
        if value in [None, False, "none", "unknown"]:
            missing.append(label)

    if not farmer.get("has_land_title"):
        missing.append("land title or formal collateral")

    return missing


def derive_alternative_data_used(farmer: dict) -> list[str]:
    used = []

    if farmer.get("mobile_money_consistency") not in [None, "unknown"]:
        used.append("mobile money consistency")

    if farmer.get("cooperative_repayment_score") is not None:
        used.append("cooperative repayment score")

    if farmer.get("peer_lending_reliability") not in [None, "none"]:
        used.append("peer lending reliability")

    if farmer.get("input_purchase_frequency") not in [None, "none"]:
        used.append("input purchase frequency")

    if farmer.get("market_payment_consistency") not in [None, "none"]:
        used.append("market payment consistency")

    if farmer.get("seasonal_income_pattern") not in [None, "unknown"]:
        used.append("seasonal income pattern")

    if farmer.get("savings_group_reliability") not in [None, "none"]:
        used.append("savings group reliability")

    if farmer.get("buyer_payment_reliability") not in [None, "none"]:
        used.append("buyer payment reliability")

    if farmer.get("extension_support"):
        used.append("extension support")

    return used


def confidence_from_evidence(alternative_data_used: list[str], missing_data: list[str]) -> str:
    if len(alternative_data_used) >= 7 and len(missing_data) <= 3:
        return "high"

    if len(alternative_data_used) >= 4:
        return "medium"

    return "low"


def score_from_probability(probability: float) -> int:
    score = int(round(probability * 100))
    return max(0, min(score, 98))


def is_material_risk_signal(signal: str) -> bool:
    text = signal.lower()

    material_keywords = [
        "missed repayment",
        "default",
        "drought",
        "pest",
        "market delay",
        "volatile",
        "buyer payment consistency = none",
        "buyer payment reliability = none",
        "market payment consistency = none",
        "mobile money consistency = unknown",
        "mobile money consistency = low",
        "peer lending reliability = none",
        "input purchase frequency = none",
        "seasonal income pattern = volatile",
    ]

    return any(keyword in text for keyword in material_keywords)


def score_farmer_with_ml(farmer: dict) -> dict:
    try:
        schema = load_feature_schema()
        pipeline = load_ml_model()

        features = schema["all_features"]
        feature_row = build_feature_row(farmer, features)

        repayment_probability = float(pipeline.predict_proba(feature_row)[0][1])
        score = score_from_probability(repayment_probability)

        tier, recommended_loan_range = tier_from_score(score)

        model_reason_codes = calculate_reason_codes(pipeline, feature_row)

        positive_signals = reason_codes_to_signal_labels(
            model_reason_codes["top_positive_reason_codes"],
            direction="positive",
        )

        technical_risk_signals = reason_codes_to_signal_labels(
            model_reason_codes["top_risk_reason_codes"],
            direction="risk",
        )

        material_risk_signals = [
            signal for signal in technical_risk_signals
            if is_material_risk_signal(signal)
        ]

        missing_data = derive_missing_data(farmer)
        alternative_data_used = derive_alternative_data_used(farmer)
        confidence = confidence_from_evidence(alternative_data_used, missing_data)

        manual_attention_required = (
            score < 60
            or len(material_risk_signals) >= 2
            or len(missing_data) >= 5
        )

        return {
            "provider": "ml_scoring_agent",
            "model_type": "logistic_regression_scorecard",
            "model_version": "synthetic-v1",
            "score": score,
            "repayment_readiness_probability": round(repayment_probability, 4),
            "tier": tier,
            "recommended_loan_range": recommended_loan_range,
            "confidence": confidence,
            "loan_officer_final_decision_required": True,
            "manual_attention_required": manual_attention_required,
            "human_review_required": True,
            "positive_signals": positive_signals,

            # Business-facing risk signals only.
            "risk_signals": material_risk_signals,

            # Technical model effects remain available for audit/model transparency.
            "technical_risk_signals": technical_risk_signals,
            "material_risk_signals": material_risk_signals,

            "missing_data": missing_data,
            "alternative_data_used": alternative_data_used,
            "model_reason_codes": model_reason_codes,
            "protected_attributes_excluded_from_training": schema.get(
                "excluded_from_training",
                [
                    "gender",
                    "age",
                    "is_youth",
                    "is_pwd",
                    "disability_type",
                    "farmer_type",
                    "has_land_title",
                ],
            ),
            "exclusion_adjustment_note": (
                "The ML scoring agent does not use gender, age, youth status, PWD status, "
                "disability type, farmer type, phone type, preferred language, or lack of land title "
                "as risk penalties. It predicts repayment readiness using alternative farmer evidence "
                "such as mobile money consistency, cooperative repayment, peer lending reliability, "
                "input purchase frequency, market payment consistency, and seasonal farming context."
            ),
            "used_for_final_decision": False,
            "final_decision_note": (
                "The ML score supports loan officer review only. "
                "The human loan officer makes the final decision."
            ),
        }

    except Exception as exc:
        fallback = calculate_fallback_score(farmer)
        fallback["provider"] = "deterministic_fallback"
        fallback["ml_scoring_error"] = str(exc)
        fallback["used_for_final_decision"] = False
        fallback["loan_officer_final_decision_required"] = True
        fallback["manual_attention_required"] = fallback.get("score", 0) < 60
        return fallback