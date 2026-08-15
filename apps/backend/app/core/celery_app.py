"""Celery application configuration for background task processing."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "miracle_birds",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.prediction_tasks",
        "app.workers.sync_tasks",
        "app.workers.workflow_tasks",
        "app.workers.email_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
    beat_schedule={
        "incremental-crm-sync": {
            "task": "app.workers.sync_tasks.run_incremental_sync_all",
            "schedule": 3600.0,  # every hour
        },
        "refresh-predictions": {
            "task": "app.workers.prediction_tasks.refresh_stale_predictions",
            "schedule": 86400.0,  # daily
        },
    },
)
