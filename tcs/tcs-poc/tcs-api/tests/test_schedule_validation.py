"""Tests for schedule validation logic.

This module tests validation of UI-generated cashflow schedules.
It covers schedule structure, period continuity, payment date calculations,
and interest calculations for IR swaps.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from trade_api.models.trade import Trade, ReadOnlyTrade


# ========== SCHEDULE STRUCTURE TESTS ==========

class TestScheduleStructure:
    """Test basic schedule structure validation."""

    def test_schedule_exists_on_swap_legs(self):
        """Test that schedules exist on swap legs."""
        trade_data = {
            "swapLegs": [
                {
                    "legIndex": 0,
                    "direction": "pay",
                    "currency": "USD",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        schedule = readonly_trade.jmesget("swapLegs[0].schedule")
        assert schedule is not None
        assert len(schedule) == 1

    def test_schedule_has_required_fields(self):
        """Test that schedule periods have required fields."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "paymentDate": "2026-02-19"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")
        assert period["periodIndex"] == 0
        assert "startDate" in period
        assert "endDate" in period
        assert "paymentDate" in period

    def test_fixed_leg_schedule_structure(self):
        """Test fixed leg schedule has rate and interest fields."""
        trade_data = {
            "swapLegs": [
                {
                    "rateType": "fixed",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "paymentDate": "2026-02-19",
                            "rate": 3.0,
                            "notional": -1000,
                            "interest": -2.67
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")
        assert "rate" in period
        assert "notional" in period
        assert "interest" in period
        assert period["rate"] == 3.0
        assert period["interest"] == -2.67

    def test_floating_leg_schedule_structure(self):
        """Test floating leg schedule has index and tenor fields."""
        trade_data = {
            "swapLegs": [
                {
                    "rateType": "floating",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "ratesetDate": "2026-02-17",
                            "paymentDate": "2026-02-19",
                            "notional": 1000,
                            "margin": 0,
                            "index": "SOFR",
                            "tenor": "1D"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")
        assert "index" in period
        assert "tenor" in period
        assert "ratesetDate" in period
        assert period["index"] == "SOFR"
        assert period["tenor"] == "1D"


# ========== PERIOD CONTINUITY TESTS ==========

class TestPeriodContinuity:
    """Test that schedule periods are continuous and properly ordered."""

    def test_periods_are_ordered(self):
        """Test that period indices are sequential."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {"periodIndex": 0, "startDate": "2026-01-16", "endDate": "2026-02-17"},
                        {"periodIndex": 1, "startDate": "2026-02-17", "endDate": "2026-03-16"}
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        schedule = readonly_trade.jmesget("swapLegs[0].schedule")
        assert schedule[0]["periodIndex"] == 0
        assert schedule[1]["periodIndex"] == 1

    def test_periods_are_contiguous(self):
        """Test that end date of period N equals start date of period N+1."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {"periodIndex": 0, "startDate": "2026-01-16", "endDate": "2026-02-17"},
                        {"periodIndex": 1, "startDate": "2026-02-17", "endDate": "2026-03-16"}
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        schedule = readonly_trade.jmesget("swapLegs[0].schedule")
        # Period 0 end date should equal period 1 start date
        assert schedule[0]["endDate"] == schedule[1]["startDate"]

    def test_detect_gap_in_periods(self):
        """Test detection of gaps between periods."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {"periodIndex": 0, "startDate": "2026-01-16", "endDate": "2026-02-17"},
                        {"periodIndex": 1, "startDate": "2026-02-20", "endDate": "2026-03-16"}  # Gap!
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        schedule = readonly_trade.jmesget("swapLegs[0].schedule")
        # There's a 3-day gap
        period0_end = schedule[0]["endDate"]
        period1_start = schedule[1]["startDate"]
        assert period0_end != period1_start  # Gap detected

    def test_dates_are_chronological(self):
        """Test that start date < end date for each period."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {"periodIndex": 0, "startDate": "2026-01-16", "endDate": "2026-02-17"}
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")
        start = datetime.strptime(period["startDate"], "%Y-%m-%d")
        end = datetime.strptime(period["endDate"], "%Y-%m-%d")
        assert start < end


# ========== PAYMENT DATE VALIDATION ==========

class TestPaymentDates:
    """Test payment date calculation and validation."""

    def test_payment_date_follows_end_date(self):
        """Test that payment date is on or after end date."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "paymentDate": "2026-02-19"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")
        end_date = datetime.strptime(period["endDate"], "%Y-%m-%d")
        payment_date = datetime.strptime(period["paymentDate"], "%Y-%m-%d")
        assert payment_date >= end_date

    def test_payment_date_settlement_offset(self):
        """Test typical T+2 settlement offset for payment dates."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "paymentDate": "2026-02-19"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")
        end_date = datetime.strptime(period["endDate"], "%Y-%m-%d")
        payment_date = datetime.strptime(period["paymentDate"], "%Y-%m-%d")

        # Payment is typically 2 business days after end date
        # This is a simplified check (doesn't account for holidays)
        days_diff = (payment_date - end_date).days
        assert 0 <= days_diff <= 5  # Reasonable settlement window

    def test_multiple_periods_payment_dates(self):
        """Test payment dates across multiple periods."""
        trade_data = {
            "swapLegs": [
                {
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "paymentDate": "2026-02-19"
                        },
                        {
                            "periodIndex": 1,
                            "startDate": "2026-02-17",
                            "endDate": "2026-03-16",
                            "paymentDate": "2026-03-18"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        schedule = readonly_trade.jmesget("swapLegs[0].schedule")
        for period in schedule:
            end_date = datetime.strptime(period["endDate"], "%Y-%m-%d")
            payment_date = datetime.strptime(period["paymentDate"], "%Y-%m-%d")
            assert payment_date >= end_date


# ========== INTEREST CALCULATION VALIDATION ==========

class TestInterestCalculations:
    """Test interest calculation validation for fixed legs."""

    def test_fixed_leg_interest_sign_convention(self):
        """Test that pay leg has negative notional and interest."""
        trade_data = {
            "swapLegs": [
                {
                    "direction": "pay",
                    "rateType": "fixed",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "rate": 3.0,
                            "notional": -1000,
                            "interest": -2.67
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        leg_direction = readonly_trade.jmesget("swapLegs[0].direction")
        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")

        assert leg_direction == "pay"
        assert period["notional"] < 0
        assert period["interest"] < 0

    def test_receive_leg_interest_sign_convention(self):
        """Test that receive leg has positive notional."""
        trade_data = {
            "swapLegs": [
                {
                    "direction": "receive",
                    "rateType": "floating",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "notional": 1000
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        leg_direction = readonly_trade.jmesget("swapLegs[0].direction")
        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")

        assert leg_direction == "receive"
        assert period["notional"] > 0

    def test_interest_calculation_reasonableness(self):
        """Test that interest calculation is reasonable (order of magnitude check)."""
        trade_data = {
            "swapLegs": [
                {
                    "direction": "pay",
                    "rateType": "fixed",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "rate": 3.0,  # 3% annual
                            "notional": -1000,
                            "interest": -2.67  # For ~1 month period
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")

        # Calculate expected interest (simplified)
        # For 1 month at 3% annual: 1000 * 0.03 * (32/360) ≈ 2.67
        rate = period["rate"] / 100  # Convert to decimal
        notional = abs(period["notional"])

        start = datetime.strptime(period["startDate"], "%Y-%m-%d")
        end = datetime.strptime(period["endDate"], "%Y-%m-%d")
        days = (end - start).days

        # Simplified day count (actual would use 30/360 or ACT/360)
        expected_interest = notional * rate * (days / 360)
        actual_interest = abs(period["interest"])

        # Check if interest is within reasonable range (±20%)
        assert 0.8 * expected_interest <= actual_interest <= 1.2 * expected_interest


# ========== SCHEDULE CONSISTENCY TESTS ==========

class TestScheduleConsistency:
    """Test consistency between swap leg dates and schedule dates."""

    def test_schedule_covers_leg_period(self):
        """Test that schedule covers the entire leg period."""
        trade_data = {
            "swapLegs": [
                {
                    "startDate": "2026-01-16",
                    "endDate": "2026-03-16",
                    "schedule": [
                        {"periodIndex": 0, "startDate": "2026-01-16", "endDate": "2026-02-17"},
                        {"periodIndex": 1, "startDate": "2026-02-17", "endDate": "2026-03-16"}
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        leg_start = readonly_trade.jmesget("swapLegs[0].startDate")
        leg_end = readonly_trade.jmesget("swapLegs[0].endDate")
        schedule = readonly_trade.jmesget("swapLegs[0].schedule")

        # First period should start on leg start date
        assert schedule[0]["startDate"] == leg_start
        # Last period should end on leg end date
        assert schedule[-1]["endDate"] == leg_end

    def test_matching_notionals_across_legs(self):
        """Test that both legs have matching notionals (opposite signs)."""
        trade_data = {
            "swapLegs": [
                {
                    "direction": "pay",
                    "schedule": [
                        {"periodIndex": 0, "notional": -1000}
                    ]
                },
                {
                    "direction": "receive",
                    "schedule": [
                        {"periodIndex": 0, "notional": 1000}
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        leg0_notional = readonly_trade.jmesget("swapLegs[0].schedule[0].notional")
        leg1_notional = readonly_trade.jmesget("swapLegs[1].schedule[0].notional")

        # Notionals should be equal in magnitude but opposite in sign
        assert abs(leg0_notional) == abs(leg1_notional)
        assert leg0_notional == -leg1_notional


# ========== RATESET DATE VALIDATION ==========

class TestRatesetDates:
    """Test rateset date validation for floating legs."""

    def test_floating_leg_has_rateset_dates(self):
        """Test that floating leg periods have rateset dates."""
        trade_data = {
            "swapLegs": [
                {
                    "rateType": "floating",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "ratesetDate": "2026-02-17"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")
        assert "ratesetDate" in period
        assert period["ratesetDate"] is not None

    def test_rateset_date_timing(self):
        """Test that rateset date is at or near period end."""
        trade_data = {
            "swapLegs": [
                {
                    "rateType": "floating",
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "ratesetDate": "2026-02-17"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        period = readonly_trade.jmesget("swapLegs[0].schedule[0]")

        # Rateset date is typically at period end for arrears fixing
        # or at period start for advance fixing
        rateset = datetime.strptime(period["ratesetDate"], "%Y-%m-%d")
        start = datetime.strptime(period["startDate"], "%Y-%m-%d")
        end = datetime.strptime(period["endDate"], "%Y-%m-%d")

        # Rateset should be between start and end (inclusive)
        assert start <= rateset <= end


# ========== REAL-WORLD SCHEDULE TEST ==========

class TestRealWorldSchedule:
    """Test with real-world schedule data from ir-swap-presave-flattened.json."""

    def test_presave_flattened_schedule_structure(self):
        """Test the actual schedule from the UI payload."""
        # Simulating the structure from ir-swap-presave-flattened.json
        trade_data = {
            "swapLegs": [
                {
                    "legIndex": 0,
                    "direction": "pay",
                    "currency": "USD",
                    "rateType": "fixed",
                    "notional": 1000,
                    "interestRate": 3,
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "paymentDate": "2026-02-19",
                            "rate": 3,
                            "notional": -1000,
                            "interest": -2.67
                        },
                        {
                            "periodIndex": 1,
                            "startDate": "2026-02-17",
                            "endDate": "2026-03-16",
                            "paymentDate": "2026-03-18",
                            "rate": 3,
                            "notional": -1000,
                            "interest": -2.33
                        }
                    ]
                },
                {
                    "legIndex": 1,
                    "direction": "receive",
                    "currency": "USD",
                    "rateType": "floating",
                    "notional": 1000,
                    "schedule": [
                        {
                            "periodIndex": 0,
                            "startDate": "2026-01-16",
                            "endDate": "2026-02-17",
                            "ratesetDate": "2026-02-17",
                            "paymentDate": "2026-02-19",
                            "notional": 1000,
                            "margin": 0,
                            "index": "SOFR",
                            "tenor": "1D"
                        },
                        {
                            "periodIndex": 1,
                            "startDate": "2026-02-17",
                            "endDate": "2026-03-16",
                            "ratesetDate": "2026-03-16",
                            "paymentDate": "2026-03-18",
                            "notional": 1000,
                            "margin": 0,
                            "index": "SOFR",
                            "tenor": "1D"
                        }
                    ]
                }
            ]
        }
        trade = Trade(trade_data)
        readonly_trade = ReadOnlyTrade(trade)

        # Verify both legs have schedules
        leg0_schedule = readonly_trade.jmesget("swapLegs[0].schedule")
        leg1_schedule = readonly_trade.jmesget("swapLegs[1].schedule")
        assert len(leg0_schedule) == 2
        assert len(leg1_schedule) == 2

        # Verify period continuity on both legs
        assert leg0_schedule[0]["endDate"] == leg0_schedule[1]["startDate"]
        assert leg1_schedule[0]["endDate"] == leg1_schedule[1]["startDate"]

        # Verify notional consistency
        assert abs(leg0_schedule[0]["notional"]) == abs(leg1_schedule[0]["notional"])

        # Verify payment dates align
        assert leg0_schedule[0]["paymentDate"] == leg1_schedule[0]["paymentDate"]
        assert leg0_schedule[1]["paymentDate"] == leg1_schedule[1]["paymentDate"]