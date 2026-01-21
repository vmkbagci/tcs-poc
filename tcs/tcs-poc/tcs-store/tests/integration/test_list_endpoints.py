"""Integration tests for list endpoints."""

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


class TestListEndpoint:
    """Tests for POST /list endpoint."""
    
    def test_list_success_with_context(self):
        """Test successful list operation with valid context."""
        # Arrange - save some trades
        for i in range(3):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-{i:03d}",
                    "data": {
                        "trade_type": "IR_SWAP",
                        "counterparty": f"BANK_{chr(65 + i)}",
                        "notional": 1000000 * (i + 1)
                    }
                }
            }
            client.post("/save/new", json=save_request)
        
        # List request
        list_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "list",
                "intent": "view_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/list", json=list_request)
        
        # Assert
        assert response.status_code == 200
        trades = response.json()
        assert len(trades) == 3
        assert all(trade["data"]["trade_type"] == "IR_SWAP" for trade in trades)
    
    def test_list_empty_filter(self):
        """Test list with empty filter returns all trades."""
        # Arrange - save some trades
        for i in range(2):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-{i:03d}",
                    "data": {"trade_type": "IR_SWAP"}
                }
            }
            client.post("/save/new", json=save_request)
        
        # List request with empty filter
        list_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "list",
                "intent": "view_all_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list", json=list_request)
        
        # Assert
        assert response.status_code == 200
        trades = response.json()
        assert len(trades) == 2
    
    def test_list_no_matches(self):
        """Test list with filter that matches no trades."""
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
        
        # List request with non-matching filter
        list_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "list",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "FX_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/list", json=list_request)
        
        # Assert
        assert response.status_code == 200
        trades = response.json()
        assert len(trades) == 0
    
    def test_list_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        request_data = {
            "filter": {}
        }
        
        # Act
        response = client.post("/list", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_list_invalid_context_empty_user(self):
        """Test error when context user is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "list",
                "intent": "view_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("user" in str(err).lower() for err in detail)
        else:
            assert "user" in detail.lower()
    
    def test_list_invalid_context_empty_agent(self):
        """Test error when context agent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "",
                "action": "list",
                "intent": "view_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("agent" in str(err).lower() for err in detail)
        else:
            assert "agent" in detail.lower()
    
    def test_list_invalid_context_empty_action(self):
        """Test error when context action is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "",
                "intent": "view_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("action" in str(err).lower() for err in detail)
        else:
            assert "action" in detail.lower()
    
    def test_list_invalid_context_empty_intent(self):
        """Test error when context intent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "list",
                "intent": ""
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("intent" in str(err).lower() for err in detail)
        else:
            assert "intent" in detail.lower()
    
    def test_list_invalid_filter_regex(self):
        """Test error when filter has invalid regex."""
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
        
        # List request with invalid regex
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "list",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"regex": "[invalid(regex"}
                }
            }
        }
        
        # Act
        response = client.post("/list", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_list_with_complex_filter(self):
        """Test list with multiple filter conditions."""
        # Arrange - save trades with different attributes
        trades_data = [
            {"id": "trade-001", "trade_type": "IR_SWAP", "notional": 1000000},
            {"id": "trade-002", "trade_type": "IR_SWAP", "notional": 2000000},
            {"id": "trade-003", "trade_type": "FX_SWAP", "notional": 1500000},
        ]
        
        for trade_data in trades_data:
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": trade_data["id"],
                    "data": {
                        "trade_type": trade_data["trade_type"],
                        "notional": trade_data["notional"]
                    }
                }
            }
            client.post("/save/new", json=save_request)
        
        # List request with multiple conditions
        list_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "list",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"},
                    "data.notional": {"gte": 1500000}
                }
            }
        }
        
        # Act
        response = client.post("/list", json=list_request)
        
        # Assert
        assert response.status_code == 200
        trades = response.json()
        assert len(trades) == 1
        assert trades[0]["id"] == "trade-002"


