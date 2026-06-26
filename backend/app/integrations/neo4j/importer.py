from app.domain.graph.graph_builder import farmer_import_payload
from app.domain.graph.similarity import build_similarity_edges
from app.integrations.neo4j.client import neo4j_client
from app.integrations.neo4j.cypher_queries import (
    CLEAR_DEMO_GRAPH,
    CREATE_CONSTRAINTS,
    LINK_BUYER,
    LINK_COOPERATIVE,
    LINK_COUNTY,
    LINK_CROP,
    LINK_EXTENSION_OFFICER,
    LINK_INPUT_SUPPLIER,
    LINK_SAVINGS_GROUP,
    LINK_SIMILAR_FARMERS,
    UPSERT_FARMER,
)


def should_link_cooperative(farmer: dict) -> bool:
    return bool(farmer.get("cooperative_member"))


def should_link_savings_group(farmer: dict) -> bool:
    return farmer.get("savings_group_reliability") not in [None, "none", "unknown"]


def should_link_buyer(farmer: dict) -> bool:
    return bool(farmer.get("has_buyer_records")) or farmer.get("buyer_payment_reliability") not in [None, "none", "unknown"]


def should_link_supplier(farmer: dict) -> bool:
    return bool(farmer.get("verified_input_purchase")) or farmer.get("input_purchase_frequency") not in [None, "none", "unknown"]


def should_link_extension(farmer: dict) -> bool:
    return bool(farmer.get("extension_support"))


def import_demo_farmers_to_neo4j(farmers: list[dict], clear_existing: bool = True) -> dict:
    status = neo4j_client.verify()

    if not status["available"]:
        return {
            "provider": "neo4j",
            "status": "unavailable",
            "imported": False,
            "connection": status,
        }

    if clear_existing:
        neo4j_client.write(CLEAR_DEMO_GRAPH)

    for query in CREATE_CONSTRAINTS:
        neo4j_client.write(query)

    imported_farmers = 0
    imported_relationships = 0

    for farmer in farmers:
        payload = farmer_import_payload(farmer)

        neo4j_client.write(UPSERT_FARMER, payload)
        imported_farmers += 1

        neo4j_client.write(LINK_COUNTY, payload)
        imported_relationships += 1

        neo4j_client.write(LINK_CROP, payload)
        imported_relationships += 1

        if should_link_cooperative(farmer):
            neo4j_client.write(LINK_COOPERATIVE, payload)
            imported_relationships += 1

        if should_link_savings_group(farmer):
            neo4j_client.write(LINK_SAVINGS_GROUP, payload)
            imported_relationships += 1

        if should_link_buyer(farmer):
            neo4j_client.write(LINK_BUYER, payload)
            imported_relationships += 1

        if should_link_supplier(farmer):
            neo4j_client.write(LINK_INPUT_SUPPLIER, payload)
            imported_relationships += 1

        if should_link_extension(farmer):
            neo4j_client.write(LINK_EXTENSION_OFFICER, payload)
            imported_relationships += 1

    similarity_edges = build_similarity_edges(farmers)

    for edge in similarity_edges:
        neo4j_client.write(LINK_SIMILAR_FARMERS, edge)
        imported_relationships += 1

    return {
        "provider": "neo4j",
        "status": "imported",
        "imported": True,
        "farmers": imported_farmers,
        "relationships": imported_relationships,
        "similarity_edges": len(similarity_edges),
        "business_use": (
            "Neo4j stores farmer relationships with cooperatives, savings groups, buyers, "
            "input suppliers, extension officers, counties, crops, and similar peer profiles."
        ),
    }