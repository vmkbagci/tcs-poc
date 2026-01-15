"""Trade template factory with hierarchical component inheritance."""

import orjson
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List, Optional
from trade_api.models.assembler import TradeAssembler


class TradeTemplateFactory:
    """Factory for creating TradeAssemblers with hierarchical template inheritance.
    
    This factory implements a component-based template system where trade structures
    are assembled from reusable JSON components organized in a hierarchy:
    
    base → type → subtype → market → leg-specific
    
    Key features:
    - Hierarchical inheritance (child components override parent)
    - Schema versioning (v1, v2, etc.) independent from trade version
    - Component caching for performance
    - Extensible (add new types by adding JSON files)
    - No code changes needed for new trade types
    
    Template Schema Version vs Trade Version:
    - Template schema version: Format/structure of templates (v1, v2, etc.)
    - Trade version: Business version of specific trade instance (1, 2, 3, etc.)
    - These are completely independent concepts
    
    Directory structure:
        templates/
        └── v1/                          # Schema version
            ├── base/                    # Universal components
            ├── swap-types/              # Trade type hierarchies
            │   └── irs/                 # Interest Rate Swaps
            │       ├── irs-base.json
            │       ├── irs-leg-base.json
            │       └── vanilla/         # Vanilla IRS subtype
            ├── leg-types/               # Leg-specific components
            └── conventions/             # Market conventions
    
    Example usage:
        factory = TradeTemplateFactory(template_dir="templates", schema_version="v1")
        
        assembler = factory.create_assembler(
            trade_type="irs",
            subtype="vanilla",
            currency="EUR",
            leg_configs=[
                {"type": "fixed", "legType": "Pay"},
                {"type": "floating-ibor", "legType": "Receive"}
            ]
        )
        
        trade_dict = assembler.assemble()
    """
    
    def __init__(self, template_dir: str = "templates", schema_version: str = "v1"):
        """Initialize factory with template directory and schema version.
        
        Args:
            template_dir: Root directory containing template files
            schema_version: Template schema version to use (v1, v2, etc.)
                          This is the template format version, NOT trade version
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
        subtype: str,
        currency: str,
        leg_configs: List[Dict[str, Any]],
        **kwargs
    ) -> TradeAssembler:
        """Create TradeAssembler for specified trade configuration.
        
        Assembles components in hierarchical order:
        1. Base components (universal)
        2. Type hierarchy (e.g., IRS base → Vanilla IRS)
        3. Market conventions (currency-specific)
        4. Legs with inheritance (base → type → subtype → leg-specific)
        
        Args:
            trade_type: Trade type identifier (e.g., "irs", "xccy")
            subtype: Subtype identifier (e.g., "vanilla", "ois", "basis")
            currency: Currency code for market conventions (e.g., "EUR", "USD")
            leg_configs: List of leg configurations, each containing:
                - type: Leg type ("fixed", "floating-ibor", "floating-ois", etc.)
                - legType: "Pay" or "Receive"
                - overrides: Optional dict of field overrides
            **kwargs: Additional parameters for future extensibility
            
        Returns:
            Configured TradeAssembler ready to assemble()
            
        Example:
            assembler = factory.create_assembler(
                trade_type="irs",
                subtype="vanilla",
                currency="EUR",
                leg_configs=[
                    {"type": "fixed", "legType": "Pay"},
                    {"type": "floating-ibor", "legType": "Receive"}
                ]
            )
        """
        components = []
        
        # 1. Load base components (universal to all trades)
        components.extend(self._load_base_components())
        
        # 2. Load type hierarchy (e.g., IRS base → Vanilla IRS)
        components.extend(self._load_type_hierarchy(trade_type, subtype))
        
        # 3. Load market conventions (currency-specific)
        convention_component = self._load_conventions(currency)
        if convention_component:
            components.append(convention_component)
        
        # 4. Build legs with inheritance
        legs_component = self._build_legs_with_inheritance(
            trade_type, subtype, leg_configs
        )
        components.append(legs_component)
        
        # Return assembler with extend strategy for legs
        return TradeAssembler(*components, list_strategy="extend")
    
    def _load_base_components(self) -> List[Dict[str, Any]]:
        """Load universal base components.
        
        Returns:
            List of base component dictionaries
        """
        base_files = [
            "base/trade-base.json",
            "base/general-base.json",
        ]
        
        components = []
        for file_path in base_files:
            component = self._load_component(file_path)
            if component:
                components.append(component)
        
        return components
    
    def _load_type_hierarchy(self, trade_type: str, subtype: str) -> List[Dict[str, Any]]:
        """Load type hierarchy components (base → subtype).
        
        Args:
            trade_type: Trade type identifier (e.g., "irs", "xccy")
            subtype: Subtype identifier (e.g., "vanilla", "ois")
            
        Returns:
            List of type hierarchy components
        """
        components = []
        
        # Load type base (e.g., irs-base.json)
        type_base = self._load_component(f"swap-types/{trade_type}/{trade_type}-base.json")
        if type_base:
            components.append(type_base)
        
        # Load subtype (e.g., vanilla/vanilla-irs.json)
        subtype_file = self._load_component(
            f"swap-types/{trade_type}/{subtype}/{subtype}-{trade_type}.json"
        )
        if subtype_file:
            components.append(subtype_file)
        
        return components
    
    def _load_conventions(self, currency: str) -> Optional[Dict[str, Any]]:
        """Load market conventions for specified currency.
        
        Args:
            currency: Currency code (e.g., "EUR", "USD", "GBP")
            
        Returns:
            Convention component dictionary or None if not found
        """
        return self._load_component(f"conventions/{currency.lower()}-conventions.json")
    
    def _build_legs_with_inheritance(
        self,
        trade_type: str,
        subtype: str,
        leg_configs: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Build legs with proper inheritance chain.
        
        Each leg inherits from:
        1. base/swap-leg-base.json (universal)
        2. swap-types/{type}/{type}-leg-base.json (type-specific)
        3. swap-types/{type}/{subtype}/{subtype}-legs.json (subtype-specific)
        4. leg-types/{leg_type}-leg.json (leg-type-specific)
        
        Args:
            trade_type: Trade type identifier
            subtype: Subtype identifier
            leg_configs: List of leg configurations
            
        Returns:
            Dictionary with "legs" key containing list of assembled legs
        """
        legs = []
        
        for leg_config in leg_configs:
            leg_type = leg_config["type"]  # e.g., "fixed", "floating-ibor"
            
            # Build inheritance chain for this leg
            leg_components = []
            
            # 1. Universal leg base
            base_leg = self._load_component("base/swap-leg-base.json")
            if base_leg:
                leg_components.append(base_leg)
            
            # 2. Type-specific leg base (e.g., irs-leg-base.json)
            type_leg_base = self._load_component(
                f"swap-types/{trade_type}/{trade_type}-leg-base.json"
            )
            if type_leg_base:
                leg_components.append(type_leg_base)
            
            # 3. Subtype-specific leg fields (e.g., vanilla-irs-legs.json)
            subtype_leg = self._load_component(
                f"swap-types/{trade_type}/{subtype}/{subtype}-{trade_type}-legs.json"
            )
            if subtype_leg:
                leg_components.append(subtype_leg)
            
            # 4. Leg-type-specific fields (e.g., fixed-leg.json)
            leg_type_component = self._load_component(f"leg-types/{leg_type}-leg.json")
            if leg_type_component:
                leg_components.append(leg_type_component)
            
            # Merge leg inheritance chain
            merged_leg = self._merge_components(leg_components)
            
            # Apply instance-specific overrides from config
            for key, value in leg_config.items():
                if key not in ["type", "overrides"]:
                    # Direct config values (e.g., legType: "Pay")
                    merged_leg[key] = value
            
            # Apply explicit overrides if provided
            if "overrides" in leg_config:
                merged_leg.update(leg_config["overrides"])
            
            legs.append(merged_leg)
        
        return {"legs": legs}
    
    def _merge_components(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge list of components using TradeAssembler logic.
        
        Args:
            components: List of component dictionaries to merge
            
        Returns:
            Merged dictionary
        """
        if not components:
            return {}
        
        # Use TradeAssembler for consistent merge logic
        assembler = TradeAssembler(*components)
        return assembler.assemble()
    
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
        swap_types_dir = self.schema_path / "swap-types"
        if not swap_types_dir.exists():
            return []
        
        return [d.name for d in swap_types_dir.iterdir() if d.is_dir()]
    
    def get_available_subtypes(self, trade_type: str) -> List[str]:
        """Get list of available subtypes for a trade type.
        
        Args:
            trade_type: Trade type identifier
            
        Returns:
            List of subtype identifiers
        """
        type_dir = self.schema_path / "swap-types" / trade_type
        if not type_dir.exists():
            return []
        
        # Return subdirectories (subtypes)
        return [d.name for d in type_dir.iterdir() if d.is_dir()]
    
    def get_available_leg_types(self) -> List[str]:
        """Get list of available leg types.
        
        Returns:
            List of leg type identifiers
        """
        leg_types_dir = self.schema_path / "leg-types"
        if not leg_types_dir.exists():
            return []
        
        # Extract leg type from filename (e.g., "fixed-leg.json" → "fixed")
        leg_types = []
        for file_path in leg_types_dir.glob("*-leg.json"):
            leg_type = file_path.stem.replace("-leg", "")
            leg_types.append(leg_type)
        
        return leg_types
    
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
