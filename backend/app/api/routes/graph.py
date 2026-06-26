from fastapi import APIRouter, HTTPException

from app.agents.graph_agent import graph_agent
from app.domain.farmer.repository import get_farmer_by_id, list_farmers
from app.integrations.neo4j.client import neo4j_client
from app.integrations.neo4j.cypher_queries import COUNT_DEMO_GRAPH
from app.integrations.neo4j.importer import import_demo_farmers_to_neo4j


router = APIRouter(prefix="/v1/graph", tags=["Graph Intelligence"])


@router.get("/status", operation_id="graph_status")
def graph_status():
    connection = neo4j_client.verify()

    counts = []

    if connection.get("available"):
        try:
            counts = neo4j_client.read(COUNT_DEMO_GRAPH)
        except Exception as exc:
            counts = [{"error": str(exc)}]

    return {
        "agent": "Neo4j Graph Intelligence Agent",
        "business_role": (
            "Reveals farmer relationship evidence across cooperatives, savings groups, buyers, "
            "input suppliers, extension officers, crops, counties, and similar peer profiles."
        ),
        "connection": connection,
        "demo_graph_counts": counts,
    }


@router.post("/import-demo", operation_id="import_demo_graph")
def import_demo_graph():
    farmers = list_farmers()
    return import_demo_farmers_to_neo4j(farmers, clear_existing=True)


@router.post("/{farmer_id}", operation_id="analyze_farmer_graph")
def analyze_farmer_graph_route(farmer_id: str):
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")

    return {
        "farmer_id": farmer["farmer_id"],
        "farmer_name": farmer["name"],
        "graph_intelligence": graph_agent.analyze(farmer),
    }