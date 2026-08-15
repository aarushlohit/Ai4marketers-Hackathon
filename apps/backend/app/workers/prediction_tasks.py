"""Celery tasks: trigger ML predictions for customers and save scores to the database."""

import httpx
import asyncio
from celery import shared_task
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from sqlalchemy import text

ML_ENGINE_URL = getattr(settings, "ML_ENGINE_URL", "http://ml_engine:8002").rstrip("/")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_stale_predictions(self):
    """Daily task: refresh predictions for all tenants with stale data."""
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(f"{ML_ENGINE_URL}/batch/refresh-predictions")
            r.raise_for_status()
            return {"status": "success", "refreshed": r.json().get("count", 0)}
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def run_prediction_for_customer(self, customer_id: str, tenant_id: str):
    """Run all predictions for a single customer, retrieve scores, and persist to DB."""
    try:
        churn_prob = None
        lead_score = None
        health_score = None

        with httpx.Client(timeout=10.0) as client:
            # 1. Predict Churn Churn
            try:
                r = client.post(f"{ML_ENGINE_URL}/predict/churn", json={
                    "customer_id": customer_id,
                    "tenant_id": tenant_id,
                })
                if r.status_code == 200:
                    churn_prob = r.json().get("churn_probability")
            except Exception as e:
                print("Failed to fetch Churn Prediction from ML Engine:", e)

            # 2. Predict Lead Score
            try:
                r = client.post(f"{ML_ENGINE_URL}/predict/lead-score", json={
                    "customer_id": customer_id,
                    "tenant_id": tenant_id,
                })
                if r.status_code == 200:
                    lead_score = r.json().get("score")
            except Exception as e:
                print("Failed to fetch Lead Score from ML Engine:", e)

            # 3. Predict Health Score
            try:
                r = client.post(f"{ML_ENGINE_URL}/predict/health-score", json={
                    "customer_id": customer_id,
                    "tenant_id": tenant_id,
                })
                if r.status_code == 200:
                    health_score = r.json().get("score")
            except Exception as e:
                print("Failed to fetch Health Score from ML Engine:", e)

        # Async function to save scores back to backend database
        async def save_scores_to_db():
            async with AsyncSessionLocal() as session:
                await session.execute(
                    text("""
                        UPDATE customers.customers
                        SET churn_probability = COALESCE(:churn, churn_probability),
                            lead_score = COALESCE(:lead, lead_score),
                            health_score = COALESCE(:health, health_score),
                            updated_at = NOW()
                        WHERE id = :id AND tenant_id = :tenant_id
                    """),
                    {
                        "churn": churn_prob,
                        "lead": lead_score,
                        "health": health_score,
                        "id": customer_id,
                        "tenant_id": tenant_id,
                    }
                )
                await session.commit()

        # Run async function synchronously within Celery task space
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(save_scores_to_db(), loop)
            future.result()
        else:
            loop.run_until_complete(save_scores_to_db())

        return {
            "status": "success",
            "customer_id": customer_id,
            "predictions": {
                "churn_probability": churn_prob,
                "lead_score": lead_score,
                "health_score": health_score,
            }
        }
    except Exception as exc:
        raise self.retry(exc=exc)
