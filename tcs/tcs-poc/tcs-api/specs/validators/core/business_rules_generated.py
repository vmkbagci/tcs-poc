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

    Current Scope: Minimal validation - only critical date format validation for now.

    Applies to: All trade types (ir-swap, commodity-option, index-swap, etc.)
    """

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        """Validate universal business rules for all trade types.

        Currently validates:
        - Trade date format (YYYY-MM-DD ISO 8601 format)

        Returns:
            ValidationResult with success=True if no errors found, False otherwise.
            Includes list of errors and warnings.
        """
        errors = []
        warnings = []

        # Validate Trade Date Format
        # Per spec: common.tradeDate must follow ISO 8601 format (YYYY-MM-DD)
        trade_date_value = trade.jmesget("common.tradeDate")

        # Per spec: Skip validation if field is None or missing
        # (structural validator handles missing fields)
        if trade_date_value is not None:
            # Attempt to parse using ISO 8601 date format
            try:
                datetime.strptime(trade_date_value, "%Y-%m-%d")
                # If parsing succeeds, validation passes (no error)
            except ValueError:
                # If parsing fails, record error with actual invalid value
                errors.append(
                    f"Invalid tradeDate format: {trade_date_value}. Expected YYYY-MM-DD"
                )

        # Return validation result
        # Per spec: Success only if no errors found
        return ValidationResult(
            success=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )