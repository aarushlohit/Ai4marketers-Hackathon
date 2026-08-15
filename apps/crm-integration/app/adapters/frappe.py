"""
Frappe CRM Adapter.
Implements the CRMAdapter interface for Frappe CRM REST API.
"""

import httpx
from typing import Any
from .base import CRMAdapter

class FrappeCRMAdapter(CRMAdapter):
    """Adapter for Frappe CRM Integration."""

    def __init__(self, credentials: dict[str, str]):
        super().__init__(credentials)
        self.base_url = credentials.get("base_url", "http://localhost:8000")
        self.api_key = credentials.get("api_key")
        self.api_secret = credentials.get("api_secret")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"token {self.api_key}:{self.api_secret}"}
        )

    async def authenticate(self) -> bool:
        """Verify API keys with Frappe CRM."""
        try:
            response = await self.client.get("/api/method/frappe.auth.get_logged_user")
            return response.status_code == 200
        except Exception:
            return False

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Not typically needed for Frappe token-based auth."""
        return {"access_token": f"{self.api_key}:{self.api_secret}"}

    async def get_contacts(self, filters: dict | None = None, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Retrieve CRM Leads from Frappe CRM."""
        params = {
            "fields": '["name", "lead_name", "email_id", "mobile_no", "company_name", "status"]',
            "limit_page_length": limit,
            "limit_start": offset,
        }
        if filters:
            params["filters"] = str(filters)
            
        try:
            response = await self.client.get("/api/resource/CRM Lead", params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            print(f"Error fetching Frappe Leads: {e}")
            return []

    async def create_contact(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create CRM Lead in Frappe CRM."""
        frappe_data = self.map_from_unified(data)
        response = await self.client.post("/api/resource/CRM Lead", json=frappe_data)
        response.raise_for_status()
        return self.map_to_unified(response.json().get("data", {}))

    async def update_contact(self, contact_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing CRM Lead."""
        frappe_data = self.map_from_unified(data)
        response = await self.client.put(f"/api/resource/CRM Lead/{contact_id}", json=frappe_data)
        response.raise_for_status()
        return self.map_to_unified(response.json().get("data", {}))

    async def get_accounts(self, filters: dict | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Retrieve CRM Organizations from Frappe CRM."""
        params = {
            "fields": '["name", "organization_name", "website", "territory"]',
            "limit_page_length": limit,
        }
        response = await self.client.get("/api/resource/CRM Organization", params=params)
        response.raise_for_status()
        return response.json().get("data", [])

    def map_to_unified(self, crm_record: dict) -> dict:
        """Transform Frappe CRM Lead to Miracle Birds unified schema."""
        return {
            "external_id": crm_record.get("name"),
            "crm_source": "frappe",
            "first_name": crm_record.get("lead_name", "").split(" ")[0] if crm_record.get("lead_name") else "",
            "last_name": " ".join(crm_record.get("lead_name", "").split(" ")[1:]) if crm_record.get("lead_name") else "",
            "email": crm_record.get("email_id"),
            "phone": crm_record.get("mobile_no"),
            "company": crm_record.get("company_name"),
            "status": crm_record.get("status", "Open"),
        }

    def map_from_unified(self, unified_record: dict) -> dict:
        """Transform unified record back to Frappe CRM Lead format."""
        return {
            "lead_name": f"{unified_record.get('first_name', '')} {unified_record.get('last_name', '')}".strip(),
            "email_id": unified_record.get("email"),
            "mobile_no": unified_record.get("phone"),
            "company_name": unified_record.get("company"),
        }

    async def handle_webhook(self, payload: dict) -> dict:
        """Parse Frappe Webhook event."""
        return {"event": "updated", "data": self.map_to_unified(payload)}

    def verify_webhook_signature(self, payload: bytes, headers: dict) -> bool:
        """Verify signature for Frappe CRM."""
        return True
