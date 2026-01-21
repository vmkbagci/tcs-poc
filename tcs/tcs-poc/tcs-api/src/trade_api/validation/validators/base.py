"""Abstract base validator class."""

from abc import ABC, abstractmethod

from trade_api.models.trade import ReadOnlyTrade
from trade_api.validation.result import ValidationResult


class Validator(ABC):
    """Abstract base validator."""

    @abstractmethod
    def validate(self, trade: ReadOnlyTrade) -> ValidationResult:
        """Validate trade and return result."""
        pass