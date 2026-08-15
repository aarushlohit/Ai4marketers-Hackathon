from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_authorize_redirects_back_with_code_and_state():
    response = client.get(
        "/oauth/zoho/authorize",
        params={
            "redirect_uri": "http://localhost:28003/zoho/callback",
            "state": "state-123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == (
        "http://localhost:28003/zoho/callback?code=mock-zoho-code&state=state-123"
    )


def test_zoho_token_response_contains_api_domain():
    response = client.post(
        "/oauth/zoho/token",
        data={"grant_type": "authorization_code", "code": "mock-zoho-code"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "mock-zoho-access-token"
    assert response.json()["api_domain"] == "http://mock_crm_provider:8900"


def test_salesforce_token_response_contains_instance_url():
    response = client.post(
        "/oauth/salesforce/token",
        data={"grant_type": "authorization_code", "code": "mock-salesforce-code"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "mock-salesforce-access-token"
    assert response.json()["instance_url"] == "http://mock_crm_provider:8900"


def test_mock_zoho_contacts_shape_matches_adapter_expectations():
    response = client.get("/crm/v3/Contacts")

    assert response.status_code == 200
    first = response.json()["data"][0]
    assert first["id"] == "ZOHO-CON-001"
    assert first["First_Name"]
    assert first["Last_Name"]
    assert first["Email"]


def test_mock_salesforce_query_shape_matches_adapter_expectations():
    response = client.get("/services/data/v58.0/query", params={"q": "SELECT Id FROM Contact"})

    assert response.status_code == 200
    body = response.json()
    assert body["done"] is True
    assert body["records"][0]["Id"] == "SF-CON-001"
    assert body["records"][0]["FirstName"]
