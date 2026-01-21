"""In-memory storage implementation with lifecycle tracing."""

import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict


class OperationLog(TypedDict):
    """Log entry for an operation with context metadata."""
    timestamp: str
    context: Dict[str, str]
    operation: str
    trade_id: str


class InMemoryStore:
    """Thread-safe in-memory storage for trades with operation logging."""
    
    def __init__(self):
        """Initialize the in-memory store."""
        self._store: Dict[str, Dict[str, Any]] = {}
        self._operation_log: List[OperationLog] = []
        self._lock = threading.RLock()
    
    def save(self, trade_id: str, trade_data: Dict[str, Any], context: Dict[str, str]) -> None:
        """
        Save a trade to the store.
        
        Args:
            trade_id: Unique identifier for the trade
            trade_data: Trade data to store
            context: Context metadata (user, agent, action, intent)
        """
        with self._lock:
            self._store[trade_id] = trade_data
            self._log_operation("save", trade_id, context)
    
    def get(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a trade from the store.
        
        Args:
            trade_id: Unique identifier for the trade
            
        Returns:
            Trade data if found, None otherwise
        """
        with self._lock:
            return self._store.get(trade_id)
    
    def exists(self, trade_id: str) -> bool:
        """
        Check if a trade exists in the store.
        
        Args:
            trade_id: Unique identifier for the trade
            
        Returns:
            True if trade exists, False otherwise
        """
        with self._lock:
            return trade_id in self._store
    
    def delete(self, trade_id: str, context: Dict[str, str]) -> bool:
        """
        Delete a trade from the store.
        
        Args:
            trade_id: Unique identifier for the trade
            context: Context metadata (user, agent, action, intent)
            
        Returns:
            True if trade was deleted, False if it didn't exist
        """
        with self._lock:
            if trade_id in self._store:
                del self._store[trade_id]
                self._log_operation("delete", trade_id, context)
                return True
            return False
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieve all trades from the store.
        
        Returns:
            List of all trade data
        """
        with self._lock:
            return list(self._store.values())
    
    def clear(self) -> None:
        """Clear all trades from the store."""
        with self._lock:
            self._store.clear()
            self._operation_log.clear()
    
    def get_operation_log(self) -> List[OperationLog]:
        """
        Retrieve the operation log for lifecycle tracing.
        
        Returns:
            List of operation log entries
        """
        with self._lock:
            return list(self._operation_log)
    
    def _log_operation(self, operation: str, trade_id: str, context: Dict[str, str]) -> None:
        """
        Log an operation with context metadata.
        
        Args:
            operation: Type of operation (save, delete, etc.)
            trade_id: Trade ID involved in the operation
            context: Context metadata
        """
        log_entry: OperationLog = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": context,
            "operation": operation,
            "trade_id": trade_id,
        }
        self._operation_log.append(log_entry)
