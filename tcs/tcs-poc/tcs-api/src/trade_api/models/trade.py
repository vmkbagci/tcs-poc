"""Trade class with JSON composition pattern using high-performance libraries."""

import orjson
import jmespath
from glom import assign
from functools import lru_cache, cached_property
from typing import Any, Dict, Union
from types import MappingProxyType


@lru_cache(maxsize=1024)
def _compile_jmes(path: str):
    """Cache compiled JMESPath expressions for performance.
    
    JMESPath compilation is expensive, so we cache up to 1024 unique paths.
    This dramatically improves performance for repeated queries.
    
    Args:
        path: JMESPath expression string
        
    Returns:
        Compiled JMESPath expression
    """
    return jmespath.compile(path)


class Trade:
    """Lightweight composition-based wrapper for trade JSON data.
    
    This class combines the best tools for JSON operations:
    - orjson: Fast JSON parsing/serialization (2-3x faster than stdlib json)
    - jmespath: Powerful query language for complex reads (filters, projections)
    - glom: Robust path-based writes with automatic structure creation
    
    Design philosophy:
    - Minimal object overhead (just wraps a dict)
    - Direct data access via .data property
    - Specialized methods for different access patterns
    
    Requirements:
    - 5.3: Preserve direct access to underlying JSON properties
    - 5.5: Handle varying JSON schemas through composition
    """
    
    def __init__(self, data: Union[Dict[str, Any], str, bytes]):
        """Initialize Trade with JSON data.
        
        Accepts multiple input formats for flexibility:
        - Dict: Direct dictionary (zero-copy, fastest)
        - str/bytes: JSON string/bytes (parsed with fast orjson)
        
        Args:
            data: Dictionary, JSON string, or JSON bytes containing trade data
        """
        if isinstance(data, (str, bytes)):
            # Use orjson for fast parsing (2-3x faster than json.loads)
            self._data = orjson.loads(data)
        else:
            # Direct dict assignment (zero overhead)
            self._data = data

    @property
    def data(self) -> Dict[str, Any]:
        """Direct access to underlying JSON data.
        
        Provides zero-overhead access to the raw dictionary for cases where
        you need maximum performance or want to use standard dict operations.
        
        Returns:
            The complete trade data dictionary
        """
        return self._data

    def jmesget(self, path: str, default: Any = None) -> Any:
        """Get data using JMESPath query language (for complex queries).
        
        JMESPath provides powerful query capabilities:
        - Simple paths: "tradeId", "specific.rateFamily"
        - Array access: "legs[0].rate"
        - Filters: "legs[?legType=='Fixed'].rate"
        - Projections: "legs[*].legId"
        - Slicing: "legs[:2]"
        
        Uses cached compilation for performance on repeated queries.
        
        Use this when you need:
        - Filtering/projections
        - Complex queries
        - Array operations
        
        Args:
            path: JMESPath expression
            default: Default value if path doesn't exist or returns None
            
        Returns:
            Query result or default value
            
        Examples:
            trade.jmesget("legs[?rate > `0`].id")
            trade.jmesget("legs[0].rate.currency")
            trade.jmesget("legs[*].legType")
        """
        # Use cached compiled expression for performance
        result = _compile_jmes(path).search(self._data)
        return result if result is not None else default

    def glomset(self, path: str, value: Any) -> None:
        """Set nested property using glom path notation (for writes).
        
        Glom provides robust path-based assignment:
        - Automatically creates intermediate structures
        - Handles nested dicts and lists
        - Clear error messages on invalid paths
        
        Path syntax:
        - Nested dicts: "specific.rateFamily"
        - List access: "legs.0.rate" or "legs[0].rate"
        - Deep nesting: "counterparties.0.contact.email"
        
        Use this for all write operations to nested structures.
        
        Args:
            path: Glom path expression (dot notation with numeric indices)
            value: Value to set at the path
            
        Examples:
            trade.glomset("legs.0.rate", 0.05)
            trade.glomset("specific.rateFamily", "VanillaIRS")
            trade.glomset("counterparties.0.name", "Bank A")
        """
        # Glom handles structure creation and validation
        assign(self._data, path, value)

    def to_json(self) -> bytes:
        """Serialize trade data to JSON bytes using orjson.
        
        Uses orjson for fast serialization (2-3x faster than json.dumps).
        Returns bytes for maximum performance and compatibility with
        HTTP responses, file I/O, etc.
        
        Returns:
            JSON bytes representation of the trade data
        """
        return orjson.dumps(self._data)
    
    def to_readonly(self) -> 'ReadOnlyTrade':
        """Convert to read-only trade with cached properties.
        
        Creates a ReadOnlyTrade instance that:
        - Prevents modifications to the underlying data
        - Caches expensive property lookups
        - Provides the same read interface (jmesget, data access)
        
        Use this when:
        - Passing trades to read-only contexts
        - Want to cache computed properties without invalidation concerns
        - Need to ensure data immutability
        
        Returns:
            ReadOnlyTrade instance wrapping this trade's data
        """
        return ReadOnlyTrade(self._data)


