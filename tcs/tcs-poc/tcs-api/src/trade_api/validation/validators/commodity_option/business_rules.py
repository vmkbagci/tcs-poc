"""Commodity Option business rules validator."""

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from ..base import Validator


class CommodityOptionBusinessRuleValidator(Validator):
    """Validates Commodity Option business rules.

    MINIMAL - placeholder for now.
    """

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        errors = []
        warnings = []
        # MINIMAL: No business rules yet
        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)