"""
Base CRM Adapter interface.
All CRM-specific adapters implement this ABC so the sync engine
and webhook processor can work with any CRM uniformly.
"""

from abc import ABC, abstractmethod
from typing import Any


class CRMAdapter(ABC):
    """Abstract base for all CRM integrations."""

    def __init__(self, credentials: dict[str, str]):
        self.credentials = credentials
        self.client = None

    # ── Authentication ────────────────────────────────────────
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the CRM and store the access token."""

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Exchange a refresh token for a new access token."""

    # ── Contacts / Customers ──────────────────────────────────
    @abstractmethod
    async def get_contacts(
        self,
        filters: dict | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Retrieve contacts/leads from the CRM."""

    @abstractmethod
    async def create_contact(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new contact in the CRM."""

    @abstractmethod
    async def update_contact(
        self, contact_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing contact in the CRM."""

    # ── Accounts / Companies ──────────────────────────────────
    @abstractmethod
    async def get_accounts(
        self,
        filters: dict | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieve accounts/companies from the CRM."""

    # ── Data Mapping ──────────────────────────────────────────
    @abstractmethod
    def map_to_unified(self, crm_record: dict) -> dict:
        """Transform a CRM-native record to the Miracle Birds unified schema."""

    @abstractmethod
    def map_from_unified(self, unified_record: dict) -> dict:
        """Transform a unified record back to the CRM-native format."""

    # ── Webhooks ──────────────────────────────────────────────
    @abstractmethod
    async def handle_webhook(self, payload: dict) -> dict:
        """Parse and normalise an inbound webhook event from the CRM."""

    @abstractmethod
    def verify_webhook_signature(
        self, payload: bytes, headers: dict
    ) -> bool:
        """Verify the HMAC/signature on an inbound webhook."""
