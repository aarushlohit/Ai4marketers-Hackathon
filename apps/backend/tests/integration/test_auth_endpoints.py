"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_health_check(self, client: AsyncClient):
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    async def test_register_new_user(self, client: AsyncClient):
        r = await client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "newuser@test.com"
        assert "hashed_password" not in data

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient):
        payload = {
            "email": "duplicate@test.com",
            "password": "SecurePass123!",
            "first_name": "A",
            "last_name": "B",
        }
        await client.post("/api/v1/auth/register", json=payload)
        r = await client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 409

    async def test_login_valid_credentials(self, client: AsyncClient, test_user):
        user, password = test_user
        r = await client.post("/api/v1/auth/login", json={
            "email": user.email,
            "password": password,
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password_returns_401(self, client: AsyncClient, test_user):
        user, _ = test_user
        r = await client.post("/api/v1/auth/login", json={
            "email": user.email,
            "password": "WrongPassword!",
        })
        assert r.status_code == 401

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        r = await client.get("/api/v1/customers")
        assert r.status_code == 403

    async def test_protected_endpoint_with_token(
        self, client: AsyncClient, auth_headers
    ):
        r = await client.get("/api/v1/customers", headers=auth_headers)
        # 200 expected even if no customers exist yet
        assert r.status_code == 200

    async def test_refresh_token(self, client: AsyncClient, test_user):
        user, password = test_user
        login = await client.post("/api/v1/auth/login", json={
            "email": user.email,
            "password": password,
        })
        refresh_token = login.json()["refresh_token"]

        r = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert r.status_code == 200
        assert "access_token" in r.json()
