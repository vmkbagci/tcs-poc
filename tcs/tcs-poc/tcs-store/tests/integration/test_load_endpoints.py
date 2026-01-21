"""Integration tests for load endpoints."""

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


class TestLoadByIdEndpoint:
    """Tests for POST /load/id endpoint."""
    
    def test_load_by_id_success(self):
        """Test successful load of a trade by ID with valid context."""
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
        
        # Load request
        load_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "load_by_id",
                "intent": "trade_review"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == save_request["trade"]
    
    def test_load_by_id_not_found(self):
        """Test error when loading a trade that doesn't exist."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load_by_id",
                "intent": "trade_review"
            },
            "id": "non-existent-trade"
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_load_by_id_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        load_request = {
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 422
    
    def test_load_by_id_empty_context_user(self):
        """Test error when context user is empty."""
        # Arrange
        load_request = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "load_by_id",
                "intent": "trade_review"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("user" in str(err).lower() for err in detail)
        else:
            assert "user" in detail.lower()
    
    def test_load_by_id_empty_context_agent(self):
        """Test error when context agent is empty."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "",
                "action": "load_by_id",
                "intent": "trade_review"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("agent" in str(err).lower() for err in detail)
        else:
            assert "agent" in detail.lower()
    
    def test_load_by_id_empty_context_action(self):
        """Test error when context action is empty."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "",
                "intent": "trade_review"
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("action" in str(err).lower() for err in detail)
        else:
            assert "action" in detail.lower()
    
    def test_load_by_id_empty_context_intent(self):
        """Test error when context intent is empty."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load_by_id",
                "intent": ""
            },
            "id": "test-trade-001"
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("intent" in str(err).lower() for err in detail)
        else:
            assert "intent" in detail.lower()
    
    def test_load_by_id_missing_id(self):
        """Test error when trade ID is missing."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load_by_id",
                "intent": "trade_review"
            }
        }
        
        # Act
        response = client.post("/load/id", json=load_request)
        
        # Assert
        assert response.status_code == 422


class TestLoadGroupEndpoint:
    """Tests for POST /load/group endpoint."""
    
    def test_load_group_success_all_found(self):
        """Test successful load of multiple trades with valid context."""
        # Arrange - save multiple trades
        trades = [
            {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP", "notional": 1000000}
            },
            {
                "id": "test-trade-002",
                "data": {"trade_type": "FX_SWAP", "notional": 2000000}
            },
            {
                "id": "test-trade-003",
                "data": {"trade_type": "COMMODITY_OPTION", "notional": 3000000}
            }
        ]
        
        for trade in trades:
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": trade
            }
            client.post("/save/new", json=save_request)
        
        # Load request
        load_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "portfolio_review"
            },
            "ids": ["test-trade-001", "test-trade-002", "test-trade-003"]
        }
        
        # Act
        response = client.post("/load/group", json=load_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert len(result["trades"]) == 3
        assert len(result["missing_ids"]) == 0
        
        # Verify all trades are present
        trade_ids = [t["id"] for t in result["trades"]]
        assert "test-trade-001" in trade_ids
        assert "test-trade-002" in trade_ids
        assert "test-trade-003" in trade_ids
    
    def test_load_group_partial_found(self):
        """Test load when some trades exist and some don't."""
        # Arrange - save only some trades
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
        
        # Load request with mix of existing and non-existing IDs
        load_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "portfolio_review"
            },
            "ids": ["test-trade-001", "non-existent-001", "non-existent-002"]
        }
        
        # Act
        response = client.post("/load/group", json=load_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert len(result["trades"]) == 1
        assert result["trades"][0]["id"] == "test-trade-001"
        assert len(result["missing_ids"]) == 2
        assert "non-existent-001" in result["missing_ids"]
        assert "non-existent-002" in result["missing_ids"]
    
    def test_load_group_none_found(self):
        """Test load when no trades exist."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "portfolio_review"
            },
            "ids": ["non-existent-001", "non-existent-002"]
        }
        
        # Act
        response = client.post("/load/group", json=load_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert len(result["trades"]) == 0
        assert len(result["missing_ids"]) == 2
        assert "non-existent-001" in result["missing_ids"]
        assert "non-existent-002" in result["missing_ids"]
    
    def test_load_group_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        load_request = {
            "ids": ["test-trade-001"]
        }
        
        # Act
        response = client.post("/load/group", json=load_request)
        
        # Assert
        assert response.status_code == 422
    
    def test_load_group_invalid_context(self):
        """Test error when context is invalid."""
        # Arrange
        load_request = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "portfolio_review"
            },
            "ids": ["test-trade-001"]
        }
        
        # Act
        response = client.post("/load/group", json=load_request)
        
        # Assert
        assert response.status_code == 422
    
    def test_load_group_empty_ids_list(self):
        """Test error when IDs list is empty."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "portfolio_review"
            },
            "ids": []
        }
        
        # Act
        response = client.post("/load/group", json=load_request)
        
        # Assert
        assert response.status_code == 422


