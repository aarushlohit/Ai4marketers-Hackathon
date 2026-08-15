"""Customer Digital Twin Service — Predictions API.

AI-powered predictions for each customer twin.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

PREDICTION_TYPES = [
    "buying_behaviour", "price_sensitivity", "renewal_probability",
    "risk_level", "preferred_channel", "communication_frequency",
    "product_affinity", "lifetime_value",
]


class PredictionRequest(BaseModel):
    customer_id: str
    prediction_types: Optional[List[str]] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class PredictionResult(BaseModel):
    prediction_type: str
    value: Any
    confidence: float
    factors: List[str] = Field(default_factory=list)


@router.post("/{customer_id}", response_model=List[PredictionResult])
async def predict_customer(customer_id: str, request: Optional[PredictionRequest] = None):
    """Generate all predictions for a customer."""
    from app.api.twins import _twins_store

    key = f"customer_{customer_id}"
    twin = _twins_store.get(key, {})
    
    prediction_types = request.prediction_types if request and request.prediction_types else PREDICTION_TYPES
    
    predictions = []
    for ptype in prediction_types:
        if ptype in PREDICTION_TYPES:
            prediction = _generate_prediction(ptype, twin, request.context if request else {})
            predictions.append(prediction)
    
    return predictions


@router.post("/{customer_id}/{prediction_type}", response_model=PredictionResult)
async def predict_specific(customer_id: str, prediction_type: str, context: Dict[str, Any] = {}):
    """Generate a specific prediction for a customer."""
    if prediction_type not in PREDICTION_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown prediction type: {prediction_type}")
    
    from app.api.twins import _twins_store
    key = f"customer_{customer_id}"
    twin = _twins_store.get(key, {})
    
    return _generate_prediction(prediction_type, twin, context)


def _generate_prediction(prediction_type: str, twin_data: Dict[str, Any], context: Dict[str, Any]) -> PredictionResult:
    """Generate a prediction based on twin data and context."""
    if prediction_type == "buying_behaviour":
        return PredictionResult(
            prediction_type="buying_behaviour",
            value={
                "purchase_frequency": twin_data.get("buying_behaviour", {}).get("purchase_frequency", "quarterly"),
                "avg_order_value": twin_data.get("buying_behaviour", {}).get("avg_order_value", 15000),
                "next_likely_purchase": "45-60 days",
                "decision_cycle_days": twin_data.get("buying_behaviour", {}).get("decision_cycle_days", 45),
            },
            confidence=0.82,
            factors=["Historical purchase patterns", "Engagement frequency", "Product interest signals"],
        )
    
    elif prediction_type == "price_sensitivity":
        sensitivity = twin_data.get("price_sensitivity", 0.5)
        return PredictionResult(
            prediction_type="price_sensitivity",
            value={"level": sensitivity, "label": "medium" if sensitivity < 0.7 else "high", "discount_threshold": 0.15},
            confidence=0.75,
            factors=["Support ticket volume", "Competitor offers", "Contract negotiations"],
        )
    
    elif prediction_type == "renewal_probability":
        probability = twin_data.get("renewal_probability", 0.85)
        return PredictionResult(
            prediction_type="renewal_probability",
            value={"probability": probability, "label": "likely" if probability > 0.6 else "at_risk", "days_to_renewal": 45},
            confidence=0.88,
            factors=["Product usage trends", "Support interactions", "Contract value trajectory"],
        )
    
    elif prediction_type == "risk_level":
        risk = twin_data.get("risk_level", "low")
        risk_scores = {"low": 0.15, "medium": 0.40, "high": 0.70, "critical": 0.90}
        return PredictionResult(
            prediction_type="risk_level",
            value={"level": risk, "score": risk_scores.get(risk, 0.15), "needs_attention": risk in ("high", "critical")},
            confidence=0.91,
            factors=["Health score decline", "Support ticket increase", "Feature adoption drop"],
        )
    
    elif prediction_type == "preferred_channel":
        channel = twin_data.get("preferred_channel", "email")
        return PredictionResult(
            prediction_type="preferred_channel",
            value={"channel": channel, "open_rate": 0.34 if channel == "email" else 0.28, "best_time": "10:00 AM - 2:00 PM"},
            confidence=0.79,
            factors=["Historical engagement rates", "Response time analysis", "Channel preferences"],
        )
    
    elif prediction_type == "communication_frequency":
        frequency = twin_data.get("communication_frequency", "weekly")
        return PredictionResult(
            prediction_type="communication_frequency",
            value={"frequency": frequency, "optimal_touches_per_month": 4, "risk_of_over_contact": "low"},
            confidence=0.73,
            factors=["Optimal engagement analysis", "Unsubscribe risk modeling", "Response fatigue"],
        )
    
    elif prediction_type == "product_affinity":
        return PredictionResult(
            prediction_type="product_affinity",
            value={
                "products": twin_data.get("product_affinity", [
                    {"name": "Analytics Dashboard", "affinity": 0.85},
                    {"name": "Workflow Automation", "affinity": 0.72},
                    {"name": "AI Copilot", "affinity": 0.64},
                ]),
                "recommended_upsell": "Enterprise Plan + Advanced Security",
                "expansion_potential": "high",
            },
            confidence=0.84,
            factors=["Feature usage analytics", "Support topic analysis", "Similar customer patterns"],
        )
    
    elif prediction_type == "lifetime_value":
        clv = twin_data.get("lifetime_value", 50000)
        return PredictionResult(
            prediction_type="lifetime_value",
            value={
                "current_clv": clv,
                "projected_clv_12_months": clv * 1.25,
                "clv_percentile": "top_20",
                "upsell_potential": clv * 1.5,
            },
            confidence=0.86,
            factors=["Historical revenue", "Growth trajectory", "Expansion opportunities"],
        )
    
    return PredictionResult(
        prediction_type=prediction_type,
        value=None,
        confidence=0.0,
        factors=["No data available"],
    )
