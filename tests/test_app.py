from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_body(client: TestClient):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
