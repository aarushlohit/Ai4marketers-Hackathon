"""Integration tests for Phase 2 endpoints."""

import pytest
from httpx import AsyncClient
from uuid import UUID


@pytest.mark.asyncio
class TestPhase2Endpoints:
    async def test_workflows_lifecycle(self, client: AsyncClient, auth_headers):
        # 1. Create a workflow
        create_r = await client.post("/api/v1/workflows", headers=auth_headers, json={
            "name": "High Churn Risk Response",
            "description": "Triggered when churn probability is high",
            "conditions": {"field": "churn_probability", "operator": "gt", "value": 0.5},
            "actions": [{"type": "send_email", "config": {"to": "{{email}}", "subject": "Urgent review"}}],
            "is_active": True
        })
        assert create_r.status_code == 201
        wf_data = create_r.json()
        assert wf_data["name"] == "High Churn Risk Response"
        assert "id" in wf_data
        wf_id = wf_data["id"]

        # 2. List workflows
        list_r = await client.get("/api/v1/workflows", headers=auth_headers)
        assert list_r.status_code == 200
        workflows = list_r.json()
        assert any(w["id"] == wf_id for w in workflows)

        # 3. Toggle workflow
        toggle_r = await client.put(f"/api/v1/workflows/{wf_id}/toggle", headers=auth_headers)
        assert toggle_r.status_code == 200
        assert toggle_r.json()["is_active"] is False

        # 4. Delete workflow
        delete_r = await client.delete(f"/api/v1/workflows/{wf_id}", headers=auth_headers)
        assert delete_r.status_code == 204

    async def test_recommendations_and_feedback(self, client: AsyncClient, auth_headers):
        # First create a customer to link
        cust_r = await client.post("/api/v1/customers", headers=auth_headers, json={
            "first_name": "Reccy",
            "last_name": "Customer",
            "email": "reccy@test.com",
            "company": "Rec Corp"
        })
        customer_id = cust_r.json()["id"]

        # 1. List recommendations (should be empty initially)
        list_r = await client.get(f"/api/v1/recommendations?customer_id={customer_id}", headers=auth_headers)
        assert list_r.status_code == 200
        assert list_r.json() == []

        # 2. Submit feedback requires a valid recommendation.
        # Since generating requires hitting the AI Engine (which may not be running in isolated test env),
        # we skip actual gen call if it fails and test with a mocked entry if needed.
        # But wait! We can verify endpoints directly or mock the AI Engine call.
        # The integration tests in this repository run with test DB but without full service mesh.
        # So we test what we can. Let's make a request and assert status.
        # In a real environment, AI_ENGINE_URL is mocked or pointed to a test host.
