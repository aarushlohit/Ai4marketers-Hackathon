"""Adapter factory — returns the correct CRM adapter by type."""

from app.adapters.base import CRMAdapter
from app.adapters.salesforce import SalesforceAdapter
from app.adapters.zoho import ZohoCRMAdapter
from app.adapters.hubspot import HubSpotAdapter
from app.adapters.dynamics import Dynamics365Adapter
from app.adapters.pipedrive import PipedriveAdapter
from app.adapters.frappe import FrappeCRMAdapter

_ADAPTER_MAP: dict[str, type[CRMAdapter]] = {
    "salesforce": SalesforceAdapter,
    "zoho":       ZohoCRMAdapter,
    "hubspot":    HubSpotAdapter,
    "dynamics":   Dynamics365Adapter,
    "pipedrive":  PipedriveAdapter,
    "frappe":     FrappeCRMAdapter,
}


def get_adapter(crm_type: str, credentials: dict) -> CRMAdapter:
    """
    Instantiate and return the correct CRM adapter.

    Args:
        crm_type: One of 'salesforce', 'zoho', 'hubspot', 'dynamics', 'pipedrive'
        credentials: Dict containing access_token, refresh_token, client_id, etc.

    Raises:
        ValueError: If the crm_type is not supported.
    """
    cls = _ADAPTER_MAP.get(crm_type.lower())
    if cls is None:
        raise ValueError(
            f"Unsupported CRM type: '{crm_type}'. "
            f"Supported: {list(_ADAPTER_MAP.keys())}"
        )
    return cls(credentials)
