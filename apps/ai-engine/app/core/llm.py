"""
LLM provider factory — swappable between OpenAI and Gemini.
Uses LangChain's unified ChatModel interface.
"""

from functools import lru_cache
from langchain_core.language_models import BaseChatModel
from app.core.config import settings


@lru_cache
def get_llm(provider: str | None = None) -> BaseChatModel:
    """Return a configured LLM instance based on the configured provider."""
    provider = provider or settings.LLM_PROVIDER

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
        )

    elif provider == "opencode":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="deepseek-v4-flash-free",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
            base_url="https://opencode.ai/zen/v1",
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            google_api_key=settings.GEMINI_API_KEY,
        )

    raise ValueError(f"Unknown LLM provider: {provider}")


def get_embeddings():
    """Return the embedding model (always OpenAI ada-002)."""
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )
