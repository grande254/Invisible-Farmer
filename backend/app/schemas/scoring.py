from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ReasonCode(BaseModel):
    feature: str
    contribution: float


class ModelReasonCodes(BaseModel):
    top_positive_reason_codes: list[ReasonCode] = Field(default_factory=list)
    top_risk_reason_codes: list[ReasonCode] = Field(default_factory=list)


class CreditReadinessResult(BaseModel):
    provider: str
    model_type: Optional[str] = None
    model_version: Optional[str] = None
    score: int = Field(ge=0, le=100)
    repayment_readiness_probability: Optional[float] = None
    tier: str
    recommended_loan_range: str
    confidence: Literal["low", "medium", "high"]
    human_review_required: bool
    positive_signals: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    alternative_data_used: list[str] = Field(default_factory=list)
    model_reason_codes: Optional[ModelReasonCodes] = None
    protected_attributes_excluded_from_training: list[str] = Field(default_factory=list)
    exclusion_adjustment_note: Optional[str] = None
    used_for_final_decision: bool = False
    final_decision_note: str


class ScoringResponse(BaseModel):
    farmer_id: str
    farmer_name: str
    credit_readiness: CreditReadinessResult
    fairness: dict[str, Any]