"""Full integration tests spanning tcs-api and tcs-store.

These tests require both services to be running:
- tcs-api on port 5000
- tcs-store on port 5500

Run with: pytest tests/test_full_integration.py -v
"""

import pytest
import httpx
import json
from pathlib import Path
from typing import Dict, Any


# Test configuration
TCS_API_URL = "http://localhost:5000"
TCS_STORE_URL = "http://localhost:5500"
TIMEOUT = 10.0


@pytest.fixture(scope="module")
def check_services():
    """Check that both services are running before tests."""
    try:
        # Check tcs-api
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{TCS_API_URL}/health")
            assert response.status_code == 200, "tcs-api not responding"
        
        # Check tcs-store
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{TCS_STORE_URL}/health")
            assert response.status_code == 200, "tcs-store not responding"
            
        return True
    except Exception as e:
        pytest.skip(f"Services not running: {e}")


@pytest.fixture
def cleanup_store():
    """Clean up store before and after each test."""
    # Purge store before test
    context = {
        "user": "test_user",
        "agent": "pytest",
        "action": "purge",
        "intent": "test_cleanup"
    }
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            client.post(
                f"{TCS_STORE_URL}/admin/purge",
                json={"context": context}
            )
    except:
        pass  # Store might be empty
    
    yield
    
    # Purge store after test
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            client.post(
                f"{TCS_STORE_URL}/admin/purge",
                json={"context": context}
            )
    except:
        pass


@pytest.fixture
def sample_trade_data() -> Dict[str, Any]:
    """Load sample trade data from JSON examples."""
    json_path = Path(__file__).parent.parent.parent / "json-examples" / "polar" / "ir-swap-presave-flattened.json"
    
    with open(json_path, 'r') as f:
        trade_data = json.load(f)
    
    # Ensure it has NEW prefix and priceMaker
    trade_data['general']['tradeId'] = 'NEW-20260120-IRSWAP-TEST-001'
    trade_data['general']['transactionRoles']['priceMaker'] = 'kbagci'
    
    return trade_data


@pytest.fixture
def context() -> Dict[str, str]:
    """Create context for save operations."""
    return {
        "user": "trader_john",
        "agent": "pytest",
        "action": "save_new",
        "intent": "integration_test"
    }


def test_services_are_running(check_services):
    """Verify both services are accessible."""
    assert check_services is True


def test_full_save_and_list_flow(check_services, cleanup_store, sample_trade_data, context):
    """Test complete flow: save trade via API, verify it appears in store list.
    
    Flow:
    1. Submit trade to tcs-api /save endpoint
    2. API validates and calls tcs-store /save/new
    3. Query tcs-store /list endpoint
    4. Verify saved trade appears in list
    """
    with httpx.Client(timeout=TIMEOUT) as client:
        # Step 1: Save trade via tcs-api
        save_request = {
            "user": context["user"],
            "agent": context["agent"],
            "action": context["action"],
            "intent": context["intent"],
            "trade_data": sample_trade_data
        }
        
        save_response = client.post(
            f"{TCS_API_URL}/api/v1/trades/save",
            json=save_request
        )
        
        assert save_response.status_code == 200, f"Save failed: {save_response.text}"
        save_data = save_response.json()
        
        assert save_data["success"] is True, f"Save not successful: {save_data.get('errors')}"
        assert save_data["errors"] == []
        assert save_data["trade_data"] is not None
        assert save_data["metadata"] is not None
        
        trade_id = sample_trade_data['general']['tradeId']
        print(f"\n✓ Trade saved via API: {trade_id}")
        
        # Step 2: Query tcs-store /list endpoint (empty filter = all trades)
        list_request = {
            "filter": {}
        }
        
        list_response = client.post(
            f"{TCS_STORE_URL}/list",
            json=list_request
        )
        
        assert list_response.status_code == 200, f"List failed: {list_response.text}"
        trades = list_response.json()
        
        assert isinstance(trades, list), "List response should be an array"
        assert len(trades) > 0, "No trades found in store"
        
        print(f"✓ Found {len(trades)} trade(s) in store")
        
        # Step 3: Verify our trade is in the list
        trade_ids = [t.get("id") for t in trades]
        assert trade_id in trade_ids, f"Trade {trade_id} not found in store list"
        
        # Step 4: Verify trade data
        saved_trade = next(t for t in trades if t.get("id") == trade_id)
        assert saved_trade["data"] is not None
        assert saved_trade["data"]["general"]["tradeId"] == trade_id
        assert saved_trade["data"]["general"]["transactionRoles"]["priceMaker"] == "kbagci"
        
        print(f"✓ Trade verified in store with correct data")


