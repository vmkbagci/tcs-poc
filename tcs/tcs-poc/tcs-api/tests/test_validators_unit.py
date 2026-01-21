"""Unit tests for individual validators.

This module tests each validator in isolation to ensure proper validation logic.
Tests cover success cases, error paths, and edge cases for all validators.
"""

import pytest
from datetime import datetime, timedelta

from trade_api.models.trade import Trade, ReadOnlyTrade
from trade_api.validation.validators import (
    CoreStructuralValidator,
    CoreBusinessRuleValidator,
    IRSwapStructuralValidator,
    IRSwapBusinessRuleValidator,
    CommodityOptionStructuralValidator,
    CommodityOptionBusinessRuleValidator,
    IndexSwapStructuralValidator,
    IndexSwapBusinessRuleValidator
)


# ========== CORE VALIDATORS ==========

class TestCoreStructuralValidator:
    """Test CoreStructuralValidator in isolation."""

    def test_valid_core_fields(self):
        """Test validation passes with all required core fields present."""
        trade_data = {
            "general": {
                "tradeId": "TRADE-001",
                "transactionRoles": {
                    "priceMaker": "John Doe"
                }
            },
            "common": {
                "book": "BOOK-001",
                "tradeDate": "2026-01-15",
                "counterparty": "CP-001",
                "inputDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_missing_trade_id(self):
        """Test validation fails when tradeId is missing."""
        trade_data = {
            "general": {},
            "common": {
                "book": "BOOK-001",
                "tradeDate": "2026-01-15",
                "counterparty": "CP-001",
                "inputDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("general.tradeId" in error for error in result.errors)

    def test_empty_trade_id_allowed(self):
        """Test validation passes when tradeId is empty (backend generates it)."""
        trade_data = {
            "general": {
                "tradeId": "",
                "transactionRoles": {
                    "priceMaker": "John Doe"
                }
            },
            "common": {
                "book": "BOOK-001",
                "tradeDate": "2026-01-15",
                "counterparty": "CP-001",
                "inputDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        # Empty tradeId should be allowed for presave payloads
        assert result.success is True
        assert len(result.errors) == 0

    def test_missing_book(self):
        """Test validation fails when book is missing."""
        trade_data = {
            "general": {
                "tradeId": "TRADE-001"
            },
            "common": {
                "tradeDate": "2026-01-15",
                "counterparty": "CP-001",
                "inputDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("common.book" in error for error in result.errors)

    def test_missing_trade_date(self):
        """Test validation fails when tradeDate is missing."""
        trade_data = {
            "general": {
                "tradeId": "TRADE-001"
            },
            "common": {
                "book": "BOOK-001",
                "counterparty": "CP-001",
                "inputDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("common.tradeDate" in error for error in result.errors)

    def test_missing_counterparty(self):
        """Test validation fails when counterparty is missing."""
        trade_data = {
            "general": {
                "tradeId": "TRADE-001"
            },
            "common": {
                "book": "BOOK-001",
                "tradeDate": "2026-01-15",
                "inputDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("common.counterparty" in error for error in result.errors)

    def test_missing_input_date(self):
        """Test validation fails when inputDate is missing."""
        trade_data = {
            "general": {
                "tradeId": "TRADE-001"
            },
            "common": {
                "book": "BOOK-001",
                "tradeDate": "2026-01-15",
                "counterparty": "CP-001"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("common.inputDate" in error for error in result.errors)

    def test_multiple_missing_fields(self):
        """Test validation reports all missing required fields."""
        trade_data = {
            "general": {},
            "common": {}
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert len(result.errors) == 6  # All 6 required fields missing


class TestCoreBusinessRuleValidator:
    """Test CoreBusinessRuleValidator in isolation."""

    def test_valid_date_format(self):
        """Test validation passes with valid date format."""
        trade_data = {
            "common": {
                "tradeDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreBusinessRuleValidator()

        result = validator.validate(readonly_trade)

        assert result.success is True
        assert len(result.errors) == 0

    def test_invalid_date_format(self):
        """Test validation fails with invalid date format."""
        trade_data = {
            "common": {
                "tradeDate": "15-01-2026"  # Wrong format
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreBusinessRuleValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("Invalid tradeDate format" in error for error in result.errors)

    def test_invalid_date_value(self):
        """Test validation fails with invalid date value."""
        trade_data = {
            "common": {
                "tradeDate": "2026-13-45"  # Invalid month and day
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreBusinessRuleValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("Invalid tradeDate format" in error for error in result.errors)

    def test_missing_trade_date(self):
        """Test validation passes when tradeDate is missing (structural validator handles this)."""
        trade_data = {
            "common": {}
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreBusinessRuleValidator()

        result = validator.validate(readonly_trade)

        # Business rule validator should not fail if field is missing
        # That's the structural validator's job
        assert result.success is True


# ========== IR SWAP VALIDATORS ==========

class TestIRSwapStructuralValidator:
    """Test IRSwapStructuralValidator in isolation."""

    def test_valid_ir_swap_structure(self):
        """Test validation passes with valid IR swap structure."""
        trade_data = {
            "swapDetails": {
                "underlying": "USD",
                "swapType": "irsOis"
            },
            "swapLegs": [
                {
                    "direction": "pay",
                    "currency": "USD"
                },
                {
                    "direction": "receive",
                    "currency": "USD"
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is True
        assert len(result.errors) == 0

    def test_missing_swap_details(self):
        """Test validation fails when swapDetails is missing."""
        trade_data = {
            "swapLegs": [
                {
                    "direction": "pay",
                    "currency": "USD"
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("swapDetails" in error for error in result.errors)

    def test_missing_swap_legs(self):
        """Test validation fails when swapLegs is missing."""
        trade_data = {
            "swapDetails": {
                "underlying": "USD"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("swapLegs" in error for error in result.errors)

    def test_empty_swap_legs_array(self):
        """Test validation fails when swapLegs array is empty."""
        trade_data = {
            "swapDetails": {
                "underlying": "USD"
            },
            "swapLegs": []
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("at least one leg" in error for error in result.errors)

    def test_leg_missing_direction(self):
        """Test validation fails when leg is missing direction."""
        trade_data = {
            "swapDetails": {
                "underlying": "USD"
            },
            "swapLegs": [
                {
                    "currency": "USD"
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("swapLegs[0]" in error and "direction" in error for error in result.errors)

    def test_leg_missing_currency(self):
        """Test validation fails when leg is missing currency."""
        trade_data = {
            "swapDetails": {
                "underlying": "USD"
            },
            "swapLegs": [
                {
                    "direction": "pay"
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("swapLegs[0]" in error and "currency" in error for error in result.errors)

    def test_multiple_legs_validation(self):
        """Test validation checks all legs."""
        trade_data = {
            "swapDetails": {
                "underlying": "USD"
            },
            "swapLegs": [
                {
                    "direction": "pay",
                    "currency": "USD"
                },
                {
                    "direction": "receive"
                    # Missing currency on second leg
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("swapLegs[1]" in error and "currency" in error for error in result.errors)


class TestIRSwapBusinessRuleValidator:
    """Test IRSwapBusinessRuleValidator in isolation."""

    def test_placeholder_passes(self):
        """Test business rule validator currently acts as placeholder."""
        trade_data = {
            "swapDetails": {
                "underlying": "USD"
            },
            "swapLegs": [
                {
                    "direction": "pay",
                    "currency": "USD"
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IRSwapBusinessRuleValidator()

        result = validator.validate(readonly_trade)

        # Currently placeholder, should always pass
        assert result.success is True
        assert len(result.errors) == 0


# ========== COMMODITY OPTION VALIDATORS ==========

class TestCommodityOptionStructuralValidator:
    """Test CommodityOptionStructuralValidator in isolation."""

    def test_valid_commodity_option_structure(self):
        """Test validation passes with valid commodity option structure."""
        trade_data = {
            "commodityDetails": {
                "commodity": "Gold",
                "optionType": "Call"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CommodityOptionStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is True
        assert len(result.errors) == 0

    def test_missing_commodity_details(self):
        """Test validation fails when commodityDetails is missing."""
        trade_data = {}
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CommodityOptionStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("commodityDetails" in error for error in result.errors)


class TestCommodityOptionBusinessRuleValidator:
    """Test CommodityOptionBusinessRuleValidator in isolation."""

    def test_placeholder_passes(self):
        """Test business rule validator currently acts as placeholder."""
        trade_data = {
            "commodityDetails": {
                "commodity": "Gold"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CommodityOptionBusinessRuleValidator()

        result = validator.validate(readonly_trade)

        # Currently placeholder, should always pass
        assert result.success is True
        assert len(result.errors) == 0


# ========== INDEX SWAP VALIDATORS ==========

class TestIndexSwapStructuralValidator:
    """Test IndexSwapStructuralValidator in isolation."""

    def test_valid_index_swap_structure(self):
        """Test validation passes with valid index swap structure."""
        trade_data = {
            "leg": {
                "index": "S&P500",
                "notional": 1000000
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IndexSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is True
        assert len(result.errors) == 0

    def test_missing_leg(self):
        """Test validation fails when leg is missing."""
        trade_data = {}
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IndexSwapStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        assert any("leg" in error for error in result.errors)


class TestIndexSwapBusinessRuleValidator:
    """Test IndexSwapBusinessRuleValidator in isolation."""

    def test_placeholder_passes(self):
        """Test business rule validator currently acts as placeholder."""
        trade_data = {
            "leg": {
                "index": "S&P500"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = IndexSwapBusinessRuleValidator()

        result = validator.validate(readonly_trade)

        # Currently placeholder, should always pass
        assert result.success is True
        assert len(result.errors) == 0


# ========== EDGE CASES AND NULL HANDLING ==========

class TestEdgeCases:
    """Test edge cases and null handling across validators."""

    def test_null_values_in_core_fields(self):
        """Test handling of null values in required fields."""
        trade_data = {
            "general": {
                "tradeId": None
            },
            "common": {
                "book": None,
                "tradeDate": None,
                "counterparty": None,
                "inputDate": None
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        # All fields should be reported as missing
        assert len(result.errors) == 5

    def test_whitespace_only_strings(self):
        """Test handling of whitespace-only strings."""
        trade_data = {
            "general": {
                "tradeId": "   "  # Whitespace only
            },
            "common": {
                "book": "BOOK-001",
                "tradeDate": "2026-01-15",
                "counterparty": "CP-001",
                "inputDate": "2026-01-15"
            }
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        # Current implementation checks for empty string, not whitespace
        # This is a potential gap, but testing current behavior
        assert result.success is True

    def test_nested_missing_fields(self):
        """Test handling of completely missing nested objects."""
        trade_data = {}
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        validator = CoreStructuralValidator()

        result = validator.validate(readonly_trade)

        assert result.success is False
        # All required fields should be missing
        assert len(result.errors) == 5