"""
Use Case: Get Customer 360
Aggregates all intelligence for a single customer:
profile, predictions, recent interactions, and recommendations.
"""

from dataclasses import dataclass
from uuid import UUID

import httpx
import structlog

from app.repositories.customer_repository import CustomerRepository

logger = structlog.get_logger()

ML_ENGINE_URL = "http://ml_engine:8002"


@dataclass
class Customer360Result:
    customer: dict
    predictions: dict
    recommendations: list[dict]


class GetCustomer360UseCase:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    async def execute(self, customer_id: UUID, tenant_id: UUID) -> Customer360Result:
        # 1. Get customer
        customer = await self.customer_repo.get_by_id(customer_id, tenant_id)
        if customer is None:
            raise ValueError(f"Customer {customer_id} not found")

        customer_dict = {
            "id": str(customer.id),
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "company": customer.company,
            "status": customer.status,
            "health_score": customer.health_score,
            "churn_probability": customer.churn_probability,
            "lead_score": customer.lead_score,
            "lifetime_value": customer.lifetime_value,
        }

        # 2. Fetch fresh predictions from ML engine
        predictions = {}
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                payload = {"customer_id": str(customer_id),
                           "tenant_id": str(tenant_id)}
                for model in ["churn", "lead-score", "health-score"]:
                    r = await client.post(f"{ML_ENGINE_URL}/predict/{model}",
                                          json=payload)
                    if r.status_code == 200:
                        predictions[model.replace("-", "_")] = r.json()
        except Exception as e:
            logger.warning("ML Engine unavailable for 360 view", error=str(e))
            # Fall back to cached scores from the DB
            predictions = {
                "churn": {"churn_probability": customer.churn_probability,
                           "risk_level": "unknown"},
                "lead_score": {"score": customer.lead_score},
                "health_score": {"score": customer.health_score},
            }

        # 3. Build recommendations based on predictions
        recommendations = _build_recommendations(predictions)

        return Customer360Result(
            customer=customer_dict,
            predictions=predictions,
            recommendations=recommendations,
        )


def _build_recommendations(predictions: dict) -> list[dict]:
    recs = []
    churn_prob = predictions.get("churn", {}).get("churn_probability", 0) or 0
    if churn_prob >= 0.7:
        recs.append({
            "type": "retention",
            "title": "Schedule urgent retention call",
            "description": f"Customer has {round(churn_prob*100)}% churn probability. "
                           "Contact immediately with a personalised offer.",
            "priority": "urgent",
        })
    elif churn_prob >= 0.4:
        recs.append({
            "type": "retention",
            "title": "Send health-check email",
            "description": "Medium churn risk detected. Proactive outreach recommended.",
            "priority": "high",
        })

    lead_score = predictions.get("lead_score", {}).get("score", 0) or 0
    if lead_score >= 80:
        recs.append({
            "type": "upsell",
            "title": "Upsell opportunity",
            "description": "High lead score — ideal candidate for plan upgrade or add-on.",
            "priority": "high",
        })

    if not recs:
        recs.append({
            "type": "next_best_action",
            "title": "Continue regular engagement",
            "description": "Customer is healthy. Maintain current cadence.",
            "priority": "low",
        })
    return recs
