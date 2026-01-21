"""Property-based tests for filter operations."""

import uuid
from hypothesis import given, settings, assume
import hypothesis.strategies as st

from tcs_store.storage.in_memory_store import InMemoryStore
from tcs_store.services.trade_service import TradeService
from tcs_store.models import Context
from tcs_store.models.filter import TradeFilter


def generate_context():
    """Generate a valid context."""
    return Context(
        user=f"user_{uuid.uuid4().hex[:8]}",
        agent="test_agent",
        action="test_action",
        intent="test_intent"
    )


# Feature: tcs-store, Property 9: Filter Correctness
@given(
    num_trades=st.integers(min_value=5, max_value=20),
    filter_value=st.text(min_size=1, max_size=20)
)
@settings(max_examples=100)
def test_filter_correctness(num_trades, filter_value):
    """
    Test filter correctness property.
    
    For any filter criteria and any set of trades in the store,
    calling load_by_filter should return all and only the trades
    that match the filter criteria according to the filter evaluation logic.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with known values
    matching_trades = []
    non_matching_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        # Half the trades match the filter, half don't
        if i % 2 == 0:
            trade = {
                "id": trade_id,
                "data": {
                    "trade_type": filter_value,
                    "index": i
                }
            }
            matching_trades.append(trade)
        else:
            trade = {
                "id": trade_id,
                "data": {
                    "trade_type": f"other_{i}",
                    "index": i
                }
            }
            non_matching_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Apply filter
    filter_obj = TradeFilter(
        filter={"data.trade_type": {"eq": filter_value}}
    )
    
    results = service.load_by_filter(filter_obj)
    
    # Verify all matching trades are returned
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in matching_trades}
    
    assert result_ids == expected_ids
    assert len(results) == len(matching_trades)
    
    # Verify no non-matching trades are returned
    non_matching_ids = {t["id"] for t in non_matching_trades}
    assert result_ids.isdisjoint(non_matching_ids)


# Feature: tcs-store, Property 9: Filter Correctness
@given(
    num_trades=st.integers(min_value=3, max_value=15)
)
@settings(max_examples=100)
def test_filter_correctness_nested_fields(num_trades):
    """
    Test filter correctness with nested field paths.
    
    For any filter on nested fields, only trades with matching
    nested values should be returned.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    target_value = 1000000
    
    # Create trades with nested data
    matching_trades = []
    non_matching_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 2 == 0:
            trade = {
                "id": trade_id,
                "data": {
                    "leg1": {
                        "notional": target_value
                    }
                }
            }
            matching_trades.append(trade)
        else:
            trade = {
                "id": trade_id,
                "data": {
                    "leg1": {
                        "notional": target_value + i
                    }
                }
            }
            non_matching_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Filter by nested field
    filter_obj = TradeFilter(
        filter={"data.leg1.notional": {"eq": target_value}}
    )
    
    results = service.load_by_filter(filter_obj)
    
    # Verify correctness
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in matching_trades}
    
    assert result_ids == expected_ids
    assert len(results) == len(matching_trades)


# Feature: tcs-store, Property 9: Filter Correctness
@given(
    num_trades=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100)
def test_empty_filter_returns_all(num_trades):
    """
    Test that empty filter returns all trades.
    
    For any set of trades, an empty filter should return all trades.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    trades = []
    for i in range(num_trades):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"index": i}
        }
        service.save_new(trade, context)
        trades.append(trade)
    
    # Empty filter
    filter_obj = TradeFilter()
    
    results = service.load_by_filter(filter_obj)
    
    # Should return all trades
    assert len(results) == num_trades
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in trades}
    assert result_ids == expected_ids



# Feature: tcs-store, Property 12: Equality Filter
@given(
    num_trades=st.integers(min_value=5, max_value=20),
    field_value=st.one_of(
        st.text(min_size=1, max_size=20),
        st.integers(min_value=-1000000, max_value=1000000),
        st.floats(min_value=-1000000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
        st.booleans()
    )
)
@settings(max_examples=100)
def test_equality_filter(num_trades, field_value):
    """
    Test equality filter property.
    
    For any field path and value, a filter with {"field": {"eq": value}}
    should return all trades where the field equals the value and no trades
    where it doesn't.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with matching and non-matching values
    matching_trades = []
    non_matching_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 2 == 0:
            # Matching trade
            trade = {
                "id": trade_id,
                "data": {
                    "test_field": field_value,
                    "index": i
                }
            }
            matching_trades.append(trade)
        else:
            # Non-matching trade - use a different value
            if isinstance(field_value, str):
                different_value = f"different_{i}"
            elif isinstance(field_value, (int, float)):
                # For numeric values, multiply by a factor to ensure difference
                # This avoids floating point precision issues with large numbers
                different_value = field_value * 2 + (i + 1) * 100
            elif isinstance(field_value, bool):
                different_value = not field_value
            else:
                different_value = None
            
            trade = {
                "id": trade_id,
                "data": {
                    "test_field": different_value,
                    "index": i
                }
            }
            non_matching_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Apply equality filter
    filter_obj = TradeFilter(
        filter={"data.test_field": {"eq": field_value}}
    )
    
    results = service.load_by_filter(filter_obj)
    
    # Verify all and only matching trades are returned
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in matching_trades}
    
    assert result_ids == expected_ids
    assert len(results) == len(matching_trades)
    
    # Verify all returned trades have the correct value
    for trade in results:
        assert trade["data"]["test_field"] == field_value
    
    # Verify no non-matching trades are returned
    non_matching_ids = {t["id"] for t in non_matching_trades}
    assert result_ids.isdisjoint(non_matching_ids)


