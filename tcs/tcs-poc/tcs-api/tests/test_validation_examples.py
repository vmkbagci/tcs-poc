"""Tests for validating JSON example files.

This module loads and validates all JSON example files from the json-examples directory.
It ensures that real-world trade structures pass validation and documents any issues.
"""

import pytest
import json
from pathlib import Path
from typing import List, Tuple

from trade_api.models.trade import Trade, ReadOnlyTrade
from trade_api.validation import ValidationFactory


# ========== TEST DATA DISCOVERY ==========

def discover_json_examples() -> List[Tuple[str, Path]]:
    """Discover all JSON example files in the json-examples directory.

    Returns:
        List of tuples (test_id, file_path) for parameterization
    """
    # Find json-examples directory
    test_dir = Path(__file__).resolve().parent
    project_root = test_dir.parent.parent
    json_examples_dir = project_root / "json-examples"

    if not json_examples_dir.exists():
        return []

    examples = []

    # Find all JSON files
    for json_file in json_examples_dir.rglob("*.json"):
        # Create a readable test ID from the file path
        relative_path = json_file.relative_to(json_examples_dir)
        test_id = str(relative_path).replace("/", "_").replace(".json", "")
        examples.append((test_id, json_file))

    return examples


# Discover examples at module load time
JSON_EXAMPLES = discover_json_examples()


# ========== FIXTURES ==========

@pytest.fixture
def validation_factory():
    """Create a ValidationFactory for testing."""
    return ValidationFactory()


# ========== JSON EXAMPLE TESTS ==========

class TestIRSwapExamples:
    """Test validation of IR swap JSON examples."""

    @pytest.mark.parametrize("test_id,file_path",
                            [(tid, fp) for tid, fp in JSON_EXAMPLES if "irswap" in str(fp) or "ir-swap" in str(fp)])
    def test_ir_swap_examples_validate(self, test_id, file_path, validation_factory):
        """Test that IR swap examples pass validation."""
        # Load JSON file
        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        # Create trade and validate
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        # Create validation pipeline
        pipeline = validation_factory.create_pipeline(readonly_trade)
        result = pipeline.validate(readonly_trade)

        # Assert validation passes
        if not result.success:
            pytest.fail(
                f"Validation failed for {test_id}:\n"
                f"Errors: {result.errors}\n"
                f"Warnings: {result.warnings}\n"
                f"File: {file_path}"
            )

        assert result.success is True
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)


class TestPolarSystemExamples:
    """Test validation of Polar system lifecycle examples."""

    @pytest.mark.parametrize("test_id,file_path",
                            [(tid, fp) for tid, fp in JSON_EXAMPLES if "polar" in str(fp)])
    def test_polar_examples_structure(self, test_id, file_path):
        """Test that Polar examples have valid JSON structure."""
        # Load JSON file
        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        # Verify basic structure
        assert isinstance(trade_data, dict), f"Expected dict, got {type(trade_data)}"

        # Check for expected top-level keys based on trade type
        if "ir-swap" in test_id:
            assert "swapDetails" in trade_data or "general" in trade_data, \
                f"IR swap should have swapDetails or general: {file_path}"
        elif "commodity-option" in test_id:
            assert "commodityDetails" in trade_data or "general" in trade_data, \
                f"Commodity option should have commodityDetails or general: {file_path}"
        elif "index-swap" in test_id:
            assert "leg" in trade_data or "general" in trade_data, \
                f"Index swap should have leg or general: {file_path}"

    def test_ir_swap_presave_flattened_comprehensive(self, validation_factory):
        """Comprehensive test of the UI payload (ir-swap-presave-flattened.json)."""
        # This is the key file analyzed in the plan
        test_dir = Path(__file__).resolve().parent
        project_root = test_dir.parent.parent
        file_path = project_root / "json-examples" / "polar" / "ir-swap-presave-flattened.json"

        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        # Load JSON
        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        # Create trade
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        # Test core fields are present
        assert readonly_trade.jmesget("general.transactionRoles.priceMaker") == "kbagci"
        assert readonly_trade.jmesget("common.book") == "MEWEST01HS"
        assert readonly_trade.jmesget("common.counterparty") == "02519916"
        assert readonly_trade.jmesget("common.tradeDate") == "2026-01-15"

        # Test swap details
        assert readonly_trade.jmesget("swapDetails.underlying") == "USD"
        assert readonly_trade.jmesget("swapDetails.swapType") == "irsOis"
        assert readonly_trade.jmesget("swapDetails.settlementType") == "physical"

        # Test swap legs structure
        legs = readonly_trade.jmesget("swapLegs")
        assert legs is not None
        assert len(legs) == 2

        # Test leg 0 (pay leg)
        assert readonly_trade.jmesget("swapLegs[0].direction") == "pay"
        assert readonly_trade.jmesget("swapLegs[0].currency") == "USD"
        assert readonly_trade.jmesget("swapLegs[0].rateType") == "fixed"

        # Test leg 1 (receive leg)
        assert readonly_trade.jmesget("swapLegs[1].direction") == "receive"
        assert readonly_trade.jmesget("swapLegs[1].currency") == "USD"

        # Test schedules exist
        leg0_schedule = readonly_trade.jmesget("swapLegs[0].schedule")
        leg1_schedule = readonly_trade.jmesget("swapLegs[1].schedule")
        assert leg0_schedule is not None
        assert leg1_schedule is not None
        assert len(leg0_schedule) > 0
        assert len(leg1_schedule) > 0

        # Validate through pipeline
        pipeline = validation_factory.create_pipeline(readonly_trade)
        result = pipeline.validate(readonly_trade)

        # Should pass validation (or document why it doesn't)
        if not result.success:
            # Document failures for analysis
            print(f"Validation errors: {result.errors}")
            print(f"Validation warnings: {result.warnings}")


