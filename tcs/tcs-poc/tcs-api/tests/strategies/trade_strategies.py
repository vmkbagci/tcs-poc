"""Hypothesis strategies for generating random trade data."""

from datetime import date, timedelta
from hypothesis import strategies as st
from tests.helpers.trade_generators import generate_schedule


# Date strategies with constraints
past_dates = st.dates(
    min_value=date.today() - timedelta(days=5*365),
    max_value=date.today()
)


@st.composite
def input_date_after_trade_date(draw, trade_date: date):
    """Generate inputDate >= tradeDate."""
    return draw(st.dates(
        min_value=trade_date,
        max_value=trade_date + timedelta(days=30)
    ))


@st.composite
def start_date_after_trade_date(draw, trade_date: date):
    """Generate startDate >= tradeDate (T+0 to T+90)."""
    return draw(st.dates(
        min_value=trade_date,
        max_value=trade_date + timedelta(days=90)
    ))


@st.composite
def end_date_after_start_date(draw, start_date: date):
    """Generate endDate > startDate (1 month to 30 years)."""
    return draw(st.dates(
        min_value=start_date + timedelta(days=30),
        max_value=start_date + timedelta(days=30*365)
    ))


# Notional strategies
notionals = st.integers(min_value=1_000, max_value=1_000_000_000)

# Rate strategies
fixed_rates = st.floats(min_value=0.01, max_value=15.0)

# Currency strategies
currencies = st.sampled_from(["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD"])

# Enum strategies
directions = st.sampled_from(["pay", "receive"])
rate_types = st.sampled_from(["fixed", "floating"])
day_count_bases = st.sampled_from(["ACT/360", "ACT/365", "30/360"])
rate_indices = st.sampled_from(["SOFR", "LIBOR", "EURIBOR", "SONIA"])
traders = st.sampled_from(["kbagci", "vmenon", "nseeley"])


@st.composite
def random_ir_swap(draw):
    """Generate a random valid IR swap trade structure.

    Returns a complete IR swap trade dict that matches the structure
    of ir-swap-presave-flattened.json with randomized values.
    """
    # Generate dates with constraints
    trade_date = draw(past_dates)
    input_date = draw(input_date_after_trade_date(trade_date))
    start_date = draw(start_date_after_trade_date(trade_date))
    end_date = draw(end_date_after_start_date(start_date))

    # Generate amounts
    notional = draw(notionals)

    # Generate rates
    fixed_rate = draw(fixed_rates)

    # Generate currencies
    currency = draw(currencies)

    # Generate identifiers
    book = f"BOOK{draw(st.integers(1, 999)):03d}"
    counterparty = f"{draw(st.integers(10000000, 99999999))}"
    trader = draw(traders)

    # Generate rate index for floating leg
    rate_index = draw(rate_indices)

    # Build trade structure (based on ir-swap-presave-flattened.json)
    return {
        "general": {
            "tradeId": "",  # Empty for presave
            "tradeType": "InterestRateSwap",
            "executionDateTime": f"{trade_date}T10:00:00Z",
            "transactionRoles": {
                "priceMaker": trader
            }
        },
        "common": {
            "book": book,
            "counterparty": counterparty,
            "tradeDate": str(trade_date),
            "inputDate": str(input_date)
        },
        "swapDetails": {
            "underlying": currency,
            "swapType": "irsOis",
            "settlementType": "physical"
        },
        "swapLegs": [
            # Pay leg (fixed)
            {
                "legIndex": 0,
                "direction": "pay",
                "currency": currency,
                "rateType": "fixed",
                "notional": -abs(notional),  # Pay leg is negative
                "interestRate": fixed_rate,
                "startDate": str(start_date),
                "endDate": str(end_date),
                "dayCountBasis": "ACT/360",
                "schedule": generate_schedule(start_date, end_date, notional, fixed_rate, "pay")
            },
            # Receive leg (floating)
            {
                "legIndex": 1,
                "direction": "receive",
                "currency": currency,
                "rateType": "floating",
                "notional": abs(notional),  # Receive leg is positive
                "startDate": str(start_date),
                "endDate": str(end_date),
                "dayCountBasis": "ACT/360",
                "ratesetRef": rate_index,
                "schedule": generate_schedule(start_date, end_date, notional, None, "receive")
            }
        ]
    }