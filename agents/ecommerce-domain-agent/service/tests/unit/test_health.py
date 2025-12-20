import pytest
from fastapi.testclient import TestClient

from ecommerce_agent.server.health import create_health_app


@pytest.fixture
def client():
    app = create_health_app()
    return TestClient(app)


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data

    def test_liveness(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200

    def test_readiness(self, client):
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert "checks" in data