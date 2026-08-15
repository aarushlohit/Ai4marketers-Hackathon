"""Celery tasks: CRM data synchronization."""

import httpx
from celery import shared_task

CRM_SERVICE_URL = "http://crm_integration:8003"


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def run_incremental_sync_all(self):
    """Hourly task: run incremental sync for all active CRM connections."""
    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(f"{CRM_SERVICE_URL}/sync/all?sync_type=incremental")
            r.raise_for_status()
            return {"status": "success", "jobs_started": r.json().get("count", 0)}
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def run_full_sync(self, connection_id: str, tenant_id: str):
    """Trigger a full sync for a specific CRM connection (usually called once on setup)."""
    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.post(
                f"{CRM_SERVICE_URL}/sync/{connection_id}/start",
                params={"sync_type": "full", "tenant_id": tenant_id},
            )
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        raise self.retry(exc=exc)
