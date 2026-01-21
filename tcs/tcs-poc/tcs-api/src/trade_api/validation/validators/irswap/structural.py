"""IR Swap structural validator."""

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult
from ..base import Validator


class IRSwapStructuralValidator(Validator):
    """Validates IR Swap specific structure (swapDetails, swapLegs).

    MINIMAL CHECKS - based on ir-swap-presave-flattened.txt reference.
    Reference: /projects/trade-capture-service/tcs-poc/json-examples/polar/ir-swap-presave-flattened.txt
    """

    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        errors = []
        warnings = []

        # MINIMAL: Check swapDetails exists
        if not trade.jmesget("swapDetails"):
            errors.append("IR Swap missing required field: swapDetails")

        # MINIMAL: Check swapLegs exists and has at least one leg
        legs = trade.jmesget("swapLegs")
        if not legs or len(legs) == 0:
            errors.append("IR Swap must have at least one leg in swapLegs array")
        else:
            # MINIMAL: Each leg must have direction and currency
            for idx, leg in enumerate(legs):
                direction = trade.jmesget(f"swapLegs[{idx}].direction")
                currency = trade.jmesget(f"swapLegs[{idx}].currency")

                if not direction:
                    errors.append(f"swapLegs[{idx}] missing required field: direction")
                if not currency:
                    errors.append(f"swapLegs[{idx}] missing required field: currency")

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)