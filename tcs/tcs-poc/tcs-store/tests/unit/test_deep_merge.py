"""Unit tests for deep merge scenarios."""

import pytest

from tcs_store.storage.in_memory_store import InMemoryStore
from tcs_store.services.trade_service import TradeService
from tcs_store.models import Context


def create_context():
    """Create a valid context for testing."""
    return Context(
        user="test_user",
        agent="test_agent",
        action="test_action",
        intent="test_intent"
    )


class TestDeepMergeScenarios:
    """Tests for specific deep merge edge cases."""
    
    def test_nested_object_removal_with_null(self):
        """Test that nested objects are removed when set to null."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Create trade with nested object
        trade = {
            "id": "trade-123",
            "data": {
                "leg1": {"notional": 1000000, "currency": "USD"},
                "leg2": {"notional": 2000000, "currency": "EUR"},
                "broker": "BROKER_A"
            }
        }
        service.save_new(trade, context)
        
        # Set leg2 (object) to null - should remove it
        updates = {"data": {"leg2": None}}
        updated = service.save_partial("trade-123", updates, context)
        
        # Verify leg2 removed
        assert "leg2" not in updated["data"]
        
        # Verify leg1 and broker preserved
        assert updated["data"]["leg1"] == {"notional": 1000000, "currency": "USD"}
        assert updated["data"]["broker"] == "BROKER_A"
    
    def test_primitive_field_set_to_null(self):
        """Test that primitive fields are set to null, not removed."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Create trade with primitive fields
        trade = {
            "id": "trade-123",
            "data": {
                "broker": "BROKER_A",
                "trader": "TRADER_1",
                "notional": 1000000
            }
        }
        service.save_new(trade, context)
        
        # Set broker (string) to null - should set to null, not remove
        updates = {"data": {"broker": None}}
        updated = service.save_partial("trade-123", updates, context)
        
        # Verify broker is null (not removed)
        assert "broker" in updated["data"]
        assert updated["data"]["broker"] is None
        
        # Verify other fields preserved
        assert updated["data"]["trader"] == "TRADER_1"
        assert updated["data"]["notional"] == 1000000
    
    def test_deeply_nested_merge_5_levels(self):
        """Test deep merge with 5+ levels of nesting."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Create trade with deeply nested structure
        trade = {
            "id": "trade-123",
            "data": {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": {
                                "level5": {
                                    "value": "original",
                                    "other": "preserved"
                                }
                            }
                        }
                    }
                }
            }
        }
        service.save_new(trade, context)
        
        # Update deeply nested value
        updates = {
            "data": {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": {
                                "level5": {
                                    "value": "updated"
                                }
                            }
                        }
                    }
                }
            }
        }
        updated = service.save_partial("trade-123", updates, context)
        
        # Verify deep value updated
        assert updated["data"]["level1"]["level2"]["level3"]["level4"]["level5"]["value"] == "updated"
        
        # Verify other deep value preserved
        assert updated["data"]["level1"]["level2"]["level3"]["level4"]["level5"]["other"] == "preserved"
    
    def test_list_replacement(self):
        """Test that lists are replaced entirely, not merged."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Create trade with list
        trade = {
            "id": "trade-123",
            "data": {
                "schedule": [
                    {"date": "2024-01-01", "amount": 1000},
                    {"date": "2024-02-01", "amount": 2000}
                ]
            }
        }
        service.save_new(trade, context)
        
        # Update schedule with new list
        updates = {
            "data": {
                "schedule": [
                    {"date": "2024-04-01", "amount": 4000}
                ]
            }
        }
        updated = service.save_partial("trade-123", updates, context)
        
        # Verify list was replaced, not merged
        assert len(updated["data"]["schedule"]) == 1
        assert updated["data"]["schedule"][0] == {"date": "2024-04-01", "amount": 4000}

    
    def test_mixed_null_handling(self):
        """Test mixed null handling for objects and primitives."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Create trade with mixed types
        trade = {
            "id": "trade-123",
            "data": {
                "leg1": {"notional": 1000000},
                "broker": "BROKER_A",
                "notional": 5000000,
                "active": True
            }
        }
        service.save_new(trade, context)
        
        # Set various fields to null
        updates = {
            "data": {
                "leg1": None,
                "broker": None,
                "notional": None,
                "active": None
            }
        }
        updated = service.save_partial("trade-123", updates, context)
        
        # Verify object removed
        assert "leg1" not in updated["data"]
        
        # Verify primitives set to null
        assert "broker" in updated["data"]
        assert updated["data"]["broker"] is None
        assert "notional" in updated["data"]
        assert updated["data"]["notional"] is None
        assert "active" in updated["data"]
        assert updated["data"]["active"] is None
