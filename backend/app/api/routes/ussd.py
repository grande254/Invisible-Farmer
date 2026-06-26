from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.ussd_agent import ussd_agent


router = APIRouter(prefix="/v1/ussd", tags=["Farmer USSD"])


class USSDRequest(BaseModel):
    session_id: Optional[str] = None
    phone_number: Optional[str] = None
    text: Optional[str] = ""


@router.get("/status", operation_id="farmer_ussd_status")
def farmer_ussd_status():
    return {
        "status": "ready",
        "agent": "Farmer USSD Service Agent",
        "business_role": (
            "Lets farmers check review status, request review, receive improvement tips, "
            "and get branch support guidance without smartphone access."
        ),
        "sample_code": "*384*55#",
    }


@router.post("", operation_id="farmer_ussd_session")
def farmer_ussd_session(payload: USSDRequest):
    return ussd_agent.handle(
        text=payload.text,
        phone_number=payload.phone_number,
    )


@router.post("/simulate", operation_id="farmer_ussd_simulate")
def farmer_ussd_simulate(payload: USSDRequest):
    return ussd_agent.handle(
        text=payload.text,
        phone_number=payload.phone_number,
    )