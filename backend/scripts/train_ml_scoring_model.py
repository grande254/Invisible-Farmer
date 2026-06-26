import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from app.domain.ml.feature_builder import (  # noqa: E402
    ALL_FEATURES,
    BOOLEAN_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    PROTECTED_OR_CONTEXT_FIELDS_EXCLUDED_FROM_TRAINING,
    build_training_matrix,
)


DATA_PATH = BACKEND_DIR / "app" / "data" / "synthetic" / "synthetic_farmer_credit_training.csv"
MODEL_DIR = BACKEND_DIR / "app" / "models"
MODEL_PATH = MODEL_DIR / "ml_scoring_agent.joblib"
FEATURE_SCHEMA_PATH = MODEL_DIR / "ml_scoring_features.json"
METRICS_PATH = MODEL_DIR / "ml_scoring_metrics.json"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "target_repaid_on_time"


def group_rate_report(df: pd.DataFrame, prediction_col: str) -> dict:
    report = {}

    for group_col in ["gender", "is_youth", "is_pwd", "farmer_type"]:
        if group_col not in df.columns:
            continue

        group_data = {}

        for group_value, part in df.groupby(group_col):
            group_data[str(group_value)] = {
                "rows": int(len(part)),
                "predicted_ready_rate": round(float(part[prediction_col].mean()), 4),
                "actual_repaid_rate": round(float(part[TARGET].mean()), 4),
            }

        report[group_col] = group_data

    return report


def delete_old_model_files():
    for path in [MODEL_PATH, FEATURE_SCHEMA_PATH, METRICS_PATH]:
        if path.exists():
            path.unlink()


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Synthetic training data not found at {DATA_PATH}. "
            "Run scripts/generate_synthetic_training_data.py first."
        )

    delete_old_model_files()

    df = pd.read_csv(DATA_PATH)

    X = build_training_matrix(df)
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test, train_index, test_index = train_test_split(
        X,
        y,
        df.index,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    boolean_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("bool", boolean_pipeline, BOOLEAN_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    classifier = LogisticRegression(
        max_iter=2500,
        class_weight="balanced",
        solver="lbfgs",
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    pipeline.fit(X_train, y_train)

    probabilities = pipeline.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

    auc = roc_auc_score(y_test, probabilities)
    accuracy = accuracy_score(y_test, predictions)

    test_report_df = df.loc[test_index].copy()
    test_report_df["predicted_ready"] = predictions
    test_report_df["predicted_probability"] = probabilities

    metrics = {
        "model_type": "logistic_regression_scorecard",
        "model_version": "synthetic-v1",
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "roc_auc": round(float(auc), 4),
        "accuracy": round(float(accuracy), 4),
        "classification_report": classification_report(y_test, predictions, output_dict=True),
        "fairness_monitoring_report": group_rate_report(test_report_df, "predicted_ready"),
        "features_used": ALL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "boolean_features": BOOLEAN_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "excluded_from_training": PROTECTED_OR_CONTEXT_FIELDS_EXCLUDED_FROM_TRAINING,
        "sklearn_version": sklearn.__version__,
        "python_executable": sys.executable,
        "important_boundary": (
            "The model predicts repayment readiness for loan officer decision support. "
            "It does not approve, reject, or disburse loans."
        ),
        "fairness_note": (
            "Protected and inclusion-related variables are excluded from training. "
            "They are used for fairness monitoring, accessibility, and exclusion-context analysis."
        ),
    }

    feature_schema = {
        "target": TARGET,
        "all_features": ALL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "boolean_features": BOOLEAN_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "excluded_from_training": PROTECTED_OR_CONTEXT_FIELDS_EXCLUDED_FROM_TRAINING,
        "sklearn_version": sklearn.__version__,
        "python_executable": sys.executable,
    }

    joblib.dump(pipeline, MODEL_PATH)
    FEATURE_SCHEMA_PATH.write_text(json.dumps(feature_schema, indent=2), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("ML scoring model trained.")
    print(f"Python executable: {sys.executable}")
    print(f"scikit-learn version: {sklearn.__version__}")
    print(f"Model: {MODEL_PATH}")
    print(f"Feature schema: {FEATURE_SCHEMA_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print(
        json.dumps(
            {
                "roc_auc": metrics["roc_auc"],
                "accuracy": metrics["accuracy"],
                "training_rows": metrics["training_rows"],
                "test_rows": metrics["test_rows"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()