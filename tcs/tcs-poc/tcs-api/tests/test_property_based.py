"""Property-based validation tests using Hypothesis.

These tests generate randomized trade data to verify validation invariants
across thousands of generated examples. All randomization happens in-memory
during test execution - no files are saved.
"""

from datetime import date
from hypothesis import given, settings
from tests.strategies.trade_strategies import random_ir_swap
from trade_api.models.trade import Trade, ReadOnlyTrade
from trade_api.validation.factory import ValidationFactory


@given(random_ir_swap())
def test_random_valid_trades_pass_validation(trade_data):
    """Property: Any validly constructed random trade should pass validation.

    This test verifies that our trade generation strategy produces valid trades
    that pass all validation rules. If this test fails, it indicates either:
    1. A bug in the trade generator
    2. A bug in the validation logic
    3. An overly strict validation rule
    """
    trade = Trade(trade_data)
    readonly_trade = ReadOnlyTrade(trade)

    factory = ValidationFactory()
    pipeline = factory.create_pipeline(readonly_trade)
    result = pipeline.validate(readonly_trade)

    assert result.success is True, f"Validation failed: {result.errors}"


@given(random_ir_swap())
def test_date_ordering_invariant(trade_data):
    """Property: tradeDate <= startDate < endDate always holds.

    This fundamental invariant must hold for all trades:
    - Trade date cannot be after the swap starts
    - Swap must have a positive tenor (start before end)
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    trade_date = date.fromisoformat(trade.jmesget("common.tradeDate"))
    start_date = date.fromisoformat(trade.jmesget("swapLegs[0].startDate"))
    end_date = date.fromisoformat(trade.jmesget("swapLegs[0].endDate"))

    assert trade_date <= start_date, f"tradeDate {trade_date} must be <= startDate {start_date}"
    assert start_date < end_date, f"startDate {start_date} must be < endDate {end_date}"


@given(random_ir_swap())
def test_notional_matching_invariant(trade_data):
    """Property: Both legs have equal absolute notionals.

    In an interest rate swap, both legs must have matching notional amounts
    (even though they have opposite signs for pay/receive).
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    leg0_notional = abs(trade.jmesget("swapLegs[0].notional"))
    leg1_notional = abs(trade.jmesget("swapLegs[1].notional"))

    assert leg0_notional == leg1_notional, \
        f"Leg notionals must match: {leg0_notional} != {leg1_notional}"


@given(random_ir_swap())
def test_notional_sign_convention(trade_data):
    """Property: Pay leg has negative notional, receive leg has positive.

    This sign convention is critical for proper P&L calculations:
    - Pay direction: negative notional (cash outflow)
    - Receive direction: positive notional (cash inflow)
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    for leg in trade.jmesget("swapLegs"):
        direction = leg["direction"]
        notional = leg["notional"]

        if direction == "pay":
            assert notional < 0 or all(p["notional"] < 0 for p in leg.get("schedule", [])), \
                f"Pay leg notional must be negative, got {notional}"
        else:  # receive
            assert notional > 0 or all(p["notional"] > 0 for p in leg.get("schedule", [])), \
                f"Receive leg notional must be positive, got {notional}"


@given(random_ir_swap())
def test_schedule_continuity_invariant(trade_data):
    """Property: Schedule periods are contiguous with no gaps.

    Each period's end date must equal the next period's start date.
    Gaps or overlaps in the schedule indicate data quality issues.
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    for leg in trade.jmesget("swapLegs"):
        schedule = leg.get("schedule", [])
        if len(schedule) < 2:
            continue

        for i in range(len(schedule) - 1):
            current_end = schedule[i]["endDate"]
            next_start = schedule[i + 1]["startDate"]
            assert current_end == next_start, \
                f"Gap in schedule at period {i}: {current_end} -> {next_start}"


@given(random_ir_swap())
def test_round_trip_serialization(trade_data):
    """Property: Serialize -> deserialize -> validate still passes.

    This verifies that:
    1. Trades can be serialized to JSON
    2. Trades can be deserialized from JSON
    3. Validation results are consistent across serialization
    """
    # Original
    trade1 = Trade(trade_data)
    readonly1 = ReadOnlyTrade(trade1)

    # Serialize
    json_bytes = trade1.to_json()

    # Deserialize
    trade2 = Trade(json_bytes)
    readonly2 = ReadOnlyTrade(trade2)

    # Validate both
    factory = ValidationFactory()
    result1 = factory.create_pipeline(readonly1).validate(readonly1)
    result2 = factory.create_pipeline(readonly2).validate(readonly2)

    assert result1.success == result2.success, \
        "Validation success should be same after round-trip"
    assert result1.errors == result2.errors, \
        f"Validation errors should be same after round-trip: {result1.errors} != {result2.errors}"


@given(random_ir_swap())
def test_currency_consistency(trade_data):
    """Property: All legs have matching currencies.

    In a single-currency swap, all legs must use the same currency
    as specified in the underlying.
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    underlying = trade.jmesget("swapDetails.underlying")
    leg_currencies = [leg["currency"] for leg in trade.jmesget("swapLegs")]

    assert all(c == underlying for c in leg_currencies), \
        f"Currency mismatch: underlying={underlying}, legs={leg_currencies}"


@given(random_ir_swap())
@settings(max_examples=100)  # Reduce examples for expensive calculations
def test_interest_calculation_reasonableness(trade_data):
    """Property: Calculated interest is within reasonable bounds.

    Interest amounts should be proportional to:
    - Notional amount
    - Interest rate
    - Period length

    This test catches calculation errors or unrealistic inputs.
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    for leg in trade.jmesget("swapLegs"):
        if leg.get("rateType") != "fixed":
            continue

        schedule = leg.get("schedule", [])
        for period in schedule:
            if "interest" not in period:
                continue

            rate = period.get("rate", 0)
            notional = period.get("notional", 0)
            interest = period.get("interest", 0)

            # Very rough approximation (ignoring day count)
            # interest ≈ notional * rate / 100 / periods_per_year
            expected_magnitude = abs(notional * rate / 100 / 12)  # Assume monthly

            actual_magnitude = abs(interest)

            # Allow 10x tolerance for day count differences
            assert actual_magnitude < expected_magnitude * 10, \
                f"Interest too large: {interest} for notional={notional}, rate={rate}"


@given(random_ir_swap())
def test_schedule_notional_matches_leg_notional(trade_data):
    """Property: Each schedule period has the same notional as its parent leg.

    All periods in a leg's schedule should inherit the leg's notional amount.
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    for leg in trade.jmesget("swapLegs"):
        leg_notional = leg["notional"]
        schedule = leg.get("schedule", [])

        for period in schedule:
            period_notional = period["notional"]
            assert period_notional == leg_notional, \
                f"Period notional {period_notional} must match leg notional {leg_notional}"


@given(random_ir_swap())
def test_schedule_dates_within_leg_bounds(trade_data):
    """Property: All schedule periods fall within leg start/end dates.

    Schedule period dates must be contained within the leg's start and end dates.
    """
    trade = ReadOnlyTrade(Trade(trade_data))

    for leg in trade.jmesget("swapLegs"):
        leg_start = date.fromisoformat(leg["startDate"])
        leg_end = date.fromisoformat(leg["endDate"])
        schedule = leg.get("schedule", [])

        for period in schedule:
            period_start = date.fromisoformat(period["startDate"])
            period_end = date.fromisoformat(period["endDate"])

            assert period_start >= leg_start, \
                f"Period start {period_start} must be >= leg start {leg_start}"
            assert period_end <= leg_end, \
                f"Period end {period_end} must be <= leg end {leg_end}"