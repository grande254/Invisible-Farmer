import json
from functools import lru_cache
from pathlib import Path

import joblib


APP_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = APP_DIR / "models" / "ml_scoring_agent.joblib"
FEATURE_SCHEMA_PATH = APP_DIR / "models" / "ml_scoring_features.json"
METRICS_PATH = APP_DIR / "models" / "ml_scoring_metrics.json"


@lru_cache
def load_ml_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found at {MODEL_PATH}. "
            "Run scripts/train_ml_scoring_model.py first."
        )

    return joblib.load(MODEL_PATH)


@lru_cache
def load_feature_schema() -> dict:
    if not FEATURE_SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Feature schema not found at {FEATURE_SCHEMA_PATH}. "
            "Run scripts/train_ml_scoring_model.py first."
        )

    return json.loads(FEATURE_SCHEMA_PATH.read_text(encoding="utf-8"))


@lru_cache
def load_model_metrics() -> dict:
    if not METRICS_PATH.exists():
        return {
            "available": False,
            "message": "Model metrics file has not been generated yet.",
            "model_type": None,
            "model_version": None,
            "roc_auc": None,
            "accuracy": None,
            "training_rows": None,
            "test_rows": None,
        }

    data = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    data["available"] = True
    return data


def clear_model_cache() -> None:
    load_ml_model.cache_clear()
    load_feature_schema.cache_clear()
    load_model_metrics.cache_clear()


def model_files_status() -> dict:
    return {
        "model_path": str(MODEL_PATH),
        "feature_schema_path": str(FEATURE_SCHEMA_PATH),
        "metrics_path": str(METRICS_PATH),
        "model_exists": MODEL_PATH.exists(),
        "feature_schema_exists": FEATURE_SCHEMA_PATH.exists(),
        "metrics_exists": METRICS_PATH.exists(),
    }