"""Trade assembler for composing trade dictionaries from components."""

from typing import Any, Dict, List, Callable, Optional, Literal
from copy import deepcopy


class TradeAssembler:
    """Compositional factory for assembling trade dictionaries from components.
    
    This class implements the Builder pattern for trade construction, allowing
    flexible composition of trade data from multiple component dictionaries.
    
    Design principles:
    - Immutable assembly (returns new dict, doesn't modify inputs)
    - Configurable merge strategies for lists
    - Optional validation hooks
    - Type-safe with proper hints
    
    Use cases:
    - Template generation from reusable components
    - Pipeline-based trade construction
    - Trade type variations with shared components
    
    Example:
        base = {"tradeType": "InterestRateSwap", "assetClass": "Rates"}
        legs = {"legs": [{"legId": "FIXED"}, {"legId": "FLOAT"}]}
        specific = {"specific": {"rateFamily": "VanillaIRS"}}
        
        assembler = TradeAssembler(base, legs, specific)
        trade = assembler.assemble()
    """
    
    def __init__(
        self,
        *components: Dict[str, Any],
        list_strategy: Literal["replace", "append", "extend"] = "replace",
        validator: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """Initialize assembler with components and merge configuration.
        
        Args:
            *components: Variable number of component dictionaries to merge.
                        Later components override earlier ones for conflicting keys.
            list_strategy: How to handle list merging:
                - "replace": Later list replaces earlier (default)
                - "append": Later list appended as single item to earlier
                - "extend": Later list items extended into earlier list
            validator: Optional validation function called after assembly.
                      Should raise exception if validation fails.
        
        Example:
            # Replace strategy (default)
            assembler = TradeAssembler(
                {"legs": [{"id": 1}]},
                {"legs": [{"id": 2}]}
            )
            # Result: {"legs": [{"id": 2}]}
            
            # Extend strategy
            assembler = TradeAssembler(
                {"legs": [{"id": 1}]},
                {"legs": [{"id": 2}]},
                list_strategy="extend"
            )
            # Result: {"legs": [{"id": 1}, {"id": 2}]}
        """
        self._components = components
        self._list_strategy = list_strategy
        self._validator = validator
    
    def assemble(self) -> Dict[str, Any]:
        """Assemble all components into a single trade dictionary.
        
        Creates a new dictionary by deep-merging all components in order.
        Does not modify input components (immutable operation).
        
        Returns:
            New dictionary containing merged trade data
            
        Raises:
            Exception: If validator is provided and validation fails
        """
        # Start with empty dict (immutable - don't modify inputs)
        trade: Dict[str, Any] = {}
        
        # Deep merge each component in order
        for component in self._components:
            self._deep_merge(trade, component)
        
        # Run optional validation
        if self._validator:
            self._validator(trade)
        
        return trade
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merge source dictionary into target.
        
        Handles nested dictionaries and lists according to configured strategy.
        Modifies target in place.
        
        Args:
            target: Dictionary to merge into (modified in place)
            source: Dictionary to merge from (not modified)
        """
        for key, source_value in source.items():
            # Key doesn't exist in target - simple assignment
            if key not in target:
                # Deep copy to avoid shared references
                target[key] = deepcopy(source_value)
                continue
            
            target_value = target[key]
            
            # Both are dicts - recursive merge
            if isinstance(target_value, dict) and isinstance(source_value, dict):
                self._deep_merge(target_value, source_value)
            
            # Both are lists - apply list strategy
            elif isinstance(target_value, list) and isinstance(source_value, list):
                target[key] = self._merge_lists(target_value, source_value)
            
            # Different types or non-mergeable - source overwrites target
            else:
                target[key] = deepcopy(source_value)
    
    def _merge_lists(self, target_list: List[Any], source_list: List[Any]) -> List[Any]:
        """Merge two lists according to configured strategy.
        
        Args:
            target_list: Existing list
            source_list: New list to merge
            
        Returns:
            Merged list according to strategy
        """
        if self._list_strategy == "replace":
            # Source replaces target completely
            return deepcopy(source_list)
        
        elif self._list_strategy == "append":
            # Source list appended as single item
            result = deepcopy(target_list)
            result.append(deepcopy(source_list))
            return result
        
        elif self._list_strategy == "extend":
            # Source list items extended into target
            result = deepcopy(target_list)
            result.extend(deepcopy(source_list))
            return result
        
        else:
            # Fallback to replace
            return deepcopy(source_list)
    
    def with_validator(self, validator: Callable[[Dict[str, Any]], None]) -> 'TradeAssembler':
        """Create new assembler with validation function.
        
        Allows fluent API for adding validation:
            assembler.with_validator(my_validator).assemble()
        
        Args:
            validator: Validation function to call after assembly
            
        Returns:
            New TradeAssembler instance with validator
        """
        return TradeAssembler(
            *self._components,
            list_strategy=self._list_strategy,
            validator=validator
        )
    
    def with_list_strategy(
        self,
        strategy: Literal["replace", "append", "extend"]
    ) -> 'TradeAssembler':
        """Create new assembler with different list merge strategy.
        
        Allows fluent API for changing strategy:
            assembler.with_list_strategy("extend").assemble()
        
        Args:
            strategy: New list merge strategy
            
        Returns:
            New TradeAssembler instance with new strategy
        """
        return TradeAssembler(
            *self._components,
            list_strategy=strategy,
            validator=self._validator
        )
    
    def add_components(self, *components: Dict[str, Any]) -> 'TradeAssembler':
        """Create new assembler with additional components.
        
        Allows fluent API for adding components:
            assembler.add_components(extra1, extra2).assemble()
        
        Args:
            *components: Additional component dictionaries
            
        Returns:
            New TradeAssembler instance with all components
        """
        return TradeAssembler(
            *self._components,
            *components,
            list_strategy=self._list_strategy,
            validator=self._validator
        )
    
    def __repr__(self) -> str:
        """String representation showing component count and strategy.
        
        Returns:
            String describing the assembler configuration
        """
        return (
            f"TradeAssembler("
            f"components={len(self._components)}, "
            f"strategy={self._list_strategy!r}, "
            f"validator={'set' if self._validator else 'none'})"
        )