# Feature: tcs-store, Property 12: Equality Filter
@given(
    num_trades=st.integers(min_value=3, max_value=15)
)
@settings(max_examples=100)
def test_equality_filter_with_none(num_trades):
    """
    Test equality filter with None values.
    
    Trades with None values should not match filters for other values,
    and vice versa.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with None and non-None values
    none_trades = []
    value_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 2 == 0:
            trade = {
                "id": trade_id,
                "data": {
                    "test_field": None
                }
            }
            none_trades.append(trade)
        else:
            trade = {
                "id": trade_id,
                "data": {
                    "test_field": "some_value"
                }
            }
            value_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Filter for None
    filter_obj = TradeFilter(
        filter={"data.test_field": {"eq": None}}
    )
    
    results = service.load_by_filter(filter_obj)
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in none_trades}
    
    assert result_ids == expected_ids
    
    # Filter for non-None value
    filter_obj2 = TradeFilter(
        filter={"data.test_field": {"eq": "some_value"}}
    )
    
    results2 = service.load_by_filter(filter_obj2)
    result_ids2 = {t["id"] for t in results2}
    expected_ids2 = {t["id"] for t in value_trades}
    
    assert result_ids2 == expected_ids2



# Feature: tcs-store, Property 13: Range Filter
@given(
    num_trades=st.integers(min_value=5, max_value=20),
    min_value=st.integers(min_value=0, max_value=100),
    max_value=st.integers(min_value=101, max_value=200)
)
@settings(max_examples=100)
def test_range_filter(num_trades, min_value, max_value):
    """
    Test range filter property.
    
    For any field path and range bounds (min, max), a filter with
    {"field": {"gte": min, "lte": max}} should return all trades where
    the field value is within the range (inclusive) and no trades outside the range.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with values inside and outside the range
    in_range_trades = []
    out_of_range_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 2 == 0:
            # In range
            value = min_value + (i % (max_value - min_value + 1))
            trade = {
                "id": trade_id,
                "data": {
                    "amount": value
                }
            }
            in_range_trades.append(trade)
        else:
            # Out of range (either below min or above max)
            if i % 4 == 1:
                value = min_value - (i + 1)
            else:
                value = max_value + (i + 1)
            
            trade = {
                "id": trade_id,
                "data": {
                    "amount": value
                }
            }
            out_of_range_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Apply range filter
    filter_obj = TradeFilter(
        filter={"data.amount": {"gte": min_value, "lte": max_value}}
    )
    
    results = service.load_by_filter(filter_obj)
    
    # Verify all and only in-range trades are returned
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in in_range_trades}
    
    assert result_ids == expected_ids
    assert len(results) == len(in_range_trades)
    
    # Verify all returned trades have values in range
    for trade in results:
        value = trade["data"]["amount"]
        assert min_value <= value <= max_value
    
    # Verify no out-of-range trades are returned
    out_of_range_ids = {t["id"] for t in out_of_range_trades}
    assert result_ids.isdisjoint(out_of_range_ids)


