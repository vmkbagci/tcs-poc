"""Property-based tests for error handling."""

import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from fastapi.testclient import TestClient

from tcs_store.main import app

client = TestClient(app)


# Strategy for generating valid context
@st.composite
def context_strategy(draw):
    """Generate valid context metadata."""
    # Generate strings with only printable ASCII characters (no control chars, no extended ASCII)
    return {
        "user": draw(st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=33, max_codepoint=126))),
        "agent": draw(st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=33, max_codepoint=126))),
        "action": draw(st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=33, max_codepoint=126))),
        "intent": draw(st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=33, max_codepoint=126))),
    }


# Strategy for generating trade IDs
trade_id_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(
    whitelist_categories=("Lu", "Ll", "Nd"),
    whitelist_characters="-_"
))


# Feature: tcs-store, Property 18: Error Response Format
@given(trade_id=trade_id_strategy, context=context_strategy())
@settings(max_examples=100)
def test_error_response_format_not_found(trade_id, context):
    """
    Property 18: Error Response Format
    
    For any error condition, the response should be valid JSON containing
    an error message and the appropriate HTTP status code.
    
    This test verifies that 404 errors have the correct format.
    
    Validates: Requirements 13.1
    """
    # Try to load a non-existent trade
    response = client.post(
        "/load/id",
        json={"context": context, "id": trade_id}
    )
    
    # Should return 404
    assert response.status_code == 404
    
    # Response should be valid JSON
    data = response.json()
    
    # Should have error field
    assert "error" in data
    assert isinstance(data["error"], str)
    assert len(data["error"]) > 0
    
    # May have detail field
    if "detail" in data:
        assert isinstance(data["detail"], str)


# Feature: tcs-store, Property 18: Error Response Format
@given(context=context_strategy(), trade_id=trade_id_strategy)
@settings(max_examples=100)
def test_error_response_format_conflict(context, trade_id):
    """
    Property 18: Error Response Format
    
    For any error condition, the response should be valid JSON containing
    an error message and the appropriate HTTP status code.
    
    This test verifies that 409 errors have the correct format.
    
    Validates: Requirements 13.1
    """
    # Create a trade with unique ID
    trade = {"id": trade_id, "data": {"test": "data"}}
    
    response = client.post(
        "/save/new",
        json={"context": context, "trade": trade}
    )
    
    # If trade already exists (from previous example), delete it first
    if response.status_code == 409:
        client.post("/delete/id", json={"context": context, "id": trade_id})
        response = client.post(
            "/save/new",
            json={"context": context, "trade": trade}
        )
    
    assert response.status_code == 201
    
    # Try to create the same trade again
    response = client.post(
        "/save/new",
        json={"context": context, "trade": trade}
    )
    
    # Should return 409
    assert response.status_code == 409
    
    # Response should be valid JSON
    data = response.json()
    
    # Should have error field
    assert "error" in data
    assert isinstance(data["error"], str)
    assert len(data["error"]) > 0
    
    # May have detail field
    if "detail" in data:
        assert isinstance(data["detail"], str)


# Feature: tcs-store, Property 18: Error Response Format
@given(trade_id=trade_id_strategy)
@settings(max_examples=100)
def test_error_response_format_validation(trade_id):
    """
    Property 18: Error Response Format
    
    For any error condition, the response should be valid JSON containing
    an error message and the appropriate HTTP status code.
    
    This test verifies that 422 validation errors have the correct format.
    
    Validates: Requirements 13.1
    """
    # Try to save without context (should fail validation)
    response = client.post(
        "/save/new",
        json={"trade": {"id": trade_id, "data": {}}}
    )
    
    # Should return 422
    assert response.status_code == 422
    
    # Response should be valid JSON
    data = response.json()
    
    # FastAPI validation errors have "detail" field (may be list or string)
    # Our custom exception handlers have "error" field
    # Both are valid error response formats
    assert "detail" in data or "error" in data
    
    if "detail" in data:
        # FastAPI validation error format
        assert data["detail"] is not None
    if "error" in data:
        # Custom exception handler format
        assert isinstance(data["error"], str)
        assert len(data["error"]) > 0



# Feature: tcs-store, Property 16: Not Found Errors
@given(trade_id=trade_id_strategy, context=context_strategy())
@settings(max_examples=100)
def test_not_found_errors_update(trade_id, context):
    """
    Property 16: Not Found Errors
    
    For any operation that references a non-existent trade ID (update, partial update, load),
    the operation should fail with HTTP status 404 and an appropriate error message.
    
    This test verifies that update operations return 404 for non-existent trades.
    
    Validates: Requirements 2.2, 3.2, 4.2
    """
    # Try to update a non-existent trade
    response = client.post(
        "/save/update",
        json={
            "context": context,
            "trade": {"id": trade_id, "data": {"test": "data"}}
        }
    )
    
    # Should return 404
    assert response.status_code == 404
    
    # Response should contain error information
    data = response.json()
    assert "detail" in data or "error" in data


