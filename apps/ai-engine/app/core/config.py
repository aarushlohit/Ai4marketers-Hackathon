"""AI Engine configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class AIEngineSettings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/miracle_birds"
    REDIS_URL: str = "redis://localhost:6379/0"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"

    LLM_PROVIDER: str = "openai"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 2048

    # RAG settings
    RAG_TOP_K: int = 10
    RAG_MIN_SIMILARITY: float = 0.75

    # Conversation memory TTL (seconds)
    CONVERSATION_TTL: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        extra = "ignore"



@lru_cache
def get_settings() -> AIEngineSettings:
    return AIEngineSettings()


settings = get_settings()
