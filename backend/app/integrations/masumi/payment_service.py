from datetime import datetime, timezone
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_mock_payment_record(job_id: str, farmer_id: str) -> dict:
    return {
        "payment_id": f"IFCR-PAY-{uuid4().hex[:10].upper()}",
        "job_id": job_id,
        "farmer_id": farmer_id,
        "payment_mode": "local_mocked",
        "payment_status": "mocked_confirmed",
        "amount": 0,
        "currency": "USD",
        "reason": (
            "Local Masumi development mode. Payment is mocked so the demo can show "
            "job creation, review execution, audit, and human outcome recording."
        ),
        "created_at": now_iso(),
    }