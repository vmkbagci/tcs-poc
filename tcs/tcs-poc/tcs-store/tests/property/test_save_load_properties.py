"""Property-based tests for save and load operations."""

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


# Feature: tcs-store, Property 1: Save-Load Round Trip
@given(
    trade_data=st.dictionaries(
        st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
        st.one_of(
            st.text(min_size=0, max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.none()
        ),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_save_load_round_trip(trade_data):
    """
    Test save-load round trip property.
    
    For any valid trade with a unique ID, saving it to the store and then
    loading it by ID should return an equivalent trade with all fields preserved.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trade with unique ID
    trade = {"id": str(uuid.uuid4()), **trade_data}
    
    # Save trade
    saved_trade = service.save_new(trade, context)
    
    # Load trade
    loaded_trade = service.load_by_id(trade["id"])
    
    # Verify round trip
    assert loaded_trade == saved_trade
    assert loaded_trade["id"] == trade["id"]
    
    # Verify all fields preserved
    for key, value in trade.items():
        assert key in loaded_trade
        assert loaded_trade[key] == value


# Feature: tcs-store, Property 1: Save-Load Round Trip
@given(
    num_trades=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_save_load_multiple_trades(num_trades):
    """
    Test save-load round trip for multiple trades.
    
    For any set of trades, saving them all and then loading each one
    should return the exact trade data that was saved.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Generate and save multiple trades
    trades = []
    for _ in range(num_trades):
        trade = generate_trade_with_id()
        service.save_new(trade, context)
        trades.append(trade)
    
    # Load each trade and verify
    for trade in trades:
        loaded_trade = service.load_by_id(trade["id"])
        assert loaded_trade == trade
        assert loaded_trade["id"] == trade["id"]


# Feature: tcs-store, Property 1: Save-Load Round Trip
@given(
    nested_data=st.recursive(
        st.one_of(
            st.text(min_size=0, max_size=50),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.none()
        ),
        lambda children: st.dictionaries(
            st.text(min_size=1, max_size=10),
            children,
            min_size=0,
            max_size=5
        ),
        max_leaves=10
    )
)
@settings(max_examples=100)
def test_save_load_nested_data(nested_data):
    """
    Test save-load round trip with deeply nested data.
    
    For any trade with deeply nested data structures, saving and loading
    should preserve the entire nested structure.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trade with nested data
    trade = {
        "id": str(uuid.uuid4()),
        "data": nested_data
    }
    
    # Save and load
    service.save_new(trade, context)
    loaded_trade = service.load_by_id(trade["id"])
    
    # Verify nested structure preserved
    assert loaded_trade == trade
    assert loaded_trade["data"] == nested_data



# Feature: tcs-store, Property 2: Duplicate Prevention
@given(
    trade_data=st.dictionaries(
        st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
        st.one_of(st.text(), st.integers()),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_duplicate_prevention(trade_data):
    """
    Test duplicate prevention property.
    
    For any trade that already exists in the store (matching by ID),
    attempting to save it again via save_new should fail with a 409 error.
    """
    from tcs_store.exceptions import TradeAlreadyExistsError
    import pytest
    
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create and save trade
    trade = {"id": str(uuid.uuid4()), **trade_data}
    service.save_new(trade, context)
    
    # Attempt to save same trade again should fail
    with pytest.raises(TradeAlreadyExistsError):
        service.save_new(trade, context)
    
    # Verify original trade still exists and unchanged
    loaded_trade = service.load_by_id(trade["id"])
    assert loaded_trade == trade


# Feature: tcs-store, Property 3: Full Update Replacement
@given(
    initial_data=st.dictionaries(
        st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
        st.one_of(st.text(), st.integers()),
        min_size=1,
        max_size=10
    ),
    updated_data=st.dictionaries(
        st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
        st.one_of(st.text(), st.integers()),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_full_update_replacement(initial_data, updated_data):
    """
    Test full update replacement property.
    
    For any existing trade and any new trade data with the same ID,
    calling save_update should completely replace the old trade data,
    and loading the trade should return the new data.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create and save initial trade
    trade_id = str(uuid.uuid4())
    initial_trade = {"id": trade_id, **initial_data}
    service.save_new(initial_trade, context)
    
    # Update with completely new data
    updated_trade = {"id": trade_id, **updated_data}
    service.save_update(updated_trade, context)
    
    # Load and verify it's the updated data, not merged
    loaded_trade = service.load_by_id(trade_id)
    assert loaded_trade == updated_trade
    
    # Verify old fields not in updated_data are gone
    for key in initial_data:
        if key not in updated_data:
            assert key not in loaded_trade or key == "id"


# Feature: tcs-store, Property 5: Delete Removes Trade
@given(
    trade_data=st.dictionaries(
        st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
        st.one_of(st.text(), st.integers()),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_delete_removes_trade(trade_data):
    """
    Test delete removes trade property.
    
    For any existing trade, deleting it by ID should make it no longer
    retrievable via load_by_id, which should return a 404 error.
    """
    from tcs_store.exceptions import TradeNotFoundError
    import pytest
    
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create and save trade
    trade = {"id": str(uuid.uuid4()), **trade_data}
    service.save_new(trade, context)
    
    # Verify trade exists
    loaded_trade = service.load_by_id(trade["id"])
    assert loaded_trade == trade
    
    # Delete trade
    service.delete_by_id(trade["id"], context)
    
    # Verify trade no longer exists
    with pytest.raises(TradeNotFoundError):
        service.load_by_id(trade["id"])


# Feature: tcs-store, Property 6: Delete Idempotency
@given(
    trade_id=st.text(min_size=1, max_size=50)
)
@settings(max_examples=100)
def test_delete_idempotency(trade_id):
    """
    Test delete idempotency property.
    
    For any trade ID (existing or not), calling delete_by_id should always
    succeed without error, making delete operations idempotent.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Delete non-existent trade should succeed (no error)
    service.delete_by_id(trade_id, context)
    
    # Delete again should also succeed
    service.delete_by_id(trade_id, context)
    
    # Create and save a trade
    trade = {"id": trade_id, "data": {"test": "value"}}
    service.save_new(trade, context)
    
    # Delete existing trade
    service.delete_by_id(trade_id, context)
    
    # Delete again should succeed (idempotent)
    service.delete_by_id(trade_id, context)
