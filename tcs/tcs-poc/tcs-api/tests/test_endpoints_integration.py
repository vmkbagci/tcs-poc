"""Integration tests for API endpoints with service layer."""

import pytest
from fastapi.testclient import TestClient
from trade_api.main import create_app


@pytest.fixture
def client():
    """Create a test client."""
    app = create_app()
    return TestClient(app)


def test_new_endpoint_integration(client):
    """Test /new endpoint returns trade data."""
    response = client.get("/api/v1/trades/new?trade_type=ir-swap")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["trade_data"] is not None
    assert data["metadata"] is not None
    assert "trade_id" in data["metadata"]
    assert "documentId" in data["metadata"]
    assert "correlationId" in data["metadata"]
    assert data["metadata"]["trade_type"] == "ir-swap"


def test_new_endpoint_invalid_type(client):
    """Test /new endpoint with invalid trade type."""
    response = client.get("/api/v1/trades/new?trade_type=invalid-type")

    # Should return error status code
    assert response.status_code in [400, 500]


def test_validate_endpoint_integration(client):
    """Test /validate endpoint validates trade data."""
    # First create a trade
    create_response = client.get("/api/v1/trades/new?trade_type=ir-swap")
    assert create_response.status_code == 200
    trade_data = create_response.json()["trade_data"]

    # Now validate it
    validate_response = client.post(
        "/api/v1/trades/validate",
        json={"trade_data": trade_data}
    )

    assert validate_response.status_code == 200
    data = validate_response.json()
    assert "success" in data
    assert isinstance(data["success"], bool)
    assert "errors" in data
    assert "warnings" in data
    assert "metadata" in data
    assert "documentId" in data["metadata"]
    assert "correlationId" in data["metadata"]


def test_validate_endpoint_invalid_data(client):
    """Test /validate endpoint with invalid data."""
    response = client.post(
        "/api/v1/trades/validate",
        json={"trade_data": {"invalid": "data"}}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert len(data["errors"]) > 0


def test_save_endpoint_placeholder(client):
    """Test /save endpoint placeholder."""
    response = client.post(
        "/api/v1/trades/save",
        json={"trade_data": {"test": "data"}}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "warnings" in data


def test_validate_endpoint_with_metadata(client):
    """Test /validate endpoint with metadata in request."""
    # First create a trade
    create_response = client.get("/api/v1/trades/new?trade_type=ir-swap")
    assert create_response.status_code == 200
    trade_data = create_response.json()["trade_data"]

    # Validate with provided metadata
    validate_response = client.post(
        "/api/v1/trades/validate",
        json={
            "trade_data": trade_data,
            "metadata": {
                "documentId": "12345678-1234-1234-1234-123456789012",
                "correlationId": "87654321-4321-4321-4321-210987654321"
            }
        }
    )

    assert validate_response.status_code == 200
    data = validate_response.json()
    assert data["metadata"]["documentId"] == "12345678-1234-1234-1234-123456789012"
    assert data["metadata"]["correlationId"] == "87654321-4321-4321-4321-210987654321"


def test_validate_endpoint_without_metadata(client):
    """Test /validate endpoint generates metadata when not provided."""
    # First create a trade
    create_response = client.get("/api/v1/trades/new?trade_type=ir-swap")
    assert create_response.status_code == 200
    trade_data = create_response.json()["trade_data"]

    # Validate without metadata
    validate_response = client.post(
        "/api/v1/trades/validate",
        json={"trade_data": trade_data}
    )

    assert validate_response.status_code == 200
    data = validate_response.json()
    assert "documentId" in data["metadata"]
    assert "correlationId" in data["metadata"]
    # Both should be valid UUIDs
    assert len(data["metadata"]["documentId"]) == 36
    assert len(data["metadata"]["correlationId"]) == 36


def test_validate_endpoint_with_partial_metadata(client):
    """Test /validate endpoint with only correlationId provided."""
    # First create a trade
    create_response = client.get("/api/v1/trades/new?trade_type=ir-swap")
    assert create_response.status_code == 200
    trade_data = create_response.json()["trade_data"]

    # Validate with only correlationId
    validate_response = client.post(
        "/api/v1/trades/validate",
        json={
            "trade_data": trade_data,
            "metadata": {
                "correlationId": "87654321-4321-4321-4321-210987654321"
            }
        }
    )

    assert validate_response.status_code == 200
    data = validate_response.json()
    # documentId should be generated
    assert "documentId" in data["metadata"]
    assert len(data["metadata"]["documentId"]) == 36
    # correlationId should be the one provided
    assert data["metadata"]["correlationId"] == "87654321-4321-4321-4321-210987654321"