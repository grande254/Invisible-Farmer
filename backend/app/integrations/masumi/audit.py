from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_job_audit_entry(
    job_id: str,
    farmer_id: str,
    event_type: str,
    message: str,
    metadata: dict | None = None,
) -> dict:
    return {
        "timestamp": now_iso(),
        "job_id": job_id,
        "farmer_id": farmer_id,
        "event_type": event_type,
        "message": message,
        "metadata": metadata or {},
    }


def build_final_audit_summary(job: dict) -> dict:
    result = job.get("result") or {}
    decision_support = result.get("decision_support") or {}

    credit = decision_support.get("credit_readiness") or {}
    graph = decision_support.get("graph_intelligence") or {}
    explanation = decision_support.get("featherless_business_explanation") or {}

    return {
        "job_id": job.get("job_id"),
        "farmer_id": job.get("farmer_id"),
        "job_status": job.get("status"),
        "payment_status": (job.get("payment") or {}).get("payment_status"),
        "ml_provider": credit.get("provider"),
        "ml_score": credit.get("score"),
        "ml_tier": credit.get("tier"),
        "graph_provider": graph.get("provider"),
        "graph_status": graph.get("status"),
        "graph_support_level": graph.get("graph_support_level"),
        "featherless_provider": explanation.get("provider"),
        "featherless_status": explanation.get("status"),
        "human_outcome": job.get("human_review_outcome"),
        "important_boundary": (
            "Masumi records the review job and audit trail. The AI agent does not approve, reject, "
            "or disburse loans. A human loan officer final outcome is required."
        ),
        "audit_events": job.get("audit_events", []),
    }