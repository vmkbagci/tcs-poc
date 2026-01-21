# AUTO-GENERATED from specs/validators/core/structural.md
# To update this validator, edit the markdown specification and regenerate

"""Core structural validator for all trades."""

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from ..base import Validator


class CoreStructuralValidator(Validator):
    """Validates that core fields required for ALL trade types are present and valid.

    These are the minimal essential fields that every trade must have, regardless
    of trade type (ir-swap, commodity-option, index-swap, etc.).

    Applies to: All trade types
    """

    # Minimal core required fields
    REQUIRED_FIELDS = [
        "general.tradeId",
        "general.transactionRoles.priceMaker",
        "common.book",
        "common.tradeDate",
        "common.counterparty",
        "common.inputDate"
    ]

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        """Check core required fields exist and are non-empty.

        Special cases:
        - general.tradeId can be empty string for presave payloads (backend generates the ID)
        - general.transactionRoles.priceMaker can be empty string for presave payloads

        Returns ValidationResult with errors for any missing or empty required fields.
        """
        errors = []
        warnings = []

        for field_path in self.REQUIRED_FIELDS:
            # Use jmesget to check field existence
            value = trade.jmesget(field_path)

            if value is None:
                # Field doesn't exist in the trade data
                errors.append(f"Required field missing: {field_path}")
            elif isinstance(value, str) and value == "":
                # Field exists but is empty string
                # Special cases: tradeId and priceMaker can be empty for presave payloads
                if field_path in ["general.tradeId", "general.transactionRoles.priceMaker"]:
                    continue  # Allow empty for presave payloads
                errors.append(f"Required field empty: {field_path}")

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)