from typing import Literal, Optional
from pydantic import BaseModel, Field


class Farmer(BaseModel):
    farmer_id: str
    name: str

    county: str
    area: str
    crop: str
    crop_stage: str
    season: str

    farmer_type: str
    gender: Literal["female", "male"]
    age: int = Field(ge=18, le=100)
    is_youth: bool
    is_pwd: bool
    disability_type: Optional[str] = None
    has_land_title: bool

    phone_number_masked: str
    phone_type: Literal["feature_phone", "smartphone", "shared_phone"]
    preferred_channel: Literal["ussd", "sms", "app", "field_officer"]
    preferred_language: Literal["en", "sw"]
    literacy_level: Literal["low", "medium", "high"]

    loan_request: int = Field(ge=0)
    loan_purpose: str

    completed_repayment_history: bool
    missed_repayment: bool
    has_formal_credit_history: bool
    has_sales_records: bool
    has_buyer_records: bool

    active_savings_group: bool
    savings_group_name: Optional[str] = None
    savings_group_reliability: Literal["none", "weak", "medium", "strong"] = "none"

    cooperative_member: bool
    cooperative_name: Optional[str] = None
    cooperative_reliability: Literal["none", "weak", "medium", "strong"] = "none"
    cooperative_repayment_score: Optional[int] = Field(default=None, ge=0, le=100)

    reliable_buyer: bool
    buyer_name: Optional[str] = None
    buyer_payment_reliability: Literal["none", "weak", "medium", "strong"] = "none"

    verified_input_purchase: bool
    input_purchase_count: int = Field(default=0, ge=0)
    input_purchase_frequency: Literal["none", "low", "medium", "high"] = "none"

    extension_support: bool

    mobile_money_consistency: Literal["unknown", "low", "medium", "high"] = "unknown"
    peer_lending_reliability: Literal["none", "weak", "medium", "strong"] = "none"
    seasonal_income_pattern: Literal["unknown", "volatile", "moderate", "stable"] = "unknown"
    market_payment_consistency: Literal["none", "weak", "medium", "strong"] = "none"

    climate_risk_level: Literal["low", "medium", "high"]
    pest_risk_level: Literal["low", "medium", "high"]
    market_delay_risk: Literal["low", "medium", "high"]
    localized_pest_outbreak: Literal["none", "low", "medium", "high"] = "none"
    localized_drought_exposure: Literal["low", "medium", "high"] = "medium"

    consent_to_process_data: bool = True
    score_confidence: Literal["low", "medium", "high"] = "medium"
