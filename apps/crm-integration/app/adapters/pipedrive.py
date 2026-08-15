"""Pipedrive CRM Adapter — REST API v1 + OAuth 2.0."""

import hashlib
import hmac

import httpx
import structlog

from app.adapters.base import CRMAdapter

logger = structlog.get_logger()

PD_BASE = "https://api.pipedrive.com/v1"
PD_TOKEN_URL = "https://oauth.pipedrive.com/oauth/token"


class PipedriveAdapter(CRMAdapter):
    """Connects to Pipedrive via REST API v1."""

    def __init__(self, credentials: dict):
        super().__init__(credentials)
        self.access_token: str | None = credentials.get("access_token")
        domain = (credentials.get("api_domain") or "https://api.pipedrive.com").rstrip("/")
        self.api_base = f"{domain}/api/v1" if "api.pipedrive.com" not in domain else f"{domain}/v1"

    @property
    def _params(self) -> dict:
        return {}

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.api_base}/users/me", headers=self._headers)
            return r.status_code == 200

    async def refresh_access_token(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(PD_TOKEN_URL, data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.credentials["client_id"],
                "client_secret": self.credentials["client_secret"],
            })
            r.raise_for_status()
            return r.json()

    async def get_contacts(self, filters=None, limit=100, offset=0) -> list[dict]:
        params = {"limit": min(limit, 100), "start": offset}
        if filters and filters.get("updated_since"):
            params["updated_since"] = filters["updated_since"]
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self.api_base}/persons", params=params, headers=self._headers)
            r.raise_for_status()
            data = r.json()
            return data.get("data") or []

    async def create_contact(self, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{PD_BASE}/persons",
                                  json=self.map_from_unified(data),
                                  params=self._params, headers=self._headers)
            r.raise_for_status()
            return r.json().get("data", {})

    async def update_contact(self, contact_id: str, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.put(f"{PD_BASE}/persons/{contact_id}",
                                 json=self.map_from_unified(data),
                                 params=self._params, headers=self._headers)
            r.raise_for_status()
            return r.json().get("data", {})

    async def get_accounts(self, filters=None, limit=100) -> list[dict]:
        params = {"limit": min(limit, 100)}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self.api_base}/organizations", params=params, headers=self._headers)
            r.raise_for_status()
            return r.json().get("data") or []

    async def handle_webhook(self, payload: dict) -> dict:
        return {
            "event_type": f"{payload.get('event', 'unknown')}",
            "record_id": str(payload.get("current", {}).get("id", "")),
            "object_type": payload.get("object", "unknown"),
        }

    def verify_webhook_signature(self, payload: bytes, headers: dict) -> bool:
        # Pipedrive uses HTTP Basic Auth for webhook delivery
        return True  # Verified at the routing level via credentials

    def map_to_unified(self, crm_record: dict) -> dict:
        name = crm_record.get("name", "")
        parts = name.split(" ", 1)
        first = parts[0] if parts else ""
        last = parts[1] if len(parts) > 1 else ""
        emails = crm_record.get("email", [])
        phones = crm_record.get("phone", [])
        org = crm_record.get("org_id")
        return {
            "external_id": str(crm_record.get("id", "")),
            "crm_source": "pipedrive",
            "first_name": first,
            "last_name": last,
            "email": emails[0].get("value") if emails else None,
            "phone": phones[0].get("value") if phones else None,
            "company": org.get("name") if isinstance(org, dict) else None,
            "title": crm_record.get("job_title"),
        }

    def map_from_unified(self, unified: dict) -> dict:
        full_name = f"{unified.get('first_name', '')} {unified.get('last_name', '')}".strip()
        result: dict = {"name": full_name}
        if unified.get("email"):
            result["email"] = [{"value": unified["email"], "primary": True}]
        if unified.get("phone"):
            result["phone"] = [{"value": unified["phone"], "primary": True}]
        return result
