"""ValidationResult dataclass for validation results."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of validation execution."""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    trade_type: Optional[str] = None