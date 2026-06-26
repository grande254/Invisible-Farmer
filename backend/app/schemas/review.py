from typing import Any, Optional

from pydantic import BaseModel, Field


class ReviewFarmerSummary(BaseModel):
    farmer_id: str
    name: str
    county: str
    area: str
    crop: str
    crop_stage: str
    season: str
    loan_request: int
    loan_purpose: str


class DecisionRecommendation(BaseModel):
    recommendation: str
    reason: str
    loan_officer_final_decision_required: bool = True
    not_an_approval: bool = True
    not_a_rejection: bool = True
    human_review_options: list[str] = Field(default_factory=list)


class FarmerMessage(BaseModel):
    sms: str
    improvement_tips: list[str] = Field(default_factory=list)
    ussd: dict[str, Any]
    farmer_safe: bool = True


class DecisionSupport(BaseModel):
    farmer: ReviewFarmerSummary
    credit_readiness: dict[str, Any]
    decision_recommendation: DecisionRecommendation
    alternative_risk_intelligence: dict[str, Any]
    risk_context: dict[str, Any]
    inclusion_context: dict[str, Any]
    fairness: dict[str, Any]
    farmer_message: FarmerMessage
    officer_memo: str


class CreditReviewResponse(BaseModel):
    review_id: str
    created_at: str
    review_type: str
    agent_name: str
    agent_version: str
    farmer_id: str
    farmer_name: str
    status: str
    decision_support: DecisionSupport
    module_status: dict[str, str]
    responsible_ai_boundary: dict[str, Any]