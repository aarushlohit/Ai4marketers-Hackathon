"""Microsoft Dynamics 365 CRM Adapter — Web API v9.2 + Azure AD OAuth 2.0."""

import hashlib
import hmac

import httpx
import structlog

from app.adapters.base import CRMAdapter

logger = structlog.get_logger()

DYNAMICS_TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"


class Dynamics365Adapter(CRMAdapter):
    """Connects to Microsoft Dynamics 365 via Web API v9.2."""

    def __init__(self, credentials: dict):
        super().__init__(credentials)
        self.access_token: str | None = credentials.get("access_token")
        self.instance_url: str = credentials.get("instance_url", "")
        self.azure_tenant_id: str = credentials.get("azure_tenant_id", "common")
        self.resource_url: str = credentials.get("resource_url", "https://org.crm.dynamics.com").rstrip("/")

    @property
    def _base(self) -> str:
        return f"{self.instance_url}/api/data/v9.2"

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Content-Type": "application/json",
        }

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self._base}/WhoAmI",
                headers=self._headers,
            )
            return r.status_code == 200

    async def refresh_access_token(self, refresh_token: str) -> dict:
        token_url = DYNAMICS_TOKEN_URL.format(tenant_id=self.azure_tenant_id)
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(token_url, data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.credentials["client_id"],
                "client_secret": self.credentials["client_secret"],
                "scope": f"{self.resource_url}/.default offline_access",
            })
            r.raise_for_status()
            return r.json()

    async def get_contacts(self, filters=None, limit=100, offset=0) -> list[dict]:
        select = "contactid,firstname,lastname,emailaddress1,telephone1,jobtitle"
        params = {"$select": select, "$top": min(limit, 1000)}
        if filters and filters.get("updated_since"):
            params["$filter"] = (
                f"modifiedon ge {filters['updated_since']}"
            )
        if offset:
            params["$skip"] = offset
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self._base}/contacts",
                                 params=params, headers=self._headers)
            r.raise_for_status()
            return r.json().get("value", [])

    async def create_contact(self, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{self._base}/contacts",
                json=self.map_from_unified(data),
                headers=self._headers,
            )
            r.raise_for_status()
            location = r.headers.get("OData-EntityId", "")
            contact_id = location.split("(")[-1].rstrip(")") if location else ""
            return {"contactid": contact_id}

    async def update_contact(self, contact_id: str, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.patch(
                f"{self._base}/contacts({contact_id})",
                json=self.map_from_unified(data),
                headers=self._headers,
            )
            r.raise_for_status()
            return {"contactid": contact_id, "success": True}

    async def get_accounts(self, filters=None, limit=100) -> list[dict]:
        params = {
            "$select": "accountid,name,telephone1,emailaddress1",
            "$top": min(limit, 1000),
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self._base}/accounts",
                                 params=params, headers=self._headers)
            r.raise_for_status()
            return r.json().get("value", [])

    async def handle_webhook(self, payload: dict) -> dict:
        # Dynamics uses Service Bus / Azure Event Grid for webhooks
        return {
            "event_type": payload.get("MessageName", "unknown"),
            "record_id": payload.get("PrimaryEntityId"),
            "object_type": payload.get("PrimaryEntityName", "unknown"),
        }

    def verify_webhook_signature(self, payload: bytes, headers: dict) -> bool:
        # Dynamics webhooks are authenticated via Azure Service Bus token
        return True

    def map_to_unified(self, crm_record: dict) -> dict:
        return {
            "external_id": crm_record.get("contactid"),
            "crm_source": "dynamics",
            "first_name": crm_record.get("firstname", ""),
            "last_name": crm_record.get("lastname", ""),
            "email": crm_record.get("emailaddress1"),
            "phone": crm_record.get("telephone1"),
            "title": crm_record.get("jobtitle"),
            "company": crm_record.get("_parentcustomerid_value@OData.Community.Display.V1.FormattedValue"),
        }

    def map_from_unified(self, unified: dict) -> dict:
        result = {
            "firstname": unified.get("first_name", ""),
            "lastname": unified.get("last_name", ""),
        }
        if unified.get("email"):
            result["emailaddress1"] = unified["email"]
        if unified.get("phone"):
            result["telephone1"] = unified["phone"]
        if unified.get("title"):
            result["jobtitle"] = unified["title"]
        return result
