"""
Pytest configuration and shared fixtures for the backend test suite.
Uses an in-memory SQLite database for unit tests (no Docker required).
Integration tests use the real PostgreSQL from docker-compose.
"""

import asyncio
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import UUID, JSONB

@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

# Monkeypatch PostgreSQL UUID bind processor for SQLite tests
def patch_uuid_bind_processor():
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    original_bind_processor = PG_UUID.bind_processor

    def new_bind_processor(self, dialect):
        original_proc = original_bind_processor(self, dialect)
        def process(value):
            if value is None:
                return None
            if isinstance(value, str):
                return value
            return original_proc(value)
        return process

    PG_UUID.bind_processor = new_bind_processor

patch_uuid_bind_processor()

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.models.user import UserModel
from main import app

# ── In-memory test database ───────────────────────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
).execution_options(
    schema_translate_map={
        "core": None,
        "customers": None,
        "workflows": None,
        "predictions": None,
        "integrations": None,
        "ai": None,
        "analytics": None,
        "security": None,
    }
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)



@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the whole test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables(event_loop):
    """Create all tables in the in-memory DB once per session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional test DB session that rolls back after each test."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client wired to the FastAPI app with test DB."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


# ── Shared test data factories ────────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_tenant_id():
    return uuid4()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant_id):
    """Create and persist a test user, return the model + raw password."""
    raw_password = "TestPass123!"
    user = UserModel(
        tenant_id=test_tenant_id,
        email=f"test-{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password(raw_password),
        first_name="Test",
        last_name="User",
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user, raw_password


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Return Authorization headers for an authenticated test user."""
    user, _ = test_user
    token = create_access_token(
        subject=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
    )
    return {"Authorization": f"Bearer {token}"}
