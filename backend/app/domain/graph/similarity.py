def shared_reason(source: dict, target: dict, field: str, label: str) -> str | None:
    if source.get(field) and source.get(field) == target.get(field):
        return label

    return None


def calculate_farmer_similarity(source: dict, target: dict) -> dict:
    reasons = []

    checks = [
        ("county", "same county"),
        ("area", "same area"),
        ("crop", "same crop"),
        ("season", "same season"),
        ("crop_stage", "same crop stage"),
        ("savings_group_reliability", "similar savings group signal"),
        ("cooperative_reliability", "similar cooperative signal"),
        ("buyer_payment_reliability", "similar buyer payment signal"),
        ("market_payment_consistency", "similar market payment signal"),
        ("climate_risk_level", "similar climate risk level"),
        ("pest_risk_level", "similar pest risk level"),
    ]

    for field, label in checks:
        reason = shared_reason(source, target, field, label)

        if reason:
            reasons.append(reason)

    score = min(1.0, round(len(reasons) / 7, 2))

    return {
        "similarity_score": score,
        "shared_reasons": reasons,
    }


def build_similarity_edges(farmers: list[dict]) -> list[dict]:
    edges = []

    for i, source in enumerate(farmers):
        for target in farmers[i + 1:]:
            similarity = calculate_farmer_similarity(source, target)

            if similarity["similarity_score"] >= 0.35:
                edges.append(
                    {
                        "source_farmer_id": source["farmer_id"],
                        "target_farmer_id": target["farmer_id"],
                        "similarity_score": similarity["similarity_score"],
                        "shared_reasons": similarity["shared_reasons"],
                    }
                )

    return edges