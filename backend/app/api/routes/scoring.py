from fastapi import APIRouter, HTTPException

from app.agents.scoring_agent import scoring_agent
from app.domain.farmer.repository import get_farmer_by_id
from app.domain.ml.model_loader import load_model_metrics


router = APIRouter(prefix="/v1/scoring", tags=["Scoring"])


@router.get("/status", operation_id="scoring_status")
def scoring_status():
    metrics = load_model_metrics()

    return {
        "status": "ready" if metrics.get("available") else "model_not_trained",
        "agent": "ML Scoring Agent",
        "model_type": metrics.get("model_type"),
        "model_version": metrics.get("model_version"),
        "roc_auc": metrics.get("roc_auc"),
        "accuracy": metrics.get("accuracy"),
        "training_rows": metrics.get("training_rows"),
        "test_rows": metrics.get("test_rows"),
        "message": (
            "ML scoring model is available."
            if metrics.get("available")
            else "Train the ML model before scoring."
        ),
    }


@router.get("/metrics", operation_id="get_scoring_metrics")
def get_scoring_metrics():
    return load_model_metrics()


@router.post("/{farmer_id}", operation_id="score_farmer")
def score_farmer(farmer_id: str):
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")

    result = scoring_agent.score(farmer)

    return {
        "farmer_id": farmer["farmer_id"],
        "farmer_name": farmer["name"],
        "credit_readiness": result["scoring_result"],
        "fairness": result["fairness"],
    }