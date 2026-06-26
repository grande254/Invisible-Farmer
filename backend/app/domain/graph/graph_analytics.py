from app.domain.graph.graph_signals import (
    build_network_risk_signals,
    build_relationship_paths,
    build_similarity_evidence,
    build_trusted_relationship_signals,
    build_verification_path,
    graph_support_level,
)
from app.integrations.neo4j.client import neo4j_client
from app.integrations.neo4j.cypher_queries import (
    GET_FARMER_DIRECT_GRAPH,
    GET_FARMER_SIMILARITY_GRAPH,
    GET_NETWORK_CONCENTRATION,
)


def local_relationships_from_farmer(farmer: dict) -> list[dict]:
    relationships = []

    relationships.append(
        {
            "relationship": "LOCATED_IN",
            "node_labels": ["County"],
            "node": {
                "name": farmer.get("county"),
            },
            "relationship_properties": {
                "business_use": "geographic risk context",
            },
        }
    )

    relationships.append(
        {
            "relationship": "GROWS",
            "node_labels": ["Crop"],
            "node": {
                "name": farmer.get("crop"),
            },
            "relationship_properties": {
                "crop_stage": farmer.get("crop_stage"),
                "season": farmer.get("season"),
                "business_use": "seasonal crop risk context",
            },
        }
    )

    if farmer.get("cooperative_member"):
        relationships.append(
            {
                "relationship": "MEMBER_OF",
                "node_labels": ["Cooperative"],
                "node": {
                    "name": f"{farmer.get('county')} {farmer.get('crop')} Cooperative",
                },
                "relationship_properties": {
                    "reliability": farmer.get("cooperative_reliability"),
                    "repayment_score": farmer.get("cooperative_repayment_score"),
                    "business_use": "cooperative contribution and repayment verification",
                },
            }
        )

    if farmer.get("savings_group_reliability") not in [None, "none", "unknown"]:
        relationships.append(
            {
                "relationship": "SAVES_WITH",
                "node_labels": ["SavingsGroup"],
                "node": {
                    "name": f"{farmer.get('area')} {farmer.get('crop')} Savings Group",
                },
                "relationship_properties": {
                    "reliability": farmer.get("savings_group_reliability"),
                    "business_use": "group savings and social repayment evidence",
                },
            }
        )

    if farmer.get("has_buyer_records") or farmer.get("buyer_payment_reliability") not in [None, "none", "unknown"]:
        relationships.append(
            {
                "relationship": "SELLS_TO",
                "node_labels": ["Buyer"],
                "node": {
                    "name": f"{farmer.get('county')} {farmer.get('crop')} Buyer Network",
                },
                "relationship_properties": {
                    "payment_reliability": farmer.get("buyer_payment_reliability"),
                    "market_payment_consistency": farmer.get("market_payment_consistency"),
                    "business_use": "buyer receipt and market payment verification",
                },
            }
        )

    if farmer.get("verified_input_purchase") or farmer.get("input_purchase_frequency") not in [None, "none", "unknown"]:
        relationships.append(
            {
                "relationship": "BUYS_FROM",
                "node_labels": ["InputSupplier"],
                "node": {
                    "name": f"{farmer.get('county')} Agrovet Supplier Network",
                },
                "relationship_properties": {
                    "input_purchase_frequency": farmer.get("input_purchase_frequency"),
                    "verified_input_purchase": farmer.get("verified_input_purchase"),
                    "business_use": "input purchase and farming activity verification",
                },
            }
        )

    if farmer.get("extension_support"):
        relationships.append(
            {
                "relationship": "ADVISED_BY",
                "node_labels": ["ExtensionOfficer"],
                "node": {
                    "name": f"{farmer.get('area')} Extension Support Desk",
                },
                "relationship_properties": {
                    "extension_support": True,
                    "business_use": "agronomy or extension support verification",
                },
            }
        )

    return relationships


