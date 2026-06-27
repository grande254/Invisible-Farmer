from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import settings
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


def setting(name: str, default=None):
    return getattr(settings, name, default)


class MasumiJobAgent:
    name = "Masumi Job and Audit Agent"
    version = "v1"

    def availability(self) -> dict:
        service_status = masumi_client.service_status()

        price_amount = setting("MASUMI_SERVICE_PRICE_AMOUNT", 50)
        price_currency = setting("MASUMI_SERVICE_PRICE_CURRENCY", "ADA")
        payment_type = setting("MASUMI_PAYMENT_TYPE", "local_mocked")

        return {
            "available": True,
            "agent": local_agent_card(),
            "masumi_services": service_status,
            "payment": {
                "payment_type": payment_type,
                "payment_enforced": False,
                "payment_status": "mocked_confirmed",
                "price": {
                    "amount": price_amount,
                    "currency": price_currency,
                    "label": f"{price_amount:g} {price_currency}",
                },
                "selling_wallet_configured": bool(
                    setting("MASUMI_SELLING_WALLET_ADDRESS")
                ),
                "purchase_wallet_configured": bool(
                    setting("MASUMI_PURCHASE_WALLET_ADDRESS")
                ),
                "prototype_note": (
                    "Payment confirmation is mocked locally for the prototype demo. "
                    "The registered Masumi agent can still show wallet and price metadata."
                ),
            },
            "business_role": (
                "Masumi acts as the job, mocked payment-status, result, and audit layer "
                "for the Invisible Farmer Credit Review Agent."
            ),
        }

    def input_schema(self) -> dict:
        price_amount = setting("MASUMI_SERVICE_PRICE_AMOUNT", 50)
        price_currency = setting("MASUMI_SERVICE_PRICE_CURRENCY", "ADA")

        return {
            "type": "object",
            "required": ["farmer_id"],
            "properties": {
                "farmer_id": {
                    "type": "string",
                    "description": "Demo farmer ID. Example: F001, F005, F008, F010, F015, F018.",
                },
                "requested_by": {
                    "type": "string",
                    "description": "Loan officer, branch, SACCO, MFI, or cooperative requesting the review.",
                },
                "purpose": {
                    "type": "string",
                    "description": "Purpose of the credit-readiness review.",
                },
                "tx_hash": {
                    "type": "string",
                    "description": (
                        "Optional. Ignored in local mocked payment mode. "
                        "Kept only so previous frontend/API calls do not break."
                    ),
                },
            },
            "price": {
                "amount": price_amount,
                "currency": price_currency,
                "label": f"{price_amount:g} {price_currency}",
            },
            "payment_mode": "local_mocked",
            "important_boundary": (
                "The agent provides decision support only. A human loan officer final decision is required."
            ),
        }

    def _new_job(
        self,
        farmer_id: str,
        requested_by: str | None,
        purpose: str | None,
    ) -> dict:
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
                message="Masumi workflow job created for farmer credit-readiness review.",
                metadata={
                    "requested_by": job["requested_by"],
                    "purpose": job["purpose"],
                },
            )
        )

        return job

    def _attach_mock_payment(self, job: dict) -> dict:
        job_id = job["job_id"]
        farmer_id = job["farmer_id"]

        job["payment"] = create_mock_payment_record(
            job_id=job_id,
            farmer_id=farmer_id,
        )

        job["audit_events"].append(
            build_job_audit_entry(
                job_id=job_id,
                farmer_id=farmer_id,
                event_type="payment_mocked",
                message="Local mocked Masumi payment confirmation attached to workflow job.",
                metadata=job["payment"],
            )
        )

        job["updated_at"] = now_iso()
        return job

    def _run_review_for_job(self, job: dict) -> dict:
        from app.domain.review.review_orchestrator import create_credit_review

        job["status"] = "running"
        job["updated_at"] = now_iso()
        save_job(job)

        farmer_id = job["farmer_id"]
        job_id = job["job_id"]

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
                    message=(
                        "Credit-readiness review completed after local mocked "
                        "Masumi payment confirmation."
                    ),
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
                    metadata={"error": str(exc)},
                )
            )

            save_job(job)

        return job

    def start_job(
        self,
        farmer_id: str,
        requested_by: str | None = None,
        purpose: str | None = None,
        tx_hash: str | None = None,
    ) -> dict:
        job = self._new_job(
            farmer_id=farmer_id,
            requested_by=requested_by,
            purpose=purpose,
        )

        job_id = job["job_id"]

        if tx_hash:
            job["audit_events"].append(
                build_job_audit_entry(
                    job_id=job_id,
                    farmer_id=farmer_id,
                    event_type="tx_hash_received_but_not_verified",
                    message=(
                        "A transaction hash was received, but this prototype is running "
                        "in local mocked payment mode, so the hash was not verified."
                    ),
                    metadata={
                        "tx_hash_present": True,
                        "payment_mode": "local_mocked",
                    },
                )
            )

        job = self._attach_mock_payment(job)
        save_job(job)

        job = self._run_review_for_job(job)

        return {
            "job_id": job_id,
            "status": job["status"],
            "payment_status": job["payment"]["payment_status"],
            "payment": job["payment"],
            "farmer_id": farmer_id,
            "message": "Masumi local mocked-payment job processed.",
            "status_url": f"/status?job_id={job_id}",
            "full_job_url": f"/v1/masumi/jobs/{job_id}",
        }

    def verify_payment_and_run(self, job_id: str, tx_hash: str | None = None) -> dict:
        """
        Compatibility endpoint for older frontend/routes.

        In local mocked mode, payment verification is not enforced. If the job has
        not run yet, this confirms a mocked payment and runs the review.
        """
        job = get_job(job_id)

        if not job:
            raise ValueError(f"Masumi job {job_id} not found")

        if job.get("status") == "completed":
            return {
                "job_id": job_id,
                "status": job["status"],
                "payment": job.get("payment"),
                "message": "Job is already completed.",
            }

        if tx_hash:
            job["audit_events"].append(
                build_job_audit_entry(
                    job_id=job_id,
                    farmer_id=job["farmer_id"],
                    event_type="tx_hash_received_but_not_verified",
                    message=(
                        "A transaction hash was received through verify-payment, "
                        "but local mocked payment mode does not verify blockchain transactions."
                    ),
                    metadata={
                        "tx_hash_present": True,
                        "payment_mode": "local_mocked",
                    },
                )
            )

        job = self._attach_mock_payment(job)
        save_job(job)

        job = self._run_review_for_job(job)

        return {
            "job_id": job_id,
            "status": job["status"],
            "payment": job["payment"],
            "message": "Mock payment confirmed. Credit-readiness review completed.",
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
            "result_available": bool(job.get("result")),
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