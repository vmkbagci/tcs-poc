"""Result DTOs for service layer operations."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class TradeCreationResult:
    """Result of creating a new trade from a template."""
    success: bool
    trade_data: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    errors: List[str] = field(default_factory=list)


@dataclass
class TradeValidationResult:
    """Result of validating a trade."""
    success: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


@dataclass
class TradeSaveResult:
    """Result of saving a trade."""
    success: bool
    trade_data: Optional[Dict[str, Any]]
    warnings: List[str]
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)