# Feature: tcs-store, Property 16: Not Found Errors
@given(trade_id=trade_id_strategy, context=context_strategy())
@settings(max_examples=100)
def test_not_found_errors_partial_update(trade_id, context):
    """
    Property 16: Not Found Errors
    
    For any operation that references a non-existent trade ID (update, partial update, load),
    the operation should fail with HTTP status 404 and an appropriate error message.
    
    This test verifies that partial update operations return 404 for non-existent trades.
    
    Validates: Requirements 2.2, 3.2, 4.2
    """
    # Try to partially update a non-existent trade
    response = client.post(
        "/save/partial",
        json={
            "context": context,
            "id": trade_id,
            "updates": {"data": {"field": "value"}}
        }
    )
    
    # Should return 404
    assert response.status_code == 404
    
    # Response should contain error information
    data = response.json()
    assert "detail" in data or "error" in data


# Feature: tcs-store, Property 16: Not Found Errors
@given(trade_id=trade_id_strategy, context=context_strategy())
@settings(max_examples=100)
def test_not_found_errors_load(trade_id, context):
    """
    Property 16: Not Found Errors
    
    For any operation that references a non-existent trade ID (update, partial update, load),
    the operation should fail with HTTP status 404 and an appropriate error message.
    
    This test verifies that load operations return 404 for non-existent trades.
    
    Validates: Requirements 2.2, 3.2, 4.2
    """
    # Try to load a non-existent trade
    response = client.post(
        "/load/id",
        json={"context": context, "id": trade_id}
    )
    
    # Should return 404
    assert response.status_code == 404
    
    # Response should contain error information
    data = response.json()
    assert "detail" in data or "error" in data



# Feature: tcs-store, Property 17: Validation Errors
@given(trade_id=trade_id_strategy)
@settings(max_examples=100)
def test_validation_errors_missing_context(trade_id):
    """
    Property 17: Validation Errors
    
    For any request with invalid JSON structure or missing required fields,
    the operation should fail with HTTP status 422 and detailed error information.
    
    This test verifies that requests without context are rejected with 422.
    
    Validates: Requirements 1.3, 2.3, 6.3, 7.3, 8.3, 11.2
    """
    # Try to save without context
    response = client.post(
        "/save/new",
        json={"trade": {"id": trade_id, "data": {}}}
    )
    
    # Should return 422
    assert response.status_code == 422
    
    # Response should contain error information
    data = response.json()
    assert "detail" in data or "error" in data


# Feature: tcs-store, Property 17: Validation Errors
@given(context=context_strategy())
@settings(max_examples=100)
def test_validation_errors_missing_trade_id(context):
    """
    Property 17: Validation Errors
    
    For any request with invalid JSON structure or missing required fields,
    the operation should fail with HTTP status 422 and detailed error information.
    
    This test verifies that requests without trade ID are rejected with 422.
    
    Validates: Requirements 1.3, 2.3, 6.3, 7.3, 8.3, 11.2
    """
    # Try to save without trade ID
    response = client.post(
        "/save/new",
        json={"context": context, "trade": {"data": {"test": "data"}}}
    )
    
    # Should return 422
    assert response.status_code == 422
    
    # Response should contain error information
    data = response.json()
    assert "detail" in data or "error" in data


# Feature: tcs-store, Property 17: Validation Errors
@given(context=context_strategy())
@settings(max_examples=100)
def test_validation_errors_empty_id_list(context):
    """
    Property 17: Validation Errors
    
    For any request with invalid JSON structure or missing required fields,
    the operation should fail with HTTP status 422 and detailed error information.
    
    This test verifies that requests with empty ID lists are rejected with 422.
    
    Validates: Requirements 1.3, 2.3, 6.3, 7.3, 8.3, 11.2
    """
    # Try to load with empty ID list
    response = client.post(
        "/load/group",
        json={"context": context, "ids": []}
    )
    
    # Should return 422
    assert response.status_code == 422
    
    # Response should contain error information
    data = response.json()
    assert "detail" in data or "error" in data


# Feature: tcs-store, Property 17: Validation Errors
def test_validation_errors_invalid_json():
    """
    Property 17: Validation Errors
    
    For any request with invalid JSON structure or missing required fields,
    the operation should fail with HTTP status 422 and detailed error information.
    
    This test verifies that requests with invalid JSON are rejected with 422.
    
    Validates: Requirements 1.3, 2.3, 6.3, 7.3, 8.3, 11.2
    """
    # Try to send invalid JSON
    response = client.post(
        "/save/new",
        data="not valid json",
        headers={"Content-Type": "application/json"}
    )
    
    # Should return 422
    assert response.status_code == 422
    
    # Response should contain error information
    data = response.json()
    assert "detail" in data or "error" in data
