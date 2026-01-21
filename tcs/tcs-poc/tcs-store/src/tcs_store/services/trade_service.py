"""Trade service with business logic."""

import re
from typing import Any, Dict, List, Tuple

from tcs_store.storage.in_memory_store import InMemoryStore
from tcs_store.models import Context
from tcs_store.models.filter import TradeFilter
from tcs_store.exceptions import (
    TradeNotFoundError,
    TradeAlreadyExistsError,
    InvalidContextError,
    InvalidFilterError,
)


class TradeService:
    """Service layer for trade operations."""
    
    def __init__(self, store: InMemoryStore):
        """
        Initialize the trade service.
        
        Args:
            store: In-memory store instance
        """
        self._store = store
    
    def _validate_context(self, context: Context) -> None:
        """
        Validate context metadata.
        
        Args:
            context: Context metadata to validate
            
        Raises:
            InvalidContextError: If context is invalid
        """
        if not context.user or not context.user.strip():
            raise InvalidContextError("Context user cannot be empty")
        if not context.agent or not context.agent.strip():
            raise InvalidContextError("Context agent cannot be empty")
        if not context.action or not context.action.strip():
            raise InvalidContextError("Context action cannot be empty")
        if not context.intent or not context.intent.strip():
            raise InvalidContextError("Context intent cannot be empty")
    
    def save_new(self, trade: Dict[str, Any], context: Context) -> Dict[str, Any]:
        """
        Save a new trade.
        
        Args:
            trade: Trade data (must include 'id' field)
            context: Context metadata
            
        Returns:
            Saved trade data
            
        Raises:
            TradeAlreadyExistsError: If trade with same ID already exists
            InvalidContextError: If context is invalid
        """
        self._validate_context(context)
        
        trade_id = trade.get("id")
        if not trade_id:
            raise ValueError("Trade must have an 'id' field")
        
        # Check if trade already exists
        if self._store.exists(trade_id):
            raise TradeAlreadyExistsError(f"Trade with ID {trade_id} already exists")
        
        # Save trade
        context_dict = context.model_dump()
        self._store.save(trade_id, trade, context_dict)
        
        return trade
    
    def save_update(self, trade: Dict[str, Any], context: Context) -> Dict[str, Any]:
        """
        Update an existing trade (full replacement).
        
        Args:
            trade: Trade data (must include 'id' field)
            context: Context metadata
            
        Returns:
            Updated trade data
            
        Raises:
            TradeNotFoundError: If trade does not exist
            InvalidContextError: If context is invalid
        """
        self._validate_context(context)
        
        trade_id = trade.get("id")
        if not trade_id:
            raise ValueError("Trade must have an 'id' field")
        
        # Check if trade exists
        if not self._store.exists(trade_id):
            raise TradeNotFoundError(f"Trade with ID {trade_id} not found")
        
        # Update trade (full replacement)
        context_dict = context.model_dump()
        self._store.save(trade_id, trade, context_dict)
        
        return trade
    
    def load_by_id(self, trade_id: str) -> Dict[str, Any]:
        """
        Load a trade by ID.
        
        Args:
            trade_id: Trade ID to load
            
        Returns:
            Trade data
            
        Raises:
            TradeNotFoundError: If trade does not exist
        """
        trade = self._store.get(trade_id)
        if trade is None:
            raise TradeNotFoundError(f"Trade with ID {trade_id} not found")
        
        return trade
    
    def delete_by_id(self, trade_id: str, context: Context) -> None:
        """
        Delete a trade by ID (idempotent).
        
        Args:
            trade_id: Trade ID to delete
            context: Context metadata
            
        Raises:
            InvalidContextError: If context is invalid
            
        Note:
            This operation is idempotent - deleting a non-existent trade
            succeeds without error.
        """
        self._validate_context(context)
        
        # Delete is idempotent - no error if trade doesn't exist
        context_dict = context.model_dump()
        self._store.delete(trade_id, context_dict)
    
    def _deep_merge(self, existing: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge updates into existing data with smart null handling.
        
        Rules:
        - If existing value is a dict and update sets it to null → Remove the field
        - If existing value is a primitive and update sets it to null → Set to null
        - Nested dicts are merged recursively
        - Lists are replaced entirely (not merged)
        
        Args:
            existing: Existing trade data
            updates: Updates to merge
            
        Returns:
            Merged trade data
        """
        result = existing.copy()
        
        for key, value in updates.items():
            if value is None:
                # Smart null handling
                if key in result:
                    existing_value = result[key]
                    if isinstance(existing_value, dict):
                        # Remove dict fields when set to null
                        del result[key]
                    else:
                        # Set primitives to null
                        result[key] = None
                else:
                    # Key doesn't exist, set to null
                    result[key] = None
            elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Replace value (including lists)
                result[key] = value
        
        return result
    
    def save_partial(self, trade_id: str, updates: Dict[str, Any], context: Context) -> Dict[str, Any]:
        """
        Partially update a trade using deep merge.
        
        Args:
            trade_id: Trade ID to update
            updates: Partial updates to merge
            context: Context metadata
            
        Returns:
            Updated trade data
            
        Raises:
            TradeNotFoundError: If trade does not exist
            InvalidContextError: If context is invalid
        """
        self._validate_context(context)
        
        # Check if trade exists
        existing_trade = self._store.get(trade_id)
        if existing_trade is None:
            raise TradeNotFoundError(f"Trade with ID {trade_id} not found")
        
        # Deep merge updates
        merged_trade = self._deep_merge(existing_trade, updates)
        
        # Save merged trade
        context_dict = context.model_dump()
        self._store.save(trade_id, merged_trade, context_dict)
        
        return merged_trade
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get a value from nested dictionary using dot notation.
        
        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., "data.leg1.notional")
            
        Returns:
            Value at the path, or None if path doesn't exist
        """
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _apply_filter(self, trade: Dict[str, Any], filter_obj: TradeFilter) -> bool:
        """
        Apply filter to a trade to determine if it matches.
        
        Supports:
        - Equality operator (eq)
        - Comparison operators (gt, gte, lt, lte)
        - Regex operator (regex)
        - List operators (in, nin)
        - Nested field paths (e.g., data.leg1.notional)
        - Multiple conditions with AND logic
        
        Args:
            trade: Trade data to filter
            filter_obj: Filter criteria
            
        Returns:
            True if trade matches filter, False otherwise
            
        Raises:
            InvalidFilterError: If filter is malformed
        """
        # If no filter criteria, match all trades
        if not filter_obj.filter:
            return True
        
        # Apply each filter condition (AND logic)
        for field_path, conditions in filter_obj.filter.items():
            if not isinstance(conditions, dict):
                raise InvalidFilterError(f"Filter conditions for '{field_path}' must be a dictionary")
            
            # Get the value from the trade
            field_value = self._get_nested_value(trade, field_path)
            
            # Apply each operator
            for operator, expected_value in conditions.items():
                if operator == "eq":
                    if field_value != expected_value:
                        return False
                
                elif operator == "ne":
                    if field_value == expected_value:
                        return False
                
                elif operator == "gt":
                    if field_value is None or not (field_value > expected_value):
                        return False
                
                elif operator == "gte":
                    if field_value is None or not (field_value >= expected_value):
                        return False
                
                elif operator == "lt":
                    if field_value is None or not (field_value < expected_value):
                        return False
                
                elif operator == "lte":
                    if field_value is None or not (field_value <= expected_value):
                        return False
                
                elif operator == "regex":
                    if field_value is None:
                        return False
                    try:
                        if not isinstance(field_value, str):
                            return False
                        if not re.search(expected_value, field_value):
                            return False
                    except re.error as e:
                        raise InvalidFilterError(f"Invalid regex pattern '{expected_value}': {e}")
                
                elif operator == "in":
                    if not isinstance(expected_value, list):
                        raise InvalidFilterError(f"'in' operator requires a list, got {type(expected_value)}")
                    if field_value not in expected_value:
                        return False
                
                elif operator == "nin":
                    if not isinstance(expected_value, list):
                        raise InvalidFilterError(f"'nin' operator requires a list, got {type(expected_value)}")
                    if field_value in expected_value:
                        return False
                
                else:
                    raise InvalidFilterError(f"Unknown filter operator: {operator}")
        
        return True
    
    def load_by_filter(self, filter_obj: TradeFilter) -> List[Dict[str, Any]]:
        """
        Load trades matching a filter.
        
        Args:
            filter_obj: Filter criteria
            
        Returns:
            List of matching trades
            
        Raises:
            InvalidFilterError: If filter is malformed
        """
        # Get all trades
        all_trades = self._store.get_all()
        
        # Apply filter
        matching_trades = [
            trade for trade in all_trades
            if self._apply_filter(trade, filter_obj)
        ]
        
        return matching_trades
    
    def list_by_filter(self, filter_obj: TradeFilter) -> List[Dict[str, Any]]:
        """
        List trades matching a filter (returns list items).
        
        Args:
            filter_obj: Filter criteria
            
        Returns:
            List of matching trade list items
            
        Raises:
            InvalidFilterError: If filter is malformed
            
        Note:
            Currently returns full trade data. In the future, this could
            return simplified list items for efficiency.
        """
        # For now, list_by_filter returns the same as load_by_filter
        # In the future, this could return simplified list items
        return self.load_by_filter(filter_obj)
    
    def count_by_filter(self, filter_obj: TradeFilter) -> int:
        """
        Count trades matching a filter.
        
        Args:
            filter_obj: Filter criteria
            
        Returns:
            Count of matching trades
            
        Raises:
            InvalidFilterError: If filter is malformed
        """
        # Get all trades
        all_trades = self._store.get_all()
        
        # Count matching trades
        count = sum(1 for trade in all_trades if self._apply_filter(trade, filter_obj))
        
        return count
    
    def load_by_ids(self, trade_ids: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Load multiple trades by their IDs.
        
        Args:
            trade_ids: List of trade IDs to load
            
        Returns:
            Tuple of (list of found trades, list of missing IDs)
            
        Note:
            This is a read operation and does not require context metadata.
        """
        found_trades = []
        missing_ids = []
        
        for trade_id in trade_ids:
            trade = self._store.get(trade_id)
            if trade is not None:
                found_trades.append(trade)
            else:
                missing_ids.append(trade_id)
        
        return found_trades, missing_ids
    
    def delete_by_ids(self, trade_ids: List[str], context: Context) -> Tuple[int, List[str]]:
        """
        Delete multiple trades by their IDs.
        
        Args:
            trade_ids: List of trade IDs to delete
            context: Context metadata
            
        Returns:
            Tuple of (count of deleted trades, list of missing IDs)
            
        Raises:
            InvalidContextError: If context is invalid
            
        Note:
            This operation is idempotent - missing IDs are tracked but don't cause errors.
        """
        self._validate_context(context)
        
        deleted_count = 0
        missing_ids = []
        context_dict = context.model_dump()
        
        for trade_id in trade_ids:
            if self._store.exists(trade_id):
                self._store.delete(trade_id, context_dict)
                deleted_count += 1
            else:
                missing_ids.append(trade_id)
        
        return deleted_count, missing_ids
