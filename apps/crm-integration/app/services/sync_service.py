"""
Sync Service — orchestrates CRM data synchronisation.

Three strategies:
  full        — Fetch all records (initial import)
  incremental — Fetch only records modified since last sync
  webhook     — Apply a single record change from a webhook event
"""

import structlog
import time
from datetime import datetime, timezone

from app.adapters.factory import get_adapter
from app.core.config import settings

logger = structlog.get_logger()

# Override with public URL to bypass Render internal networking DNS issues
BACKEND_API_URL = "https://mb-backend-rnhn.onrender.com/api/v1/internal"


class SyncService:
    async def run(
        self,
        connection: dict,
        sync_type: str = "incremental",
    ) -> dict:
        """
        Run a sync job for a CRM connection.

        Args:
            connection: Dict with crm_type, credentials, tenant_id, last_sync_at
            sync_type: 'full' | 'incremental'

        Returns:
            Summary dict with records_synced, errors, duration
        """
        started_at = datetime.now(timezone.utc)
        crm_type = connection["crm_type"]
        tenant_id = connection["tenant_id"]

        logger.info("Sync started", crm_type=crm_type, sync_type=sync_type, tenant_id=tenant_id)

        adapter = get_adapter(crm_type, connection["credentials"])
        credentials = connection["credentials"]
        if credentials.get("refresh_token") and credentials.get("expires_at", 0) <= time.time() + 60:
            refreshed = await adapter.refresh_access_token(credentials["refresh_token"])
            credentials["access_token"] = refreshed["access_token"]
            credentials["expires_at"] = time.time() + int(refreshed.get("expires_in", 3600))
            if refreshed.get("refresh_token"):
                credentials["refresh_token"] = refreshed["refresh_token"]
            if refreshed.get("instance_url"):
                credentials["instance_url"] = refreshed["instance_url"]
            if refreshed.get("api_domain"):
                credentials["api_domain"] = refreshed["api_domain"]
            adapter = get_adapter(crm_type, credentials)

        is_auth = await adapter.authenticate()
        if not is_auth and credentials.get("refresh_token"):
            refreshed = await adapter.refresh_access_token(credentials["refresh_token"])
            credentials["access_token"] = refreshed["access_token"]
            credentials["expires_at"] = time.time() + int(refreshed.get("expires_in", 3600))
            credentials["refresh_token"] = refreshed.get("refresh_token", credentials["refresh_token"])
            adapter = get_adapter(crm_type, credentials)
            is_auth = await adapter.authenticate()
        if not is_auth:
            raise RuntimeError(f"Authentication failed for {crm_type} connection")

        # Build filters for incremental sync
        filters = {}
        last_sync_at = connection.get("last_sync_at") or connection.get("last_sync")
        if sync_type == "incremental" and last_sync_at:
            filters["updated_since"] = last_sync_at

        # Paginate through all contacts
        records_synced = 0
        errors = 0
        offset = 0
        page_size = 100

        while True:
            try:
                records = await adapter.get_contacts(
                    filters=filters, limit=page_size, offset=offset
                )
                if not records:
                    break

                unified = [adapter.map_to_unified(r) for r in records]
                await self._upsert_customers(unified, tenant_id)

                records_synced += len(records)
                offset += len(records)

                if len(records) < page_size:
                    break  # Last page
            except Exception as e:
                logger.error("Sync page failed", error=str(e), offset=offset)
                errors += 1
                if errors >= 5:
                    logger.error("Too many errors — aborting sync")
                    break

        duration_s = (datetime.now(timezone.utc) - started_at).total_seconds()
        logger.info(
            "Sync completed",
            crm_type=crm_type,
            records_synced=records_synced,
            errors=errors,
            duration_s=round(duration_s, 2),
        )

        return {
            "status": "completed" if errors == 0 else "completed_with_errors",
            "records_synced": records_synced,
            "errors": errors,
            "duration_seconds": round(duration_s, 2),
            "last_sync_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _upsert_customers(self, records: list[dict], tenant_id: str):
        """
        Upsert unified customer records into the Miracle Birds database.
        In production: direct DB write via SQLAlchemy; here we call the Backend API.
        """
        import httpx
        headers = {}
        if settings.INTERNAL_API_KEY:
            headers["X-Internal-API-Key"] = settings.INTERNAL_API_KEY

        async with httpx.AsyncClient(timeout=30.0) as client:
            for record in records:
                record["tenant_id"] = tenant_id
                try:
                    r = await client.post(
                        f"{BACKEND_API_URL}/customers/upsert",
                        json=record,
                        headers=headers,
                    )
                    r.raise_for_status()
                except Exception as e:
                    logger.warning("Customer upsert failed", error=str(e),
                                   external_id=record.get("external_id"))
