"""Trade template factory with simple composition."""

import orjson
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List, Optional
from trade_api.models.assembler import TradeAssembler


class TradeTemplateFactory:
    """Factory for creating TradeAssemblers with simple template composition.
    
    This factory implements a simple component-based template system where trade
    structures are assembled by merging JSON files in a specific order:
    
    1. Base layer: core/general.json + core/common.json (shared by ALL trades)
    2. Trade-specific overrides: trade-types/{type}/general.json + trade-types/{type}/common.json
    3. Trade-specific blocks: trade-types/{type}/*.json (economic blocks)
    
    All template files start from root {} and show the full path to where their
    content belongs. The assembler simply merges them together using deep merge.
    
    Key features:
    - Simple composition (no complex inheritance)
    - Schema versioning (v1, v2, etc.)
    - Component caching for performance
    - Extensible (add new types by adding JSON files)
    - No code changes needed for new trade types
    
    Directory structure:
        templates/
        └── v1/                          # Schema version
            ├── core/                    # Base layer (shared by ALL trades)
            │   ├── general.json         # { "general": {...} }
            │   └── common.json          # { "common": {...} }
            └── trade-types/             # Trade-specific layers
                ├── ir-swap/
                │   ├── general.json     # { "general": {...} } - IR-specific additions
                │   ├── swap-details.json # { "swapDetails": {...} }
                │   ├── swap-leg-fixed.json # { "swapLegs": [{...}] }
                │   └── swap-leg-floating-ois.json # { "swapLegs": [{...}] }
                ├── commodity-option/
                │   ├── general.json
                │   ├── commodity-details.json
                │   └── ...
                └── index-swap/
                    ├── general.json
                    └── leg.json
    
    Example usage:
        factory = TradeTemplateFactory(template_dir="templates", schema_version="v1")
        
        # Create IR Swap
        assembler = factory.create_assembler(trade_type="ir-swap")
        trade_dict = assembler.assemble()
        
        # Create Commodity Option
        assembler = factory.create_assembler(trade_type="commodity-option")
        trade_dict = assembler.assemble()
    """
    
    def __init__(self, template_dir: str = "templates", schema_version: str = "v1"):
        """Initialize factory with template directory and schema version.
        
        Args:
            template_dir: Root directory containing template files
            schema_version: Template schema version to use (v1, v2, etc.)
        """
        self.template_dir = Path(template_dir)
        self.schema_version = schema_version
        self.schema_path = self.template_dir / schema_version
        
        if not self.schema_path.exists():
            raise ValueError(
                f"Template schema version '{schema_version}' not found at {self.schema_path}"
            )
    
    def create_assembler(
        self,
        trade_type: str,
        **kwargs
    ) -> TradeAssembler:
        """Create TradeAssembler for specified trade type.
        
        Loads template files in composition order:
        1. core/general.json
        2. core/common.json
        3. trade-types/{type}/general.json (if exists)
        4. trade-types/{type}/common.json (if exists)
        5. trade-types/{type}/*.json (all other files in trade type directory)
        
        Args:
            trade_type: Trade type identifier ("ir-swap", "commodity-option", "index-swap")
            **kwargs: Reserved for future use
            
        Returns:
            Configured TradeAssembler ready to assemble()
            
        Example:
            assembler = factory.create_assembler(trade_type="ir-swap")
            trade_dict = assembler.assemble()
        """
        components = []
        
        # 1. Load base core components (shared by ALL trades)
        components.extend(self._load_core_components())
        
        # 2. Load trade-specific components in order
        components.extend(self._load_trade_components(trade_type))
        
        # Return assembler with extend strategy for arrays
        return TradeAssembler(*components, list_strategy="extend")
    
    def _load_core_components(self) -> List[Dict[str, Any]]:
        """Load base core components shared by all trades.
        
        Returns:
            List containing general and common base components
        """
        core_files = [
            "core/general.json",
            "core/common.json",
        ]
        
        components = []
        for file_path in core_files:
            component = self._load_component(file_path)
            if component:
                components.append(component)
            else:
                raise ValueError(f"Required core component not found: {file_path}")
        
        return components
    
    def _load_trade_components(self, trade_type: str) -> List[Dict[str, Any]]:
        """Load trade-specific components in composition order.
        
        Order:
        1. trade-types/{type}/general.json (if exists) - trade-specific general additions
        2. trade-types/{type}/common.json (if exists) - trade-specific common additions
        3. All other .json files in trade-types/{type}/ directory (sorted alphabetically)
        
        Args:
            trade_type: Trade type identifier
            
        Returns:
            List of trade-specific components
        """
        components = []
        trade_dir = self.schema_path / "trade-types" / trade_type
        
        if not trade_dir.exists():
            raise ValueError(f"Trade type '{trade_type}' not found at {trade_dir}")
        
        # 1. Load trade-specific general.json (if exists)
        general_override = self._load_component(f"trade-types/{trade_type}/general.json")
        if general_override:
            components.append(general_override)
        
        # 2. Load trade-specific common.json (if exists)
        common_override = self._load_component(f"trade-types/{trade_type}/common.json")
        if common_override:
            components.append(common_override)
        
        # 3. Load all other JSON files (excluding general.json and common.json)
        other_files = sorted([
            f for f in trade_dir.glob("*.json")
            if f.name not in ["general.json", "common.json"]
        ])
        
        for file_path in other_files:
            relative_path = file_path.relative_to(self.schema_path)
            component = self._load_component(str(relative_path))
            if component:
                components.append(component)
        
        return components
    
    @lru_cache(maxsize=256)
    def _load_component(self, relative_path: str) -> Optional[Dict[str, Any]]:
        """Load and cache a component file.
        
        Uses LRU cache to avoid repeated file I/O for the same components.
        Cache size of 256 should handle most template sets.
        
        Args:
            relative_path: Path relative to schema directory
            
        Returns:
            Component dictionary or None if file doesn't exist
        """
        file_path = self.schema_path / relative_path
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                return orjson.loads(f.read())
        except Exception as e:
            raise ValueError(f"Error loading component {relative_path}: {e}")
    
    def clear_cache(self):
        """Clear the component cache.
        
        Useful for testing or when templates are modified at runtime.
        """
        self._load_component.cache_clear()
    
    def get_available_types(self) -> List[str]:
        """Get list of available trade types.
        
        Returns:
            List of trade type identifiers
        """
        trade_types_dir = self.schema_path / "trade-types"
        if not trade_types_dir.exists():
            return []
        
        return [d.name for d in trade_types_dir.iterdir() if d.is_dir()]
    
    def __repr__(self) -> str:
        """String representation showing configuration.
        
        Returns:
            String describing the factory configuration
        """
        return (
            f"TradeTemplateFactory("
            f"schema_version={self.schema_version!r}, "
            f"template_dir={str(self.template_dir)!r})"
        )