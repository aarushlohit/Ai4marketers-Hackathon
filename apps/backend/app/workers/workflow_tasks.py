"""Celery tasks: trigger or coordinate workflow executions."""

import httpx
import structlog
from celery import shared_task
from app.core.config import settings

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_workflow(self, workflow_id: str, payload: dict):
    """Trigger the workflow execution inside the Workflow Engine."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                f"{settings.WORKFLOW_ENGINE_URL}/executions/trigger",
                json={
                    "event_type": payload.get("event_type", "manual"),
                    "entity_id": payload.get("entity_id"),
                    "tenant_id": payload.get("tenant_id"),
                    "payload": payload.get("payload", {})
                }
            )
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.error("Failed to trigger workflow execution", workflow_id=workflow_id, error=str(exc))
        raise self.retry(exc=exc)
