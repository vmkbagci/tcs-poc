"""Property-based tests for deep merge operations."""

import uuid
from hypothesis import given, settings, assume
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


# Feature: tcs-store, Property 4: Deep Merge Preservation
@given(
    initial_fields=st.dictionaries(
        st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
        st.one_of(st.text(), st.integers(), st.booleans()),
        min_size=2,
        max_size=10
    ),
    update_fields=st.dictionaries(
        st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
        st.one_of(st.text(), st.integers(), st.booleans()),
        min_size=1,
        max_size=5
    )
)
@settings(max_examples=100)
def test_deep_merge_preserves_unmentioned_fields(initial_fields, update_fields):
    """
    Test that deep merge preserves fields not mentioned in the update.
    
    For any existing trade and any partial update payload, calling save_partial
    should preserve all fields not mentioned in the update.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create initial trade
    trade_id = str(uuid.uuid4())
    initial_trade = {"id": trade_id, **initial_fields}
    service.save_new(initial_trade, context)
    
    # Partial update
    updated_trade = service.save_partial(trade_id, update_fields, context)
    
    # Verify unmentioned fields are preserved
    for key, value in initial_fields.items():
        if key not in update_fields:
            assert key in updated_trade
            assert updated_trade[key] == value


# Feature: tcs-store, Property 4: Deep Merge Preservation
@given(
    initial_value=st.one_of(st.text(), st.integers(), st.booleans()),
    update_value=st.one_of(st.text(), st.integers(), st.booleans()),
    field_name=st.text(min_size=1, max_size=20).filter(lambda x: x != "id")
)
@settings(max_examples=100)
def test_deep_merge_overrides_mentioned_fields(initial_value, update_value, field_name):
    """
    Test that deep merge overrides fields that are mentioned in the update.
    
    For any field that exists in both the existing trade and the update,
    the update value should win.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create initial trade
    trade_id = str(uuid.uuid4())
    initial_trade = {"id": trade_id, field_name: initial_value}
    service.save_new(initial_trade, context)
    
    # Partial update with same field
    updates = {field_name: update_value}
    updated_trade = service.save_partial(trade_id, updates, context)
    
    # Verify field was overridden
    assert updated_trade[field_name] == update_value


# Feature: tcs-store, Property 4: Deep Merge Preservation
@given(
    nested_dict=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.one_of(st.text(), st.integers()),
        min_size=2,
        max_size=5
    ),
    update_key=st.text(min_size=1, max_size=10),
    update_value=st.one_of(st.text(), st.integers())
)
@settings(max_examples=100)
def test_deep_merge_nested_dict_preservation(nested_dict, update_key, update_value):
    """
    Test that deep merge recursively merges nested dictionaries.
    
    For nested objects, updating one field should preserve other fields
    in the same nested object.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create initial trade with nested data
    trade_id = str(uuid.uuid4())
    initial_trade = {
        "id": trade_id,
        "data": nested_dict.copy()
    }
    service.save_new(initial_trade, context)
    
    # Partial update of nested field
    updates = {"data": {update_key: update_value}}
    updated_trade = service.save_partial(trade_id, updates, context)
    
    # Verify nested field was updated
    assert updated_trade["data"][update_key] == update_value
    
    # Verify other nested fields preserved
    for key, value in nested_dict.items():
        if key != update_key:
            assert key in updated_trade["data"]
            assert updated_trade["data"][key] == value


# Feature: tcs-store, Property 4: Deep Merge Preservation
@given(
    dict_field_name=st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
    dict_content=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.one_of(st.text(), st.integers()),
        min_size=1,
        max_size=5
    )
)
@settings(max_examples=100)
def test_deep_merge_null_removes_dict_fields(dict_field_name, dict_content):
    """
    Test that setting a dict field to null removes it.
    
    For nested objects set to null, if the existing value is an object,
    the field should be removed entirely.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create initial trade with dict field
    trade_id = str(uuid.uuid4())
    initial_trade = {
        "id": trade_id,
        dict_field_name: dict_content,
        "other_field": "preserved"
    }
    service.save_new(initial_trade, context)
    
    # Set dict field to null
    updates = {dict_field_name: None}
    updated_trade = service.save_partial(trade_id, updates, context)
    
    # Verify dict field was removed
    assert dict_field_name not in updated_trade
    
    # Verify other fields preserved
    assert updated_trade["other_field"] == "preserved"


# Feature: tcs-store, Property 4: Deep Merge Preservation
@given(
    primitive_field_name=st.text(min_size=1, max_size=20).filter(lambda x: x != "id"),
    primitive_value=st.one_of(st.text(), st.integers(), st.booleans())
)
@settings(max_examples=100)
def test_deep_merge_null_sets_primitive_to_null(primitive_field_name, primitive_value):
    """
    Test that setting a primitive field to null sets it to null.
    
    For primitives set to null, the field should remain but with null value.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create initial trade with primitive field
    trade_id = str(uuid.uuid4())
    initial_trade = {
        "id": trade_id,
        primitive_field_name: primitive_value,
        "other_field": "preserved"
    }
    service.save_new(initial_trade, context)
    
    # Set primitive field to null
    updates = {primitive_field_name: None}
    updated_trade = service.save_partial(trade_id, updates, context)
    
    # Verify primitive field is null
    assert primitive_field_name in updated_trade
    assert updated_trade[primitive_field_name] is None
    
    # Verify other fields preserved
    assert updated_trade["other_field"] == "preserved"


# Feature: tcs-store, Property 4: Deep Merge Preservation
@given(
    list_content=st.lists(st.one_of(st.text(), st.integers()), min_size=1, max_size=5),
    new_list_content=st.lists(st.one_of(st.text(), st.integers()), min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_deep_merge_replaces_lists(list_content, new_list_content):
    """
    Test that lists are replaced entirely, not merged.
    
    For list fields, the entire list should be replaced with the new list,
    not merged element by element.
    """
    store = InMemoryStore()
    service = TradeService(store)
    context = generate_context()
    
    # Create initial trade with list
    trade_id = str(uuid.uuid4())
    initial_trade = {
        "id": trade_id,
        "items": list_content
    }
    service.save_new(initial_trade, context)
    
    # Update list
    updates = {"items": new_list_content}
    updated_trade = service.save_partial(trade_id, updates, context)
    
    # Verify list was replaced (equals new list)
    assert updated_trade["items"] == new_list_content