# Feature: tcs-store, Property 13: Range Filter
@given(
    num_trades=st.integers(min_value=5, max_value=15),
    threshold=st.integers(min_value=50, max_value=150)
)
@settings(max_examples=100)
def test_range_filter_gt_lt(num_trades, threshold):
    """
    Test range filter with gt and lt operators (exclusive bounds).
    
    For any threshold, gt should return values strictly greater,
    and lt should return values strictly less.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with values above, at, and below threshold
    above_trades = []
    at_threshold_trades = []
    below_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 3 == 0:
            # Above threshold
            trade = {
                "id": trade_id,
                "data": {"value": threshold + i + 1}
            }
            above_trades.append(trade)
        elif i % 3 == 1:
            # At threshold
            trade = {
                "id": trade_id,
                "data": {"value": threshold}
            }
            at_threshold_trades.append(trade)
        else:
            # Below threshold
            trade = {
                "id": trade_id,
                "data": {"value": threshold - i - 1}
            }
            below_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Test gt (greater than, exclusive)
    filter_gt = TradeFilter(
        filter={"data.value": {"gt": threshold}}
    )
    results_gt = service.load_by_filter(filter_gt)
    result_ids_gt = {t["id"] for t in results_gt}
    expected_ids_gt = {t["id"] for t in above_trades}
    
    assert result_ids_gt == expected_ids_gt
    
    # Verify no trades at or below threshold
    at_or_below_ids = {t["id"] for t in at_threshold_trades + below_trades}
    assert result_ids_gt.isdisjoint(at_or_below_ids)
    
    # Test lt (less than, exclusive)
    filter_lt = TradeFilter(
        filter={"data.value": {"lt": threshold}}
    )
    results_lt = service.load_by_filter(filter_lt)
    result_ids_lt = {t["id"] for t in results_lt}
    expected_ids_lt = {t["id"] for t in below_trades}
    
    assert result_ids_lt == expected_ids_lt
    
    # Verify no trades at or above threshold
    at_or_above_ids = {t["id"] for t in at_threshold_trades + above_trades}
    assert result_ids_lt.isdisjoint(at_or_above_ids)



# Feature: tcs-store, Property 14: Regex Filter
@given(
    num_trades=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=100)
def test_regex_filter(num_trades):
    """
    Test regex filter property.
    
    For any field path and regex pattern, a filter with {"field": {"regex": pattern}}
    should return all trades where the field value matches the regex pattern
    and no trades that don't match.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with matching and non-matching patterns
    matching_trades = []
    non_matching_trades = []
    
    pattern = "^BANK.*"
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 2 == 0:
            # Matching pattern
            trade = {
                "id": trade_id,
                "data": {
                    "counterparty": f"BANK_{i}"
                }
            }
            matching_trades.append(trade)
        else:
            # Non-matching pattern
            trade = {
                "id": trade_id,
                "data": {
                    "counterparty": f"CORP_{i}"
                }
            }
            non_matching_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Apply regex filter
    filter_obj = TradeFilter(
        filter={"data.counterparty": {"regex": pattern}}
    )
    
    results = service.load_by_filter(filter_obj)
    
    # Verify all and only matching trades are returned
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in matching_trades}
    
    assert result_ids == expected_ids
    assert len(results) == len(matching_trades)
    
    # Verify all returned trades match the pattern
    import re
    for trade in results:
        value = trade["data"]["counterparty"]
        assert re.search(pattern, value) is not None
    
    # Verify no non-matching trades are returned
    non_matching_ids = {t["id"] for t in non_matching_trades}
    assert result_ids.isdisjoint(non_matching_ids)


