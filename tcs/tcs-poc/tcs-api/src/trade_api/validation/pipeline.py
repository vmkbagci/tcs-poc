"""ValidationPipeline for executing validation stages in compositional order."""

from typing import List

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from trade_api.validation.validators import Validator


class ValidationPipeline:
    """Pipeline for executing validation stages in compositional order."""

    def __init__(self, core_validators: List[Validator], trade_validators: List[Validator], trade_type: str):
        self.core_validators = core_validators      # Validate general.*, common.*
        self.trade_validators = trade_validators    # Validate trade-specific fields
        self.trade_type = trade_type

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        """Execute validators in composition order: core first, then trade-specific."""
        errors = []
        warnings = []

        # Stage 1: Core validation (applies to ALL trades)
        for validator in self.core_validators:
            result = validator.validate(trade)
            errors.extend(result.errors)
            warnings.extend(result.warnings)

        # Stage 2: Trade-specific validation (applies to this trade type)
        for validator in self.trade_validators:
            result = validator.validate(trade)
            errors.extend(result.errors)
            warnings.extend(result.warnings)

        return ValidationResult(
            success=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            trade_type=self.trade_type
        )