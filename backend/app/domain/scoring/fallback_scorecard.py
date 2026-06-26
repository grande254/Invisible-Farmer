from app.domain.scoring.tiering import tier_from_score


def calculate_fallback_score(farmer: dict) -> dict:
    score = 30
    positive_signals = []
    risk_signals = []
    missing_data = []
    alternative_data_used = []

    def add(points: int, label: str, alternative: bool = False) -> None:
        nonlocal score
        score += points
        positive_signals.append(label)

        if alternative:
            alternative_data_used.append(label)

    def subtract(points: int, label: str) -> None:
        nonlocal score
        score -= points
        risk_signals.append(label)

    def missing(label: str) -> None:
        if label not in missing_data:
            missing_data.append(label)

    if not farmer.get("consent_to_process_data", False):
        return {
            "provider": "fallback_scorecard",
            "score": 0,
            "tier": "Not Reviewable",
            "recommended_loan_range": "Consent required before review",
            "confidence": "low",
            "human_review_required": True,
            "positive_signals": [],
            "risk_signals": ["farmer consent missing"],
            "missing_data": ["consent to process data"],
            "alternative_data_used": [],
            "used_for_final_decision": False,
        }

    if farmer.get("completed_repayment_history"):
        add(18, "completed repayment history")
    else:
        missing("repayment history")

    if farmer.get("missed_repayment"):
        subtract(20, "missed repayment record")

    savings = farmer.get("savings_group_reliability", "none")

    if savings == "strong":
        add(14, "strong savings group reliability", alternative=True)
    elif savings == "medium":
        add(9, "medium savings group reliability", alternative=True)
    elif savings == "weak":
        add(4, "weak savings group reliability", alternative=True)
    else:
        missing("savings group reliability")

    peer = farmer.get("peer_lending_reliability", "none")

    if peer == "strong":
        add(10, "strong peer lending reliability", alternative=True)
    elif peer == "medium":
        add(6, "medium peer lending reliability", alternative=True)
    elif peer == "weak":
        add(2, "weak peer lending reliability", alternative=True)
    else:
        missing("peer lending reliability")

    mobile_money = farmer.get("mobile_money_consistency", "unknown")

    if mobile_money == "high":
        add(10, "high mobile money consistency", alternative=True)
    elif mobile_money == "medium":
        add(6, "medium mobile money consistency", alternative=True)
    elif mobile_money == "low":
        add(2, "visible but low mobile money consistency", alternative=True)
    else:
        missing("mobile money consistency")

    coop_score = farmer.get("cooperative_repayment_score")

    if coop_score is not None:
        if coop_score >= 80:
            add(12, "high cooperative repayment score", alternative=True)
        elif coop_score >= 60:
            add(8, "medium cooperative repayment score", alternative=True)
        elif coop_score >= 40:
            add(3, "limited cooperative repayment score", alternative=True)
        else:
            subtract(5, "weak cooperative repayment score")
    elif farmer.get("cooperative_member"):
        missing("cooperative repayment score")

    market_payment = farmer.get("market_payment_consistency", "none")

    if market_payment == "strong":
        add(10, "strong market payment consistency", alternative=True)
    elif market_payment == "medium":
        add(6, "medium market payment consistency", alternative=True)
    elif market_payment == "weak":
        add(2, "weak market payment consistency", alternative=True)
    else:
        missing("market payment consistency")

    input_frequency = farmer.get("input_purchase_frequency", "none")

    if input_frequency == "high":
        add(10, "high input purchase frequency", alternative=True)
    elif input_frequency == "medium":
        add(7, "medium input purchase frequency", alternative=True)
    elif input_frequency == "low":
        add(3, "low input purchase frequency", alternative=True)
    else:
        missing("input purchase frequency")

    seasonal = farmer.get("seasonal_income_pattern", "unknown")

    if seasonal == "stable":
        add(8, "stable seasonal income pattern", alternative=True)
    elif seasonal == "moderate":
        add(4, "moderate seasonal income pattern", alternative=True)
    elif seasonal == "volatile":
        subtract(6, "volatile seasonal income pattern")
    else:
        missing("seasonal income pattern")

    if farmer.get("has_sales_records"):
        add(7, "sales records available", alternative=True)
    else:
        missing("sales records")

    if farmer.get("extension_support"):
        add(4, "extension support available", alternative=True)

    if farmer.get("localized_drought_exposure") == "high":
        subtract(10, "high localized drought exposure")
    elif farmer.get("localized_drought_exposure") == "medium":
        subtract(5, "medium localized drought exposure")

    if farmer.get("localized_pest_outbreak") == "high":
        subtract(8, "high localized pest outbreak")
    elif farmer.get("localized_pest_outbreak") == "medium":
        subtract(4, "medium localized pest outbreak")

    if farmer.get("market_delay_risk") == "high":
        subtract(7, "high market delay risk")
    elif farmer.get("market_delay_risk") == "medium":
        subtract(4, "medium market delay risk")

    if not farmer.get("has_land_title"):
        missing("land title or formal collateral")

    score = max(0, min(100, score))
    tier, recommended_loan_range = tier_from_score(score)

    return {
        "provider": "fallback_scorecard",
        "model_type": "transparent_scorecard",
        "model_version": "fallback-v1",
        "score": score,
        "repayment_readiness_probability": round(score / 100, 4),
        "tier": tier,
        "recommended_loan_range": recommended_loan_range,
        "confidence": farmer.get("score_confidence", "medium"),
        "human_review_required": score < 60 or len(risk_signals) > 0,
        "positive_signals": positive_signals,
        "risk_signals": risk_signals,
        "missing_data": missing_data,
        "alternative_data_used": alternative_data_used,
        "protected_attributes_excluded_from_training": [
            "gender",
            "age",
            "youth status",
            "PWD status",
            "disability type",
            "lack of land title",
        ],
        "exclusion_adjustment_note": (
            "The fallback scorecard does not use gender, youth status, PWD status, "
            "disability type, or lack of land title as negative scoring factors."
        ),
        "used_for_final_decision": False,
        "final_decision_note": "The fallback score supports loan officer review only.",
    }