# Feature: tcs-store, Property 14: Regex Filter
@given(
    num_trades=st.integers(min_value=5, max_value=15)
)
@settings(max_examples=100)
def test_regex_filter_case_sensitive(num_trades):
    """
    Test that regex filter is case-sensitive.
    
    Regex patterns should be case-sensitive by default.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with different cases
    uppercase_trades = []
    lowercase_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 2 == 0:
            trade = {
                "id": trade_id,
                "data": {"name": f"UPPER_{i}"}
            }
            uppercase_trades.append(trade)
        else:
            trade = {
                "id": trade_id,
                "data": {"name": f"upper_{i}"}
            }
            lowercase_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Filter for uppercase only
    filter_obj = TradeFilter(
        filter={"data.name": {"regex": "^UPPER.*"}}
    )
    
    results = service.load_by_filter(filter_obj)
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in uppercase_trades}
    
    assert result_ids == expected_ids
    
    # Verify lowercase trades are not returned
    lowercase_ids = {t["id"] for t in lowercase_trades}
    assert result_ids.isdisjoint(lowercase_ids)


# Feature: tcs-store, Property 14: Regex Filter
@given(
    num_trades=st.integers(min_value=3, max_value=10)
)
@settings(max_examples=100)
def test_regex_filter_non_string_values(num_trades):
    """
    Test that regex filter only matches string values.
    
    Non-string values should not match regex filters.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with string and non-string values
    string_trades = []
    non_string_trades = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 2 == 0:
            trade = {
                "id": trade_id,
                "data": {"field": "123"}
            }
            string_trades.append(trade)
        else:
            trade = {
                "id": trade_id,
                "data": {"field": 123}  # Integer, not string
            }
            non_string_trades.append(trade)
        
        service.save_new(trade, context)
    
    # Filter with regex
    filter_obj = TradeFilter(
        filter={"data.field": {"regex": "123"}}
    )
    
    results = service.load_by_filter(filter_obj)
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in string_trades}
    
    # Only string values should match
    assert result_ids == expected_ids
    
    # Non-string values should not match
    non_string_ids = {t["id"] for t in non_string_trades}
    assert result_ids.isdisjoint(non_string_ids)



# Feature: tcs-store, Property 15: Multiple Filter Conditions (AND Logic)
@given(
    num_trades=st.integers(min_value=8, max_value=20),
    type_value=st.text(min_size=1, max_size=20),
    min_amount=st.integers(min_value=100, max_value=500)
)
@settings(max_examples=100)
def test_multiple_filter_conditions_and_logic(num_trades, type_value, min_amount):
    """
    Test multiple filter conditions with AND logic.
    
    For any filter with multiple conditions, only trades that satisfy
    ALL conditions should be returned (AND logic).
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with different combinations
    both_match = []
    type_only = []
    amount_only = []
    neither_match = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        # Distribute trades across all combinations
        if i % 4 == 0:
            # Both conditions match
            trade = {
                "id": trade_id,
                "data": {
                    "trade_type": type_value,
                    "amount": min_amount + i
                }
            }
            both_match.append(trade)
        elif i % 4 == 1:
            # Only type matches
            trade = {
                "id": trade_id,
                "data": {
                    "trade_type": type_value,
                    "amount": min_amount - i - 1
                }
            }
            type_only.append(trade)
        elif i % 4 == 2:
            # Only amount matches
            trade = {
                "id": trade_id,
                "data": {
                    "trade_type": f"other_{i}",
                    "amount": min_amount + i
                }
            }
            amount_only.append(trade)
        else:
            # Neither matches
            trade = {
                "id": trade_id,
                "data": {
                    "trade_type": f"other_{i}",
                    "amount": min_amount - i - 1
                }
            }
            neither_match.append(trade)
        
        service.save_new(trade, context)
    
    # Apply filter with multiple conditions (AND logic)
    filter_obj = TradeFilter(
        filter={
            "data.trade_type": {"eq": type_value},
            "data.amount": {"gte": min_amount}
        }
    )
    
    results = service.load_by_filter(filter_obj)
    
    # Only trades matching BOTH conditions should be returned
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in both_match}
    
    assert result_ids == expected_ids
    assert len(results) == len(both_match)
    
    # Verify all returned trades satisfy both conditions
    for trade in results:
        assert trade["data"]["trade_type"] == type_value
        assert trade["data"]["amount"] >= min_amount
    
    # Verify trades matching only one condition are not returned
    partial_match_ids = {t["id"] for t in type_only + amount_only + neither_match}
    assert result_ids.isdisjoint(partial_match_ids)


# Feature: tcs-store, Property 15: Multiple Filter Conditions (AND Logic)
@given(
    num_trades=st.integers(min_value=6, max_value=15)
)
@settings(max_examples=100)
def test_multiple_filter_conditions_three_conditions(num_trades):
    """
    Test multiple filter conditions with three conditions.
    
    All three conditions must be satisfied for a trade to match.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades - only some match all three conditions
    all_match = []
    partial_match = []
    
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        if i % 3 == 0:
            # All three conditions match
            trade = {
                "id": trade_id,
                "data": {
                    "type": "SWAP",
                    "status": "ACTIVE",
                    "amount": 1000
                }
            }
            all_match.append(trade)
        else:
            # At least one condition doesn't match
            trade = {
                "id": trade_id,
                "data": {
                    "type": "SWAP" if i % 2 == 0 else "OPTION",
                    "status": "ACTIVE" if i % 2 == 1 else "INACTIVE",
                    "amount": 1000 if i % 4 == 0 else 500
                }
            }
            partial_match.append(trade)
        
        service.save_new(trade, context)
    
    # Filter with three conditions
    filter_obj = TradeFilter(
        filter={
            "data.type": {"eq": "SWAP"},
            "data.status": {"eq": "ACTIVE"},
            "data.amount": {"eq": 1000}
        }
    )
    
    results = service.load_by_filter(filter_obj)
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in all_match}
    
    # Only trades matching all three conditions
    assert result_ids == expected_ids
    
    # Verify all returned trades satisfy all conditions
    for trade in results:
        assert trade["data"]["type"] == "SWAP"
        assert trade["data"]["status"] == "ACTIVE"
        assert trade["data"]["amount"] == 1000



