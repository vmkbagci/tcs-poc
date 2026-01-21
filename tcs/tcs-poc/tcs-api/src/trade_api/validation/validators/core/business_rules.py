# AUTO-GENERATED from specs/validators/core/business_rules.md
# To update this validator, edit the markdown specification and regenerate

"""Core business rules validator for all trades."""

from datetime import datetime

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from ..base import Validator


class CoreBusinessRuleValidator(Validator):
    """Validates universal business rules that apply to ALL trade types.

    These are fundamental business logic checks that ensure data quality and
    consistency across the entire trading system.

    Current Scope: Minimal validation - only critical date format validation.

    Applies to: All trade types (ir-swap, commodity-option, index-swap, etc.)
    """

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        """Check universal business rules (minimal).

        Currently validates:
        - Trade date format (YYYY-MM-DD ISO 8601 format)

        Returns ValidationResult with errors for any business rule violations.
        """
        errors = []
        warnings = []

        # Validate tradeDate format (YYYY-MM-DD)
        trade_date_str = trade.jmesget("common.tradeDate")
        if trade_date_str:
            # Only validate if field exists (structural validator handles missing fields)
            try:
                datetime.strptime(trade_date_str, "%Y-%m-%d")
            except ValueError:
                errors.append(f"Invalid tradeDate format: {trade_date_str}. Expected YYYY-MM-DD")

        # That's it for now - keep minimal
        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)