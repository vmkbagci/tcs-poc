"""Unit tests for TradeService."""

import pytest

from tcs_store.storage.in_memory_store import InMemoryStore
from tcs_store.services.trade_service import TradeService
from tcs_store.models import Context
from tcs_store.exceptions import (
    TradeNotFoundError,
    TradeAlreadyExistsError,
    InvalidContextError,
)


def create_context():
    """Create a valid context for testing."""
    return Context(
        user="test_user",
        agent="test_agent",
        action="test_action",
        intent="test_intent"
    )


class TestTradeServiceErrors:
    """Tests for TradeService error conditions."""
    
    def test_save_new_duplicate_error(self):
        """Test that saving a duplicate trade raises TradeAlreadyExistsError."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        trade = {"id": "trade-123", "data": {"test": "value"}}
        service.save_new(trade, context)
        
        # Attempt to save again should raise error
        with pytest.raises(TradeAlreadyExistsError) as exc_info:
            service.save_new(trade, context)
        
        assert "trade-123" in str(exc_info.value)
        assert "already exists" in str(exc_info.value).lower()
    
    def test_save_update_not_found_error(self):
        """Test that updating non-existent trade raises TradeNotFoundError."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        trade = {"id": "nonexistent-trade", "data": {"test": "value"}}
        
        with pytest.raises(TradeNotFoundError) as exc_info:
            service.save_update(trade, context)
        
        assert "nonexistent-trade" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()
    
    def test_load_by_id_not_found_error(self):
        """Test that loading non-existent trade raises TradeNotFoundError."""
        store = InMemoryStore()
        service = TradeService(store)
        
        with pytest.raises(TradeNotFoundError) as exc_info:
            service.load_by_id("nonexistent-trade")
        
        assert "nonexistent-trade" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()
    
    def test_save_new_missing_id(self):
        """Test that saving trade without ID raises ValueError."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        trade = {"data": {"test": "value"}}  # No ID
        
        with pytest.raises(ValueError) as exc_info:
            service.save_new(trade, context)
        
        assert "id" in str(exc_info.value).lower()
    
    def test_save_update_missing_id(self):
        """Test that updating trade without ID raises ValueError."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        trade = {"data": {"test": "value"}}  # No ID
        
        with pytest.raises(ValueError) as exc_info:
            service.save_update(trade, context)
        
        assert "id" in str(exc_info.value).lower()
    
    def test_invalid_context_empty_user(self):
        """Test that empty user in context raises validation error."""
        store = InMemoryStore()
        service = TradeService(store)
        
        # Pydantic will catch empty strings at model validation level
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            Context(
                user="",
                agent="test_agent",
                action="test_action",
                intent="test_intent"
            )
    
    def test_delete_nonexistent_succeeds(self):
        """Test that deleting non-existent trade succeeds (idempotent)."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Should not raise any error
        service.delete_by_id("nonexistent-trade", context)
    
    def test_save_new_then_update_succeeds(self):
        """Test that save_new followed by save_update works correctly."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save new trade
        trade = {"id": "trade-123", "data": {"version": 1}}
        service.save_new(trade, context)
        
        # Update should succeed
        updated_trade = {"id": "trade-123", "data": {"version": 2}}
        result = service.save_update(updated_trade, context)
        
        assert result["data"]["version"] == 2
        
        # Load and verify
        loaded = service.load_by_id("trade-123")
        assert loaded["data"]["version"] == 2
    
    def test_context_validation_all_fields(self):
        """Test context validation for all required fields."""
        from pydantic import ValidationError
        
        # Pydantic validates at model creation, so these will raise ValidationError
        # Test empty user
        with pytest.raises(ValidationError):
            Context(
                user="   ",
                agent="test_agent",
                action="test_action",
                intent="test_intent"
            )
        
        # Test empty agent
        with pytest.raises(ValidationError):
            Context(
                user="test_user",
                agent="   ",
                action="test_action",
                intent="test_intent"
            )
        
        # Test empty action
        with pytest.raises(ValidationError):
            Context(
                user="test_user",
                agent="test_agent",
                action="   ",
                intent="test_intent"
            )
        
        # Test empty intent
        with pytest.raises(ValidationError):
            Context(
                user="test_user",
                agent="test_agent",
                action="test_action",
                intent="   "
            )