# Feature: tcs-store, Property 10: Count Matches Filter
@given(
    num_trades=st.integers(min_value=5, max_value=25),
    filter_value=st.text(min_size=1, max_size=20)
)
@settings(max_examples=100)
def test_count_matches_filter(num_trades, filter_value):
    """
    Test count matches filter property.
    
    For any filter criteria, the count returned by count_by_filter should
    equal the number of trades that would be returned by load_by_filter
    with the same criteria.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with some matching the filter
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        # Some trades match, some don't
        if i % 3 == 0:
            trade = {
                "id": trade_id,
                "data": {"category": filter_value}
            }
        else:
            trade = {
                "id": trade_id,
                "data": {"category": f"other_{i}"}
            }
        
        service.save_new(trade, context)
    
    # Create filter
    filter_obj = TradeFilter(
        filter={"data.category": {"eq": filter_value}}
    )
    
    # Get count
    count = service.count_by_filter(filter_obj)
    
    # Get actual trades
    trades = service.load_by_filter(filter_obj)
    
    # Count should match the number of trades returned
    assert count == len(trades)


# Feature: tcs-store, Property 10: Count Matches Filter
@given(
    num_trades=st.integers(min_value=3, max_value=20),
    min_value=st.integers(min_value=0, max_value=100),
    max_value=st.integers(min_value=101, max_value=200)
)
@settings(max_examples=100)
def test_count_matches_filter_range(num_trades, min_value, max_value):
    """
    Test count matches filter with range conditions.
    
    Count should match the number of trades in the range.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with various amounts
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        # Distribute values across the range
        if i % 3 == 0:
            amount = min_value + (i % (max_value - min_value + 1))
        elif i % 3 == 1:
            amount = min_value - (i + 1)
        else:
            amount = max_value + (i + 1)
        
        trade = {
            "id": trade_id,
            "data": {"amount": amount}
        }
        service.save_new(trade, context)
    
    # Filter with range
    filter_obj = TradeFilter(
        filter={"data.amount": {"gte": min_value, "lte": max_value}}
    )
    
    # Get count and trades
    count = service.count_by_filter(filter_obj)
    trades = service.load_by_filter(filter_obj)
    
    # Count should match
    assert count == len(trades)


# Feature: tcs-store, Property 10: Count Matches Filter
@given(
    num_trades=st.integers(min_value=1, max_value=15)
)
@settings(max_examples=100)
def test_count_matches_filter_empty_filter(num_trades):
    """
    Test count with empty filter returns total count.
    
    Empty filter should count all trades.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    for i in range(num_trades):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"index": i}
        }
        service.save_new(trade, context)
    
    # Empty filter
    filter_obj = TradeFilter()
    
    # Get count and trades
    count = service.count_by_filter(filter_obj)
    trades = service.load_by_filter(filter_obj)
    
    # Should count all trades
    assert count == num_trades
    assert count == len(trades)


# Feature: tcs-store, Property 10: Count Matches Filter
@given(
    num_trades=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=100)
def test_count_matches_filter_no_matches(num_trades):
    """
    Test count returns zero when no trades match.
    
    Filter with no matches should return count of 0.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades that won't match the filter
    for i in range(num_trades):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"type": f"TYPE_{i}"}
        }
        service.save_new(trade, context)
    
    # Filter that won't match any trade
    filter_obj = TradeFilter(
        filter={"data.type": {"eq": "NONEXISTENT_TYPE"}}
    )
    
    # Get count and trades
    count = service.count_by_filter(filter_obj)
    trades = service.load_by_filter(filter_obj)
    
    # Should be zero
    assert count == 0
    assert len(trades) == 0