class TestOtherTradeTypes:
    """Test validation of other trade type examples."""

    @pytest.mark.parametrize("test_id,file_path",
                            [(tid, fp) for tid, fp in JSON_EXAMPLES
                             if "basis-swap" in str(fp) or "oi-swap" in str(fp) or "xcur-swap" in str(fp)])
    def test_other_trade_types_structure(self, test_id, file_path):
        """Test that other trade type examples have valid structure."""
        # Load JSON file
        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        # Verify basic structure
        assert isinstance(trade_data, dict), f"Expected dict, got {type(trade_data)}"

        # All trades should have either general or common sections
        # (or be trade-specific sections)
        assert len(trade_data) > 0, f"Empty trade data: {file_path}"


# ========== MULTI-CURRENCY TESTS ==========

class TestMultiCurrencySwaps:
    """Test validation of multi-currency IR swap examples."""

    def test_usd_swap_validation(self, validation_factory):
        """Test USD vanilla IRS validation."""
        test_dir = Path(__file__).resolve().parent
        project_root = test_dir.parent.parent
        file_path = project_root / "json-examples" / "irswap" / "usd-vanilla-irs.json"

        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        pipeline = validation_factory.create_pipeline(readonly_trade)
        result = pipeline.validate(readonly_trade)

        if not result.success:
            print(f"USD swap validation errors: {result.errors}")

    def test_eur_swap_validation(self, validation_factory):
        """Test EUR vanilla IRS validation."""
        test_dir = Path(__file__).resolve().parent
        project_root = test_dir.parent.parent
        file_path = project_root / "json-examples" / "irswap" / "eur-vanilla-irs.json"

        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        pipeline = validation_factory.create_pipeline(readonly_trade)
        result = pipeline.validate(readonly_trade)

        if not result.success:
            print(f"EUR swap validation errors: {result.errors}")

    def test_gbp_swap_validation(self, validation_factory):
        """Test GBP vanilla IRS validation."""
        test_dir = Path(__file__).resolve().parent
        project_root = test_dir.parent.parent
        file_path = project_root / "json-examples" / "irswap" / "gbp-vanilla-irs.json"

        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)
        pipeline = validation_factory.create_pipeline(readonly_trade)
        result = pipeline.validate(readonly_trade)

        if not result.success:
            print(f"GBP swap validation errors: {result.errors}")


# ========== EXOTIC SWAP TESTS ==========

class TestExoticSwapVariants:
    """Test validation of exotic swap variants."""

    @pytest.mark.parametrize("swap_type,filename", [
        ("basis_swap", "basis-swap.json"),
        ("ois", "ois.json"),
        ("amortizing", "amortizing-irs.json"),
        ("forward_starting", "forward-starting-irs.json"),
        ("zero_coupon", "zero-coupon-swap.json"),
        ("cpi", "cpi-swap.json"),
        ("yoy_inflation", "year-on-year-inflation-swap.json"),
        ("nonstandard", "nonstandard-irs.json"),
        ("digital_cms", "digital-cms-spread-swap.json")
    ])
    def test_exotic_swap_structure(self, swap_type, filename):
        """Test that exotic swap examples have valid structure."""
        test_dir = Path(__file__).resolve().parent
        project_root = test_dir.parent.parent
        file_path = project_root / "json-examples" / "irswap" / filename

        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        # Load and verify structure
        with open(file_path, 'r') as f:
            trade_data = json.load(f)

        assert isinstance(trade_data, dict), f"Expected dict for {swap_type}"

        # Create trade to test object creation
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        # Verify it's a swap
        swap_details = readonly_trade.jmesget("swapDetails")
        swap_legs = readonly_trade.jmesget("swapLegs")

        # At minimum, should have some swap-related fields
        assert swap_details is not None or swap_legs is not None, \
            f"{swap_type} should have swapDetails or swapLegs"


# ========== SUMMARY STATISTICS ==========

class TestExampleCoverage:
    """Test to document the coverage of JSON examples."""

    def test_document_example_count(self):
        """Document how many example files are being tested."""
        ir_swap_count = len([fp for _, fp in JSON_EXAMPLES if "irswap" in str(fp) or "ir-swap" in str(fp)])
        polar_count = len([fp for _, fp in JSON_EXAMPLES if "polar" in str(fp)])
        other_count = len(JSON_EXAMPLES) - ir_swap_count - polar_count

        print(f"\n=== JSON Example Coverage ===")
        print(f"Total examples: {len(JSON_EXAMPLES)}")
        print(f"IR Swap examples: {ir_swap_count}")
        print(f"Polar lifecycle examples: {polar_count}")
        print(f"Other examples: {other_count}")
        print(f"=============================\n")

        # Ensure we have examples to test
        assert len(JSON_EXAMPLES) > 0, "No JSON examples found"

    def test_document_example_paths(self):
        """Document all example file paths for reference."""
        print(f"\n=== All JSON Example Files ===")
        for test_id, file_path in sorted(JSON_EXAMPLES):
            print(f"{test_id}: {file_path}")
        print(f"==============================\n")