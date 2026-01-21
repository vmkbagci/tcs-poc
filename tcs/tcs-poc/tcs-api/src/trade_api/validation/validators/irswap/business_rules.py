"""IR Swap business rules validator."""

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from ..base import Validator


class IRSwapBusinessRuleValidator(Validator):
    """Validates IR Swap specific business rules.

    MINIMAL - no business rules for now, just placeholder.
    """

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        errors = []
        warnings = []

        # MINIMAL: No business rules yet - just structural checks for now
        # Will add date ordering, notional validation, etc. later

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)