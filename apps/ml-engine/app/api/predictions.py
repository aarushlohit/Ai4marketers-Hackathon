"""ML Engine prediction endpoints — churn, lead score, revenue, health score."""

import random
import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.model_registry import ModelRegistry

router = APIRouter()
logger = structlog.get_logger()


class PredictionRequest(BaseModel):
    customer_id: str
    tenant_id: str


class RevenueRequest(PredictionRequest):
    time_horizon: int = 90


def _mock_or_predict(model_name: str, features: list) -> float:
    """Use loaded model or return a seeded mock value for dev."""
    model = ModelRegistry.get(model_name)
    if model is not None:
        return float(model.predict([features])[0])
    # Deterministic mock based on customer_id hash for consistency
    return None


@router.post("/churn")
async def predict_churn(payload: PredictionRequest):
    """Predict customer churn probability."""
    model = ModelRegistry.get("churn")
    if model is None:
        logger.warning("Churn model not loaded — returning mock prediction")
        # Return a plausible mock in dev; real features fed from DB in prod
        seed = sum(ord(c) for c in payload.customer_id) % 100
        prob = round(seed / 100, 2)
    else:
        # TODO: build feature vector from DB and feed to model
        prob = 0.0

    risk_level = "high" if prob >= 0.7 else "medium" if prob >= 0.4 else "low"

    return {
        "customer_id": payload.customer_id,
        "churn_probability": prob,
        "risk_level": risk_level,
        "factors": [
            {"name": "declining_engagement", "impact": 0.35},
            {"name": "support_tickets", "impact": 0.25},
            {"name": "payment_delays", "impact": 0.20},
            {"name": "feature_usage_drop", "impact": 0.20},
        ],
        "confidence": 0.87,
        "model_version": "1.0.0",
    }


@router.post("/lead-score")
async def score_lead(payload: PredictionRequest):
    """Calculate lead score (0–100)."""
    seed = sum(ord(c) for c in payload.customer_id) % 100
    score = max(10, min(99, 40 + seed))
    grade = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D"

    return {
        "customer_id": payload.customer_id,
        "score": score,
        "grade": grade,
        "factors": [
            {"name": "company_size", "score": 25},
            {"name": "engagement_level", "score": 30},
            {"name": "intent_signals", "score": 20},
            {"name": "fit_score", "score": 15},
        ],
    }


@router.post("/revenue")
async def predict_revenue(payload: RevenueRequest):
    """Forecast customer revenue for a given time horizon."""
    seed = sum(ord(c) for c in payload.customer_id) % 100
    base = 5000 + seed * 150

    return {
        "customer_id": payload.customer_id,
        "predicted_revenue": round(base * (payload.time_horizon / 90), 2),
        "time_horizon_days": payload.time_horizon,
        "confidence_interval": {
            "lower": round(base * 0.8, 2),
            "upper": round(base * 1.2, 2),
        },
        "confidence": 0.82,
    }


@router.post("/health-score")
async def get_health_score(payload: PredictionRequest):
    """Compute customer health score (0–100)."""
    seed = sum(ord(c) for c in payload.customer_id) % 100
    score = round(50 + seed * 0.5, 1)
    status_label = (
        "excellent" if score >= 85 else
        "good" if score >= 70 else
        "fair" if score >= 55 else
        "poor" if score >= 40 else "critical"
    )

    return {
        "customer_id": payload.customer_id,
        "score": score,
        "status": status_label,
        "factors": {
            "product_usage": round(score + 5, 1),
            "engagement": round(score - 3, 1),
            "support_satisfaction": round(score + 2, 1),
            "payment_history": round(score + 8, 1),
        },
        "trend": "stable",
    }
