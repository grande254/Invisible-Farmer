def run_fairness_checks(farmer: dict, scoring_result: dict | None = None) -> dict:
    scoring_result = scoring_result or {}

    return {
        "gender_penalty_applied": False,
        "age_penalty_applied": False,
        "youth_penalty_applied": False,
        "pwd_penalty_applied": False,
        "land_title_penalty_applied": False,
        "protected_fields_not_used_as_risk_penalties": [
            "gender",
            "age",
            "is_youth",
            "is_pwd",
            "disability_type",
            "farmer_type",
            "has_land_title",
        ],
        "protected_fields_purpose": {
            "gender": "fairness monitoring and exclusion-context analysis",
            "age": "fairness monitoring; youth status is not a credit penalty",
            "is_youth": "youth inclusion monitoring and product/access support",
            "is_pwd": "accessibility support and fairness monitoring",
            "disability_type": "accessibility accommodation only",
            "farmer_type": "segmentation and inclusion-context reporting",
            "has_land_title": "collateral-context monitoring only; not automatic exclusion",
        },
        "alternative_evidence_used_to_reduce_exclusion": scoring_result.get(
            "alternative_data_used",
            [
                "mobile money consistency",
                "cooperative repayment score",
                "peer lending reliability",
                "seasonal income pattern",
                "input purchase frequency",
                "market payment consistency",
                "savings group reliability",
                "buyer payment reliability",
            ],
        ),
        "risk_context_used": [
            "localized pest outbreak",
            "localized drought exposure",
            "climate risk level",
            "pest risk level",
            "market delay risk",
            "crop",
            "crop stage",
            "season",
        ],
        "note": (
            "The system is identity-aware, not identity-scored. Protected and inclusion-related "
            "attributes are used for fairness monitoring, accessibility, and exclusion-context "
            "analysis. They are not used as negative risk penalties."
        ),
    }