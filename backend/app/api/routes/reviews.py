from fastapi import APIRouter, HTTPException

from app.domain.review.review_orchestrator import create_credit_review


router = APIRouter(prefix="/v1/reviews", tags=["Reviews"])


@router.post("/{farmer_id}", operation_id="create_credit_review")
def create_review(farmer_id: str):
    try:
        return create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))