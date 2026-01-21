"""Unit tests for filter edge cases."""

import uuid
import pytest

from tcs_store.storage.in_memory_store import InMemoryStore
from tcs_store.services.trade_service import TradeService
from tcs_store.models import Context
from tcs_store.models.filter import TradeFilter
from tcs_store.exceptions import InvalidFilterError


def generate_context():
    """Generate a valid context."""
    return Context(
        user=f"user_{uuid.uuid4().hex[:8]}",
        agent="test_agent",
        action="test_action",
        intent="test_intent"
    )


def test_empty_filter_returns_all_trades():
    """
    Test that empty filter returns all trades.
    
    Requirements: 6.2
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create multiple trades
    trades = []
    for i in range(5):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"index": i}
        }
        service.save_new(trade, context)
        trades.append(trade)
    
    # Empty filter
    filter_obj = TradeFilter()
    
    # Should return all trades
    results = service.load_by_filter(filter_obj)
    assert len(results) == 5
    
    result_ids = {t["id"] for t in results}
    expected_ids = {t["id"] for t in trades}
    assert result_ids == expected_ids


def test_filter_with_no_matches():
    """
    Test filter that matches no trades.
    
    Requirements: 6.2
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    for i in range(5):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"type": f"TYPE_{i}"}
        }
        service.save_new(trade, context)
    
    # Filter that won't match any trade
    filter_obj = TradeFilter(
        filter={"data.type": {"eq": "NONEXISTENT_TYPE"}}
    )
    
    # Should return empty list
    results = service.load_by_filter(filter_obj)
    assert len(results) == 0
    assert results == []


def test_filter_with_nonexistent_field():
    """
    Test filter on a field that doesn't exist in any trade.
    
    Requirements: 6.2
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades without the filtered field
    for i in range(3):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"existing_field": i}
        }
        service.save_new(trade, context)
    
    # Filter on non-existent field
    filter_obj = TradeFilter(
        filter={"data.nonexistent_field": {"eq": "value"}}
    )
    
    # Should return empty list (no trades have this field)
    results = service.load_by_filter(filter_obj)
    assert len(results) == 0


def test_invalid_filter_structure_non_dict_conditions():
    """
    Test that filter with non-dict conditions raises error.
    
    Requirements: 6.3
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create a trade
    trade = {
        "id": str(uuid.uuid4()),
        "data": {"field": "value"}
    }
    service.save_new(trade, context)
    
    # Invalid filter - conditions should be a dict, not a string
    filter_obj = TradeFilter(
        filter={"data.field": "value"}  # Should be {"eq": "value"}
    )
    
    # Should raise InvalidFilterError
    with pytest.raises(InvalidFilterError, match="must be a dictionary"):
        service.load_by_filter(filter_obj)


def test_invalid_filter_unknown_operator():
    """
    Test that filter with unknown operator raises error.
    
    Requirements: 6.3
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create a trade
    trade = {
        "id": str(uuid.uuid4()),
        "data": {"field": "value"}
    }
    service.save_new(trade, context)
    
    # Invalid filter - unknown operator
    filter_obj = TradeFilter(
        filter={"data.field": {"unknown_op": "value"}}
    )
    
    # Should raise InvalidFilterError
    with pytest.raises(InvalidFilterError, match="Unknown filter operator"):
        service.load_by_filter(filter_obj)


def test_invalid_filter_regex_pattern():
    """
    Test that filter with invalid regex pattern raises error.
    
    Requirements: 6.3
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create a trade
    trade = {
        "id": str(uuid.uuid4()),
        "data": {"field": "value"}
    }
    service.save_new(trade, context)
    
    # Invalid regex pattern
    filter_obj = TradeFilter(
        filter={"data.field": {"regex": "[invalid(regex"}}
    )
    
    # Should raise InvalidFilterError
    with pytest.raises(InvalidFilterError, match="Invalid regex pattern"):
        service.load_by_filter(filter_obj)


def test_invalid_filter_in_operator_non_list():
    """
    Test that 'in' operator with non-list value raises error.
    
    Requirements: 6.3
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create a trade
    trade = {
        "id": str(uuid.uuid4()),
        "data": {"field": "value"}
    }
    service.save_new(trade, context)
    
    # Invalid 'in' operator - should be a list
    filter_obj = TradeFilter(
        filter={"data.field": {"in": "not_a_list"}}
    )
    
    # Should raise InvalidFilterError
    with pytest.raises(InvalidFilterError, match="'in' operator requires a list"):
        service.load_by_filter(filter_obj)


def test_invalid_filter_nin_operator_non_list():
    """
    Test that 'nin' operator with non-list value raises error.
    
    Requirements: 6.3
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create a trade
    trade = {
        "id": str(uuid.uuid4()),
        "data": {"field": "value"}
    }
    service.save_new(trade, context)
    
    # Invalid 'nin' operator - should be a list
    filter_obj = TradeFilter(
        filter={"data.field": {"nin": "not_a_list"}}
    )
    
    # Should raise InvalidFilterError
    with pytest.raises(InvalidFilterError, match="'nin' operator requires a list"):
        service.load_by_filter(filter_obj)


