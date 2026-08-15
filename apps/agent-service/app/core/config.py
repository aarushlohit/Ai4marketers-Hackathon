"""Agent Service — Configuration."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Miracle Birds Agent Service"
    app_version: str = "3.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://miracle_birds_user:devpassword@postgres:5432/miracle_birds"

    # Redis
    redis_url: str = "redis://:devpassword@redis:6379/0"

    # LLM
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    embedding_model: str = "text-embedding-ada-002"

    # Service URLs
    memory_service_url: str = "http://memory-service:8102"
    knowledge_service_url: str = "http://knowledge-service:8103"
    search_service_url: str = "http://search-service:8104"
    reasoning_service_url: str = "http://reasoning-service:8105"
    simulation_service_url: str = "http://simulation-service:8106"
    executive_service_url: str = "http://executive-service:8107"

    # Agent config
    max_agent_iterations: int = 10
    agent_timeout_seconds: int = 120

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"



settings = Settings()
