"""Property-based tests for concurrency and thread safety."""

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from hypothesis import given, settings
import hypothesis.strategies as st

from tcs_store.storage.in_memory_store import InMemoryStore


def generate_trade_data():
    """Generate random trade data."""
    return {
        "id": str(uuid.uuid4()),
        "data": {
            "trade_type": "IR_SWAP",
            "notional": 1000000,
        }
    }


def generate_context():
    """Generate random context metadata."""
    return {
        "user": f"user_{uuid.uuid4().hex[:8]}",
        "agent": "test_agent",
        "action": "save",
        "intent": "testing",
    }


# Feature: tcs-store, Property 19: Thread-Safe Operations
@given(
    num_trades=st.integers(min_value=10, max_value=50),
    num_workers=st.integers(min_value=5, max_value=10),
)
@settings(max_examples=100, deadline=None)
def test_concurrent_save_operations(num_trades, num_workers):
    """
    Test that concurrent save operations are thread-safe.
    
    For any sequence of concurrent save operations on different trades,
    all operations should complete successfully without data corruption
    or race conditions.
    """
    store = InMemoryStore()
    trades = [generate_trade_data() for _ in range(num_trades)]
    
    def save_trade(trade):
        context = generate_context()
        store.save(trade["id"], trade, context)
        return trade["id"]
    
    # Execute concurrent saves
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(save_trade, trade) for trade in trades]
        saved_ids = [f.result() for f in as_completed(futures)]
    
    # Verify all trades were saved
    assert len(saved_ids) == num_trades
    
    # Verify all trades can be retrieved
    for trade in trades:
        retrieved = store.get(trade["id"])
        assert retrieved is not None
        assert retrieved["id"] == trade["id"]
    
    # Verify operation log has all saves
    op_log = store.get_operation_log()
    assert len(op_log) == num_trades
    assert all(entry["operation"] == "save" for entry in op_log)


# Feature: tcs-store, Property 19: Thread-Safe Operations
@given(
    num_trades=st.integers(min_value=10, max_value=50),
    num_workers=st.integers(min_value=5, max_value=10),
)
@settings(max_examples=100, deadline=None)
def test_concurrent_mixed_operations(num_trades, num_workers):
    """
    Test that concurrent mixed operations (save, get, delete) are thread-safe.
    
    For any sequence of concurrent save, load, and delete operations,
    all operations should complete successfully without data corruption.
    """
    store = InMemoryStore()
    trades = [generate_trade_data() for _ in range(num_trades)]
    
    # Pre-populate store with half the trades
    for trade in trades[:num_trades // 2]:
        context = generate_context()
        store.save(trade["id"], trade, context)
    
    def mixed_operation(index):
        trade = trades[index]
        context = generate_context()
        
        if index % 3 == 0:
            # Save operation
            store.save(trade["id"], trade, context)
            return ("save", trade["id"])
        elif index % 3 == 1:
            # Get operation
            result = store.get(trade["id"])
            return ("get", trade["id"], result is not None)
        else:
            # Delete operation
            result = store.delete(trade["id"], context)
            return ("delete", trade["id"], result)
    
    # Execute concurrent mixed operations
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(mixed_operation, i) for i in range(num_trades)]
        results = [f.result() for f in as_completed(futures)]
    
    # Verify no exceptions occurred and all operations completed
    assert len(results) == num_trades
    
    # Verify store is in a consistent state (no corruption)
    all_trades = store.get_all()
    assert isinstance(all_trades, list)
    
    # Verify each trade in store has valid structure
    for trade in all_trades:
        assert "id" in trade
        assert isinstance(trade["id"], str)


# Feature: tcs-store, Property 19: Thread-Safe Operations
@given(
    num_operations=st.integers(min_value=20, max_value=100),
)
@settings(max_examples=100, deadline=None)
def test_concurrent_read_write_consistency(num_operations):
    """
    Test that concurrent reads and writes maintain consistency.
    
    For any sequence of concurrent read and write operations on the same trade,
    reads should always return either the old value or the new value, never
    a corrupted or partial value.
    """
    store = InMemoryStore()
    trade_id = str(uuid.uuid4())
    
    # Initial save
    initial_trade = {"id": trade_id, "data": {"version": 0}}
    context = generate_context()
    store.save(trade_id, initial_trade, context)
    
    def update_trade(version):
        trade = {"id": trade_id, "data": {"version": version}}
        context = generate_context()
        store.save(trade_id, trade, context)
        return version
    
    def read_trade():
        trade = store.get(trade_id)
        if trade:
            return trade["data"]["version"]
        return None
    
    # Execute concurrent reads and writes
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit write operations
        write_futures = [executor.submit(update_trade, i) for i in range(1, num_operations)]
        # Submit read operations
        read_futures = [executor.submit(read_trade) for _ in range(num_operations)]
        
        # Collect results
        write_results = [f.result() for f in as_completed(write_futures)]
        read_results = [f.result() for f in as_completed(read_futures)]
    
    # Verify all writes completed
    assert len(write_results) == num_operations - 1
    
    # Verify all reads returned valid versions (not corrupted)
    assert all(isinstance(v, int) and 0 <= v < num_operations for v in read_results if v is not None)
    
    # Verify final state is consistent
    final_trade = store.get(trade_id)
    assert final_trade is not None
    assert "data" in final_trade
    assert "version" in final_trade["data"]
    assert isinstance(final_trade["data"]["version"], int)