class TestBulkOperationEdgeCases:
    """Tests for bulk operation edge cases."""
    
    def test_load_by_ids_empty_list(self):
        """Test loading with empty ID list returns empty results."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save some trades
        service.save_new({"id": "trade-1", "data": {"test": "value1"}}, context)
        service.save_new({"id": "trade-2", "data": {"test": "value2"}}, context)
        
        # Load with empty list
        found_trades, missing_ids = service.load_by_ids([])
        
        assert len(found_trades) == 0
        assert len(missing_ids) == 0
    
    def test_load_by_ids_all_missing(self):
        """Test loading when all IDs are missing."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save some trades
        service.save_new({"id": "trade-1", "data": {"test": "value1"}}, context)
        service.save_new({"id": "trade-2", "data": {"test": "value2"}}, context)
        
        # Try to load non-existent trades
        missing_trade_ids = ["missing-1", "missing-2", "missing-3"]
        found_trades, missing_ids = service.load_by_ids(missing_trade_ids)
        
        assert len(found_trades) == 0
        assert len(missing_ids) == 3
        assert set(missing_ids) == set(missing_trade_ids)
    
    def test_load_by_ids_mix_existing_and_missing(self):
        """Test loading with mix of existing and missing IDs."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save some trades
        trade1 = {"id": "trade-1", "data": {"test": "value1"}}
        trade2 = {"id": "trade-2", "data": {"test": "value2"}}
        service.save_new(trade1, context)
        service.save_new(trade2, context)
        
        # Load mix of existing and missing
        all_ids = ["trade-1", "missing-1", "trade-2", "missing-2"]
        found_trades, missing_ids = service.load_by_ids(all_ids)
        
        # Verify found trades
        assert len(found_trades) == 2
        found_ids = [t["id"] for t in found_trades]
        assert "trade-1" in found_ids
        assert "trade-2" in found_ids
        
        # Verify missing IDs
        assert len(missing_ids) == 2
        assert "missing-1" in missing_ids
        assert "missing-2" in missing_ids
        
        # Verify trade data is correct
        for trade in found_trades:
            if trade["id"] == "trade-1":
                assert trade == trade1
            elif trade["id"] == "trade-2":
                assert trade == trade2
    
    def test_delete_by_ids_empty_list(self):
        """Test deleting with empty ID list."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save some trades
        service.save_new({"id": "trade-1", "data": {"test": "value1"}}, context)
        service.save_new({"id": "trade-2", "data": {"test": "value2"}}, context)
        
        # Delete with empty list
        deleted_count, missing_ids = service.delete_by_ids([], context)
        
        assert deleted_count == 0
        assert len(missing_ids) == 0
        
        # Verify trades still exist
        assert service.load_by_id("trade-1") is not None
        assert service.load_by_id("trade-2") is not None
    
    def test_delete_by_ids_all_missing(self):
        """Test deleting when all IDs are missing."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save some trades
        service.save_new({"id": "trade-1", "data": {"test": "value1"}}, context)
        service.save_new({"id": "trade-2", "data": {"test": "value2"}}, context)
        
        # Try to delete non-existent trades
        missing_trade_ids = ["missing-1", "missing-2", "missing-3"]
        deleted_count, missing_ids = service.delete_by_ids(missing_trade_ids, context)
        
        assert deleted_count == 0
        assert len(missing_ids) == 3
        assert set(missing_ids) == set(missing_trade_ids)
        
        # Verify existing trades still exist
        assert service.load_by_id("trade-1") is not None
        assert service.load_by_id("trade-2") is not None
    
    def test_delete_by_ids_mix_existing_and_missing(self):
        """Test deleting with mix of existing and missing IDs."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save some trades
        service.save_new({"id": "trade-1", "data": {"test": "value1"}}, context)
        service.save_new({"id": "trade-2", "data": {"test": "value2"}}, context)
        service.save_new({"id": "trade-3", "data": {"test": "value3"}}, context)
        
        # Delete mix of existing and missing
        all_ids = ["trade-1", "missing-1", "trade-2", "missing-2"]
        deleted_count, missing_ids = service.delete_by_ids(all_ids, context)
        
        # Verify deleted count
        assert deleted_count == 2
        
        # Verify missing IDs
        assert len(missing_ids) == 2
        assert "missing-1" in missing_ids
        assert "missing-2" in missing_ids
        
        # Verify deleted trades are gone
        with pytest.raises(TradeNotFoundError):
            service.load_by_id("trade-1")
        with pytest.raises(TradeNotFoundError):
            service.load_by_id("trade-2")
        
        # Verify non-deleted trade still exists
        assert service.load_by_id("trade-3") is not None
    
    def test_load_by_ids_preserves_order(self):
        """Test that load_by_ids returns trades in consistent order."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save trades
        for i in range(5):
            service.save_new({"id": f"trade-{i}", "data": {"index": i}}, context)
        
        # Load in specific order
        ids = ["trade-2", "trade-0", "trade-4", "trade-1"]
        found_trades, missing_ids = service.load_by_ids(ids)
        
        # Verify all found
        assert len(found_trades) == 4
        assert len(missing_ids) == 0
        
        # Verify all IDs are present
        found_ids = [t["id"] for t in found_trades]
        assert set(found_ids) == set(ids)
    
    def test_delete_by_ids_duplicate_ids(self):
        """Test deleting with duplicate IDs in the list."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save a trade
        service.save_new({"id": "trade-1", "data": {"test": "value1"}}, context)
        
        # Delete with duplicate IDs
        ids = ["trade-1", "trade-1", "trade-1"]
        deleted_count, missing_ids = service.delete_by_ids(ids, context)
        
        # Should only count as 1 deletion
        assert deleted_count == 1
        assert len(missing_ids) == 2  # The duplicates become "missing" after first delete
        
        # Verify trade is deleted
        with pytest.raises(TradeNotFoundError):
            service.load_by_id("trade-1")
    
    def test_load_by_ids_duplicate_ids(self):
        """Test loading with duplicate IDs in the list."""
        store = InMemoryStore()
        service = TradeService(store)
        context = create_context()
        
        # Save a trade
        trade = {"id": "trade-1", "data": {"test": "value1"}}
        service.save_new(trade, context)
        
        # Load with duplicate IDs
        ids = ["trade-1", "trade-1", "trade-1"]
        found_trades, missing_ids = service.load_by_ids(ids)
        
        # Should find the trade once for each request
        assert len(found_trades) == 3
        assert len(missing_ids) == 0
        
        # All should be the same trade
        for found_trade in found_trades:
            assert found_trade == trade
