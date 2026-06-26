import json
import sys
from pathlib import Path

import joblib
import sklearn


BACKEND_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BACKEND_DIR / "app" / "models"

MODEL_PATH = MODEL_DIR / "ml_scoring_agent.joblib"
FEATURE_SCHEMA_PATH = MODEL_DIR / "ml_scoring_features.json"
METRICS_PATH = MODEL_DIR / "ml_scoring_metrics.json"


def main():
    print("Python executable:")
    print(sys.executable)
    print()

    print("scikit-learn version:")
    print(sklearn.__version__)
    print()

    print("Model files:")
    print({
        "model_exists": MODEL_PATH.exists(),
        "feature_schema_exists": FEATURE_SCHEMA_PATH.exists(),
        "metrics_exists": METRICS_PATH.exists(),
        "model_path": str(MODEL_PATH),
    })
    print()

    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        print("Saved model metrics:")
        print(json.dumps({
            "model_type": metrics.get("model_type"),
            "model_version": metrics.get("model_version"),
            "roc_auc": metrics.get("roc_auc"),
            "accuracy": metrics.get("accuracy"),
            "sklearn_version": metrics.get("sklearn_version"),
            "python_executable": metrics.get("python_executable"),
        }, indent=2))
        print()

    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            print("Model load test: OK")
            print(type(model))
        except Exception as exc:
            print("Model load test: FAILED")
            print(str(exc))


if __name__ == "__main__":
    main()