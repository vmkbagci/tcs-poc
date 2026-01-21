"""Property-based tests for context metadata requirements."""

from hypothesis import given, settings
import hypothesis.strategies as st
import pytest
from pydantic import ValidationError

from tcs_store.models import Context, SaveNewRequest


# Feature: tcs-store, Property 20: Context Metadata Required
@given(
    user=st.one_of(st.none(), st.just(""), st.text(min_size=0, max_size=0)),
)
@settings(max_examples=100)
def test_context_requires_non_empty_user(user):
    """
    Test that context requires a non-empty user field.
    
    For any request, if the context user field is None, empty, or whitespace,
    the validation should fail with an error.
    """
    with pytest.raises(ValidationError):
        Context(
            user=user if user is not None else "",
            agent="test_agent",
            action="test_action",
            intent="test_intent"
        )


# Feature: tcs-store, Property 20: Context Metadata Required
@given(
    agent=st.one_of(st.none(), st.just(""), st.text(min_size=0, max_size=0)),
)
@settings(max_examples=100)
def test_context_requires_non_empty_agent(agent):
    """
    Test that context requires a non-empty agent field.
    
    For any request, if the context agent field is None, empty, or whitespace,
    the validation should fail with an error.
    """
    with pytest.raises(ValidationError):
        Context(
            user="test_user",
            agent=agent if agent is not None else "",
            action="test_action",
            intent="test_intent"
        )


# Feature: tcs-store, Property 20: Context Metadata Required
@given(
    action=st.one_of(st.none(), st.just(""), st.text(min_size=0, max_size=0)),
)
@settings(max_examples=100)
def test_context_requires_non_empty_action(action):
    """
    Test that context requires a non-empty action field.
    
    For any request, if the context action field is None, empty, or whitespace,
    the validation should fail with an error.
    """
    with pytest.raises(ValidationError):
        Context(
            user="test_user",
            agent="test_agent",
            action=action if action is not None else "",
            intent="test_intent"
        )


# Feature: tcs-store, Property 20: Context Metadata Required
@given(
    intent=st.one_of(st.none(), st.just(""), st.text(min_size=0, max_size=0)),
)
@settings(max_examples=100)
def test_context_requires_non_empty_intent(intent):
    """
    Test that context requires a non-empty intent field.
    
    For any request, if the context intent field is None, empty, or whitespace,
    the validation should fail with an error.
    """
    with pytest.raises(ValidationError):
        Context(
            user="test_user",
            agent="test_agent",
            action="test_action",
            intent=intent if intent is not None else ""
        )


# Feature: tcs-store, Property 20: Context Metadata Required
@given(
    user=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    agent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    action=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    intent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
)
@settings(max_examples=100)
def test_context_accepts_valid_fields(user, agent, action, intent):
    """
    Test that context accepts valid non-empty fields.
    
    For any request with all context fields non-empty and non-whitespace,
    the validation should succeed.
    """
    context = Context(
        user=user,
        agent=agent,
        action=action,
        intent=intent
    )
    assert context.user.strip() == user.strip()
    assert context.agent.strip() == agent.strip()
    assert context.action.strip() == action.strip()
    assert context.intent.strip() == intent.strip()


# Feature: tcs-store, Property 20: Context Metadata Required
@given(
    trade_data=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
        min_size=1
    )
)
@settings(max_examples=100)
def test_request_without_context_fails(trade_data):
    """
    Test that requests without context metadata fail validation.
    
    For any request payload without a context field, the validation
    should fail with an error indicating the context is required.
    """
    with pytest.raises(ValidationError) as exc_info:
        SaveNewRequest(trade=trade_data)
    
    # Verify the error mentions context
    assert "context" in str(exc_info.value).lower()


# Feature: tcs-store, Property 20: Context Metadata Required
@given(
    user=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    agent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    action=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    intent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    trade_data=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.one_of(st.text(), st.integers()),
        min_size=1
    )
)
@settings(max_examples=100)
def test_request_with_valid_context_succeeds(user, agent, action, intent, trade_data):
    """
    Test that requests with valid context metadata succeed.
    
    For any request payload with a valid context containing all required fields,
    the validation should succeed.
    """
    request = SaveNewRequest(
        context=Context(
            user=user,
            agent=agent,
            action=action,
            intent=intent
        ),
        trade=trade_data
    )
    assert request.context.user.strip() == user.strip()
    assert request.context.agent.strip() == agent.strip()
    assert request.context.action.strip() == action.strip()
    assert request.context.intent.strip() == intent.strip()
    assert request.trade == trade_data



# Feature: tcs-store, Property 21: Context Metadata Logged
@given(
    user=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    agent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    action=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    intent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    trade_data=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.one_of(st.text(), st.integers()),
        min_size=1
    )
)
@settings(max_examples=100)
def test_context_metadata_logged_on_save(user, agent, action, intent, trade_data):
    """
    Test that context metadata is logged for save operations.
    
    For any mutating operation (save), the context metadata should be stored
    in the operation log with a timestamp for lifecycle tracing.
    """
    from tcs_store.storage.in_memory_store import InMemoryStore
    from tcs_store.services.trade_service import TradeService
    import uuid
    
    store = InMemoryStore()
    service = TradeService(store)
    
    context = Context(
        user=user,
        agent=agent,
        action=action,
        intent=intent
    )
    
    trade = {"id": str(uuid.uuid4()), **trade_data}
    service.save_new(trade, context)
    
    # Check operation log
    op_log = store.get_operation_log()
    assert len(op_log) > 0
    
    # Find the save operation
    save_ops = [op for op in op_log if op["operation"] == "save"]
    assert len(save_ops) > 0
    
    last_save = save_ops[-1]
    assert "context" in last_save
    assert last_save["context"]["user"] == user.strip()
    assert last_save["context"]["agent"] == agent.strip()
    assert last_save["context"]["action"] == action.strip()
    assert last_save["context"]["intent"] == intent.strip()
    assert "timestamp" in last_save
    assert last_save["trade_id"] == trade["id"]


# Feature: tcs-store, Property 21: Context Metadata Logged
@given(
    user=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    agent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    action=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    intent=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
)
@settings(max_examples=100)
def test_context_metadata_logged_on_delete(user, agent, action, intent):
    """
    Test that context metadata is logged for delete operations.
    
    For any mutating operation (delete), the context metadata should be stored
    in the operation log with a timestamp for lifecycle tracing.
    """
    from tcs_store.storage.in_memory_store import InMemoryStore
    from tcs_store.services.trade_service import TradeService
    import uuid
    
    store = InMemoryStore()
    service = TradeService(store)
    
    context = Context(
        user=user,
        agent=agent,
        action=action,
        intent=intent
    )
    
    # Create and save a trade first
    trade_id = str(uuid.uuid4())
    trade = {"id": trade_id, "data": {"test": "value"}}
    service.save_new(trade, context)
    
    # Delete the trade
    service.delete_by_id(trade_id, context)
    
    # Check operation log
    op_log = store.get_operation_log()
    
    # Find the delete operation
    delete_ops = [op for op in op_log if op["operation"] == "delete"]
    assert len(delete_ops) > 0
    
    last_delete = delete_ops[-1]
    assert "context" in last_delete
    assert last_delete["context"]["user"] == user.strip()
    assert last_delete["context"]["agent"] == agent.strip()
    assert last_delete["context"]["action"] == action.strip()
    assert last_delete["context"]["intent"] == intent.strip()
    assert "timestamp" in last_delete
    assert last_delete["trade_id"] == trade_id
