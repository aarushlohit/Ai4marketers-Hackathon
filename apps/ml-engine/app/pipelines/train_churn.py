"""
Churn Prediction Training Pipeline

Usage:
    python -m app.pipelines.train_churn

Steps:
  1. Load training data from PostgreSQL
  2. Compute features via feature engineering pipeline
  3. Train XGBoost model with cross-validation
  4. Evaluate on held-out test set (AUC-ROC, F1)
  5. Log to MLflow experiment
  6. Save model to models/saved/churn_model.joblib
"""

import json
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import structlog
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    classification_report,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

logger = structlog.get_logger()

MODELS_DIR = Path(__file__).parent.parent.parent / "models" / "saved"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MLFLOW_EXPERIMENT = "churn_prediction"

# XGBoost hyperparameters (tuned via Optuna in production)
XGBOOST_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 3,
    "scale_pos_weight": 3,  # class imbalance: ~3:1 non-churn:churn
    "use_label_encoder": False,
    "eval_metric": "auc",
    "random_state": 42,
    "n_jobs": -1,
}


def load_training_data() -> tuple[pd.DataFrame, pd.Series]:
    """
    Load labelled training data.
    In production: query PostgreSQL for customers with known churn outcome.
    Here we generate a synthetic dataset for dev/testing.
    """
    np.random.seed(42)
    n = 5000

    # Simulate realistic feature distributions
    data = pd.DataFrame({
        "days_since_last_interaction": np.random.exponential(30, n),
        "interaction_count_30d": np.random.poisson(4, n),
        "interaction_count_90d": np.random.poisson(12, n),
        "interaction_velocity": np.random.uniform(0, 1.5, n),
        "email_count_90d": np.random.poisson(6, n),
        "call_count_90d": np.random.poisson(2, n),
        "meeting_count_90d": np.random.poisson(1, n),
        "avg_sentiment_30d": np.random.beta(5, 2, n),
        "negative_sentiment_ratio": np.random.beta(1, 5, n),
        "account_age_days": np.random.randint(30, 1825, n),
        "has_email": np.random.binomial(1, 0.9, n),
        "has_phone": np.random.binomial(1, 0.7, n),
        "has_company": np.random.binomial(1, 0.8, n),
        "health_score": np.random.normal(68, 18, n).clip(0, 100),
        "lead_score": np.random.randint(10, 100, n),
        "log_lifetime_value": np.random.normal(8, 2, n).clip(0),
        "status_encoded": np.random.choice([1, 0, -1], n, p=[0.7, 0.2, 0.1]),
    })

    # Simulate churn label: correlated with low engagement + low health
    churn_prob = (
        0.3 * (data["days_since_last_interaction"] > 60).astype(float)
        + 0.25 * (data["health_score"] < 50).astype(float)
        + 0.2 * (data["negative_sentiment_ratio"] > 0.4).astype(float)
        + 0.15 * (data["interaction_count_30d"] < 2).astype(float)
        + 0.1 * np.random.uniform(0, 1, n)
    ).clip(0, 1)
    labels = (churn_prob > 0.5).astype(int)

    logger.info(
        "Training data loaded",
        samples=n,
        churn_rate=f"{labels.mean():.1%}",
    )
    return data, labels


def train() -> dict:
    """Run the full training pipeline. Returns evaluation metrics."""
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    X, y = load_training_data()

    model_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", XGBClassifier(**XGBOOST_PARAMS)),
    ])

    with mlflow.start_run(run_name="churn_xgboost") as run:
        mlflow.log_params(XGBOOST_PARAMS)

        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_auc = cross_val_score(model_pipeline, X, y, cv=cv,
                                  scoring="roc_auc", n_jobs=-1)
        mlflow.log_metric("cv_auc_mean", cv_auc.mean())
        mlflow.log_metric("cv_auc_std", cv_auc.std())
        logger.info(
            "Cross-validation complete",
            auc_mean=f"{cv_auc.mean():.4f}",
            auc_std=f"{cv_auc.std():.4f}",
        )

        # Final fit on all data
        model_pipeline.fit(X, y)

        # Evaluate on training set (full eval should use held-out test set)
        y_pred = model_pipeline.predict(X)
        y_prob = model_pipeline.predict_proba(X)[:, 1]
        auc = roc_auc_score(y, y_prob)
        f1 = f1_score(y, y_pred)

        mlflow.log_metric("train_auc", auc)
        mlflow.log_metric("train_f1", f1)
        mlflow.sklearn.log_model(model_pipeline, "churn_model")

        # Save locally for ModelRegistry to pick up
        model_path = MODELS_DIR / "churn_model.joblib"
        joblib.dump(model_pipeline, model_path)

        feature_names = list(X.columns)
        feat_path = MODELS_DIR / "churn_features.json"
        feat_path.write_text(json.dumps(feature_names))

        metrics = {
            "run_id": run.info.run_id,
            "cv_auc_mean": round(cv_auc.mean(), 4),
            "train_auc": round(auc, 4),
            "train_f1": round(f1, 4),
            "model_path": str(model_path),
        }
        logger.info("Training complete", **metrics)
        return metrics


if __name__ == "__main__":
    result = train()
    print(json.dumps(result, indent=2))
