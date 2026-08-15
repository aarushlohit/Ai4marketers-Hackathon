"""Integration tests for customer CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCustomerEndpoints:
    async def test_list_customers_empty(self, client: AsyncClient, auth_headers):
        r = await client.get("/api/v1/customers", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "customers" in data
        assert "total" in data
        assert "page" in data

    async def test_create_customer(self, client: AsyncClient, auth_headers):
        r = await client.post("/api/v1/customers", headers=auth_headers, json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "company": "Acme Corp",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["first_name"] == "Alice"
        assert data["email"] == "alice@example.com"
        assert "id" in data

    async def test_get_customer(self, client: AsyncClient, auth_headers):
        # Create first
        create_r = await client.post("/api/v1/customers", headers=auth_headers, json={
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob@example.com",
        })
        customer_id = create_r.json()["id"]

        # Then fetch
        r = await client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["id"] == customer_id

    async def test_get_nonexistent_customer_returns_404(
        self, client: AsyncClient, auth_headers
    ):
        fake_id = "00000000-0000-0000-0000-000000000999"
        r = await client.get(f"/api/v1/customers/{fake_id}", headers=auth_headers)
        assert r.status_code == 404

    async def test_update_customer(self, client: AsyncClient, auth_headers):
        create_r = await client.post("/api/v1/customers", headers=auth_headers, json={
            "first_name": "Carol",
            "last_name": "White",
        })
        customer_id = create_r.json()["id"]

        r = await client.put(
            f"/api/v1/customers/{customer_id}",
            headers=auth_headers,
            json={"title": "CEO"},
        )
        assert r.status_code == 200
        assert r.json()["title"] == "CEO"

    async def test_delete_customer(self, client: AsyncClient, auth_headers):
        create_r = await client.post("/api/v1/customers", headers=auth_headers, json={
            "first_name": "Dave",
            "last_name": "Brown",
        })
        customer_id = create_r.json()["id"]

        r = await client.delete(
            f"/api/v1/customers/{customer_id}", headers=auth_headers
        )
        assert r.status_code == 204

        # Should now be gone
        r2 = await client.get(
            f"/api/v1/customers/{customer_id}", headers=auth_headers
        )
        assert r2.status_code == 404

    async def test_search_customers(self, client: AsyncClient, auth_headers):
        # Create a searchable customer
        await client.post("/api/v1/customers", headers=auth_headers, json={
            "first_name": "SearchMe",
            "last_name": "Unique",
            "email": "searchme@findme.com",
        })
        r = await client.get(
            "/api/v1/customers?search=SearchMe", headers=auth_headers
        )
        assert r.status_code == 200
        names = [c["first_name"] for c in r.json()["customers"]]
        assert "SearchMe" in names

    async def test_pagination(self, client: AsyncClient, auth_headers):
        r = await client.get(
            "/api/v1/customers?page=1&page_size=5", headers=auth_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["customers"]) <= 5
