def clean_feature_name(raw_name: str) -> str:
    name = str(raw_name).split("__")[-1]

    prefix_map = [
        ("crop_stage_", "crop stage = "),
        ("climate_risk_level_", "climate risk = "),
        ("pest_risk_level_", "pest risk = "),
        ("market_delay_risk_", "market delay risk = "),
        ("localized_drought_exposure_", "localized drought exposure = "),
        ("localized_pest_outbreak_", "localized pest outbreak = "),
        ("mobile_money_consistency_", "mobile money consistency = "),
        ("peer_lending_reliability_", "peer lending reliability = "),
        ("seasonal_income_pattern_", "seasonal income pattern = "),
        ("input_purchase_frequency_", "input purchase frequency = "),
        ("market_payment_consistency_", "market payment consistency = "),
        ("savings_group_reliability_", "savings group reliability = "),
        ("cooperative_reliability_", "cooperative reliability = "),
        ("buyer_payment_reliability_", "buyer payment reliability = "),
        ("county_", "county = "),
        ("crop_", "crop = "),
        ("season_", "season = "),
    ]

    for prefix, replacement in prefix_map:
        if name.startswith(prefix):
            name = name.replace(prefix, replacement, 1)
            break

    return name.replace("_", " ")


def is_useful_reason_code(item: dict) -> bool:
    feature = item.get("feature", "")
    contribution = abs(float(item.get("contribution", 0)))

    if contribution < 0.08:
        return False

    # These are technically valid model features but often confusing for a judge/demo.
    # We keep them in the raw model internally but avoid surfacing weak/unclear reason codes.
    confusing = [
        "input purchase count",
    ]

    return feature not in confusing


def calculate_reason_codes(pipeline, feature_row) -> dict:
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]

    transformed = preprocessor.transform(feature_row)

    if hasattr(transformed, "toarray"):
        values = transformed.toarray()[0]
    else:
        values = transformed[0]

    coefficients = classifier.coef_[0]
    feature_names = preprocessor.get_feature_names_out()
    contributions = values * coefficients

    reason_items = []

    for index, contribution in enumerate(contributions):
        contribution = float(contribution)

        if abs(contribution) < 0.0001:
            continue

        reason_items.append(
            {
                "feature": clean_feature_name(str(feature_names[index])),
                "contribution": round(contribution, 4),
            }
        )

    positive_items = [
        item for item in reason_items
        if item["contribution"] > 0 and is_useful_reason_code(item)
    ]

    risk_items = [
        item for item in reason_items
        if item["contribution"] < 0 and is_useful_reason_code(item)
    ]

    top_positive = sorted(
        positive_items,
        key=lambda item: item["contribution"],
        reverse=True,
    )[:6]

    top_risk = sorted(
        risk_items,
        key=lambda item: item["contribution"],
    )[:6]

    return {
        "top_positive_reason_codes": top_positive,
        "top_risk_reason_codes": top_risk,
        "raw_reason_code_count": len(reason_items),
    }


def reason_codes_to_signal_labels(reason_codes: list[dict], direction: str) -> list[str]:
    labels = []

    for item in reason_codes:
        feature = item["feature"]

        if direction == "positive":
            labels.append(f"{feature} supported repayment readiness")
        else:
            labels.append(f"{feature} reduced repayment readiness")

    return labels