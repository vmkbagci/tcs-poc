#!/usr/bin/env python3
"""
Example client demonstrating all TCS Store API operations with context metadata.

This script demonstrates:
- Saving new trades with context
- Loading trades by ID
- Updating trades (full and partial)
- Filtering trades
- Listing and counting trades
- Deleting trades
- Bulk operations

Run the TCS Store API first:
    cd tcs-store
    ./run-store.sh

Then run this script:
    poetry run python examples/example_client.py
"""

import requests
import json
from typing import Dict, Any, List
from datetime import datetime


# API Configuration
BASE_URL = "http://localhost:5500"


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_response(response: requests.Response) -> None:
    """Print response details."""
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def create_context(user: str, agent: str, action: str, intent: str) -> Dict[str, str]:
    """Create context metadata for API requests."""
    return {
        "user": user,
        "agent": agent,
        "action": action,
        "intent": intent
    }


def example_save_new_trade() -> str:
    """Example: Save a new trade."""
    print_section("1. Save New Trade")
    
    trade_id = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
    
    payload = {
        "context": create_context(
            user="trader_john",
            agent="example_client",
            action="save_new",
            intent="new_trade_booking"
        ),
        "trade": {
            "id": trade_id,
            "data": {
                "trade_type": "IR_SWAP",
                "counterparty": "BANK_A",
                "notional": 1000000,
                "currency": "USD",
                "trade_date": "2024-01-15",
                "maturity_date": "2029-01-15",
                "leg1": {
                    "type": "fixed",
                    "rate": 0.045,
                    "notional": 1000000
                },
                "leg2": {
                    "type": "floating",
                    "index": "SOFR",
                    "spread": 0.002,
                    "notional": 1000000
                }
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/save/new", json=payload)
    print_response(response)
    
    return trade_id


def example_load_by_id(trade_id: str) -> None:
    """Example: Load a trade by ID."""
    print_section("2. Load Trade by ID")
    
    payload = {
        "id": trade_id
    }
    
    response = requests.post(f"{BASE_URL}/load/id", json=payload)
    print_response(response)


def example_full_update(trade_id: str) -> None:
    """Example: Full update (replace entire trade)."""
    print_section("3. Full Update (Replace Trade)")
    
    payload = {
        "context": create_context(
            user="trader_john",
            agent="example_client",
            action="update",
            intent="counterparty_correction"
        ),
        "trade": {
            "id": trade_id,
            "data": {
                "trade_type": "IR_SWAP",
                "counterparty": "BANK_B",  # Changed
                "notional": 1000000,
                "currency": "USD",
                "trade_date": "2024-01-15",
                "maturity_date": "2029-01-15",
                "leg1": {
                    "type": "fixed",
                    "rate": 0.045,
                    "notional": 1000000
                },
                "leg2": {
                    "type": "floating",
                    "index": "SOFR",
                    "spread": 0.002,
                    "notional": 1000000
                }
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/save/update", json=payload)
    print_response(response)


def example_partial_update(trade_id: str) -> None:
    """Example: Partial update using deep merge."""
    print_section("4. Partial Update (Deep Merge)")
    
    # Update only the notional and leg1 rate
    payload = {
        "context": create_context(
            user="trader_jane",
            agent="example_client",
            action="partial_update",
            intent="notional_adjustment"
        ),
        "id": trade_id,
        "updates": {
            "data": {
                "notional": 1500000,  # Update notional
                "leg1": {
                    "rate": 0.048  # Update leg1 rate only
                }
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/save/partial", json=payload)
    print_response(response)


def example_partial_update_with_null() -> None:
    """Example: Partial update with null handling."""
    print_section("5. Partial Update with Null Handling")
    
    # First, create a trade with optional fields
    trade_id = "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7"
    
    payload = {
        "context": create_context(
            user="trader_john",
            agent="example_client",
            action="save_new",
            intent="new_trade_booking"
        ),
        "trade": {
            "id": trade_id,
            "data": {
                "trade_type": "FX_SWAP",
                "counterparty": "BANK_C",
                "notional": 500000,
                "broker": "BROKER_X",
                "metadata": {
                    "tags": ["urgent", "high-value"],
                    "notes": "Important trade"
                }
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/save/new", json=payload)
    print("Created trade with optional fields:")
    print_response(response)
    
    # Now remove the metadata object and set broker to null
    payload = {
        "context": create_context(
            user="trader_john",
            agent="example_client",
            action="partial_update",
            intent="cleanup_metadata"
        ),
        "id": trade_id,
        "updates": {
            "data": {
                "metadata": None,  # Remove entire metadata object
                "broker": None     # Set broker to null
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/save/partial", json=payload)
    print("After partial update with null:")
    print_response(response)


def example_save_multiple_trades() -> List[str]:
    """Example: Save multiple trades for filtering."""
    print_section("6. Save Multiple Trades for Filtering")
    
    trade_ids = []
    
    trades = [
        {
            "id": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7b8",
            "data": {
                "trade_type": "IR_SWAP",
                "counterparty": "BANK_D",
                "notional": 2000000,
                "currency": "EUR"
            }
        },
        {
            "id": "d4e5f6g7h8i9j0k1l2m3n4o5p6a7b8c9",
            "data": {
                "trade_type": "FX_SWAP",
                "counterparty": "BANK_E",
                "notional": 750000,
                "currency": "GBP"
            }
        },
        {
            "id": "e5f6g7h8i9j0k1l2m3n4o5p6a7b8c9d0",
            "data": {
                "trade_type": "COMMODITY_OPTION",
                "counterparty": "BANK_F",
                "notional": 300000,
                "currency": "USD"
            }
        }
    ]
    
    for trade in trades:
        payload = {
            "context": create_context(
                user="trader_system",
                agent="example_client",
                action="save_new",
                intent="bulk_import"
            ),
            "trade": trade
        }
        
        response = requests.post(f"{BASE_URL}/save/new", json=payload)
        print(f"Saved trade {trade['id']}: {response.status_code}")
        trade_ids.append(trade["id"])
    
    print()
    return trade_ids


def example_filter_equality() -> None:
    """Example: Filter trades by equality."""
    print_section("7. Filter Trades - Equality")
    
    payload = {
        "filter": {
            "data.trade_type": {"eq": "IR_SWAP"}
        }
    }
    
    response = requests.post(f"{BASE_URL}/load/filter", json=payload)
    print_response(response)


def example_filter_range() -> None:
    """Example: Filter trades by range."""
    print_section("8. Filter Trades - Range")
    
    payload = {
        "filter": {
            "data.notional": {
                "gte": 1000000,
                "lte": 2000000
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/load/filter", json=payload)
    print_response(response)


def example_filter_regex() -> None:
    """Example: Filter trades by regex."""
    print_section("9. Filter Trades - Regex")
    
    payload = {
        "filter": {
            "data.counterparty": {"regex": "^BANK_[A-C]$"}
        }
    }
    
    response = requests.post(f"{BASE_URL}/load/filter", json=payload)
    print_response(response)


def example_filter_multiple_conditions() -> None:
    """Example: Filter trades with multiple conditions (AND logic)."""
    print_section("10. Filter Trades - Multiple Conditions")
    
    payload = {
        "filter": {
            "data.trade_type": {"eq": "IR_SWAP"},
            "data.notional": {"gte": 1000000},
            "data.currency": {"eq": "USD"}
        }
    }
    
    response = requests.post(f"{BASE_URL}/load/filter", json=payload)
    print_response(response)


def example_list_trades() -> None:
    """Example: List trades."""
    print_section("11. List Trades")
    
    payload = {
        "filter": {
            "data.trade_type": {"eq": "IR_SWAP"}
        }
    }
    
    response = requests.post(f"{BASE_URL}/list", json=payload)
    print_response(response)


def example_count_trades() -> None:
    """Example: Count trades."""
    print_section("12. Count Trades")
    
    payload = {
        "filter": {
            "data.notional": {"gte": 1000000}
        }
    }
    
    response = requests.post(f"{BASE_URL}/list/count", json=payload)
    print_response(response)


def example_load_group(trade_ids: List[str]) -> None:
    """Example: Load multiple trades by IDs."""
    print_section("13. Load Group (Bulk Load)")
    
    payload = {
        "ids": trade_ids[:3]  # Load first 3 trades
    }
    
    response = requests.post(f"{BASE_URL}/load/group", json=payload)
    print_response(response)


def example_delete_by_id(trade_id: str) -> None:
    """Example: Delete a single trade."""
    print_section("14. Delete Trade by ID")
    
    payload = {
        "context": create_context(
            user="trader_john",
            agent="example_client",
            action="delete",
            intent="trade_cancellation"
        ),
        "id": trade_id
    }
    
    response = requests.post(f"{BASE_URL}/delete/id", json=payload)
    print_response(response)
    
    # Verify deletion (should return 404)
    print("Verify deletion (should return 404):")
    verify_payload = {"id": trade_id}
    response = requests.post(f"{BASE_URL}/load/id", json=verify_payload)
    print_response(response)


def example_delete_group(trade_ids: List[str]) -> None:
    """Example: Delete multiple trades by IDs."""
    print_section("15. Delete Group (Bulk Delete)")
    
    payload = {
        "context": create_context(
            user="trader_system",
            agent="example_client",
            action="bulk_delete",
            intent="portfolio_cleanup"
        ),
        "ids": trade_ids
    }
    
    response = requests.post(f"{BASE_URL}/delete/group", json=payload)
    print_response(response)


def example_idempotent_delete() -> None:
    """Example: Demonstrate idempotent delete."""
    print_section("16. Idempotent Delete")
    
    trade_id = "nonexistent_trade_id"
    
    payload = {
        "context": create_context(
            user="trader_john",
            agent="example_client",
            action="delete",
            intent="cleanup"
        ),
        "id": trade_id
    }
    
    print("Deleting non-existent trade (should return 200):")
    response = requests.post(f"{BASE_URL}/delete/id", json=payload)
    print_response(response)


def example_health_check() -> None:
    """Example: Health check."""
    print_section("17. Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("  TCS Store API - Example Client")
    print("  Demonstrating all operations with context metadata")
    print("=" * 80)
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print(f"\nError: TCS Store API is not responding correctly")
            print(f"Please start the API first: cd tcs-store && ./run-store.sh")
            return
    except requests.exceptions.RequestException:
        print(f"\nError: Cannot connect to TCS Store API at {BASE_URL}")
        print(f"Please start the API first: cd tcs-store && ./run-store.sh")
        return
    
    # Run examples
    example_health_check()
    
    # Save operations
    trade_id = example_save_new_trade()
    example_load_by_id(trade_id)
    example_full_update(trade_id)
    example_partial_update(trade_id)
    example_partial_update_with_null()
    
    # Save multiple trades for filtering
    additional_trade_ids = example_save_multiple_trades()
    
    # Filter operations
    example_filter_equality()
    example_filter_range()
    example_filter_regex()
    example_filter_multiple_conditions()
    
    # List and count operations
    example_list_trades()
    example_count_trades()
    
    # Bulk operations
    example_load_group([trade_id] + additional_trade_ids)
    
    # Delete operations
    example_delete_by_id(trade_id)
    example_delete_group(additional_trade_ids)
    example_idempotent_delete()
    
    print_section("Examples Complete")
    print("All examples executed successfully!")
    print("\nFor more information, visit: http://localhost:5500/docs")


if __name__ == "__main__":
    main()
