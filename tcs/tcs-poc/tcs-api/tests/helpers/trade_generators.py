"""Trade generation helpers for property-based testing."""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional


def generate_schedule(
    start_date: date,
    end_date: date,
    notional: float,
    rate: Optional[float],
    direction: str
) -> List[Dict[str, Any]]:
    """Generate a valid schedule array for a swap leg.

    Args:
        start_date: Leg start date
        end_date: Leg end date
        notional: Leg notional amount
        rate: Fixed rate (None for floating legs)
        direction: "pay" or "receive"

    Returns:
        List of schedule period dicts
    """
    # Determine sign based on direction
    signed_notional = -abs(notional) if direction == "pay" else abs(notional)

    # Generate monthly periods (simplified)
    periods = []
    current = start_date
    period_index = 0

    while current < end_date:
        # Calculate next period end (monthly)
        # Use approximately 30 days, but don't exceed end_date
        next_date = min(
            current + timedelta(days=30),
            end_date
        )

        # Payment date is typically T+2 business days after end
        payment_date = next_date + timedelta(days=2)

        period = {
            "periodIndex": period_index,
            "startDate": str(current),
            "endDate": str(next_date),
            "paymentDate": str(payment_date),
            "notional": signed_notional
        }

        # Add fixed leg specific fields
        if rate is not None:
            period["rate"] = rate
            # Simplified interest calculation (using ACT/360)
            days = (next_date - current).days
            period["interest"] = signed_notional * rate / 100 * days / 360

        # Add floating leg specific fields
        else:
            period["ratesetDate"] = str(next_date)
            period["margin"] = 0.0

        periods.append(period)
        current = next_date
        period_index += 1

    return periods