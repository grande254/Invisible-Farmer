from app.domain.explanation.farmer_message_builder import (
    build_farmer_improvement_tips,
    build_farmer_sms,
    build_farmer_ussd_summary,
)
from app.domain.explanation.officer_memo_builder import build_officer_memo


def build_recommendation(scoring_result: dict, graph_result: dict | None = None) -> dict:
    graph_result = graph_result or {}

    score = scoring_result.get("score", 0)
    risk_signals = scoring_result.get("risk_signals", [])
    missing_data = scoring_result.get("missing_data", [])
    graph_support = graph_result.get("graph_support_level", "not_available")
    graph_risks = graph_result.get("network_risk_signals", [])

    if score >= 80:
        recommendation = "Proceed to loan officer review"
        reason = "Strong repayment-readiness signals are available, but human review remains required."
    elif score >= 60:
        recommendation = "Proceed with caution to loan officer review"
        reason = "Useful repayment-readiness signals are present, but some risks or missing records require officer review."
    elif score >= 40:
        recommendation = "Request more information before loan processing"
        reason = "Some alternative evidence exists, but risk signals or missing records are material."
    else:
        recommendation = "Defer for record-building support"
        reason = "The farmer needs stronger records or risk mitigation before normal loan processing."

    if graph_support in ["strong", "moderate_to_strong"]:
        reason += " Neo4j graph intelligence found useful relationship verification paths."

    if graph_support in ["thin_graph", "limited"]:
        reason += " Relationship evidence is limited, so the officer should collect additional verification records."

    if len(risk_signals) >= 4:
        reason += " Multiple scoring risk signals should be reviewed."

    if len(graph_risks) >= 1:
        reason += " Network risk signals should be reviewed."

    if len(missing_data) >= 4:
        reason += " Several important records are missing."

    return {
        "recommendation": recommendation,
        "reason": reason,
        "loan_officer_final_decision_required": True,
        "not_an_approval": True,
        "not_a_rejection": True,
        "human_review_options": [
            "Proceed to loan processing",
            "Request more information",
            "Adjust recommended amount",
            "Defer for record building",
            "Manual decline",
        ],
    }


def build_alternative_risk_intelligence(farmer: dict, scoring_result: dict, graph_result: dict | None = None) -> dict:
    graph_result = graph_result or {}

    return {
        "mobile_money_consistency": farmer.get("mobile_money_consistency"),
        "cooperative_repayment_score": farmer.get("cooperative_repayment_score"),
        "peer_lending_reliability": farmer.get("peer_lending_reliability"),
        "seasonal_income_pattern": farmer.get("seasonal_income_pattern"),
        "input_purchase_frequency": farmer.get("input_purchase_frequency"),
        "market_payment_consistency": farmer.get("market_payment_consistency"),
        "alternative_data_used": scoring_result.get("alternative_data_used", []),
        "graph_support_level": graph_result.get("graph_support_level"),
        "trusted_relationship_signals": graph_result.get("trusted_relationship_signals", []),
        "relationship_paths": graph_result.get("relationship_paths", []),
        "exclusion_adjustment_note": scoring_result.get("exclusion_adjustment_note"),
    }


def build_risk_context(farmer: dict) -> dict:
    return {
        "county": farmer.get("county"),
        "area": farmer.get("area"),
        "crop": farmer.get("crop"),
        "crop_stage": farmer.get("crop_stage"),
        "season": farmer.get("season"),
        "climate_risk_level": farmer.get("climate_risk_level"),
        "pest_risk_level": farmer.get("pest_risk_level"),
        "market_delay_risk": farmer.get("market_delay_risk"),
        "localized_pest_outbreak": farmer.get("localized_pest_outbreak"),
        "localized_drought_exposure": farmer.get("localized_drought_exposure"),
    }


def build_inclusion_context(farmer: dict) -> dict:
    return {
        "farmer_type": farmer.get("farmer_type"),
        "gender": farmer.get("gender"),
        "age": farmer.get("age"),
        "is_youth": farmer.get("is_youth"),
        "is_pwd": farmer.get("is_pwd"),
        "disability_type": farmer.get("disability_type"),
        "has_land_title": farmer.get("has_land_title"),
        "phone_type": farmer.get("phone_type"),
        "preferred_channel": farmer.get("preferred_channel"),
        "preferred_language": farmer.get("preferred_language"),
        "literacy_level": farmer.get("literacy_level"),
        "how_used": (
            "These fields are used for fairness monitoring, accessibility, segmentation, "
            "and exclusion-context analysis. They are not used as negative risk penalties."
        ),
    }


def build_farmer_message(farmer: dict, scoring_result: dict) -> dict:
    return {
        "sms": build_farmer_sms(farmer, scoring_result),
        "improvement_tips": build_farmer_improvement_tips(farmer, scoring_result),
        "ussd": build_farmer_ussd_summary(farmer, scoring_result),
        "farmer_safe": True,
    }


def build_decision_support(
    farmer: dict,
    scoring_result: dict,
    fairness: dict,
    graph_result: dict | None = None,
) -> dict:
    graph_result = graph_result or {
        "provider": "not_run",
        "status": "not_run",
        "graph_support_level": "not_available",
        "trusted_relationship_signals": [],
        "network_risk_signals": [],
        "relationship_paths": [],
        "similarity_evidence": [],
        "recommended_verification_path": [],
    }

    return {
        "farmer": {
            "farmer_id": farmer["farmer_id"],
            "name": farmer["name"],
            "county": farmer["county"],
            "area": farmer["area"],
            "crop": farmer["crop"],
            "crop_stage": farmer["crop_stage"],
            "season": farmer["season"],
            "loan_request": farmer["loan_request"],
            "loan_purpose": farmer["loan_purpose"],
        },
        "credit_readiness": scoring_result,
        "graph_intelligence": graph_result,
        "decision_recommendation": build_recommendation(scoring_result, graph_result),
        "alternative_risk_intelligence": build_alternative_risk_intelligence(farmer, scoring_result, graph_result),
        "risk_context": build_risk_context(farmer),
        "inclusion_context": build_inclusion_context(farmer),
        "fairness": fairness,
        "farmer_message": build_farmer_message(farmer, scoring_result),
        "officer_memo": build_officer_memo(farmer, scoring_result, fairness),
    }