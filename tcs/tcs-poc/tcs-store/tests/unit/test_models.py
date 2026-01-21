"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from tcs_store.models import (
    Context,
    TradeFilter,
    SaveNewRequest,
    PartialUpdateRequest,
    LoadGroupRequest,
    DeleteGroupRequest,
)


class TestContextModel:
    """Tests for Context model."""
    
    def test_valid_context(self):
        """Test creating a valid context."""
        context = Context(
            user="trader_123",
            agent="trading_platform",
            action="save_new",
            intent="new_trade_booking"
        )
        assert context.user == "trader_123"
        assert context.agent == "trading_platform"
        assert context.action == "save_new"
        assert context.intent == "new_trade_booking"
    
    def test_context_strips_whitespace(self):
        """Test that context fields strip whitespace."""
        context = Context(
            user="  trader_123  ",
            agent="  trading_platform  ",
            action="  save_new  ",
            intent="  new_trade_booking  "
        )
        assert context.user == "trader_123"
        assert context.agent == "trading_platform"
        assert context.action == "save_new"
        assert context.intent == "new_trade_booking"
    
    def test_context_missing_user(self):
        """Test that missing user field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                agent="trading_platform",
                action="save_new",
                intent="new_trade_booking"
            )
        assert "user" in str(exc_info.value)
    
    def test_context_empty_user(self):
        """Test that empty user field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                user="",
                agent="trading_platform",
                action="save_new",
                intent="new_trade_booking"
            )
        assert "user" in str(exc_info.value).lower()
    
    def test_context_whitespace_only_user(self):
        """Test that whitespace-only user field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                user="   ",
                agent="trading_platform",
                action="save_new",
                intent="new_trade_booking"
            )
        assert "empty" in str(exc_info.value).lower() or "whitespace" in str(exc_info.value).lower()
    
    def test_context_missing_agent(self):
        """Test that missing agent field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                user="trader_123",
                action="save_new",
                intent="new_trade_booking"
            )
        assert "agent" in str(exc_info.value)
    
    def test_context_missing_action(self):
        """Test that missing action field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                user="trader_123",
                agent="trading_platform",
                intent="new_trade_booking"
            )
        assert "action" in str(exc_info.value)
    
    def test_context_missing_intent(self):
        """Test that missing intent field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                user="trader_123",
                agent="trading_platform",
                action="save_new"
            )
        assert "intent" in str(exc_info.value)
    
    def test_context_serialization(self):
        """Test context serialization to dict."""
        context = Context(
            user="trader_123",
            agent="trading_platform",
            action="save_new",
            intent="new_trade_booking"
        )
        data = context.model_dump()
        assert data == {
            "user": "trader_123",
            "agent": "trading_platform",
            "action": "save_new",
            "intent": "new_trade_booking"
        }
    
    def test_context_deserialization(self):
        """Test context deserialization from dict."""
        data = {
            "user": "trader_123",
            "agent": "trading_platform",
            "action": "save_new",
            "intent": "new_trade_booking"
        }
        context = Context(**data)
        assert context.user == "trader_123"
        assert context.agent == "trading_platform"


class TestTradeFilterModel:
    """Tests for TradeFilter model."""
    
    def test_empty_filter(self):
        """Test creating an empty filter."""
        filter = TradeFilter()
        assert filter.id is None
        assert filter.ids is None
        assert filter.filter is None
        assert filter.limit is None
        assert filter.offset is None
    
    def test_filter_with_id(self):
        """Test filter with single ID."""
        filter = TradeFilter(id="trade-123")
        assert filter.id == "trade-123"
    
    def test_filter_with_ids(self):
        """Test filter with multiple IDs."""
        filter = TradeFilter(ids=["trade-123", "trade-456"])
        assert filter.ids == ["trade-123", "trade-456"]
    
    def test_filter_with_json_filter(self):
        """Test filter with JSON filter criteria."""
        filter = TradeFilter(
            filter={
                "data.trade_type": {"eq": "IR_SWAP"},
                "data.notional": {"gte": 1000000}
            }
        )
        assert filter.filter is not None
        assert "data.trade_type" in filter.filter
        assert filter.filter["data.trade_type"]["eq"] == "IR_SWAP"
    
    def test_filter_with_pagination(self):
        """Test filter with pagination."""
        filter = TradeFilter(limit=10, offset=20)
        assert filter.limit == 10
        assert filter.offset == 20
    
    def test_filter_invalid_limit(self):
        """Test that negative limit raises validation error."""
        with pytest.raises(ValidationError):
            TradeFilter(limit=0)
    
    def test_filter_invalid_offset(self):
        """Test that negative offset raises validation error."""
        with pytest.raises(ValidationError):
            TradeFilter(offset=-1)


