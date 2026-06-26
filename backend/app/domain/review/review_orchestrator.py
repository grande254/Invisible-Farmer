from datetime import datetime, timezone
from uuid import uuid4

from app.agents.explanation_agent import explanation_agent
from app.agents.graph_agent import graph_agent
from app.agents.scoring_agent import scoring_agent
from app.domain.farmer.repository import get_farmer_by_id
from app.domain.review.decision_support import build_decision_support


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_credit_review(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        raise ValueError(f"Farmer {farmer_id} not found")

    scoring_agent_result = scoring_agent.score(farmer)
    scoring_result = scoring_agent_result["scoring_result"]
    fairness = scoring_agent_result["fairness"]

    graph_result = graph_agent.analyze(
        farmer=farmer,
        scoring_result=scoring_result,
    )

    decision_support = build_decision_support(
        farmer=farmer,
        scoring_result=scoring_result,
        fairness=fairness,
        graph_result=graph_result,
    )

    decision_support = explanation_agent.enrich(decision_support)

    explanation_status = decision_support.get(
        "featherless_business_explanation",
        {},
    ).get("status", "unknown")

    graph_status = graph_result.get("status", "unknown")

    review_id = f"IFCR-REV-{uuid4().hex[:10].upper()}"

    return {
        "review_id": review_id,
        "created_at": now_iso(),
        "review_type": "credit_readiness_review",
        "agent_name": "Invisible Farmer Credit Review Agent",
        "agent_version": "v2",
        "farmer_id": farmer["farmer_id"],
        "farmer_name": farmer["name"],
        "status": "completed",
        "decision_support": decision_support,
        "module_status": {
            "ml_scoring_agent": "live",
            "fairness_checks": "live",
            "farmer_safe_messages": "live",
            "featherless_explanations": explanation_status,
            "neo4j_graph_intelligence": graph_status,
            "masumi_job_audit": "planned_stage_6",
            "human_review_outcome": "planned_stage_6",
        },
        "responsible_ai_boundary": {
            "agent_approves_or_rejects_loans": False,
            "agent_disburses_money": False,
            "loan_officer_final_decision_required": True,
            "message": (
                "This agent prepares credit-readiness decision support only. "
                "A human loan officer must make and record the final review outcome."
            ),
        },
    }