class TestCountEndpoint:
    """Tests for POST /list/count endpoint."""
    
    def test_count_success_with_context(self):
        """Test successful count operation with valid context."""
        # Arrange - save some trades
        for i in range(5):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-{i:03d}",
                    "data": {
                        "trade_type": "IR_SWAP" if i < 3 else "FX_SWAP",
                        "notional": 1000000
                    }
                }
            }
            client.post("/save/new", json=save_request)
        
        # Count request
        count_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "count",
                "intent": "count_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/list/count", json=count_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 3
    
    def test_count_empty_filter(self):
        """Test count with empty filter returns total count."""
        # Arrange - save some trades
        for i in range(4):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-{i:03d}",
                    "data": {"trade_type": "IR_SWAP"}
                }
            }
            client.post("/save/new", json=save_request)
        
        # Count request with empty filter
        count_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "count",
                "intent": "count_all_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list/count", json=count_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 4
    
    def test_count_no_matches(self):
        """Test count with filter that matches no trades returns zero."""
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
        
        # Count request with non-matching filter
        count_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "count",
                "intent": "count_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "FX_SWAP"}
                }
            }
        }
        
        # Act
        response = client.post("/list/count", json=count_request)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 0
    
    def test_count_missing_context(self):
        """Test error when context is missing."""
        # Arrange
        request_data = {
            "filter": {}
        }
        
        # Act
        response = client.post("/list/count", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_count_invalid_context_empty_user(self):
        """Test error when context user is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "",
                "agent": "trading_platform",
                "action": "count",
                "intent": "count_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list/count", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("user" in str(err).lower() for err in detail)
        else:
            assert "user" in detail.lower()
    
    def test_count_invalid_context_empty_agent(self):
        """Test error when context agent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "",
                "action": "count",
                "intent": "count_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list/count", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("agent" in str(err).lower() for err in detail)
        else:
            assert "agent" in detail.lower()
    
    def test_count_invalid_context_empty_action(self):
        """Test error when context action is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "",
                "intent": "count_trades"
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list/count", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("action" in str(err).lower() for err in detail)
        else:
            assert "action" in detail.lower()
    
    def test_count_invalid_context_empty_intent(self):
        """Test error when context intent is empty."""
        # Arrange
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "count",
                "intent": ""
            },
            "filter": {}
        }
        
        # Act
        response = client.post("/list/count", json=request_data)
        
        # Assert
        assert response.status_code == 422
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert any("intent" in str(err).lower() for err in detail)
        else:
            assert "intent" in detail.lower()
    
    def test_count_invalid_filter_regex(self):
        """Test error when filter has invalid regex."""
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
        
        # Count request with invalid regex
        request_data = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "count",
                "intent": "count_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"regex": "[invalid(regex"}
                }
            }
        }
        
        # Act
        response = client.post("/list/count", json=request_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_count_matches_list_length(self):
        """Test that count matches the length of list results."""
        # Arrange - save some trades
        for i in range(3):
            save_request = {
                "context": {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                },
                "trade": {
                    "id": f"test-trade-{i:03d}",
                    "data": {
                        "trade_type": "IR_SWAP",
                        "notional": 1000000 * (i + 1)
                    }
                }
            }
            client.post("/save/new", json=save_request)
        
        # Filter criteria
        filter_criteria = {
            "filter": {
                "data.notional": {"gte": 1500000}
            }
        }
        
        # Get list
        list_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "list",
                "intent": "view_trades"
            },
            "filter": filter_criteria
        }
        list_response = client.post("/list", json=list_request)
        
        # Get count
        count_request = {
            "context": {
                "user": "trader_123",
                "agent": "trading_platform",
                "action": "count",
                "intent": "count_trades"
            },
            "filter": filter_criteria
        }
        count_response = client.post("/list/count", json=count_request)
        
        # Assert
        assert list_response.status_code == 200
        assert count_response.status_code == 200
        
        list_result = list_response.json()
        count_result = count_response.json()
        
        assert len(list_result) == count_result["count"]
        assert count_result["count"] == 2  # trades with notional >= 1500000
