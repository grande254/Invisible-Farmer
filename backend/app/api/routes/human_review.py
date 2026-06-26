from fastapi import APIRouter

router = APIRouter(prefix="/v1/human-review", tags=["Human Review"])


@router.get("/status", operation_id="human_review_status")
def human_review_status():
    return {
        "status": "placeholder",
        "message": "Human review outcome service will be added later."
    }
