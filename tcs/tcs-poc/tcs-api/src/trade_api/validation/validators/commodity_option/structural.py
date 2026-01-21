"""Commodity Option structural validator."""

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from ..base import Validator


class CommodityOptionStructuralValidator(Validator):
    """Validates Commodity Option structure.

    MINIMAL - just check commodityDetails exists.
    """

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        errors = []
        warnings = []

        # MINIMAL: Just check commodityDetails exists
        if not trade.jmesget("commodityDetails"):
            errors.append("Commodity Option missing required field: commodityDetails")

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)