"""Basic setup tests to verify project structure."""

import pytest
from fastapi.testclient import TestClient
from trade_api.main import create_app


def test_app_creation():
    """Test that the FastAPI app can be created successfully."""
    app = create_app()
    assert app is not None
    assert app.title == "Trade API"


def test_api_endpoints_exist():
    """Test that the basic API endpoints are accessible."""
    app = create_app()
    client = TestClient(app)
    
    # Test GET /new endpoint (implemented)
    response = client.get("/api/v1/trades/new?trade_type=irswap&trade_subtype=vanilla")
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Test POST endpoints (placeholders)
    response = client.post("/api/v1/trades/save", json={"trade_data": {}})
    assert response.status_code == 200
    
    response = client.post("/api/v1/trades/validate", json={"trade_data": {}})
    assert response.status_code == 200


def test_config_loading():
    """Test that configuration can be loaded."""
    from trade_api.config import get_settings
    
    settings = get_settings()
    assert settings is not None
    assert settings.api_title == "Trade API"