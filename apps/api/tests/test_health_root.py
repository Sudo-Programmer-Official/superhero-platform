from fastapi.testclient import TestClient

from app.main import app  # noqa: E402


def test_health_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
