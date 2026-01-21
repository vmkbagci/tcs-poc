"""Index Swap structural validator."""

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from ..base import Validator


class IndexSwapStructuralValidator(Validator):
    """Validates Index Swap structure.

    MINIMAL - just check leg exists.
    """

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        errors = []
        warnings = []

        # MINIMAL: Just check leg field exists
        if not trade.jmesget("leg"):
            errors.append("Index Swap missing required field: leg")

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)