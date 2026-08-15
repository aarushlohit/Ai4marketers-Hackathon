"""HubSpot CRM Adapter — API v3 + OAuth 2.0."""

import hashlib
import hmac
from typing import Any

import httpx
import structlog

from app.adapters.base import CRMAdapter

logger = structlog.get_logger()

HS_BASE = "https://api.hubapi.com"
HS_AUTH_URL = "https://api.hubapi.com/oauth/v3/token"


class HubSpotAdapter(CRMAdapter):
    """Connects to HubSpot via REST API v3."""

    def __init__(self, credentials: dict):
        super().__init__(credentials)
        self.access_token: str | None = credentials.get("access_token")

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"}

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{HS_BASE}/oauth/v1/access-tokens/{self.access_token}")
            return r.status_code == 200

    async def refresh_access_token(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(HS_AUTH_URL, data={
                "grant_type": "refresh_token",
                "client_id": self.credentials["client_id"],
                "client_secret": self.credentials["client_secret"],
                "refresh_token": refresh_token,
            })
            r.raise_for_status()
            return r.json()

    async def get_contacts(self, filters=None, limit=100, offset=0) -> list[dict]:
        params = {"limit": min(limit, 100), "after": offset or None}
        if filters and filters.get("updated_since"):
            params["updatedAfter"] = filters["updated_since"]
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{HS_BASE}/crm/v3/objects/contacts",
                                 params={k: v for k, v in params.items() if v},
                                 headers=self._headers)
            r.raise_for_status()
            return r.json().get("results", [])

    async def create_contact(self, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{HS_BASE}/crm/v3/objects/contacts",
                                  json={"properties": self.map_from_unified(data)},
                                  headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def update_contact(self, contact_id: str, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.patch(f"{HS_BASE}/crm/v3/objects/contacts/{contact_id}",
                                   json={"properties": self.map_from_unified(data)},
                                   headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def get_accounts(self, filters=None, limit=100) -> list[dict]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{HS_BASE}/crm/v3/objects/companies",
                                 params={"limit": min(limit, 100)}, headers=self._headers)
            r.raise_for_status()
            return r.json().get("results", [])

    async def handle_webhook(self, payload: dict) -> dict:
        return {
            "event_type": payload.get("subscriptionType", "unknown"),
            "record_id": str(payload.get("objectId", "")),
            "object_type": payload.get("subscriptionType", "").split(".")[0],
        }

    def verify_webhook_signature(self, payload: bytes, headers: dict) -> bool:
        secret = self.credentials.get("webhook_secret", "").encode()
        sig = headers.get("x-hubspot-signature", "")
        expected = hashlib.sha256(secret + payload).hexdigest()
        return hmac.compare_digest(expected, sig)

    def map_to_unified(self, crm_record: dict) -> dict:
        props = crm_record.get("properties", crm_record)
        return {
            "external_id": crm_record.get("id"),
            "crm_source": "hubspot",
            "first_name": props.get("firstname", ""),
            "last_name": props.get("lastname", ""),
            "email": props.get("email"),
            "phone": props.get("phone"),
            "company": props.get("company"),
            "title": props.get("jobtitle"),
        }

    def map_from_unified(self, unified: dict) -> dict:
        return {
            "firstname": unified.get("first_name", ""),
            "lastname": unified.get("last_name", ""),
            "email": unified.get("email"),
            "phone": unified.get("phone"),
            "company": unified.get("company"),
            "jobtitle": unified.get("title"),
        }
