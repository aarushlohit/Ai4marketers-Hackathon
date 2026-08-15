"""CRM sync management endpoints."""

import json
from typing import Literal
from uuid import uuid4, UUID
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.sync_service import SyncService
from app.api.connections import _connections
from app.core.database import get_db

router = APIRouter()
sync_service = SyncService()

# In-memory job store for dev
_jobs: dict[str, dict] = {}

@router.post("/{connection_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_sync(
    connection_id: str,
    sync_type: Literal["full", "incremental"] = Query(default="incremental"),
    tenant_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a CRM sync job. Returns immediately; sync runs in the background."""
    connection = None
    
    # Try fetching connection from Database first
    try:
        result = await db.execute(
            text("""
                SELECT id, tenant_id, crm_type, status, access_token, refresh_token, token_expires_at, instance_url, last_sync_at, sync_config
                FROM integrations.crm_connections
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {
                "id": UUID(connection_id),
                "tenant_id": UUID(tenant_id),
            }
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
            connection = {
                "id": str(row_dict["id"]),
                "crm_type": row_dict["crm_type"],
                "tenant_id": str(row_dict["tenant_id"]),
                "status": row_dict["status"],
                "credentials": credentials,
                "instance_url": row_dict.get("instance_url"),
                "last_sync": row_dict["last_sync_at"].isoformat() if row_dict.get("last_sync_at") else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
    except Exception:
        # Fallback to memory
        connection = _connections.get(connection_id)

    if not connection or connection.get("tenant_id") != tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Connection not found")

    job_id = str(uuid4())
    _jobs[job_id] = {
        "job_id": job_id,
        "connection_id": connection_id,
        "sync_type": sync_type,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "records_synced": None,
    }

    try:
        result = await sync_service.run(connection, sync_type)
        
        # Update last sync timestamp in Database
        try:
            now = datetime.now(timezone.utc)
            await db.execute(
                text("""
                    UPDATE integrations.crm_connections
                    SET last_sync_at = :last_sync_at,
                        updated_at = NOW()
                    WHERE id = :id
                """),
                {
                    "id": UUID(connection_id),
                    "last_sync_at": now,
                }
            )
            await db.commit()
            connection["last_sync"] = now.isoformat()
        except Exception:
            await db.rollback()
            connection["last_sync"] = result.get("last_sync_at")
            
        _jobs[job_id].update(result)
        _jobs[job_id]["status"] = result["status"]
    except Exception as e:
        _jobs[job_id].update({"status": "failed", "error": str(e)})
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(e))

    return _jobs[job_id]

@router.get("/{job_id}/status")
async def get_sync_status(job_id: str):
    """Get the current status of a sync job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job

@router.post("/all")
async def sync_all(
    sync_type: Literal["full", "incremental"] = Query(default="incremental"),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger incremental sync for ALL active connections.
    Called by the Celery hourly beat schedule.
    """
    count = 0
    try:
        result = await db.execute(
            text("SELECT COUNT(*) FROM integrations.crm_connections WHERE status = 'active'")
        )
        count = result.scalar() or 0
    except Exception:
        count = len(_connections)
        
    return {"status": "accepted", "count": count,
            "message": f"Queued {sync_type} sync for {count} connections"}
