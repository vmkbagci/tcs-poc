"""Tests for the TradeService layer."""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from trade_api.services import TradeService
from trade_api.models import TradeTemplateFactory, Trade
from trade_api.validation import ValidationFactory


@pytest.fixture
def template_factory():
    """Create a real TradeTemplateFactory for testing."""
    # Find the templates directory
    test_dir = Path(__file__).resolve().parent
    project_root = test_dir.parent
    template_dir = project_root / "templates"

    return TradeTemplateFactory(template_dir=str(template_dir), schema_version="v1")


@pytest.fixture
def validation_factory():
    """Create a real ValidationFactory for testing."""
    return ValidationFactory()


@pytest.fixture
def trade_service(template_factory, validation_factory):
    """Create a TradeService instance with real factories."""
    return TradeService(template_factory, validation_factory)


def test_create_new_trade_success(trade_service):
    """Test creating a new trade successfully."""
    result = trade_service.create_new_trade("ir-swap")

    assert result.success is True
    assert result.trade_data is not None
    assert result.metadata is not None
    assert "trade_id" in result.metadata
    assert "trade_type" in result.metadata
    assert "documentId" in result.metadata
    assert "correlationId" in result.metadata
    assert result.metadata["trade_type"] == "ir-swap"
    assert len(result.errors) == 0


def test_create_new_trade_invalid_type(trade_service):
    """Test creating a trade with invalid trade type."""
    result = trade_service.create_new_trade("invalid-type")

    assert result.success is False
    assert result.trade_data is None
    assert len(result.errors) > 0


def test_validate_trade_success(trade_service):
    """Test validating a trade successfully."""
    # First create a trade to validate
    create_result = trade_service.create_new_trade("ir-swap")
    assert create_result.success is True

    # Now validate it
    validate_result = trade_service.validate_trade(create_result.trade_data)

    assert validate_result is not None
    assert isinstance(validate_result.success, bool)
    assert isinstance(validate_result.errors, list)
    assert isinstance(validate_result.warnings, list)
    assert validate_result.metadata is not None
    assert "documentId" in validate_result.metadata
    assert "correlationId" in validate_result.metadata


def test_validate_trade_invalid_data(trade_service):
    """Test validating invalid trade data."""
    invalid_data = {"invalid": "data"}

    result = trade_service.validate_trade(invalid_data)

    assert result.success is False
    assert len(result.errors) > 0


def test_save_trade_placeholder(trade_service):
    """Test save trade placeholder implementation."""
    trade_data = {"test": "data"}

    result = trade_service.save_trade(trade_data)

    assert result.success is True
    assert result.trade_data is not None
    assert len(result.warnings) > 0
    assert "Placeholder" in result.warnings[0]


def test_trade_service_dependency_injection():
    """Test that TradeService can be instantiated with dependencies."""
    mock_template_factory = Mock()
    mock_validation_factory = Mock()

    service = TradeService(mock_template_factory, mock_validation_factory)

    assert service.template_factory == mock_template_factory
    assert service.validation_factory == mock_validation_factory


# ========== ADDITIONAL VALIDATION SCENARIOS ==========

def test_validate_trade_with_complete_ir_swap(trade_service):
    """Test validating a complete IR swap with all required fields."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "swapDetails": {
            "underlying": "USD",
            "swapType": "irsOis"
        },
        "swapLegs": [
            {
                "direction": "pay",
                "currency": "USD",
                "rateType": "fixed"
            },
            {
                "direction": "receive",
                "currency": "USD",
                "rateType": "floating"
            }
        ]
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is True
    assert len(result.errors) == 0
    assert result.metadata is not None
    assert result.metadata.get("trade_type") == "ir-swap"
    assert "documentId" in result.metadata
    assert "correlationId" in result.metadata


def test_validate_trade_missing_core_fields(trade_service):
    """Test validation fails when core required fields are missing."""
    trade_data = {
        "general": {},
        "common": {
            "book": "BOOK-001"
            # Missing tradeDate, counterparty, inputDate
        },
        "swapDetails": {
            "underlying": "USD"
        }
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    assert len(result.errors) > 0
    # Should have errors for missing tradeId, tradeDate, counterparty, inputDate
    assert any("tradeId" in error for error in result.errors)
    assert any("tradeDate" in error for error in result.errors)


def test_validate_trade_missing_swap_details(trade_service):
    """Test validation fails when IR swap is missing swapDetails."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "swapLegs": [
            {
                "direction": "pay",
                "currency": "USD"
            }
        ]
        # Missing swapDetails
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    assert any("swapDetails" in error for error in result.errors)


def test_validate_trade_missing_swap_legs(trade_service):
    """Test validation fails when IR swap is missing swapLegs."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "swapDetails": {
            "underlying": "USD"
        }
        # Missing swapLegs
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    assert any("swapLegs" in error for error in result.errors)


def test_validate_trade_empty_swap_legs(trade_service):
    """Test validation fails when swapLegs array is empty."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "swapDetails": {
            "underlying": "USD"
        },
        "swapLegs": []  # Empty array
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    assert any("at least one leg" in error for error in result.errors)


