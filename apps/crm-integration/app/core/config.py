"""CRM Integration Service configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class CRMSettings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/miracle_birds"
    REDIS_URL: str = "redis://localhost:6379/0"

    # CRM OAuth credentials (loaded from env)
    SALESFORCE_CLIENT_ID: str = ""
    SALESFORCE_CLIENT_SECRET: str = ""
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    ZOHO_ACCOUNTS_URL: str = "https://accounts.zoho.com"
    HUBSPOT_CLIENT_ID: str = ""
    HUBSPOT_CLIENT_SECRET: str = ""
    DYNAMICS_CLIENT_ID: str = ""
    DYNAMICS_CLIENT_SECRET: str = ""
    DYNAMICS_TENANT_ID: str = "common"
    PIPEDRIVE_CLIENT_ID: str = ""
    PIPEDRIVE_CLIENT_SECRET: str = ""
    FRAPPE_BASE_URL: str = ""
    FRAPPE_API_KEY: str = ""
    FRAPPE_API_SECRET: str = ""
    DYNAMICS_RESOURCE_URL: str = "https://org.crm.dynamics.com"
    DYNAMICS_INSTANCE_URL: str = ""

    # Local mock CRM provider for demos/tests without real CRM accounts.
    CRM_MOCK_MODE: bool = False
    MOCK_CRM_PUBLIC_URL: str = "http://localhost:28900"
    MOCK_CRM_INTERNAL_URL: str = "http://mock_crm_provider:8900"

    # Sync settings
    INCREMENTAL_SYNC_LOOKBACK_HOURS: int = 2
    FULL_SYNC_PAGE_SIZE: int = 100
    MAX_SYNC_ERRORS: int = 5

    # Internal backend API
    BACKEND_INTERNAL_URL: str = "https://mb-backend.onrender.com"
    INTERNAL_API_KEY: str = ""
    SALESFORCE_API_VERSION: str = "v58.0"

    class Config:
        env_file = ".env"
        extra = "ignore"



@lru_cache
def get_settings() -> CRMSettings:
    return CRMSettings()


settings = get_settings()