def test_save_with_validation_error(check_services, cleanup_store, context):
    """Test that validation errors are returned without calling store."""
    # Create invalid trade (missing priceMaker)
    invalid_trade = {
        "general": {
            "tradeId": "NEW-20260120-INVALID-001",
            "transactionRoles": {}  # Missing priceMaker
        },
        "common": {
            "book": "BOOK-001",
            "tradeDate": "2026-01-20",
            "counterparty": "BANK_A",
            "inputDate": "2026-01-20"
        }
    }
    
    with httpx.Client(timeout=TIMEOUT) as client:
        save_request = {
            "user": context["user"],
            "agent": context["agent"],
            "action": context["action"],
            "intent": context["intent"],
            "trade_data": invalid_trade
        }
        
        save_response = client.post(
            f"{TCS_API_URL}/api/v1/trades/save",
            json=save_request
        )
        
        assert save_response.status_code == 200
        save_data = save_response.json()
        
        # Should fail validation
        assert save_data["success"] is False
        assert len(save_data["errors"]) > 0
        assert save_data["trade_data"] is None
        
        print(f"\n✓ Validation error correctly returned: {save_data['errors'][0]}")
        
        # Verify trade was NOT saved to store
        list_response = client.post(
            f"{TCS_STORE_URL}/list",
            json={"filter": {}}
        )
        
        trades = list_response.json()
        trade_ids = [t.get("id") for t in trades]
        assert "NEW-20260120-INVALID-001" not in trade_ids
        
        print(f"✓ Invalid trade not saved to store")


def test_save_duplicate_trade(check_services, cleanup_store, sample_trade_data, context):
    """Test that saving duplicate trade ID returns error."""
    with httpx.Client(timeout=TIMEOUT) as client:
        save_request = {
            "user": context["user"],
            "agent": context["agent"],
            "action": context["action"],
            "intent": context["intent"],
            "trade_data": sample_trade_data
        }
        
        # First save should succeed
        response1 = client.post(
            f"{TCS_API_URL}/api/v1/trades/save",
            json=save_request
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["success"] is True
        
        print(f"\n✓ First save succeeded")
        
        # Second save with same ID should fail
        response2 = client.post(
            f"{TCS_API_URL}/api/v1/trades/save",
            json=save_request
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["success"] is False
        assert len(data2["errors"]) > 0
        assert "already exists" in data2["errors"][0].lower() or "409" in str(data2["errors"])
        
        print(f"✓ Duplicate save correctly rejected: {data2['errors'][0]}")


def test_filter_by_trader(check_services, cleanup_store, sample_trade_data, context):
    """Test filtering trades by trader (priceMaker)."""
    # Save trade with specific trader
    sample_trade_data['general']['tradeId'] = 'NEW-20260120-FILTER-TEST-001'
    sample_trade_data['general']['transactionRoles']['priceMaker'] = 'vmenon'
    
    with httpx.Client(timeout=TIMEOUT) as client:
        save_request = {
            "user": context["user"],
            "agent": context["agent"],
            "action": context["action"],
            "intent": context["intent"],
            "trade_data": sample_trade_data
        }
        
        save_response = client.post(
            f"{TCS_API_URL}/api/v1/trades/save",
            json=save_request
        )
        assert save_response.status_code == 200
        assert save_response.json()["success"] is True
        
        print(f"\n✓ Trade saved with trader: vmenon")
        
        # Filter by trader
        list_request = {
            "filter": {
                "data.general.transactionRoles.priceMaker": {"eq": "vmenon"}
            }
        }
        
        list_response = client.post(
            f"{TCS_STORE_URL}/list",
            json=list_request
        )
        
        assert list_response.status_code == 200
        trades = list_response.json()
        
        assert len(trades) > 0, "No trades found with filter"
        
        # Verify all returned trades have the correct trader
        for trade in trades:
            trader = trade["data"]["general"]["transactionRoles"]["priceMaker"]
            assert trader == "vmenon", f"Wrong trader: {trader}"
        
        print(f"✓ Filter by trader working: found {len(trades)} trade(s)")


if __name__ == "__main__":
    print("Run with: pytest tests/test_full_integration.py -v")
    print("\nMake sure both services are running:")
    print("  - tcs-api on port 5000")
    print("  - tcs-store on port 5500")