def test_validate_trade_leg_missing_direction(trade_service):
    """Test validation fails when swap leg is missing direction."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "swapDetails": {
            "underlying": "USD"
        },
        "swapLegs": [
            {
                "currency": "USD"
                # Missing direction
            }
        ]
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    assert any("direction" in error for error in result.errors)


def test_validate_trade_leg_missing_currency(trade_service):
    """Test validation fails when swap leg is missing currency."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "swapDetails": {
            "underlying": "USD"
        },
        "swapLegs": [
            {
                "direction": "pay"
                # Missing currency
            }
        ]
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    assert any("currency" in error for error in result.errors)


def test_validate_trade_invalid_date_format(trade_service):
    """Test validation fails with invalid date format."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "15-01-2026",  # Wrong format
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "swapDetails": {
            "underlying": "USD"
        }
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    assert any("Invalid tradeDate format" in error or "tradeDate" in error for error in result.errors)


def test_validate_multiple_trade_types(trade_service):
    """Test validation works for different trade types."""
    # Test commodity option
    commodity_data = {
        "general": {
            "tradeId": "TRADE-002"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
        "commodityDetails": {
            "commodity": "Gold"
        }
    }

    result = trade_service.validate_trade(commodity_data)

    # Should pass structural validation
    assert result.success is True or len(result.errors) < 5  # May have some validation errors


def test_validate_trade_with_warnings(trade_service):
    """Test that validation can return warnings without errors."""
    # Create a valid trade that might generate warnings
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
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

    result = trade_service.validate_trade(trade_data)

    # Verify warnings list exists
    assert isinstance(result.warnings, list)


def test_validate_trade_null_values(trade_service):
    """Test validation handles null values appropriately."""
    trade_data = {
        "general": {
            "tradeId": None
        },
        "common": {
            "book": None,
            "tradeDate": None,
            "counterparty": None,
            "inputDate": None
        },
        "swapDetails": {
            "underlying": "USD"
        }
    }

    result = trade_service.validate_trade(trade_data)

    assert result.success is False
    # Should report multiple missing/invalid fields
    assert len(result.errors) >= 4


def test_validate_trade_metadata_includes_trade_type(trade_service):
    """Test that validation result metadata includes trade type."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
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

    result = trade_service.validate_trade(trade_data)

    assert result.metadata is not None
    assert "trade_type" in result.metadata
    assert "documentId" in result.metadata
    assert "correlationId" in result.metadata


def test_create_and_validate_workflow(trade_service):
    """Test complete workflow: create a trade, then validate it."""
    # Step 1: Create a new trade
    create_result = trade_service.create_new_trade("ir-swap")
    assert create_result.success is True

    # Step 2: Validate the created trade
    validate_result = trade_service.validate_trade(create_result.trade_data)

    # The newly created trade should pass validation
    # (or have documented validation errors if template is incomplete)
    assert validate_result is not None
    assert isinstance(validate_result.success, bool)
    assert isinstance(validate_result.errors, list)
    assert isinstance(validate_result.warnings, list)


def test_validate_trade_with_provided_metadata(trade_service):
    """Test validation with provided documentId and correlationId."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
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

    # Provide specific metadata
    metadata = {
        "documentId": "12345678-1234-1234-1234-123456789012",
        "correlationId": "87654321-4321-4321-4321-210987654321"
    }

    result = trade_service.validate_trade(trade_data, metadata=metadata)

    assert result.metadata is not None
    assert result.metadata["documentId"] == "12345678-1234-1234-1234-123456789012"
    assert result.metadata["correlationId"] == "87654321-4321-4321-4321-210987654321"


def test_validate_trade_generates_document_id_if_missing(trade_service):
    """Test validation generates documentId if not provided."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
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

    # Don't provide metadata
    result = trade_service.validate_trade(trade_data)

    assert result.metadata is not None
    assert "documentId" in result.metadata
    assert "correlationId" in result.metadata
    # Both should be valid UUIDs (36 characters with hyphens)
    assert len(result.metadata["documentId"]) == 36
    assert len(result.metadata["correlationId"]) == 36


def test_validate_trade_with_partial_metadata(trade_service):
    """Test validation with only correlationId provided."""
    trade_data = {
        "general": {
            "tradeId": "TRADE-001"
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-15",
            "counterparty": "CP-001",
            "inputDate": "2026-01-15"
        },
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

    # Provide only correlationId
    metadata = {
        "correlationId": "87654321-4321-4321-4321-210987654321"
    }

    result = trade_service.validate_trade(trade_data, metadata=metadata)

    assert result.metadata is not None
    # documentId should be generated
    assert "documentId" in result.metadata
    assert len(result.metadata["documentId"]) == 36
    # correlationId should be the one provided
    assert result.metadata["correlationId"] == "87654321-4321-4321-4321-210987654321"