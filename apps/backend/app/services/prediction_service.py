"""
Prediction Service — coordinates ML Engine calls and caches results.
Acts as a façade over the ML Engine microservice.
"""

import structlog
import httpx
from uuid import UUID

from app.core.config import settings

logger = structlog.get_logger()

ML_ENGINE_URL = "http://ml_engine:8002"


class PredictionService:
    """Wraps ML Engine HTTP calls with error handling and result caching."""

    async def predict_churn(self, customer_id: UUID, tenant_id: UUID) -> dict:
        return await self._call_ml(
            "/predict/churn",
            {"customer_id": str(customer_id), "tenant_id": str(tenant_id)},
        )

    async def score_lead(self, customer_id: UUID, tenant_id: UUID) -> dict:
        return await self._call_ml(
            "/predict/lead-score",
            {"customer_id": str(customer_id), "tenant_id": str(tenant_id)},
        )

    async def forecast_revenue(
        self, customer_id: UUID, tenant_id: UUID, time_horizon: int = 90
    ) -> dict:
        return await self._call_ml(
            "/predict/revenue",
            {
                "customer_id": str(customer_id),
                "tenant_id": str(tenant_id),
                "time_horizon": time_horizon,
            },
        )

    async def health_score(self, customer_id: UUID, tenant_id: UUID) -> dict:
        return await self._call_ml(
            "/predict/health-score",
            {"customer_id": str(customer_id), "tenant_id": str(tenant_id)},
        )

    async def all_predictions(self, customer_id: UUID, tenant_id: UUID) -> dict:
        """Run all 4 predictions and return them as a bundle."""
        results = {}
        for model, method in [
            ("churn", self.predict_churn),
            ("lead_score", self.score_lead),
            ("revenue", self.forecast_revenue),
            ("health_score", self.health_score),
        ]:
            try:
                results[model] = await method(customer_id, tenant_id)
            except Exception as e:
                logger.warning(f"Prediction failed: {model}", error=str(e))
                results[model] = {"error": str(e)}
        return results

    async def _call_ml(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.post(f"{ML_ENGINE_URL}{path}", json=payload)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                logger.error("ML Engine HTTP error", path=path,
                             status=e.response.status_code)
                raise
            except httpx.RequestError as e:
                logger.error("ML Engine connection error", path=path, error=str(e))
                raise
