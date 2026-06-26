def is_strong(value) -> bool:
    return str(value).lower() in ["strong", "high", "stable", "reliable", "good"]


def is_weak(value) -> bool:
    return str(value).lower() in ["weak", "low", "none", "unknown", "volatile", "high_risk"]


def relationship_node_name(item: dict) -> str:
    node = item.get("node") or {}
    return node.get("name") or node.get("farmer_id") or "Unknown node"


def relationship_type(item: dict) -> str:
    return item.get("relationship") or "UNKNOWN"


def build_relationship_paths(direct_relationships: list[dict]) -> list[dict]:
    paths = []

    for item in direct_relationships:
        rel = relationship_type(item)

        if not item.get("node"):
            continue

        paths.append(
            {
                "path": f"Farmer -[{rel}]-> {relationship_node_name(item)}",
                "relationship": rel,
                "business_use": (item.get("relationship_properties") or {}).get("business_use"),
            }
        )

    return paths


def build_trusted_relationship_signals(farmer: dict, direct_relationships: list[dict]) -> list[str]:
    signals = []

    if is_strong(farmer.get("savings_group_reliability")):
        signals.append("Savings group relationship can support social repayment evidence.")

    if is_strong(farmer.get("cooperative_reliability")):
        signals.append("Cooperative relationship can support contribution, delivery, or repayment verification.")

    if is_strong(farmer.get("buyer_payment_reliability")) or is_strong(farmer.get("market_payment_consistency")):
        signals.append("Buyer or market payment relationship can support produce sales verification.")

    if is_strong(farmer.get("input_purchase_frequency")):
        signals.append("Input supplier relationship can verify active farming investment.")

    if farmer.get("extension_support"):
        signals.append("Extension officer relationship can support crop management verification.")

    if farmer.get("mobile_money_consistency") == "high":
        signals.append("Mobile money pattern provides additional relationship-adjacent transaction evidence.")

    relationship_types = {relationship_type(item) for item in direct_relationships}

    if "MEMBER_OF" in relationship_types and "SAVES_WITH" in relationship_types:
        signals.append("Farmer has both cooperative and savings-group verification paths.")

    return signals


def build_network_risk_signals(farmer: dict) -> list[str]:
    risks = []

    if farmer.get("localized_drought_exposure") == "high" or farmer.get("climate_risk_level") == "high":
        risks.append("High climate or drought exposure should be reviewed against repayment timing.")

    if farmer.get("localized_pest_outbreak") == "high" or farmer.get("pest_risk_level") == "high":
        risks.append("High pest exposure should be reviewed with extension or input supplier evidence.")

    if farmer.get("market_delay_risk") == "high":
        risks.append("High market delay risk may affect repayment schedule timing.")

    if is_weak(farmer.get("buyer_payment_reliability")):
        risks.append("Weak buyer payment reliability may reduce confidence in sales-based repayment evidence.")

    if is_weak(farmer.get("cooperative_reliability")) and farmer.get("cooperative_member"):
        risks.append("Cooperative exists but reliability is weak; verify records before loan processing.")

    return risks


def build_similarity_evidence(similar_farmers: list[dict]) -> list[dict]:
    evidence = []

    for item in similar_farmers:
        peer = item.get("peer") or {}

        if not peer:
            continue

        evidence.append(
            {
                "peer_farmer_id": peer.get("farmer_id"),
                "peer_name": peer.get("name"),
                "similarity_score": item.get("similarity_score"),
                "shared_reasons": item.get("shared_reasons", []),
                "business_use": (
                    "Peer similarity helps the loan officer compare this farmer against similar branch profiles. "
                    "It does not approve or reject the farmer."
                ),
            }
        )

    return sorted(
        evidence,
        key=lambda item: item.get("similarity_score") or 0,
        reverse=True,
    )[:5]


def graph_support_level(
    trusted_relationships: list[str],
    network_risks: list[str],
    similarity_evidence: list[dict],
) -> str:
    trusted_count = len(trusted_relationships)
    risk_count = len(network_risks)
    peer_count = len(similarity_evidence)

    if trusted_count >= 4 and risk_count == 0:
        return "strong"

    if trusted_count >= 3 and risk_count <= 1:
        return "moderate_to_strong"

    if trusted_count >= 2 or peer_count >= 1:
        return "moderate"

    if trusted_count == 1:
        return "limited"

    return "thin_graph"


def build_verification_path(
    farmer: dict,
    trusted_relationships: list[str],
    network_risks: list[str],
) -> list[str]:
    steps = [
        "Confirm farmer identity, KYC details, and consent to use relationship evidence.",
    ]

    if is_strong(farmer.get("savings_group_reliability")):
        steps.append("Verify savings group contributions or repayment references.")

    if farmer.get("cooperative_member"):
        steps.append("Verify cooperative membership, contributions, produce delivery, or repayment score.")

    if farmer.get("has_buyer_records") or farmer.get("buyer_payment_reliability") not in [None, "none", "unknown"]:
        steps.append("Verify buyer receipts, produce sales records, or market payment confirmations.")

    if farmer.get("verified_input_purchase") or is_strong(farmer.get("input_purchase_frequency")):
        steps.append("Verify input purchase receipts from agrovet or supplier.")

    if farmer.get("extension_support"):
        steps.append("Verify extension officer or agronomist support record.")

    if network_risks:
        steps.append("Discuss network risk signals with the farmer and record mitigation notes.")

    steps.append("Record human loan officer outcome before any normal loan processing step.")

    deduped = []

    for step in steps:
        if step not in deduped:
            deduped.append(step)

    return deduped