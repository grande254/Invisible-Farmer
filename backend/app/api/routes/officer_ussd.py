from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.officer_branch_agent import officer_branch_agent


router = APIRouter(prefix="/v1/officer-ussd", tags=["Officer Branch USSD"])


class OfficerUSSDRequest(BaseModel):
    session_id: Optional[str] = None
    phone_number: Optional[str] = None
    text: Optional[str] = ""


@router.get("/status", operation_id="officer_ussd_status")
def officer_ussd_status():
    return {
        "status": "ready",
        "agent": "Officer Branch USSD Service Agent",
        "business_role": (
            "Lets rural loan officers start reviews, check summaries, copy farmer messages, "
            "check Masumi job status, and record human outcomes through low-bandwidth USSD."
        ),
        "demo_pin": "1234",
        "important_boundary": (
            "Officer Branch USSD records human outcomes only. It does not approve or reject loans autonomously."
        ),
    }


@router.post("", operation_id="officer_ussd_session")
def officer_ussd_session(payload: OfficerUSSDRequest):
    return officer_branch_agent.handle(
        text=payload.text,
        phone_number=payload.phone_number,
    )


@router.post("/simulate", operation_id="officer_ussd_simulate")
def officer_ussd_simulate(payload: OfficerUSSDRequest):
    return officer_branch_agent.handle(
        text=payload.text,
        phone_number=payload.phone_number,
    )