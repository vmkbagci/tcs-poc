"""Property-based tests for bulk operations."""

import uuid
from hypothesis import given, settings
import hypothesis.strategies as st

from tcs_store.storage.in_memory_store import InMemoryStore
from tcs_store.services.trade_service import TradeService
from tcs_store.models import Context


def generate_context():
    """Generate a valid context."""
    return Context(
        user=f"user_{uuid.uuid4().hex[:8]}",
        agent="test_agent",
        action="test_action",
        intent="test_intent"
    )


def generate_trade_with_id():
    """Generate a trade with a unique ID."""
    return {
        "id": str(uuid.uuid4()),
        "data": {
            "trade_type": "IR_SWAP",
            "counterparty": "BANK_A",
            "notional": 1000000
        }
    }


# Feature: tcs-store, Property 7: Group Load Completeness
@given(
    num_existing=st.integers(min_value=0, max_value=20),
    num_missing=st.integers(min_value=0, max_value=20)
)
@settings(max_examples=100)
def test_group_load_completeness(num_existing, num_missing):
    """
    Test group load completeness property.
    
    For any list of trade IDs, calling load_by_ids should return exactly
    the trades that exist in the store and correctly identify all missing
    IDs in the response.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create and save existing trades
    existing_trades = []
    existing_ids = []
    for _ in range(num_existing):
        trade = generate_trade_with_id()
        service.save_new(trade, context)
        existing_trades.append(trade)
        existing_ids.append(trade["id"])
    
    # Generate missing IDs (not in store)
    missing_ids = [str(uuid.uuid4()) for _ in range(num_missing)]
    
    # Combine existing and missing IDs
    all_ids = existing_ids + missing_ids
    
    # Load by IDs
    found_trades, returned_missing_ids = service.load_by_ids(all_ids)
    
    # Verify all existing trades are found
    assert len(found_trades) == num_existing
    found_ids = [trade["id"] for trade in found_trades]
    for trade_id in existing_ids:
        assert trade_id in found_ids
    
    # Verify all missing IDs are reported
    assert len(returned_missing_ids) == num_missing
    assert set(returned_missing_ids) == set(missing_ids)
    
    # Verify found trades match original trades
    for trade in existing_trades:
        matching_found = [t for t in found_trades if t["id"] == trade["id"]]
        assert len(matching_found) == 1
        assert matching_found[0] == trade


# Feature: tcs-store, Property 7: Group Load Completeness
@given(
    trades_data=st.lists(
        st.dictionaries(
            st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
            st.one_of(st.text(), st.integers()),
            min_size=1,
            max_size=5
        ),
        min_size=1,
        max_size=15
    )
)
@settings(max_examples=100)
def test_group_load_preserves_data(trades_data):
    """
    Test that group load preserves all trade data.
    
    For any set of trades, loading them via load_by_ids should return
    trades with all fields preserved exactly as they were saved.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with unique IDs
    trades = []
    trade_ids = []
    for data in trades_data:
        trade = {"id": str(uuid.uuid4()), **data}
        service.save_new(trade, context)
        trades.append(trade)
        trade_ids.append(trade["id"])
    
    # Load all trades
    found_trades, missing_ids = service.load_by_ids(trade_ids)
    
    # Verify no missing IDs
    assert len(missing_ids) == 0
    
    # Verify all trades found
    assert len(found_trades) == len(trades)
    
    # Verify each trade matches original
    for original_trade in trades:
        matching = [t for t in found_trades if t["id"] == original_trade["id"]]
        assert len(matching) == 1
        assert matching[0] == original_trade