def test_filter_with_null_values():
    """
    Test filtering with null values.
    
    Requirements: 6.2
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades with null and non-null values
    trade1 = {
        "id": str(uuid.uuid4()),
        "data": {"field": None}
    }
    trade2 = {
        "id": str(uuid.uuid4()),
        "data": {"field": "value"}
    }
    
    service.save_new(trade1, context)
    service.save_new(trade2, context)
    
    # Filter for null
    filter_obj = TradeFilter(
        filter={"data.field": {"eq": None}}
    )
    
    results = service.load_by_filter(filter_obj)
    assert len(results) == 1
    assert results[0]["id"] == trade1["id"]


def test_filter_deeply_nested_field():
    """
    Test filtering on deeply nested field paths.
    
    Requirements: 6.2
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trade with deeply nested structure
    trade = {
        "id": str(uuid.uuid4()),
        "data": {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep_value"
                        }
                    }
                }
            }
        }
    }
    service.save_new(trade, context)
    
    # Filter on deeply nested field
    filter_obj = TradeFilter(
        filter={"data.level1.level2.level3.level4.value": {"eq": "deep_value"}}
    )
    
    results = service.load_by_filter(filter_obj)
    assert len(results) == 1
    assert results[0]["id"] == trade["id"]


def test_count_with_empty_filter():
    """
    Test count with empty filter returns total count.
    
    Requirements: 8.1
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    num_trades = 7
    for i in range(num_trades):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"index": i}
        }
        service.save_new(trade, context)
    
    # Empty filter
    filter_obj = TradeFilter()
    
    # Should count all trades
    count = service.count_by_filter(filter_obj)
    assert count == num_trades


def test_count_with_no_matches():
    """
    Test count returns zero when no trades match.
    
    Requirements: 8.1
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    for i in range(5):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"type": f"TYPE_{i}"}
        }
        service.save_new(trade, context)
    
    # Filter that won't match
    filter_obj = TradeFilter(
        filter={"data.type": {"eq": "NONEXISTENT"}}
    )
    
    # Should return zero
    count = service.count_by_filter(filter_obj)
    assert count == 0


def test_list_with_empty_filter():
    """
    Test list with empty filter returns all trades.
    
    Requirements: 7.1
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    num_trades = 6
    for i in range(num_trades):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"index": i}
        }
        service.save_new(trade, context)
    
    # Empty filter
    filter_obj = TradeFilter()
    
    # Should return all trades
    results = service.list_by_filter(filter_obj)
    assert len(results) == num_trades


def test_list_with_no_matches():
    """
    Test list returns empty when no trades match.
    
    Requirements: 7.1
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    for i in range(5):
        trade = {
            "id": str(uuid.uuid4()),
            "data": {"category": f"CAT_{i}"}
        }
        service.save_new(trade, context)
    
    # Filter that won't match
    filter_obj = TradeFilter(
        filter={"data.category": {"eq": "NONEXISTENT"}}
    )
    
    # Should return empty list
    results = service.list_by_filter(filter_obj)
    assert len(results) == 0
    assert results == []


def test_filter_in_operator():
    """
    Test 'in' operator filters correctly.
    
    Requirements: 6.1
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    trade1 = {
        "id": str(uuid.uuid4()),
        "data": {"type": "SWAP"}
    }
    trade2 = {
        "id": str(uuid.uuid4()),
        "data": {"type": "OPTION"}
    }
    trade3 = {
        "id": str(uuid.uuid4()),
        "data": {"type": "FUTURE"}
    }
    
    service.save_new(trade1, context)
    service.save_new(trade2, context)
    service.save_new(trade3, context)
    
    # Filter with 'in' operator
    filter_obj = TradeFilter(
        filter={"data.type": {"in": ["SWAP", "OPTION"]}}
    )
    
    results = service.load_by_filter(filter_obj)
    assert len(results) == 2
    
    result_ids = {t["id"] for t in results}
    assert trade1["id"] in result_ids
    assert trade2["id"] in result_ids
    assert trade3["id"] not in result_ids


def test_filter_nin_operator():
    """
    Test 'nin' (not in) operator filters correctly.
    
    Requirements: 6.1
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    trade1 = {
        "id": str(uuid.uuid4()),
        "data": {"type": "SWAP"}
    }
    trade2 = {
        "id": str(uuid.uuid4()),
        "data": {"type": "OPTION"}
    }
    trade3 = {
        "id": str(uuid.uuid4()),
        "data": {"type": "FUTURE"}
    }
    
    service.save_new(trade1, context)
    service.save_new(trade2, context)
    service.save_new(trade3, context)
    
    # Filter with 'nin' operator
    filter_obj = TradeFilter(
        filter={"data.type": {"nin": ["SWAP", "OPTION"]}}
    )
    
    results = service.load_by_filter(filter_obj)
    assert len(results) == 1
    assert results[0]["id"] == trade3["id"]


def test_filter_ne_operator():
    """
    Test 'ne' (not equal) operator filters correctly.
    
    Requirements: 6.1
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create trades
    trade1 = {
        "id": str(uuid.uuid4()),
        "data": {"status": "ACTIVE"}
    }
    trade2 = {
        "id": str(uuid.uuid4()),
        "data": {"status": "INACTIVE"}
    }
    trade3 = {
        "id": str(uuid.uuid4()),
        "data": {"status": "PENDING"}
    }
    
    service.save_new(trade1, context)
    service.save_new(trade2, context)
    service.save_new(trade3, context)
    
    # Filter with 'ne' operator
    filter_obj = TradeFilter(
        filter={"data.status": {"ne": "ACTIVE"}}
    )
    
    results = service.load_by_filter(filter_obj)
    assert len(results) == 2
    
    result_ids = {t["id"] for t in results}
    assert trade1["id"] not in result_ids
    assert trade2["id"] in result_ids
    assert trade3["id"] in result_ids
