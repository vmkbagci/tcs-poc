"""ValidationFactory for creating validation pipelines using registry pattern."""

from typing import Dict, List, Optional, Type

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.pipeline import ValidationPipeline
from trade_api.validation.validators import (
    Validator,
    CoreStructuralValidator,
    CoreBusinessRuleValidator,
    IRSwapStructuralValidator,
    IRSwapBusinessRuleValidator,
    CommodityOptionStructuralValidator,
    CommodityOptionBusinessRuleValidator,
    IndexSwapStructuralValidator,
    IndexSwapBusinessRuleValidator,
)


class ValidationFactory:
    """Factory for creating validation pipelines using registry pattern."""

    def __init__(self):
        """Initialize factory and build validator registry."""
        self._validator_registry: Optional[Dict[str, List[Type[Validator]]]] = None
        self._core_validator_classes: Optional[List[Type[Validator]]] = None

    def _ensure_registry_initialized(self) -> None:
        """Build validator registry on first call (lazy initialization)."""
        if self._validator_registry is not None:
            return  # Already initialized

        # Build CORE validator registry (applies to ALL trades)
        self._core_validator_classes = [
            CoreStructuralValidator,
            CoreBusinessRuleValidator
        ]

        # Build TRADE-SPECIFIC validator registry
        self._validator_registry = {
            "ir-swap": [
                IRSwapStructuralValidator,
                IRSwapBusinessRuleValidator
            ],
            "commodity-option": [
                CommodityOptionStructuralValidator,
                CommodityOptionBusinessRuleValidator
            ],
            "index-swap": [
                IndexSwapStructuralValidator,
                IndexSwapBusinessRuleValidator
            ]
        }

    def create_pipeline(self, trade: ReadOnlyTrade) -> ValidationPipeline:
        """Create validation pipeline with core + trade-specific validators."""
        # Ensure registry is initialized
        self._ensure_registry_initialized()

        # Detect trade type from structure
        trade_type = self._detect_trade_type(trade)

        # Create CORE validators (apply to ALL trades)
        core_validators = self._create_core_validators()

        # Create TRADE-SPECIFIC validators from registry
        trade_validators = self._create_trade_validators(trade_type)

        # Return pipeline with compositional order
        return ValidationPipeline(core_validators, trade_validators, trade_type)

    def _create_core_validators(self) -> List[Validator]:
        """Instantiate core validators from registry."""
        return [validator_cls() for validator_cls in self._core_validator_classes]

    def _create_trade_validators(self, trade_type: str) -> List[Validator]:
        """Instantiate trade-specific validators from registry."""
        validator_classes = self._validator_registry.get(trade_type, [])
        if not validator_classes:
            raise ValueError(f"No validators registered for trade type: {trade_type}")
        return [validator_cls() for validator_cls in validator_classes]

    def _detect_trade_type(self, trade: ReadOnlyTrade) -> str:
        """Detect trade type using jmesget queries."""
        # Check for distinctive fields using jmesget
        if trade.jmesget("swapDetails") or trade.jmesget("swapLegs"):
            return "ir-swap"
        elif trade.jmesget("commodityDetails") or trade.jmesget("premium"):
            return "commodity-option"
        elif trade.jmesget("leg"):
            return "index-swap"
        raise ValueError("Unable to detect trade type")

    def get_supported_trade_types(self) -> List[str]:
        """Get list of supported trade types from registry."""
        self._ensure_registry_initialized()
        return list(self._validator_registry.keys())