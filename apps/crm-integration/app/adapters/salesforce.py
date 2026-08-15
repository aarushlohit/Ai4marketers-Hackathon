"""Salesforce CRM Adapter — REST API v58.0 + OAuth 2.0."""

import hashlib
import hmac
from typing import Any

import httpx
import structlog

from app.adapters.base import CRMAdapter

logger = structlog.get_logger()

SF_AUTH_URL = "https://login.salesforce.com/services/oauth2"


class SalesforceAdapter(CRMAdapter):
    """Connects to Salesforce via REST API v58.0."""

    def __init__(self, credentials: dict):
        super().__init__(credentials)
        self.instance_url: str | None = credentials.get("instance_url")
        self.access_token: str | None = credentials.get("access_token")
        self.api_version = credentials.get("api_version", "v58.0")

    @property
    def _base(self) -> str:
        return f"{self.instance_url}/services/data/{self.api_version}"

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"}

    async def authenticate(self) -> bool:
        """Verify current access token is valid."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self.instance_url}/services/oauth2/userinfo",
                headers=self._headers,
            )
            return r.status_code == 200

    async def refresh_access_token(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{SF_AUTH_URL}/token", data={
                "grant_type": "refresh_token",
                "client_id": self.credentials["client_id"],
                "client_secret": self.credentials["client_secret"],
                "refresh_token": refresh_token,
            })
            r.raise_for_status()
            return r.json()

    async def get_contacts(self, filters=None, limit=100, offset=0) -> list[dict]:
        query = f"SELECT Id,FirstName,LastName,Email,Phone,AccountId,Title FROM Contact LIMIT {limit} OFFSET {offset}"
        if filters and filters.get("updated_since"):
            query = (f"SELECT Id,FirstName,LastName,Email,Phone,AccountId,Title "
                     f"FROM Contact WHERE LastModifiedDate >= {filters['updated_since']} "
                     f"LIMIT {limit} OFFSET {offset}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self._base}/query", params={"q": query},
                                 headers=self._headers)
            r.raise_for_status()
            return r.json().get("records", [])

    async def create_contact(self, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self._base}/sobjects/Contact/",
                                  json=self.map_from_unified(data), headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def update_contact(self, contact_id: str, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.patch(f"{self._base}/sobjects/Contact/{contact_id}",
                                   json=self.map_from_unified(data), headers=self._headers)
            r.raise_for_status()
            return {"id": contact_id, "success": True}

    async def get_accounts(self, filters=None, limit=100) -> list[dict]:
        query = f"SELECT Id,Name,Phone,BillingCity,Industry FROM Account LIMIT {limit}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self._base}/query", params={"q": query},
                                 headers=self._headers)
            r.raise_for_status()
            return r.json().get("records", [])

    async def handle_webhook(self, payload: dict) -> dict:
        return {
            "event_type": payload.get("event", {}).get("type", "unknown"),
            "record_id": payload.get("sobject", {}).get("Id"),
            "object_type": payload.get("event", {}).get("sobjectType", "unknown"),
        }

    def verify_webhook_signature(self, payload: bytes, headers: dict) -> bool:
        secret = self.credentials.get("webhook_secret", "").encode()
        sig = headers.get("x-sfdc-signature", "")
        expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig)

    def map_to_unified(self, crm_record: dict) -> dict:
        return {
            "external_id": crm_record.get("Id"),
            "crm_source": "salesforce",
            "first_name": crm_record.get("FirstName", ""),
            "last_name": crm_record.get("LastName", ""),
            "email": crm_record.get("Email"),
            "phone": crm_record.get("Phone"),
            "title": crm_record.get("Title"),
            "company": crm_record.get("Account", {}).get("Name") if isinstance(
                crm_record.get("Account"), dict) else None,
        }

    def map_from_unified(self, unified: dict) -> dict:
        return {
            "FirstName": unified.get("first_name", ""),
            "LastName": unified.get("last_name", ""),
            "Email": unified.get("email"),
            "Phone": unified.get("phone"),
            "Title": unified.get("title"),
        }
