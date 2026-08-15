from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Miracle Birds Phase 2 API is running"}


def test_health_check():
    response = client.get("/api/v2/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "2.0.0"}
