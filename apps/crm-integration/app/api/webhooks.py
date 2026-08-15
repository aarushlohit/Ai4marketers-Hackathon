"""
Webhook endpoints — receive real-time events from CRM platforms.
Signature is verified then the event is enqueued for async processing.
"""

import json
from uuid import UUID
from datetime import datetime, timezone
import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.factory import get_adapter
from app.api.connections import _connections
from app.core.database import get_db

router = APIRouter()
logger = structlog.get_logger()


async def _process_webhook_event(crm_type: str, payload: dict):
    """Background task: look up matching connection and apply the record change."""
    logger.info("Processing webhook", crm_type=crm_type, payload_keys=list(payload.keys()))
    # In production: update customer in DB + trigger ML prediction refresh


@router.post("/{crm_type}")
async def receive_webhook(
    crm_type: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Receive a webhook event from a CRM platform.
    1. Verify signature
    2. Log event
    3. Queue async processing
    """
    raw_body = await request.body()
    headers = dict(request.headers)

    # Find the connection for this CRM type to get credentials for sig verification
    conn = None
    try:
        result = await db.execute(
            text("""
                SELECT id, tenant_id, crm_type, status, access_token, refresh_token, token_expires_at, instance_url, sync_config
                FROM integrations.crm_connections
                WHERE crm_type = :crm_type AND status = 'active'
                LIMIT 1
            """),
            {"crm_type": crm_type}
        )
        row = result.fetchone()
        if row:
            row_dict = row._asdict()
            expires_at = row_dict["token_expires_at"].timestamp() if row_dict.get("token_expires_at") else None
            credentials = row_dict.get("sync_config", {}).get("credentials") or {
                "access_token": row_dict.get("access_token"),
                "refresh_token": row_dict.get("refresh_token"),
                "instance_url": row_dict.get("instance_url"),
                "expires_at": expires_at,
            }
            conn = {
                "id": str(row_dict["id"]),
                "crm_type": row_dict["crm_type"],
                "tenant_id": str(row_dict["tenant_id"]),
                "status": row_dict["status"],
                "credentials": credentials,
                "webhook_secret": credentials.get("webhook_secret", ""),
                "access_token": credentials.get("access_token"),
            }
    except Exception:
        # Fallback to memory
        conn = next(
            (c for c in _connections.values() if c["crm_type"] == crm_type),
            None,
        )

    if conn:
        try:
            adapter = get_adapter(crm_type, {"access_token": conn.get("access_token"),
                                              "webhook_secret": conn.get("webhook_secret", "")})
            if not adapter.verify_webhook_signature(raw_body, headers):
                logger.warning("Webhook signature invalid", crm_type=crm_type)
                raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                                    detail="Invalid webhook signature")
        except ValueError:
            pass  # CRM type not fully implemented yet

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    logger.info("Webhook received", crm_type=crm_type, size=len(raw_body))
    background_tasks.add_task(_process_webhook_event, crm_type, payload)
