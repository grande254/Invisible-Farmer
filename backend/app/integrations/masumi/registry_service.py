import os
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def local_agent_card() -> dict:
    return {
        "agent_identifier": os.getenv(
            "MASUMI_AGENT_IDENTIFIER",
            "local-invisible-farmer-credit-review-agent",
        ),
        "name": os.getenv("MASUMI_AGENT_NAME", "Invisible Farmer Credit Review Agent"),
        "version": os.getenv("MASUMI_AGENT_VERSION", "v2"),
        "mode": os.getenv("MASUMI_MODE", "local"),
        "description": (
            "Masumi-compatible AI business agent for rural lenders. It performs credit-readiness "
            "review using ML scoring, Neo4j relationship intelligence, Featherless explanations, "
            "farmer-safe messaging, and human loan officer outcome recording."
        ),
        "business_user": "Rural SACCO, MFI, cooperative, or agri-finance loan officer",
        "does_not_do": [
            "Does not approve loans",
            "Does not reject farmers automatically",
            "Does not disburse funds",
            "Does not replace human loan officer final decision",
        ],
        "inputs": {
            "farmer_id": "Demo farmer identifier such as F001, F005, F008, or F010",
        },
        "outputs": [
            "credit_readiness_score",
            "alternative_evidence",
            "graph_relationship_intelligence",
            "officer_memo",
            "credit_committee_brief",
            "farmer_sms",
            "ussd_summary",
            "data_collection_checklist",
            "risk_mitigation_notes",
            "audit_trail",
            "human_review_outcome",
        ],
        "created_at": now_iso(),
    }