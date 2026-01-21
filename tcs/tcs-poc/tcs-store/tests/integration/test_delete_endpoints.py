"""Integration tests for delete endpoints."""

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


class TestDeleteByIdEndpoint:
    """Tests for POST /delete/id endpoint."""
    
    def test_delete_by_id_success(self):
        """Test successful delete of an existing trade with valid context."""
        # Arrange - save a trade first
        save_request = {
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
        client.post("/save/new", json=save_request)
        
        # Delete request
        delete_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "cleanup_cancelled_trade"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/delete/id", json=delete_request)
        
        # Assert
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify trade is actually deleted
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load",
                "intent": "verify_deletion"
            },
            "id": "test-trade-001"
        }
        load_response = client.post("/load/id", json=load_request)
        assert load_response.status_code == 404
    
    def test_delete_by_id_idempotent(self):
        """Test idempotent behavior - deleting non-existent trade succeeds."""
        # Arrange
        delete_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "cleanup"
            },
            "id": "non-existent-trade"
        }
        
        # Act
        response = client.post("/delete/id", json=delete_request)
        
        # Assert - should succeed even though trade doesn't exist
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
    
    def test_delete_by_id_idempotent_multiple_calls(self):
        """Test idempotent behavior - deleting same trade multiple times succeeds."""
        # Arrange - save a trade first
        save_request = {
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
        client.post("/save/new", json=save_request)
        
        delete_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "cleanup"
            },
            "id": "test-trade-001"
        }
        
        # Act - delete multiple times
        response1 = client.post("/delete/id", json=delete_request)
        response2 = client.post("/delete/id", json=delete_request)
        response3 = client.post("/delete/id", json=delete_request)
        
        # Assert - all should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
    
    def test_delete_by_id_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        request_data = {
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/delete/id", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_delete_by_id_empty_context_user(self):
        """Test error when context user is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "cleanup"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/delete/id", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("user" in str(err).lower() for err in detail)
        else:
            assert "user" in detail.lower()
    
    def test_delete_by_id_empty_context_agent(self):
        """Test error when context agent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "",
                "action": "delete",
                "intent": "cleanup"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/delete/id", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("agent" in str(err).lower() for err in detail)
        else:
            assert "agent" in detail.lower()
    
    def test_delete_by_id_empty_context_action(self):
        """Test error when context action is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "",
                "intent": "cleanup"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/delete/id", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("action" in str(err).lower() for err in detail)
        else:
            assert "action" in detail.lower()
    
    def test_delete_by_id_empty_context_intent(self):
        """Test error when context intent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "delete",
                "intent": ""
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/delete/id", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("intent" in str(err).lower() for err in detail)
        else:
            assert "intent" in detail.lower()
    
    def test_delete_by_id_missing_id(self):
        """Test error when trade ID is missing."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "cleanup"
            }
        }
        
        # Act
        response = client.post("/delete/id", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_delete_by_id_invalid_json(self):
        """Test error when JSON is invalid."""
        # Act
        response = client.post(
            "/delete/id",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code == 422


class TestDeleteGroupEndpoint:
    """Tests for POST /delete/group endpoint."""
    
    def test_delete_group_success_all_found(self):
        """Test successful delete of multiple existing trades with valid context."""
        # Arrange - save multiple trades
        for i in range(1, 4):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-00{i}",
                    "data": {"trade_type": "IR_SWAP"}
                }
            }
            client.post("/save/new", json=save_request)
        
        # Delete request
        delete_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup_cancelled_trades"
            },
            "ids": ["test-trade-001", "test-trade-002", "test-trade-003"]
        }
        
        # Act
        response = client.post("/delete/group", json=delete_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["deleted_count"] == 3
        assert result["missing_ids"] == []
        
        # Verify trades are actually deleted
        for i in range(1, 4):
            load_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "load",
                    "intent": "verify_deletion"
                },
                "id": f"test-trade-00{i}"
            }
            load_response = client.post("/load/id", json=load_request)
            assert load_response.status_code == 404
    
    def test_delete_group_partial_found(self):
        """Test delete when some trades exist and some don't."""
        # Arrange - save only 2 out of 3 trades
        for i in range(1, 3):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-00{i}",
                    "data": {"trade_type": "IR_SWAP"}
                }
            }
            client.post("/save/new", json=save_request)
        
        # Delete request includes non-existent trade
        delete_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup"
            },
            "ids": ["test-trade-001", "test-trade-002", "test-trade-003"]
        }
        
        # Act
        response = client.post("/delete/group", json=delete_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["deleted_count"] == 2
        assert result["missing_ids"] == ["test-trade-003"]
    
    def test_delete_group_none_found(self):
        """Test delete when no trades exist."""
        # Arrange
        delete_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup"
            },
            "ids": ["non-existent-1", "non-existent-2", "non-existent-3"]
        }
        
        # Act
        response = client.post("/delete/group", json=delete_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["deleted_count"] == 0
        assert set(result["missing_ids"]) == {"non-existent-1", "non-existent-2", "non-existent-3"}
    
    def test_delete_group_idempotent(self):
        """Test idempotent behavior - deleting same group multiple times."""
        # Arrange - save trades
        for i in range(1, 3):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-00{i}",
                    "data": {"trade_type": "IR_SWAP"}
                }
            }
            client.post("/save/new", json=save_request)
        
        delete_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup"
            },
            "ids": ["test-trade-001", "test-trade-002"]
        }
        
        # Act - delete multiple times
        response1 = client.post("/delete/group", json=delete_request)
        response2 = client.post("/delete/group", json=delete_request)
        
        # Assert
        assert response1.status_code == 200
        assert response1.json()["deleted_count"] == 2
        assert response1.json()["missing_ids"] == []
        
        assert response2.status_code == 200
        assert response2.json()["deleted_count"] == 0
        assert set(response2.json()["missing_ids"]) == {"test-trade-001", "test-trade-002"}
    
    def test_delete_group_empty_list(self):
        """Test delete with empty ID list."""
        # Arrange
        delete_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup"
            },
            "ids": []
        }
        
        # Act
        response = client.post("/delete/group", json=delete_request)
        
        # Assert
        assert response.status_code == 422  # Validation error for empty list
    
    def test_delete_group_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        request_data = {
            "ids": ["test-trade-001", "test-trade-002"]
        }
        
        # Act
        response = client.post("/delete/group", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_delete_group_invalid_context(self):
        """Test error when context is invalid."""
        # Arrange
        request_data = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup"
            },
            "ids": ["test-trade-001", "test-trade-002"]
        }
        
        # Act
        response = client.post("/delete/group", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_delete_group_missing_ids(self):
        """Test error when IDs list is missing."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup"
            }
        }
        
        # Act
        response = client.post("/delete/group", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_delete_group_invalid_json(self):
        """Test error when JSON is invalid."""
        # Act
        response = client.post(
            "/delete/group",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_delete_group_single_trade(self):
        """Test delete group with single trade."""
        # Arrange - save a trade
        save_request = {
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
        client.post("/save/new", json=save_request)
        
        # Delete request
        delete_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "cleanup"
            },
            "ids": ["test-trade-001"]
        }
        
        # Act
        response = client.post("/delete/group", json=delete_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["deleted_count"] == 1
        assert result["missing_ids"] == []
