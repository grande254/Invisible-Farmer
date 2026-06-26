from fastapi import APIRouter, HTTPException

from app.domain.review.review_orchestrator import create_credit_review


router = APIRouter(prefix="/v1/explanations", tags=["Explanations"])


@router.get("/status", operation_id="explanations_status")
def explanations_status():
    return {
        "status": "ready",
        "agent": "Featherless Business Explanation Agent",
        "business_role": (
            "Generates loan officer memo, credit committee brief, branch action plan, "
            "farmer-safe SMS/USSD, missing-data checklist, risk mitigation notes, "
            "inclusion note, audit explanation, and model limitations."
        ),
    }


@router.post("/{farmer_id}", operation_id="generate_farmer_explanations")
def generate_farmer_explanations(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    decision_support = review["decision_support"]

    return {
        "farmer_id": review["farmer_id"],
        "farmer_name": review["farmer_name"],
        "review_id": review["review_id"],
        "featherless_business_explanation": decision_support.get("featherless_business_explanation"),
        "officer_memo": decision_support.get("officer_memo"),
        "credit_committee_brief": decision_support.get("credit_committee_brief"),
        "branch_action_plan": decision_support.get("branch_action_plan"),
        "farmer_message": decision_support.get("farmer_message"),
        "data_collection_checklist": decision_support.get("data_collection_checklist"),
        "risk_mitigation_notes": decision_support.get("risk_mitigation_notes"),
        "audit_explanation": decision_support.get("audit_explanation"),
        "model_limitations": decision_support.get("model_limitations"),
    }