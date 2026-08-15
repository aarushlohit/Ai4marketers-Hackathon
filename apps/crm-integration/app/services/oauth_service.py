"""
OAuth 2.0 service — manages authorization URLs, token exchange,
secure token storage, and automatic token refresh.
"""

import secrets
import structlog
import base64
from urllib.parse import urlencode

import httpx

logger = structlog.get_logger()

# OAuth app credentials per CRM (loaded from env)
CRM_OAUTH_CONFIG: dict[str, dict] = {
    "salesforce": {
        "auth_url": "https://login.salesforce.com/services/oauth2/authorize",
        "token_url": "https://login.salesforce.com/services/oauth2/token",
        "scope": "full api refresh_token",
    },
    "zoho": {
        "auth_url": "https://accounts.zoho.com/oauth/v2/auth",
        "token_url": "https://accounts.zoho.com/oauth/v2/token",
        "scope": "ZohoCRM.modules.ALL ZohoCRM.settings.ALL ZohoCRM.notifications.ALL",
    },
    "hubspot": {
        "auth_url": "https://app.hubspot.com/oauth/authorize",
        "token_url": "https://api.hubapi.com/oauth/v3/token",
        "scope": "oauth crm.objects.contacts.read crm.objects.contacts.write "
                 "crm.objects.companies.read crm.objects.companies.write "
                 "crm.objects.deals.read crm.objects.deals.write",
    },
    "dynamics": {
        "auth_url": "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        "scope": "offline_access",
    },
    "pipedrive": {
        "auth_url": "https://oauth.pipedrive.com/oauth/authorize",
        "token_url": "https://oauth.pipedrive.com/oauth/token",
        "scope": "admin",
    },
}


class OAuthService:
    def __init__(self, settings):
        self.settings = settings
        # In production, persist states in Redis/DB to survive restarts
        self._pending_states: dict[str, dict] = {}

    def get_client_credentials(self, crm_type: str) -> tuple[str, str]:
        """Return (client_id, client_secret) for a CRM type from env config."""
        crm = crm_type.upper()
        client_id = getattr(self.settings, f"{crm}_CLIENT_ID", "")
        client_secret = getattr(self.settings, f"{crm}_CLIENT_SECRET", "")
        if self.is_mock_mode() and crm_type in {"salesforce", "zoho"}:
            client_id = client_id or f"mock-{crm_type}-client"
            client_secret = client_secret or f"mock-{crm_type}-secret"
        return client_id, client_secret

    def is_mock_mode(self) -> bool:
        """Return whether CRM OAuth/API calls should target the local mock provider."""
        return bool(getattr(self.settings, "CRM_MOCK_MODE", False))

    def _oauth_config(self, crm_type: str) -> dict:
        config = CRM_OAUTH_CONFIG.get(crm_type)
        if not config:
            raise ValueError(f"Unknown CRM type: {crm_type}")
        if self.is_mock_mode() and crm_type in {"salesforce", "zoho"}:
            public_base = getattr(self.settings, "MOCK_CRM_PUBLIC_URL", "http://localhost:28900").rstrip("/")
            internal_base = getattr(self.settings, "MOCK_CRM_INTERNAL_URL", "http://mock_crm_provider:8900").rstrip("/")
            return {
                **config,
                "auth_url": f"{public_base}/oauth/{crm_type}/authorize",
                "token_url": f"{internal_base}/oauth/{crm_type}/token",
            }
        if crm_type == "zoho":
            accounts_url = getattr(self.settings, "ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com").rstrip("/")
            return {
                **config,
                "auth_url": f"{accounts_url}/oauth/v2/auth",
                "token_url": f"{accounts_url}/oauth/v2/token",
            }
        return config

    def build_authorization_url(
        self, crm_type: str, tenant_id: str, redirect_uri: str
    ) -> str:
        """Generate the OAuth authorization URL and store state."""
        config = self._oauth_config(crm_type)

        state = secrets.token_urlsafe(32)
        self._pending_states[state] = {
            "crm_type": crm_type,
            "tenant_id": tenant_id,
            "redirect_uri": redirect_uri,
        }

        client_id, _ = self.get_client_credentials(crm_type)
        if not client_id:
            raise ValueError(f"Missing {crm_type.upper()}_CLIENT_ID")

        auth_url = config["auth_url"]

        # Dynamics needs a real Azure tenant ID in the URL
        if crm_type == "dynamics":
            dynamics_tenant = getattr(self.settings, "DYNAMICS_TENANT_ID", "common")
            auth_url = auth_url.replace("{tenant_id}", dynamics_tenant)
            resource_url = getattr(self.settings, "DYNAMICS_RESOURCE_URL", "https://org.crm.dynamics.com").rstrip("/")
            params_scope = f"{resource_url}/user_impersonation offline_access"
        else:
            params_scope = config["scope"]

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": params_scope,
            "state": state,
            "access_type": "offline",
        }
        if crm_type == "zoho":
            params["prompt"] = "consent"

        return f"{auth_url}?{urlencode(params)}"

    def consume_state(self, state: str, crm_type: str) -> dict:
        """Validate and remove a pending OAuth state value."""
        context = self._pending_states.pop(state, None)
        if not context or context.get("crm_type") != crm_type:
            raise ValueError("Invalid or expired OAuth state")
        return context

    async def exchange_code_for_tokens(
        self, crm_type: str, code: str, redirect_uri: str
    ) -> dict:
        """Exchange an authorization code for access + refresh tokens."""
        config = self._oauth_config(crm_type)
        client_id, client_secret = self.get_client_credentials(crm_type)
        if not client_id or not client_secret:
            raise ValueError(f"Missing {crm_type.upper()} OAuth client credentials")

        token_url = config["token_url"]

        if crm_type == "dynamics":
            dynamics_tenant = getattr(self.settings, "DYNAMICS_TENANT_ID", "common")
            token_url = token_url.replace("{tenant_id}", dynamics_tenant)

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if crm_type == "dynamics":
            resource_url = getattr(self.settings, "DYNAMICS_RESOURCE_URL", "https://org.crm.dynamics.com").rstrip("/")
            payload["scope"] = f"{resource_url}/.default offline_access"

        headers = None
        if crm_type == "pipedrive":
            basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            headers = {"Authorization": f"Basic {basic}"}
            payload.pop("client_id", None)
            payload.pop("client_secret", None)

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(token_url, data=payload, headers=headers)
            r.raise_for_status()
            tokens = r.json()

        logger.info("OAuth token exchange successful", crm_type=crm_type)
        return {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in", 3600),
            "issued_at": tokens.get("issued_at"),
            "instance_url": tokens.get("instance_url"),  # Salesforce only
        "api_domain": tokens.get("api_domain"),  # Zoho accounts location
            "accounts_url": config["token_url"].rsplit("/oauth", 1)[0] if crm_type == "zoho" else None,
        }