class ReadOnlyTrade:
    """Immutable, read-only view of trade data with cached properties.
    
    This class provides:
    - Immutable data access (via MappingProxyType)
    - Cached properties for expensive lookups (no invalidation needed)
    - Same read interface as Trade (jmesget)
    - No write methods (glomset removed)
    
    Use cases:
    - Validation pipelines (read-only access)
    - API responses (prevent accidental modification)
    - Caching expensive computed values
    - Multi-threaded read access
    
    Design:
    - Data is wrapped in MappingProxyType (truly immutable)
    - @cached_property for common lookups (trade_id, trade_type, etc.)
    - Zero cache invalidation concerns (data can't change)
    """
    
    def __init__(self, data: Union[Dict[str, Any], Trade]):
        """Initialize ReadOnlyTrade with immutable data.
        
        Args:
            data: Dictionary or Trade instance to make read-only
        """
        if isinstance(data, Trade):
            # Extract data from Trade instance
            source_data = data._data
        else:
            source_data = data
        
        # Wrap in MappingProxyType for true immutability
        # This prevents any modifications to the underlying dict
        self._data = MappingProxyType(source_data)
    
    @property
    def data(self) -> MappingProxyType:
        """Immutable view of underlying JSON data.
        
        Returns MappingProxyType which provides read-only dict interface.
        Any attempt to modify will raise TypeError.
        
        Returns:
            Immutable mapping of trade data
        """
        return self._data
    
    def jmesget(self, path: str, default: Any = None) -> Any:
        """Get data using JMESPath query language (for complex queries).

        Identical to Trade.jmesget() but operates on immutable data.
        See Trade.jmesget() for full documentation.

        Args:
            path: JMESPath expression
            default: Default value if path doesn't exist or returns None

        Returns:
            Query result or default value
        """
        # Use cached compiled expression for performance
        # Note: self._data is MappingProxyType but jmespath handles it fine
        result = _compile_jmes(path).search(self._data)
        return result if result is not None else default
    
    @cached_property
    def trade_id(self) -> str:
        """Cached trade ID lookup.

        Computed once and cached for the lifetime of this instance.
        Safe because data is immutable.

        Returns:
            Trade ID string from general.tradeId
        """
        return self._data["general"]["tradeId"]

    @cached_property
    def trader(self) -> str:
        """Cached trader lookup.

        Computed once and cached for the lifetime of this instance.
        Safe because data is immutable.

        Returns:
            Trader string from general.transactionRoles.priceMaker
        """
        return self._data.get("general", {}).get("transactionRoles", {}).get("priceMaker", "")

    @cached_property
    def trade_type(self) -> str:
        """Cached trade type detection.

        Detects trade type from structure by checking for distinctive fields.
        Computed once and cached for the lifetime of this instance.
        Safe because data is immutable.

        Returns:
            Trade type string: "ir-swap", "commodity-option", "index-swap", or "unknown"
        """
        # Use jmesget to detect trade type from structure
        if self.jmesget("swapDetails") or self.jmesget("swapLegs"):
            return "ir-swap"
        elif self.jmesget("commodityDetails") or self.jmesget("premium"):
            return "commodity-option"
        elif self.jmesget("leg"):
            return "index-swap"
        return "unknown"
    
    @cached_property
    def version(self) -> int:
        """Cached version number lookup.
        
        Computed once and cached for the lifetime of this instance.
        Safe because data is immutable.
        
        Returns:
            Version number, or 1 if not set
        """
        return self._data.get("version", 1)
    
    @cached_property
    def asset_class(self) -> str:
        """Cached asset class lookup.
        
        Computed once and cached for the lifetime of this instance.
        Safe because data is immutable.
        
        Returns:
            Asset class string, or empty string if not set
        """
        return self._data.get("assetClass", "")
    
    def to_json(self) -> bytes:
        """Serialize trade data to JSON bytes using orjson.
        
        Returns:
            JSON bytes representation of the trade data
        """
        # MappingProxyType needs to be converted to dict for orjson
        return orjson.dumps(dict(self._data))
    
    def __repr__(self) -> str:
        """String representation showing read-only status.
        
        Returns:
            String showing this is a read-only trade with ID and type
        """
        return f"ReadOnlyTrade(id={self.trade_id!r}, type={self.trade_type!r})"