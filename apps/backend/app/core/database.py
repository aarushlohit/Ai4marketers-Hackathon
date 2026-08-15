"""
Database engine, session factory, and Row-Level Security helpers.
Uses SQLAlchemy 2.0 async API.
"""

from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ── Base model ────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


from sqlalchemy import text
from fastapi import Request

# ── Session dependency ────────────────────────────────────────────────────────
async def get_db(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session.
    Sets the PostgreSQL RLS context variable for multi-tenant isolation.
    """
    async with AsyncSessionLocal() as session:
        if request and hasattr(request.state, "tenant_id"):
            await set_rls_context(session, request.state.tenant_id)
        yield session


async def set_rls_context(session: AsyncSession, tenant_id: UUID) -> None:
    """Set PostgreSQL RLS session variable for tenant isolation."""
    await session.execute(
        text(f"SELECT set_config('app.tenant_id', '{tenant_id}', true)")
    )