class TestRequestModels:
    """Tests for request models."""
    
    def test_save_new_request_valid(self):
        """Test creating a valid SaveNewRequest."""
        request = SaveNewRequest(
            context=Context(
                user="trader_123",
                agent="trading_platform",
                action="save_new",
                intent="new_trade_booking"
            ),
            trade={"id": "trade-123", "data": {"trade_type": "IR_SWAP"}}
        )
        assert request.context.user == "trader_123"
        assert request.trade["id"] == "trade-123"
    
    def test_save_new_request_missing_context(self):
        """Test that missing context raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SaveNewRequest(
                trade={"id": "trade-123", "data": {"trade_type": "IR_SWAP"}}
            )
        assert "context" in str(exc_info.value)
    
    def test_partial_update_request_valid(self):
        """Test creating a valid PartialUpdateRequest."""
        request = PartialUpdateRequest(
            context=Context(
                user="trader_123",
                agent="trading_platform",
                action="save_partial",
                intent="update_schedule"
            ),
            id="trade-123",
            updates={"data": {"leg1": {"notional": 2000000}}}
        )
        assert request.id == "trade-123"
        assert "data" in request.updates
    
    def test_partial_update_request_empty_id(self):
        """Test that empty ID raises validation error."""
        with pytest.raises(ValidationError):
            PartialUpdateRequest(
                context=Context(
                    user="trader_123",
                    agent="trading_platform",
                    action="save_partial",
                    intent="update_schedule"
                ),
                id="",
                updates={"data": {"leg1": {"notional": 2000000}}}
            )
    
    def test_load_group_request_valid(self):
        """Test creating a valid LoadGroupRequest."""
        request = LoadGroupRequest(
            context=Context(
                user="trader_123",
                agent="trading_platform",
                action="load_group",
                intent="portfolio_review"
            ),
            ids=["trade-123", "trade-456"]
        )
        assert len(request.ids) == 2
        assert "trade-123" in request.ids
    
    def test_load_group_request_empty_ids(self):
        """Test that empty IDs list raises validation error."""
        with pytest.raises(ValidationError):
            LoadGroupRequest(
                context=Context(
                    user="trader_123",
                    agent="trading_platform",
                    action="load_group",
                    intent="portfolio_review"
                ),
                ids=[]
            )
    
    def test_delete_group_request_valid(self):
        """Test creating a valid DeleteGroupRequest."""
        request = DeleteGroupRequest(
            context=Context(
                user="trader_123",
                agent="trading_platform",
                action="delete_group",
                intent="cleanup"
            ),
            ids=["trade-123", "trade-456"]
        )
        assert len(request.ids) == 2
    
    def test_request_serialization(self):
        """Test request serialization."""
        request = SaveNewRequest(
            context=Context(
                user="trader_123",
                agent="trading_platform",
                action="save_new",
                intent="new_trade_booking"
            ),
            trade={"id": "trade-123", "data": {"trade_type": "IR_SWAP"}}
        )
        data = request.model_dump()
        assert "context" in data
        assert "trade" in data
        assert data["context"]["user"] == "trader_123"
        assert data["trade"]["id"] == "trade-123"
