"""Workflow Engine configuration settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class WorkflowEngineSettings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://miracle_birds_user:ashlin@localhost:5432/miracle_birds"
    REDIS_URL: str = "redis://:change-this-password@localhost:6379/0"
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://:change-this-password@localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://:change-this-password@localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> WorkflowEngineSettings:
    return WorkflowEngineSettings()


settings = get_settings()
