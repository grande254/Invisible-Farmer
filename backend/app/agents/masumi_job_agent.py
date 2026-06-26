from datetime import datetime, timezone
from uuid import uuid4

from app.integrations.masumi.audit import build_final_audit_summary, build_job_audit_entry
from app.integrations.masumi.client import masumi_client
from app.integrations.masumi.job_store import get_job, list_jobs, save_job, update_job
from app.integrations.masumi.payment_service import create_mock_payment_record
from app.integrations.masumi.registry_service import local_agent_card


ALLOWED_HUMAN_OUTCOMES = [
    "Proceed to loan processing",
    "Request more information",
    "Adjust recommended amount",
    "Defer for record building",
    "Manual decline",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MasumiJobAgent:
    name = "Masumi Job and Audit Agent"
    version = "v1"

    def availability(self) -> dict:
        service_status = masumi_client.service_status()

        return {
            "available": True,
            "agent": local_agent_card(),
            "masumi_services": service_status,
            "business_role": (
                "Masumi acts as the job, payment-status, result, and audit layer for the "
                "Invisible Farmer Credit Review Agent."
            ),
        }

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "required": ["farmer_id"],
            "properties": {
                "farmer_id": {
                    "type": "string",
                    "description": "Demo farmer ID. Example: F001, F005, F008, F010.",
                },
                "requested_by": {
                    "type": "string",
                    "description": "Loan officer, branch, SACCO, MFI, or cooperative requesting the review.",
                },
                "purpose": {
                    "type": "string",
                    "description": "Purpose of the credit-readiness review.",
                },
            },
            "important_boundary": (
                "The agent provides decision support only. A human loan officer final decision is required."
            ),
        }

    def start_job(self, farmer_id: str, requested_by: str | None = None, purpose: str | None = None) -> dict:
        from app.domain.review.review_orchestrator import create_credit_review

        job_id = f"MASUMI-IFCR-{uuid4().hex[:12].upper()}"

        job = {
            "job_id": job_id,
            "agent_identifier": masumi_client.agent_identifier,
            "agent_name": masumi_client.agent_name,
            "agent_version": masumi_client.agent_version,
            "farmer_id": farmer_id,
            "requested_by": requested_by or "demo-loan-officer",
            "purpose": purpose or "credit-readiness review",
            "status": "created",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "payment": None,
            "result": None,
            "human_review_outcome": None,
            "audit_events": [],
            "responsible_ai_boundary": {
                "agent_approves_or_rejects_loans": False,
                "agent_disburses_money": False,
                "loan_officer_final_decision_required": True,
            },
        }

        job["audit_events"].append(
            build_job_audit_entry(
                job_id=job_id,
                farmer_id=farmer_id,
                event_type="job_created",
                message="Masumi local job created for farmer credit-readiness review.",
                metadata={
                    "requested_by": job["requested_by"],
                    "purpose": job["purpose"],
                },
            )
        )

        job["payment"] = create_mock_payment_record(job_id=job_id, farmer_id=farmer_id)

        job["audit_events"].append(
            build_job_audit_entry(
                job_id=job_id,
                farmer_id=farmer_id,
                event_type="payment_mocked",
                message="Local mocked payment status attached to Masumi job.",
                metadata=job["payment"],
            )
        )

        job["status"] = "running"
        job["updated_at"] = now_iso()

        save_job(job)

        try:
            review = create_credit_review(farmer_id)

            job["result"] = review
            job["status"] = "completed"
            job["updated_at"] = now_iso()

            decision_support = review.get("decision_support", {})
            credit = decision_support.get("credit_readiness", {})
            graph = decision_support.get("graph_intelligence", {})
            explanation = decision_support.get("featherless_business_explanation", {})

            job["audit_events"].append(
                build_job_audit_entry(
                    job_id=job_id,
                    farmer_id=farmer_id,
                    event_type="review_completed",
                    message="Credit-readiness review completed and attached to Masumi job.",
                    metadata={
                        "review_id": review.get("review_id"),
                        "ml_provider": credit.get("provider"),
                        "ml_score": credit.get("score"),
                        "ml_tier": credit.get("tier"),
                        "graph_provider": graph.get("provider"),
                        "graph_status": graph.get("status"),
                        "featherless_provider": explanation.get("provider"),
                        "featherless_status": explanation.get("status"),
                    },
                )
            )

            save_job(job)

        except Exception as exc:
            job["status"] = "failed"
            job["updated_at"] = now_iso()
            job["error"] = str(exc)

            job["audit_events"].append(
                build_job_audit_entry(
                    job_id=job_id,
                    farmer_id=farmer_id,
                    event_type="review_failed",
                    message="Credit-readiness review failed.",
                    metadata={
                        "error": str(exc),
                    },
                )
            )

            save_job(job)

        return {
            "job_id": job_id,
            "status": job["status"],
            "payment_status": job["payment"]["payment_status"],
            "farmer_id": farmer_id,
            "message": "Masumi local job processed.",
            "status_url": f"/status?job_id={job_id}",
            "full_job_url": f"/v1/masumi/jobs/{job_id}",
        }

    def get_status(self, job_id: str) -> dict:
        job = get_job(job_id)

        if not job:
            raise ValueError(f"Masumi job {job_id} not found")

        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "farmer_id": job["farmer_id"],
            "payment": job.get("payment"),
            "created_at": job.get("created_at"),
            "updated_at": job.get("updated_at"),
            "human_review_outcome": job.get("human_review_outcome"),
            "responsible_ai_boundary": job.get("responsible_ai_boundary"),
        }

    def get_job(self, job_id: str) -> dict:
        job = get_job(job_id)

        if not job:
            raise ValueError(f"Masumi job {job_id} not found")

        job["audit_summary"] = build_final_audit_summary(job)
        return job

    def list_jobs(self) -> list[dict]:
        return list_jobs()

    def record_human_outcome(
        self,
        job_id: str,
        outcome: str,
        officer_name: str | None = None,
        notes: str | None = None,
    ) -> dict:
        if outcome not in ALLOWED_HUMAN_OUTCOMES:
            raise ValueError(
                f"Invalid outcome. Allowed outcomes: {', '.join(ALLOWED_HUMAN_OUTCOMES)}"
            )

        job = get_job(job_id)

        if not job:
            raise ValueError(f"Masumi job {job_id} not found")

        human_review_outcome = {
            "outcome": outcome,
            "officer_name": officer_name or "demo-loan-officer",
            "notes": notes or "",
            "recorded_at": now_iso(),
            "important_boundary": (
                "This is a human loan officer outcome. It is not an autonomous AI approval or rejection."
            ),
        }

        audit_events = job.get("audit_events", [])

        audit_events.append(
            build_job_audit_entry(
                job_id=job_id,
                farmer_id=job["farmer_id"],
                event_type="human_outcome_recorded",
                message="Human loan officer outcome recorded against Masumi job.",
                metadata=human_review_outcome,
            )
        )

        updated = update_job(
            job_id,
            {
                "human_review_outcome": human_review_outcome,
                "audit_events": audit_events,
                "updated_at": now_iso(),
            },
        )

        return {
            "job_id": job_id,
            "status": updated["status"],
            "human_review_outcome": human_review_outcome,
            "audit_summary": build_final_audit_summary(updated),
        }


masumi_job_agent = MasumiJobAgent()