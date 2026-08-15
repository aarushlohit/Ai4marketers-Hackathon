from urllib.parse import parse_qs, urlparse

import pytest

from app.api import connections
from app.services.oauth_service import OAuthService


class Settings:
    SALESFORCE_CLIENT_ID = "sf-client"
    SALESFORCE_CLIENT_SECRET = "sf-secret"
    ZOHO_CLIENT_ID = "zoho-client"
    ZOHO_CLIENT_SECRET = "zoho-secret"
    HUBSPOT_CLIENT_ID = ""
    HUBSPOT_CLIENT_SECRET = ""
    DYNAMICS_CLIENT_ID = ""
    DYNAMICS_CLIENT_SECRET = ""
    DYNAMICS_TENANT_ID = "common"
    PIPEDRIVE_CLIENT_ID = ""
    PIPEDRIVE_CLIENT_SECRET = ""
    CRM_MOCK_MODE = False
    MOCK_CRM_PUBLIC_URL = "http://localhost:28900"
    MOCK_CRM_INTERNAL_URL = "http://mock_crm_provider:8900"


class MockSettings(Settings):
    SALESFORCE_CLIENT_ID = ""
    SALESFORCE_CLIENT_SECRET = ""
    ZOHO_CLIENT_ID = ""
    ZOHO_CLIENT_SECRET = ""
    CRM_MOCK_MODE = True


def test_salesforce_authorization_url_is_encoded_and_stateful():
    service = OAuthService(Settings())
    redirect_uri = "http://localhost:18000/api/v1/integrations/salesforce/callback"

    url = service.build_authorization_url("salesforce", "tenant-1", redirect_uri)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert parsed.netloc == "login.salesforce.com"
    assert query["client_id"] == ["sf-client"]
    assert query["redirect_uri"] == [redirect_uri]
    assert query["response_type"] == ["code"]
    assert "refresh_token" in query["scope"][0]

    state_context = service.consume_state(query["state"][0], "salesforce")
    assert state_context == {
        "crm_type": "salesforce",
        "tenant_id": "tenant-1",
        "redirect_uri": redirect_uri,
    }


def test_zoho_authorization_url_requests_consent_for_refresh_token():
    service = OAuthService(Settings())
    redirect_uri = "http://localhost:18000/api/v1/integrations/zoho/callback"

    url = service.build_authorization_url("zoho", "tenant-2", redirect_uri)
    query = parse_qs(urlparse(url).query)

    assert query["client_id"] == ["zoho-client"]
    assert query["redirect_uri"] == [redirect_uri]
    assert query["prompt"] == ["consent"]
    assert "ZohoCRM.modules.ALL" in query["scope"][0]


def test_mock_mode_authorization_uses_public_mock_provider_and_demo_clients():
    service = OAuthService(MockSettings())
    redirect_uri = "http://localhost:18000/api/v1/integrations/zoho/callback"

    url = service.build_authorization_url("zoho", "tenant-2", redirect_uri)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    assert parsed.scheme == "http"
    assert parsed.netloc == "localhost:28900"
    assert parsed.path == "/oauth/zoho/authorize"
    assert query["client_id"] == ["mock-zoho-client"]
    assert query["redirect_uri"] == [redirect_uri]


def test_mock_mode_token_exchange_uses_internal_mock_provider():
    service = OAuthService(MockSettings())

    assert service._oauth_config("salesforce")["token_url"] == (
        "http://mock_crm_provider:8900/oauth/salesforce/token"
    )


@pytest.mark.asyncio
async def test_callback_stores_credentials_for_sync(monkeypatch):
    connections._connections.clear()
    state = "valid-state"
    monkeypatch.setattr(
        connections.oauth_service,
        "consume_state",
        lambda actual_state, crm_type: {
            "crm_type": crm_type,
            "tenant_id": "00000000-0000-0000-0000-000000000001",
            "redirect_uri": "http://localhost:18000/api/v1/integrations/salesforce/callback",
        }
        if actual_state == state
        else None,
    )
    monkeypatch.setattr(
        connections.oauth_service,
        "get_client_credentials",
        lambda crm_type: ("sf-client", "sf-secret"),
    )

    async def exchange_code_for_tokens(crm_type, code, redirect_uri):
        assert crm_type == "salesforce"
        assert code == "oauth-code"
        assert redirect_uri == "http://localhost:18000/api/v1/integrations/salesforce/callback"
        return {
            "access_token": "access",
            "refresh_token": "refresh",
            "instance_url": "https://example.my.salesforce.com",
        }

    monkeypatch.setattr(
        connections.oauth_service,
        "exchange_code_for_tokens",
        exchange_code_for_tokens,
    )

    class FailingDatabase:
        async def execute(self, *_args, **_kwargs):
            raise RuntimeError("database unavailable in unit test")

        async def rollback(self):
            return None

    result = await connections.oauth_callback(
        "salesforce", "oauth-code", state, db=FailingDatabase()
    )

    stored = connections._connections[result["connection_id"]]
    assert stored["tenant_id"] == "00000000-0000-0000-0000-000000000001"
    assert stored["credentials"] == {
        "access_token": "access",
        "refresh_token": "refresh",
        "client_id": "sf-client",
        "client_secret": "sf-secret",
        "instance_url": "https://example.my.salesforce.com",
    }
