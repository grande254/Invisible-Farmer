import pandas as pd


NUMERIC_FEATURES = [
    "loan_request",
    "input_purchase_count",
    "cooperative_repayment_score",
]

BOOLEAN_FEATURES = [
    "completed_repayment_history",
    "missed_repayment",
    "has_formal_credit_history",
    "has_sales_records",
    "has_buyer_records",
    "active_savings_group",
    "cooperative_member",
    "reliable_buyer",
    "verified_input_purchase",
    "extension_support",
]

CATEGORICAL_FEATURES = [
    "county",
    "crop",
    "crop_stage",
    "season",
    "savings_group_reliability",
    "cooperative_reliability",
    "buyer_payment_reliability",
    "mobile_money_consistency",
    "peer_lending_reliability",
    "seasonal_income_pattern",
    "localized_pest_outbreak",
    "localized_drought_exposure",
    "input_purchase_frequency",
    "market_payment_consistency",
    "climate_risk_level",
    "pest_risk_level",
    "market_delay_risk",
]

ALL_FEATURES = NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES

PROTECTED_OR_CONTEXT_FIELDS_EXCLUDED_FROM_TRAINING = [
    "farmer_id",
    "name",
    "gender",
    "age",
    "is_youth",
    "is_pwd",
    "disability_type",
    "farmer_type",
    "has_land_title",
    "phone_number_masked",
    "phone_type",
    "preferred_channel",
    "preferred_language",
    "literacy_level",
    "repayment_outcome",
    "latent_repayment_probability",
    "target_repaid_on_time",
]


def default_value(feature: str):
    defaults = {
        "loan_request": 0,
        "input_purchase_count": 0,
        "cooperative_repayment_score": None,

        "completed_repayment_history": False,
        "missed_repayment": False,
        "has_formal_credit_history": False,
        "has_sales_records": False,
        "has_buyer_records": False,
        "active_savings_group": False,
        "cooperative_member": False,
        "reliable_buyer": False,
        "verified_input_purchase": False,
        "extension_support": False,

        "county": "unknown",
        "crop": "unknown",
        "crop_stage": "unknown",
        "season": "unknown",
        "savings_group_reliability": "none",
        "cooperative_reliability": "none",
        "buyer_payment_reliability": "none",
        "mobile_money_consistency": "unknown",
        "peer_lending_reliability": "none",
        "seasonal_income_pattern": "unknown",
        "localized_pest_outbreak": "none",
        "localized_drought_exposure": "medium",
        "input_purchase_frequency": "none",
        "market_payment_consistency": "none",
        "climate_risk_level": "medium",
        "pest_risk_level": "medium",
        "market_delay_risk": "medium",
    }

    return defaults.get(feature)


def to_binary(value) -> int:
    if value in [True, 1, "1", "true", "True", "yes", "Yes"]:
        return 1

    return 0


def build_feature_row(farmer: dict, features: list[str] | None = None) -> pd.DataFrame:
    features = features or ALL_FEATURES

    row = {}

    for feature in features:
        value = farmer.get(feature, default_value(feature))

        if feature in BOOLEAN_FEATURES:
            value = to_binary(value)

        row[feature] = value

    return pd.DataFrame([row])


def build_training_matrix(df: pd.DataFrame) -> pd.DataFrame:
    matrix = df[ALL_FEATURES].copy()

    for column in BOOLEAN_FEATURES:
        matrix[column] = matrix[column].apply(to_binary).astype("int64")

    return matrix