def analyze_graph_from_components(
    farmer: dict,
    direct_relationships: list[dict],
    similar_farmers: list[dict],
    network_concentration: dict | None,
    provider: str,
    status: str,
) -> dict:
    relationship_paths = build_relationship_paths(direct_relationships)
    trusted_relationships = build_trusted_relationship_signals(farmer, direct_relationships)
    network_risk_signals = build_network_risk_signals(farmer)
    similarity_evidence = build_similarity_evidence(similar_farmers)

    support_level = graph_support_level(
        trusted_relationships=trusted_relationships,
        network_risks=network_risk_signals,
        similarity_evidence=similarity_evidence,
    )

    verification_path = build_verification_path(
        farmer=farmer,
        trusted_relationships=trusted_relationships,
        network_risks=network_risk_signals,
    )

    return {
        "provider": provider,
        "status": status,
        "graph_support_level": support_level,
        "business_use": (
            "Graph intelligence converts hidden farmer relationships into verification paths, "
            "network risk context, and alternative evidence for loan officer decision support."
        ),
        "trusted_relationship_signals": trusted_relationships,
        "network_risk_signals": network_risk_signals,
        "relationship_paths": relationship_paths,
        "similarity_evidence": similarity_evidence,
        "network_concentration": network_concentration or {},
        "recommended_verification_path": verification_path,
        "graph_summary": build_graph_summary(
            support_level=support_level,
            trusted_relationships=trusted_relationships,
            network_risk_signals=network_risk_signals,
            relationship_paths=relationship_paths,
        ),
        "score_handling": {
            "does_not_override_ml_score": True,
            "does_not_approve_or_reject": True,
            "used_for": "relationship verification, risk context, and loan officer review guidance",
        },
    }


def build_graph_summary(
    support_level: str,
    trusted_relationships: list[str],
    network_risk_signals: list[str],
    relationship_paths: list[dict],
) -> str:
    if trusted_relationships:
        trust_text = f"{len(trusted_relationships)} trusted relationship signal(s)"
    else:
        trust_text = "no strong relationship signal"

    if network_risk_signals:
        risk_text = f"{len(network_risk_signals)} network risk signal(s)"
    else:
        risk_text = "no material network risk signal"

    return (
        f"Graph support level is {support_level}. "
        f"The graph found {len(relationship_paths)} relationship path(s), {trust_text}, and {risk_text}. "
        f"Use this to verify alternative evidence before the human loan officer records the final outcome."
    )


def analyze_farmer_graph(farmer: dict) -> dict:
    connection = neo4j_client.verify()

    if not connection["available"]:
        direct_relationships = local_relationships_from_farmer(farmer)

        return analyze_graph_from_components(
            farmer=farmer,
            direct_relationships=direct_relationships,
            similar_farmers=[],
            network_concentration={
                "source": "local_fallback",
                "reason": connection.get("status"),
            },
            provider="local_graph_fallback",
            status="fallback",
        )

    try:
        direct_rows = neo4j_client.read(
            GET_FARMER_DIRECT_GRAPH,
            {"farmer_id": farmer["farmer_id"]},
        )

        similarity_rows = neo4j_client.read(
            GET_FARMER_SIMILARITY_GRAPH,
            {"farmer_id": farmer["farmer_id"]},
        )

        network_rows = neo4j_client.read(
            GET_NETWORK_CONCENTRATION,
            {"farmer_id": farmer["farmer_id"]},
        )

        if not direct_rows:
            direct_relationships = local_relationships_from_farmer(farmer)

            return analyze_graph_from_components(
                farmer=farmer,
                direct_relationships=direct_relationships,
                similar_farmers=[],
                network_concentration={
                    "source": "local_fallback",
                    "reason": "farmer_not_imported_to_neo4j",
                },
                provider="local_graph_fallback",
                status="fallback",
            )

        direct_relationships = [
            item for item in direct_rows[0].get("direct_relationships", [])
            if item.get("relationship") is not None
        ]

        similar_farmers = [
            item for item in similarity_rows[0].get("similar_farmers", [])
            if item.get("peer") is not None
        ] if similarity_rows else []

        network_concentration = network_rows[0] if network_rows else {}

        return analyze_graph_from_components(
            farmer=farmer,
            direct_relationships=direct_relationships,
            similar_farmers=similar_farmers,
            network_concentration=network_concentration,
            provider="neo4j_graph_intelligence",
            status="live",
        )

    except Exception as exc:
        direct_relationships = local_relationships_from_farmer(farmer)

        result = analyze_graph_from_components(
            farmer=farmer,
            direct_relationships=direct_relationships,
            similar_farmers=[],
            network_concentration={
                "source": "local_fallback",
                "error": str(exc),
            },
            provider="local_graph_fallback",
            status="fallback",
        )

        result["neo4j_error"] = str(exc)
        return result