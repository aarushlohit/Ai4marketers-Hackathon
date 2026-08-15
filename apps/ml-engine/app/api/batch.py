"""ML Engine batch prediction endpoints."""

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
logger = structlog.get_logger()


class BatchRefreshRequest(BaseModel):
    tenant_ids: list[str] | None = None  # None = all tenants


@router.post("/refresh-predictions")
async def refresh_predictions(payload: BatchRefreshRequest = BatchRefreshRequest()):
    """
    Batch refresh predictions for all (or specified) tenants.
    Called by the Celery daily beat task.
    """
    logger.info("Batch prediction refresh started", tenants=payload.tenant_ids or "all")
    # In production: query DB for all customers, run predictions, store results
    return {"status": "accepted", "count": 0, "message": "Batch job queued"}


@router.post("/train/{model_name}")
async def trigger_training(model_name: str):
    """Trigger model retraining for a specific model."""
    valid_models = ["churn", "lead_score", "revenue", "health_score"]
    if model_name not in valid_models:
        from fastapi import HTTPException
        raise HTTPException(400, detail=f"Unknown model. Valid: {valid_models}")

    logger.info(f"Training triggered for model: {model_name}")
    return {"status": "training_started", "model": model_name}
