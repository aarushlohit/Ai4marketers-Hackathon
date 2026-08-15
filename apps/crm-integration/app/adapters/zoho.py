"""Zoho CRM Adapter — API v3 + OAuth 2.0."""

import hashlib
import hmac
from typing import Any

import httpx
import structlog

from app.adapters.base import CRMAdapter

logger = structlog.get_logger()

DEFAULT_ZOHO_AUTH_URL = "https://accounts.zoho.com/oauth/v2/token"


class ZohoCRMAdapter(CRMAdapter):
    """Connects to Zoho CRM via REST API v3."""

    def __init__(self, credentials: dict):
        super().__init__(credentials)
        self.access_token: str | None = credentials.get("access_token")
        self.api_domain: str = credentials.get("api_domain") or "https://www.zohoapis.com"
        self.accounts_url: str = credentials.get("accounts_url") or DEFAULT_ZOHO_AUTH_URL.rsplit("/oauth", 1)[0]

    @property
    def _base(self) -> str:
        return f"{self.api_domain.rstrip('/')}/crm/v3"

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"}

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self._base}/users?type=CurrentUser", headers=self._headers)
            return r.status_code == 200

    async def refresh_access_token(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self.accounts_url.rstrip('/')}/oauth/v2/token", data={
                "grant_type": "refresh_token",
                "client_id": self.credentials["client_id"],
                "client_secret": self.credentials["client_secret"],
                "refresh_token": refresh_token,
            })
            r.raise_for_status()
            return r.json()

    async def get_contacts(self, filters=None, limit=100, offset=0) -> list[dict]:
        params = {"per_page": min(limit, 200), "page": (offset // 200) + 1}
        if filters and filters.get("updated_since"):
            params["Last_Activity_Time:greater_equal"] = filters["updated_since"]
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self._base}/Contacts", params=params, headers=self._headers)
            if r.status_code == 204:
                return []
            r.raise_for_status()
            return r.json().get("data", [])

    async def create_contact(self, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self._base}/Contacts",
                                  json={"data": [self.map_from_unified(data)]},
                                  headers=self._headers)
            r.raise_for_status()
            return r.json().get("data", [{}])[0]

    async def update_contact(self, contact_id: str, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.put(f"{self._base}/Contacts/{contact_id}",
                                 json={"data": [self.map_from_unified(data)]},
                                 headers=self._headers)
            r.raise_for_status()
            return {"id": contact_id, "success": True}

    async def get_accounts(self, filters=None, limit=100) -> list[dict]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self._base}/Accounts",
                                 params={"per_page": min(limit, 200)}, headers=self._headers)
            if r.status_code == 204:
                return []
            r.raise_for_status()
            return r.json().get("data", [])

    async def handle_webhook(self, payload: dict) -> dict:
        return {
            "event_type": payload.get("operation", "unknown"),
            "record_id": payload.get("ids", [None])[0],
            "object_type": payload.get("module", "unknown"),
        }

    def verify_webhook_signature(self, payload: bytes, headers: dict) -> bool:
        # Zoho uses token-based verification
        token = headers.get("x-zoho-webhook-token", "")
        return token == self.credentials.get("webhook_token", "")

    def map_to_unified(self, crm_record: dict) -> dict:
        return {
            "external_id": crm_record.get("id"),
            "crm_source": "zoho",
            "first_name": crm_record.get("First_Name", ""),
            "last_name": crm_record.get("Last_Name", ""),
            "email": crm_record.get("Email"),
            "phone": crm_record.get("Phone"),
            "company": crm_record.get("Account_Name", {}).get("name")
                       if isinstance(crm_record.get("Account_Name"), dict) else None,
            "title": crm_record.get("Title"),
        }

    def map_from_unified(self, unified: dict) -> dict:
        return {
            "First_Name": unified.get("first_name", ""),
            "Last_Name": unified.get("last_name", ""),
            "Email": unified.get("email"),
            "Phone": unified.get("phone"),
            "Title": unified.get("title"),
        }
