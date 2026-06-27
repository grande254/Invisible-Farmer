from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import settings


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_mock_payment_record(job_id: str, farmer_id: str) -> dict:
    return {
        "payment_id": f"IFCR-PAY-{uuid4().hex[:10].upper()}",
        "job_id": job_id,
        "farmer_id": farmer_id,
        "payment_mode": "local_mocked",
        "payment_status": "mocked_confirmed",
        "amount": settings.MASUMI_SERVICE_PRICE_AMOUNT,
        "currency": settings.MASUMI_SERVICE_PRICE_CURRENCY,
        "price_label": f"{settings.MASUMI_SERVICE_PRICE_AMOUNT:g} {settings.MASUMI_SERVICE_PRICE_CURRENCY}",
        "selling_wallet_configured": bool(settings.MASUMI_SELLING_WALLET_ADDRESS),
        "purchase_wallet_configured": bool(settings.MASUMI_PURCHASE_WALLET_ADDRESS),
        "reason": (
            "Local Masumi prototype mode. The agent is registered with wallet and price metadata, "
            "but payment confirmation is mocked so the demo can reliably show job creation, "
            "review execution, audit trail, and human outcome recording."
        ),
        "important_boundary": (
            "This payment record is for prototype workflow demonstration only. It is not a loan "
            "approval, loan rejection, or loan disbursement."
        ),
        "created_at": now_iso(),
    }