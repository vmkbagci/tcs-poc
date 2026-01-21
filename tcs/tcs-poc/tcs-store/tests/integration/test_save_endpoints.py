"""Integration tests for save endpoints."""

import pytest
from fastapi.testclient import TestClient

from tcs_store.main import app, store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the store before each test."""
    store.clear()
    yield
    store.clear()


client = TestClient(app)


class TestSaveNewEndpoint:
    """Tests for POST /save/new endpoint."""
    
    def test_save_new_success(self):
        """Test successful save of a new trade with valid context."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {
                    "trade_type": "IR_SWAP",
                    "counterparty": "BANK_A",
                    "notional": 1000000
                }
            }
        }
        
        # Act
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json() == request_data["trade"]
    
    def test_save_new_duplicate_error(self):
        """Test error when saving a trade that already exists."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Save trade first time
        client.post("/save/new", json=request_data)
        
        # Act - try to save again
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()
    
    def test_save_new_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        request_data = {
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_save_new_empty_context_user(self):
        """Test error when context user is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        # Pydantic returns a list of validation errors or a string
        if isinstance(detail, list):
            assert any("user" in str(err).lower() for err in detail)
        else:
            assert "user" in detail.lower()
    
    def test_save_new_empty_context_agent(self):
        """Test error when context agent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("agent" in str(err).lower() for err in detail)
        else:
            assert "agent" in detail.lower()
    
    def test_save_new_empty_context_action(self):
        """Test error when context action is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("action" in str(err).lower() for err in detail)
        else:
            assert "action" in detail.lower()
    
    def test_save_new_empty_context_intent(self):
        """Test error when context intent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": ""
            },
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("intent" in str(err).lower() for err in detail)
        else:
            assert "intent" in detail.lower()
    
    def test_save_new_missing_trade_id(self):
        """Test error when trade ID is missing."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/new", json=request_data)
        
        # Assert
        assert response.status_code == 422
        assert "id" in response.json()["detail"].lower()
    
    def test_save_new_invalid_json(self):
        """Test error when JSON is invalid."""
        # Act
        response = client.post(
            "/save/new",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code == 422


class TestSaveUpdateEndpoint:
    """Tests for POST /save/update endpoint."""
    
    def test_save_update_success(self):
        """Test successful update of an existing trade with valid context."""
        # Arrange - save initial trade
        initial_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {
                    "trade_type": "IR_SWAP",
                    "counterparty": "BANK_A",
                    "notional": 1000000
                }
            }
        }
        client.post("/save/new", json=initial_request)
        
        # Update request
        update_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "save_update",
                "intent": "trade_correction"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {
                    "trade_type": "IR_SWAP",
                    "counterparty": "BANK_B",
                    "notional": 2000000
                }
            }
        }
        
        # Act
        response = client.post("/save/update", json=update_request)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == update_request["trade"]
    
    def test_save_update_not_found(self):
        """Test error when updating a trade that doesn't exist."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_update",
                "intent": "trade_correction"
            },
            "trade": {
                "id": "non-existent-trade",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/update", json=request_data)
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_save_update_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        request_data = {
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/update", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_save_update_invalid_context(self):
        """Test error when context is invalid."""
        # Arrange
        request_data = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "save_update",
                "intent": "trade_correction"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/update", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_save_update_missing_trade_id(self):
        """Test error when trade ID is missing."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_update",
                "intent": "trade_correction"
            },
            "trade": {
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        # Act
        response = client.post("/save/update", json=request_data)
        
        # Assert
        assert response.status_code == 422


class TestSavePartialEndpoint:
    """Tests for POST /save/partial endpoint."""
    
    def test_save_partial_success(self):
        """Test successful partial update with valid context."""
        # Arrange - save initial trade
        initial_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {
                    "trade_type": "IR_SWAP",
                    "counterparty": "BANK_A",
                    "notional": 1000000,
                    "leg1": {
                        "schedule": {"start_date": "2024-01-01"}
                    }
                }
            }
        }
        client.post("/save/new", json=initial_request)
        
        # Partial update request
        partial_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "save_partial",
                "intent": "update_schedule"
            },
            "id": "test-trade-001",
            "updates": {
                "data": {
                    "notional": 2000000
                }
            }
        }
        
        # Act
        response = client.post("/save/partial", json=partial_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == "test-trade-001"
        assert result["data"]["notional"] == 2000000
        assert result["data"]["counterparty"] == "BANK_A"  # Preserved
        assert result["data"]["trade_type"] == "IR_SWAP"  # Preserved
    
    def test_save_partial_not_found(self):
        """Test error when partially updating a trade that doesn't exist."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_partial",
                "intent": "update_schedule"
            },
            "id": "non-existent-trade",
            "updates": {
                "data": {"notional": 2000000}
            }
        }
        
        # Act
        response = client.post("/save/partial", json=request_data)
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_save_partial_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        request_data = {
            "id": "test-trade-001",
            "updates": {
                "data": {"notional": 2000000}
            }
        }
        
        # Act
        response = client.post("/save/partial", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_save_partial_invalid_context(self):
        """Test error when context is invalid."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "",
                "action": "save_partial",
                "intent": "update_schedule"
            },
            "id": "test-trade-001",
            "updates": {
                "data": {"notional": 2000000}
            }
        }
        
        # Act
        response = client.post("/save/partial", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_save_partial_deep_merge(self):
        """Test deep merge behavior in partial update."""
        # Arrange - save initial trade
        initial_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "test-trade-001",
                "data": {
                    "leg1": {
                        "notional": 1000000,
                        "schedule": {"start_date": "2024-01-01"}
                    },
                    "broker": "BrokerA"
                }
            }
        }
        client.post("/save/new", json=initial_request)
        
        # Partial update with nested changes
        partial_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "save_partial",
                "intent": "update_schedule"
            },
            "id": "test-trade-001",
            "updates": {
                "data": {
                    "leg1": {
                        "schedule": {"end_date": "2025-01-01"}
                    }
                }
            }
        }
        
        # Act
        response = client.post("/save/partial", json=partial_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["data"]["leg1"]["notional"] == 1000000  # Preserved
        assert result["data"]["leg1"]["schedule"]["start_date"] == "2024-01-01"  # Preserved
        assert result["data"]["leg1"]["schedule"]["end_date"] == "2025-01-01"  # Added
        assert result["data"]["broker"] == "BrokerA"  # Preserved
