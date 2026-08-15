"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings

INSECURE_DEFAULTS = {
    "change-me-in-production",
    "change-this-to-a-random-256-bit-secret",
}


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"
    TRUSTED_HOSTS: str = "localhost,127.0.0.1"
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/miracle_birds"

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        import json
        try:
            parsed = json.loads(self.ALLOWED_ORIGINS)
            if isinstance(parsed, list):
                origins = [str(o).strip() for o in parsed]
                return [*origins, "https://miracle-birds-crm-frontend.vercel.app"]
        except Exception:
            pass
        origins = [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]
        return [*origins, "https://miracle-birds-crm-frontend.vercel.app"]


    # ── AI ────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENCODE_API_KEY: str = ""
    OPENCODE_MODEL: str = "deepseek-v4-flash-free"
    OPENCODE_API_URL: str = "https://opencode.ai/zen/v1/chat/completions"
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"

    # ── Email ────────────────────────────────────────────────
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "onboarding@resend.dev"

    # ── CRM OAuth ─────────────────────────────────────────────
    SALESFORCE_CLIENT_ID: str = ""
    SALESFORCE_CLIENT_SECRET: str = ""
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    HUBSPOT_CLIENT_ID: str = ""
    HUBSPOT_CLIENT_SECRET: str = ""
    DYNAMICS_CLIENT_ID: str = ""
    DYNAMICS_CLIENT_SECRET: str = ""
    DYNAMICS_TENANT_ID: str = ""
    PIPEDRIVE_CLIENT_ID: str = ""
    PIPEDRIVE_CLIENT_SECRET: str = ""

    # ── Engine Service URLs ───────────────────────────────────
    AI_ENGINE_URL: str = "http://localhost:8001"
    ML_ENGINE_URL: str = "http://localhost:8002"
    CRM_SERVICE_URL: str = "http://crm_integration:8003"
    SECURITY_ENGINE_URL: str = "http://localhost:8004"
    WORKFLOW_ENGINE_URL: str = "http://localhost:8005"

    # ── Service Security ──────────────────────────────────────
    INTERNAL_API_KEY: str = ""
    WEBHOOK_SECRET: str = ""

    @property
    def trusted_hosts_list(self) -> List[str]:
        return [h.strip() for h in self.TRUSTED_HOSTS.split(",") if h.strip()]

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT != "production":
            return self

        if self.JWT_SECRET in INSECURE_DEFAULTS or len(self.JWT_SECRET) < 32:
            raise ValueError("JWT_SECRET must be a secure 32+ char value in production")
        if self.SECRET_KEY in INSECURE_DEFAULTS or len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be a secure 32+ char value in production")
        if not self.INTERNAL_API_KEY:
            raise ValueError("INTERNAL_API_KEY is required in production")
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
