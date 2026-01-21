"""Unit tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient

from tcs_store.main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    """
    Test that health endpoint returns 200 status code.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    response = client.get("/health")
    
    assert response.status_code == 200


def test_health_endpoint_returns_service_information():
    """
    Test that health endpoint returns service status, version, and timestamp.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Should have status field
    assert "status" in data
    assert isinstance(data["status"], str)
    assert len(data["status"]) > 0
    
    # Should have version field
    assert "version" in data
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0
    
    # Should have timestamp field
    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)
    assert len(data["timestamp"]) > 0


def test_health_endpoint_status_is_healthy():
    """
    Test that health endpoint returns 'healthy' status.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"


def test_health_endpoint_no_context_required():
    """
    Test that health endpoint does not require context metadata.
    
    Unlike other endpoints, health check should work without context.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    # Health endpoint should work with just a GET request
    response = client.get("/health")
    
    assert response.status_code == 200
    
    # Should not require any request body or context
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data


def test_liveness_endpoint_returns_200():
    """
    Test that liveness probe endpoint returns 200 status code.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    response = client.get("/health/live")
    
    assert response.status_code == 200


def test_liveness_endpoint_returns_service_information():
    """
    Test that liveness endpoint returns service status, version, and timestamp.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    response = client.get("/health/live")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Should have status field
    assert "status" in data
    assert data["status"] == "healthy"
    
    # Should have version field
    assert "version" in data
    assert isinstance(data["version"], str)
    
    # Should have timestamp field
    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)


def test_readiness_endpoint_returns_200():
    """
    Test that readiness probe endpoint returns 200 status code when ready.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    response = client.get("/health/ready")
    
    assert response.status_code == 200


def test_readiness_endpoint_returns_checks():
    """
    Test that readiness endpoint returns dependency checks.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    response = client.get("/health/ready")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Should have status field
    assert "status" in data
    assert data["status"] == "ready"
    
    # Should have version field
    assert "version" in data
    
    # Should have timestamp field
    assert "timestamp" in data
    
    # Should have checks field
    assert "checks" in data
    assert isinstance(data["checks"], dict)
    
    # Should have runtime check
    assert "runtime" in data["checks"]
    assert data["checks"]["runtime"] == "ok"
    
    # Should have storage check
    assert "storage" in data["checks"]
    assert data["checks"]["storage"] == "ok"
    
    # Should have service check
    assert "service" in data["checks"]
    assert data["checks"]["service"] == "ok"
