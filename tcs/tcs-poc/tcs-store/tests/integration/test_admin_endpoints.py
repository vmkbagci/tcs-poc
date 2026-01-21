"""Integration tests for admin endpoints."""

import pytest
from fastapi.testclient import TestClient

from tcs_store.main import app, store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the store before each test."""
    store.clear()
    yield
    store.clear()


def test_seed_endpoint_creates_trades():
    """Test that seed endpoint creates the specified number of trades."""
    client = TestClient(app)
    
    # Seed with 5 trades
    response = client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 5
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Successfully seeded 5 IR swap trades"
    assert data["trades_created"] == 5
    assert len(data["trade_ids"]) == 5
    
    # Verify trades were created
    count_response = client.post("/list/count", json={"filter": {}})
    assert count_response.json()["count"] == 5


def test_seed_endpoint_default_count():
    """Test that seed endpoint uses default count of 30."""
    client = TestClient(app)
    
    response = client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            }
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["trades_created"] == 30
    assert len(data["trade_ids"]) == 30


def test_seed_endpoint_validates_context():
    """Test that seed endpoint requires valid context."""
    client = TestClient(app)
    
    # Missing context
    response = client.post(
        "/admin/seed",
        json={"count": 5}
    )
    
    assert response.status_code == 422


def test_seed_endpoint_validates_count_range():
    """Test that seed endpoint validates count range."""
    client = TestClient(app)
    
    # Count too high
    response = client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 101
        }
    )
    
    assert response.status_code == 422
    
    # Count too low
    response = client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 0
        }
    )
    
    assert response.status_code == 422


def test_seeded_trades_have_valid_structure():
    """Test that seeded trades have valid IR swap structure."""
    client = TestClient(app)
    
    # Seed one trade
    seed_response = client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 1
        }
    )
    
    trade_id = seed_response.json()["trade_ids"][0]
    
    # Load the trade
    load_response = client.post("/load/id", json={"id": trade_id})
    assert load_response.status_code == 200
    
    trade = load_response.json()
    
    # Verify structure
    assert "id" in trade
    assert "data" in trade
    assert "general" in trade["data"]
    assert "common" in trade["data"]
    assert "swapDetails" in trade["data"]
    assert "swapLegs" in trade["data"]
    
    # Verify general section
    assert trade["data"]["general"]["tradeId"] == trade_id
    assert trade["data"]["general"]["transactionRoles"]["priceMaker"] in ["kbagci", "vmenon", "nseeley"]
    
    # Verify common section (no trader field)
    assert "trader" not in trade["data"]["common"]
    assert "book" in trade["data"]["common"]
    assert "counterparty" in trade["data"]["common"]
    
    # Verify swap legs
    assert len(trade["data"]["swapLegs"]) == 2
    
    # Verify schedules exist and are populated
    fixed_leg = trade["data"]["swapLegs"][0]
    floating_leg = trade["data"]["swapLegs"][1]
    
    assert "schedule" in fixed_leg
    assert "schedule" in floating_leg
    assert len(fixed_leg["schedule"]) > 0
    assert len(floating_leg["schedule"]) > 0
    assert len(fixed_leg["schedule"]) == len(floating_leg["schedule"])
    
    # Verify schedule periods have required fields
    for period in fixed_leg["schedule"]:
        assert "periodIndex" in period
        assert "startDate" in period
        assert "endDate" in period
        assert "paymentDate" in period
        assert "rate" in period
        assert "notional" in period
    
    for period in floating_leg["schedule"]:
        assert "periodIndex" in period
        assert "startDate" in period
        assert "endDate" in period
        assert "paymentDate" in period
        assert "notional" in period
        assert "margin" in period


def test_seeded_trades_have_schedule_variations():
    """Test that seeded trades have varying numbers of schedule periods."""
    client = TestClient(app)
    
    # Seed multiple trades
    seed_response = client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 10
        }
    )
    
    trade_ids = seed_response.json()["trade_ids"]
    
    # Check schedule lengths
    schedule_lengths = set()
    for trade_id in trade_ids:
        load_response = client.post("/load/id", json={"id": trade_id})
        trade = load_response.json()
        schedule_length = len(trade["data"]["swapLegs"][0]["schedule"])
        schedule_lengths.add(schedule_length)
    
    # Should have variation (at least 2 different lengths)
    assert len(schedule_lengths) >= 2
    # All should be between 1 and 6
    assert all(1 <= length <= 6 for length in schedule_lengths)


def test_purge_endpoint_clears_store():
    """Test that purge endpoint clears all trades."""
    client = TestClient(app)
    
    # Seed some trades
    client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 10
        }
    )
    
    # Verify trades exist
    count_response = client.post("/list/count", json={"filter": {}})
    assert count_response.json()["count"] == 10
    
    # Purge the store
    purge_response = client.post(
        "/admin/purge",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "purge",
                "intent": "integration_test"
            }
        }
    )
    
    assert purge_response.status_code == 200
    data = purge_response.json()
    assert data["message"] == "Store purged successfully"
    assert data["trades_deleted"] == 10
    
    # Verify store is empty
    count_response = client.post("/list/count", json={"filter": {}})
    assert count_response.json()["count"] == 0


def test_purge_endpoint_validates_context():
    """Test that purge endpoint requires valid context."""
    client = TestClient(app)
    
    # Missing context
    response = client.post("/admin/purge", json={})
    
    assert response.status_code == 422


def test_purge_empty_store():
    """Test that purging an empty store works."""
    client = TestClient(app)
    
    # Purge empty store
    purge_response = client.post(
        "/admin/purge",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "purge",
                "intent": "integration_test"
            }
        }
    )
    
    assert purge_response.status_code == 200
    data = purge_response.json()
    assert data["trades_deleted"] == 0


def test_seed_after_purge():
    """Test that seeding works after purging."""
    client = TestClient(app)
    
    # Seed, purge, seed again
    client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 5
        }
    )
    
    client.post(
        "/admin/purge",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "purge",
                "intent": "integration_test"
            }
        }
    )
    
    seed_response = client.post(
        "/admin/seed",
        json={
            "context": {
                "user": "test_admin",
                "agent": "test_client",
                "action": "seed",
                "intent": "integration_test"
            },
            "count": 3
        }
    )
    
    assert seed_response.status_code == 201
    assert seed_response.json()["trades_created"] == 3
    
    # Verify count
    count_response = client.post("/list/count", json={"filter": {}})
    assert count_response.json()["count"] == 3