# Feature: tcs-store, Property 11: List Matches Filter
@given(
    num_trades=st.integers(min_value=5, max_value=25),
    filter_value=st.text(min_size=1, max_size=20)
)
@settings(max_examples=100)
def test_list_matches_filter(num_trades, filter_value):
    """
    Test list matches filter property.
    
    For any filter criteria, the list items returned by list_by_filter should
    correspond exactly to the trades returned by load_by_filter with the same
    criteria (same IDs, same count).
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        # Some trades match, some don't
        if i % 3 == 0:
            trade = {
                "id": trade_id,
                "data": {"status": filter_value}
            }
        else:
            trade = {
                "id": trade_id,
                "data": {"status": f"other_{i}"}
            }
        
        service.save_new(trade, context)
    
    # Create filter
    filter_obj = TradeFilter(
        filter={"data.status": {"eq": filter_value}}
    )
    
    # Get list items and full trades
    list_items = service.list_by_filter(filter_obj)
    full_trades = service.load_by_filter(filter_obj)
    
    # Should have same count
    assert len(list_items) == len(full_trades)
    
    # Should have same IDs
    list_ids = {item["id"] for item in list_items}
    trade_ids = {trade["id"] for trade in full_trades}
    assert list_ids == trade_ids


# Feature: tcs-store, Property 11: List Matches Filter
@given(
    num_trades=st.integers(min_value=3, max_value=20),
    min_value=st.integers(min_value=0, max_value=100),
    max_value=st.integers(min_value=101, max_value=200)
)
@settings(max_examples=100)
def test_list_matches_filter_complex(num_trades, min_value, max_value):
    """
    Test list matches filter with complex filter conditions.
    
    List and load should return the same trades for complex filters.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with various values
    for i in range(num_trades):
        trade_id = str(uuid.uuid4())
        
        trade = {
            "id": trade_id,
            "data": {
                "type": "SWAP" if i % 2 == 0 else "OPTION",
                "amount": min_value + (i * 10)
            }
        }
        service.save_new(trade, context)
    
    # Complex filter
    filter_obj = TradeFilter(
        filter={
            "data.type": {"eq": "SWAP"},
            "data.amount": {"gte": min_value, "lte": max_value}
        }
    )
    
    # Get list and load results
    list_items = service.list_by_filter(filter_obj)
    full_trades = service.load_by_filter(filter_obj)
    
    # Should match
    assert len(list_items) == len(full_trades)
    
    list_ids = {item["id"] for item in list_items}
    trade_ids = {trade["id"] for trade in full_trades}
    assert list_ids == trade_ids


# Feature: tcs-store, Property 11: List Matches Filter
@given(
    num_trades=st.integers(min_value=1, max_value=15)
)
@settings(max_examples=100)
def test_list_matches_filter_empty_filter(num_trades):
    """
    Test list matches filter with empty filter.
    
    Empty filter should return all trades in both list and load.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    for i in range(num_trades):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"index": i}
        }
        service.save_new(trade, context)
    
    # Empty filter
    filter_obj = TradeFilter()
    
    # Get list and load results
    list_items = service.list_by_filter(filter_obj)
    full_trades = service.load_by_filter(filter_obj)
    
    # Should return all trades
    assert len(list_items) == num_trades
    assert len(full_trades) == num_trades
    
    # Same IDs
    list_ids = {item["id"] for item in list_items}
    trade_ids = {trade["id"] for trade in full_trades}
    assert list_ids == trade_ids


# Feature: tcs-store, Property 11: List Matches Filter
@given(
    num_trades=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=100)
def test_list_matches_filter_no_matches(num_trades):
    """
    Test list matches filter when no trades match.
    
    Both list and load should return empty results.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    for i in range(num_trades):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"category": f"CAT_{i}"}
        }
        service.save_new(trade, context)
    
    # Filter that won't match
    filter_obj = TradeFilter(
        filter={"data.category": {"eq": "NONEXISTENT"}}
    )
    
    # Get list and load results
    list_items = service.list_by_filter(filter_obj)
    full_trades = service.load_by_filter(filter_obj)
    
    # Both should be empty
    assert len(list_items) == 0
    assert len(full_trades) == 0
