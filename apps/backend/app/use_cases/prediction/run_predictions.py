"""
Use Case: Run All Predictions for a Customer
Coordinates ML Engine calls, updates cached scores in the DB,
and triggers workflow engine events when thresholds are crossed.
"""

import structlog
import httpx
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.customer_repository import CustomerRepository
from app.services.prediction_service import PredictionService

logger = structlog.get_logger()

WORKFLOW_ENGINE_URL = "http://workflow_engine:8003"
CHURN_HIGH_RISK_THRESHOLD = 0.70


class RunPredictionsUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.prediction_service = PredictionService()

    async def execute(self, customer_id: UUID, tenant_id: UUID) -> dict:
        """
        Run all predictions, persist cached scores, fire workflow events.
        Returns a dict of all prediction results.
        """
        # 1. Fetch all predictions from ML engine
        predictions = await self.prediction_service.all_predictions(
            customer_id, tenant_id
        )

        # 2. Update cached scores on the customer record
        customer = await self.customer_repo.get_by_id(customer_id, tenant_id)
        if customer:
            churn_data = predictions.get("churn", {})
            lead_data = predictions.get("lead_score", {})
            health_data = predictions.get("health_score", {})

            churn_prob = churn_data.get("churn_probability")
            if churn_prob is not None:
                customer.churn_probability = churn_prob
            if lead_data.get("score") is not None:
                customer.lead_score = lead_data["score"]
            if health_data.get("score") is not None:
                customer.health_score = health_data["score"]

            await self.db.commit()

            # 3. Fire workflow event if churn risk is high
            if churn_prob and churn_prob >= CHURN_HIGH_RISK_THRESHOLD:
                await self._fire_workflow_event(
                    event_type="churn_risk_high",
                    entity_id=str(customer_id),
                    tenant_id=str(tenant_id),
                    payload={"churn_probability": churn_prob},
                )

        logger.info(
            "Predictions completed",
            customer_id=str(customer_id),
            churn_prob=predictions.get("churn", {}).get("churn_probability"),
        )
        return predictions

    async def _fire_workflow_event(
        self,
        event_type: str,
        entity_id: str,
        tenant_id: str,
        payload: dict,
    ) -> None:
        """Notify the Workflow Engine of a prediction threshold event."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{WORKFLOW_ENGINE_URL}/executions/trigger",
                    json={
                        "event_type": event_type,
                        "entity_id": entity_id,
                        "tenant_id": tenant_id,
                        "payload": payload,
                    },
                )
        except Exception as e:
            # Non-critical: log but don't fail the prediction run
            logger.warning("Workflow trigger failed", error=str(e),
                           event_type=event_type)
