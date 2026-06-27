from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.masumi_job_agent import ALLOWED_HUMAN_OUTCOMES, masumi_job_agent


router = APIRouter(tags=["Masumi"])


class StartJobRequest(BaseModel):
    farmer_id: str
    requested_by: Optional[str] = None
    purpose: Optional[str] = None
    tx_hash: Optional[str] = None


class VerifyPaymentRequest(BaseModel):
    tx_hash: str


class HumanOutcomeRequest(BaseModel):
    outcome: str
    officer_name: Optional[str] = None
    notes: Optional[str] = None


@router.get("/availability", operation_id="masumi_availability")
def availability():
    return masumi_job_agent.availability()


@router.get("/input_schema", operation_id="masumi_input_schema")
def input_schema():
    return masumi_job_agent.input_schema()


@router.post("/start_job", operation_id="masumi_start_job")
def start_job(payload: StartJobRequest):
    return masumi_job_agent.start_job(
        farmer_id=payload.farmer_id,
        requested_by=payload.requested_by,
        purpose=payload.purpose,
        tx_hash=payload.tx_hash,
    )


@router.get("/status", operation_id="masumi_job_status")
def status(job_id: str):
    try:
        return masumi_job_agent.get_status(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/v1/masumi/availability", operation_id="v1_masumi_availability")
def v1_availability():
    return masumi_job_agent.availability()


@router.get("/v1/masumi/input-schema", operation_id="v1_masumi_input_schema")
def v1_input_schema():
    return masumi_job_agent.input_schema()


@router.post("/v1/masumi/start-job", operation_id="v1_masumi_start_job")
def v1_start_job(payload: StartJobRequest):
    return masumi_job_agent.start_job(
        farmer_id=payload.farmer_id,
        requested_by=payload.requested_by,
        purpose=payload.purpose,
        tx_hash=payload.tx_hash,
    )

@router.post("/v1/masumi/jobs/{job_id}/verify-payment", operation_id="v1_masumi_verify_payment")
def v1_verify_payment(job_id: str, payload: VerifyPaymentRequest):
    try:
        return masumi_job_agent.verify_payment_and_run(
            job_id=job_id,
            tx_hash=payload.tx_hash,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    
@router.get("/v1/masumi/jobs/{job_id}/payment", operation_id="v1_masumi_job_payment")
def v1_get_job_payment(job_id: str):
    try:
        job = masumi_job_agent.get_job(job_id)
        return {
            "job_id": job_id,
            "payment": job.get("payment"),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    

@router.get("/v1/masumi/jobs", operation_id="v1_masumi_list_jobs")
def v1_list_jobs():
    return {
        "jobs": masumi_job_agent.list_jobs(),
    }


@router.get("/v1/masumi/jobs/{job_id}", operation_id="v1_masumi_get_job")
def v1_get_job(job_id: str):
    try:
        return masumi_job_agent.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/v1/masumi/jobs/{job_id}/human-outcome", operation_id="v1_masumi_record_human_outcome")
def v1_record_human_outcome(job_id: str, payload: HumanOutcomeRequest):
    try:
        return masumi_job_agent.record_human_outcome(
            job_id=job_id,
            outcome=payload.outcome,
            officer_name=payload.officer_name,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/v1/masumi/human-outcome-options", operation_id="v1_masumi_human_outcome_options")
def v1_human_outcome_options():
    return {
        "allowed_outcomes": ALLOWED_HUMAN_OUTCOMES,
        "important_boundary": (
            "Proceed to loan processing is not an approval. It means the loan officer may continue "
            "normal institutional loan processing after reviewing the agent output."
        ),
    }