"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient
from trade_api.main import create_app


@pytest.fixture
def client():
    """Create a test client."""
    app = create_app()
    return TestClient(app)


def test_health_endpoint(client):
    """Test basic /health endpoint returns 200 and correct structure."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_liveness_endpoint(client):
    """Test /health/live endpoint returns 200 and correct structure."""
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_readiness_endpoint(client):
    """Test /health/ready endpoint returns 200 and correct structure."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "timestamp" in data
    assert "version" in data
    assert "checks" in data
    assert data["version"] == "0.1.0"


def test_readiness_checks_runtime(client):
    """Test /health/ready endpoint includes runtime check."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert "checks" in data
    assert "runtime" in data["checks"]
    assert data["checks"]["runtime"] == "ok"


def test_readiness_checks_templates(client):
    """Test /health/ready endpoint includes templates check."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert "checks" in data
    assert "templates" in data["checks"]
    assert data["checks"]["templates"] == "ok"


def test_readiness_checks_validation(client):
    """Test /health/ready endpoint includes validation check."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert "checks" in data
    assert "validation" in data["checks"]
    assert data["checks"]["validation"] == "ok"


def test_health_endpoint_fast_response(client):
    """Test health endpoints respond quickly (< 1 second)."""
    import time

    start = time.time()
    response = client.get("/health/live")
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 1.0, f"Health check took {duration}s, should be < 1s"


def test_readiness_endpoint_fast_response(client):
    """Test readiness endpoint responds quickly (< 1 second)."""
    import time

    start = time.time()
    response = client.get("/health/ready")
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 1.0, f"Readiness check took {duration}s, should be < 1s"


def test_health_timestamp_format(client):
    """Test that timestamps are in ISO format with Z suffix."""
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    timestamp = data["timestamp"]
    # Should end with Z for UTC
    assert timestamp.endswith("Z")
    # Should be valid ISO format (basic validation)
    assert "T" in timestamp


def test_multiple_health_checks(client):
    """Test that multiple health checks work consistently."""
    for _ in range(5):
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_multiple_readiness_checks(client):
    """Test that multiple readiness checks work consistently."""
    for _ in range(5):
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"