class TestLoadFilterEndpoint:
    """Tests for POST /load/filter endpoint."""
    
    def test_load_filter_success_with_matches(self):
        """Test successful load with filter that matches trades."""
        # Arrange - save multiple trades
        trades = [
            {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP", "notional": 1000000}
            },
            {
                "id": "test-trade-002",
                "data": {"trade_type": "FX_SWAP", "notional": 2000000}
            },
            {
                "id": "test-trade-003",
                "data": {"trade_type": "IR_SWAP", "notional": 3000000}
            }
        ]
        
        for trade in trades:
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": trade
            }
            client.post("/save/new", json=save_request)
        
        # Load request with filter
        load_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2
        trade_ids = [t["id"] for t in result]
        assert "test-trade-001" in trade_ids
        assert "test-trade-003" in trade_ids
    
    def test_load_filter_no_matches(self):
        """Test load with filter that matches no trades."""
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
        
        # Load request with filter that doesn't match
        load_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "FX_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0
    
    def test_load_filter_empty_filter(self):
        """Test load with empty filter returns all trades."""
        # Arrange - save multiple trades
        trades = [
            {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            },
            {
                "id": "test-trade-002",
                "data": {"trade_type": "FX_SWAP"}
            }
        ]
        
        for trade in trades:
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": trade
            }
            client.post("/save/new", json=save_request)
        
        # Load request with empty filter
        load_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2
    
    def test_load_filter_multiple_conditions(self):
        """Test load with multiple filter conditions (AND logic)."""
        # Arrange - save multiple trades
        trades = [
            {
                "id": "test-trade-001",
                "data": {"trade_type": "IR_SWAP", "notional": 1000000}
            },
            {
                "id": "test-trade-002",
                "data": {"trade_type": "IR_SWAP", "notional": 2000000}
            },
            {
                "id": "test-trade-003",
                "data": {"trade_type": "FX_SWAP", "notional": 3000000}
            }
        ]
        
        for trade in trades:
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": trade
            }
            client.post("/save/new", json=save_request)
        
        # Load request with multiple conditions
        load_request = {
            "context": {
                "user": "trader_456",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"},
                    "data.notional": {"gte": 2000000}
                }
            }
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == "test-trade-002"
    
    def test_load_filter_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        load_request = {
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 422
    
    def test_load_filter_invalid_context(self):
        """Test error when context is invalid."""
        # Arrange
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 422
    
    def test_load_filter_invalid_filter_structure(self):
        """Test error when filter structure is invalid."""
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
        
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": "IR_SWAP"  # Should be a dict with operator
                }
            }
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 422
        assert "filter" in response.json()["detail"].lower()
    
    def test_load_filter_invalid_operator(self):
        """Test error when filter uses invalid operator."""
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
        
        load_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"invalid_op": "IR_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/load/filter", json=load_request)
        
        # Assert
        assert response.status_code == 422
        assert "operator" in response.json()["detail"].lower()