# Feature: tcs-store, Property 7: Group Load Completeness
@given(
    num_trades=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_group_load_empty_list(num_trades):
    """
    Test group load with empty ID list.
    
    Loading with an empty list should return empty results.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Save some trades
    for _ in range(num_trades):
        trade = generate_trade_with_id()
        service.save_new(trade, context)
    
    # Load with empty list
    found_trades, missing_ids = service.load_by_ids([])
    
    # Verify empty results
    assert len(found_trades) == 0
    assert len(missing_ids) == 0



# Feature: tcs-store, Property 8: Group Delete Completeness
@given(
    num_existing=st.integers(min_value=0, max_value=20),
    num_missing=st.integers(min_value=0, max_value=20)
)
@settings(max_examples=100)
def test_group_delete_completeness(num_existing, num_missing):
    """
    Test group delete completeness property.
    
    For any list of trade IDs, calling delete_by_ids should remove all
    existing trades from the store and correctly report the count of
    deleted trades and missing IDs.
    """
    from tcs_store.exceptions import TradeNotFoundError
    import pytest
    
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create and save existing trades
    existing_ids = []
    for _ in range(num_existing):
        trade = generate_trade_with_id()
        service.save_new(trade, context)
        existing_ids.append(trade["id"])
    
    # Generate missing IDs (not in store)
    missing_ids = [str(uuid.uuid4()) for _ in range(num_missing)]
    
    # Combine existing and missing IDs
    all_ids = existing_ids + missing_ids
    
    # Delete by IDs
    deleted_count, returned_missing_ids = service.delete_by_ids(all_ids, context)
    
    # Verify correct count of deleted trades
    assert deleted_count == num_existing
    
    # Verify all missing IDs are reported
    assert len(returned_missing_ids) == num_missing
    assert set(returned_missing_ids) == set(missing_ids)
    
    # Verify all existing trades are now deleted
    for trade_id in existing_ids:
        with pytest.raises(TradeNotFoundError):
            service.load_by_id(trade_id)


# Feature: tcs-store, Property 8: Group Delete Completeness
@given(
    num_trades=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_group_delete_removes_all(num_trades):
    """
    Test that group delete removes all specified trades.
    
    For any set of existing trades, deleting them via delete_by_ids
    should remove all of them from the store.
    """
    from tcs_store.exceptions import TradeNotFoundError
    import pytest
    
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create and save trades
    trade_ids = []
    for _ in range(num_trades):
        trade = generate_trade_with_id()
        service.save_new(trade, context)
        trade_ids.append(trade["id"])
    
    # Verify all trades exist
    for trade_id in trade_ids:
        service.load_by_id(trade_id)  # Should not raise
    
    # Delete all trades
    deleted_count, missing_ids = service.delete_by_ids(trade_ids, context)
    
    # Verify correct count
    assert deleted_count == num_trades
    assert len(missing_ids) == 0
    
    # Verify all trades are deleted
    for trade_id in trade_ids:
        with pytest.raises(TradeNotFoundError):
            service.load_by_id(trade_id)


# Feature: tcs-store, Property 8: Group Delete Completeness
@given(
    num_trades=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_group_delete_idempotency(num_trades):
    """
    Test that group delete is idempotent.
    
    Deleting the same set of IDs multiple times should be safe and
    report correct counts each time.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create and save trades
    trade_ids = []
    for _ in range(num_trades):
        trade = generate_trade_with_id()
        service.save_new(trade, context)
        trade_ids.append(trade["id"])
    
    # First delete - should delete all
    deleted_count1, missing_ids1 = service.delete_by_ids(trade_ids, context)
    assert deleted_count1 == num_trades
    assert len(missing_ids1) == 0
    
    # Second delete - should find none (all missing)
    deleted_count2, missing_ids2 = service.delete_by_ids(trade_ids, context)
    assert deleted_count2 == 0
    assert len(missing_ids2) == num_trades
    assert set(missing_ids2) == set(trade_ids)


# Feature: tcs-store, Property 8: Group Delete Completeness
@given(
    num_trades=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_group_delete_empty_list(num_trades):
    """
    Test group delete with empty ID list.
    
    Deleting with an empty list should succeed with zero deletions.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Save some trades
    for _ in range(num_trades):
        trade = generate_trade_with_id()
        service.save_new(trade, context)
    
    # Delete with empty list
    deleted_count, missing_ids = service.delete_by_ids([], context)
    
    # Verify zero deletions
    assert deleted_count == 0
    assert len(missing_ids) == 0
