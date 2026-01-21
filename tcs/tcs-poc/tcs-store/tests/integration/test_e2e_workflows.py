"""End-to-end integration tests for complete workflows."""

import pytest
from fastapi.testclient import TestClient

from tcs_store.main import app, store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the store before each test."""
    store.clear()
    yield
    store.clear()


client = TestClient(app)


class TestCompleteWorkflows:
    """Test complete workflows with context metadata."""
    
    def test_save_load_update_delete_workflow(self):
        """Test complete workflow: save → load → update → delete with context."""
        # Step 1: Save a new trade
        save_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "workflow-trade-001",
                "data": {
                    "trade_type": "IR_SWAP",
                    "counterparty": "BANK_A",
                    "notional": 1000000,
                    "trade_date": "2024-01-15"
                }
            }
        }
        
        save_response = client.post("/save/new", json=save_request)
        assert save_response.status_code == 201
        assert save_response.json()["id"] == "workflow-trade-001"
        
        # Step 2: Load the trade
        load_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "load",
                "intent": "view_trade"
            },
            "id": "workflow-trade-001"
        }
        
        load_response = client.post("/load/id", json=load_request)
        assert load_response.status_code == 200
        loaded_trade = load_response.json()
        assert loaded_trade["id"] == "workflow-trade-001"
        assert loaded_trade["data"]["notional"] == 1000000
        
        # Step 3: Update the trade
        update_request = {
            "context": {
                "user": "trader_bob",
                "agent": "trading_platform",
                "action": "save_update",
                "intent": "trade_correction"
            },
            "trade": {
                "id": "workflow-trade-001",
                "data": {
                    "trade_type": "IR_SWAP",
                    "counterparty": "BANK_B",
                    "notional": 2000000,
                    "trade_date": "2024-01-15"
                }
            }
        }
        
        update_response = client.post("/save/update", json=update_request)
        assert update_response.status_code == 200
        updated_trade = update_response.json()
        assert updated_trade["data"]["counterparty"] == "BANK_B"
        assert updated_trade["data"]["notional"] == 2000000
        
        # Step 4: Verify the update by loading again
        verify_response = client.post("/load/id", json=load_request)
        assert verify_response.status_code == 200
        verified_trade = verify_response.json()
        assert verified_trade["data"]["counterparty"] == "BANK_B"
        
        # Step 5: Delete the trade
        delete_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "trade_cancellation"
            },
            "id": "workflow-trade-001"
        }
        
        delete_response = client.post("/delete/id", json=delete_request)
        assert delete_response.status_code == 200
        
        # Step 6: Verify deletion
        final_load_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "load",
                "intent": "verify_deletion"
            },
            "id": "workflow-trade-001"
        }
        final_load_response = client.post("/load/id", json=final_load_request)
        assert final_load_response.status_code == 404
    
    def test_partial_update_workflow(self):
        """Test workflow with partial updates preserving fields."""
        # Step 1: Save initial trade with nested structure
        save_request = {
            "context": {
                "user": "trader_charlie",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "partial-trade-001",
                "data": {
                    "trade_type": "IR_SWAP",
                    "counterparty": "BANK_A",
                    "notional": 1000000,
                    "leg1": {
                        "notional": 1000000,
                        "schedule": {
                            "start_date": "2024-01-01",
                            "end_date": "2025-01-01",
                            "frequency": "quarterly"
                        }
                    },
                    "leg2": {
                        "notional": 1000000,
                        "schedule": {
                            "start_date": "2024-01-01",
                            "end_date": "2025-01-01",
                            "frequency": "semi-annual"
                        }
                    }
                }
            }
        }
        
        save_response = client.post("/save/new", json=save_request)
        assert save_response.status_code == 201
        
        # Step 2: Partial update - modify only leg1 schedule
        partial_request = {
            "context": {
                "user": "trader_charlie",
                "agent": "trading_platform",
                "action": "save_partial",
                "intent": "schedule_adjustment"
            },
            "id": "partial-trade-001",
            "updates": {
                "data": {
                    "leg1": {
                        "schedule": {
                            "end_date": "2026-01-01"
                        }
                    }
                }
            }
        }
        
        partial_response = client.post("/save/partial", json=partial_request)
        assert partial_response.status_code == 200
        
        # Step 3: Verify partial update preserved other fields
        load_request = {
            "context": {
                "user": "trader_charlie",
                "agent": "trading_platform",
                "action": "load",
                "intent": "verify_update"
            },
            "id": "partial-trade-001"
        }
        load_response = client.post("/load/id", json=load_request)
        assert load_response.status_code == 200
        
        result = load_response.json()
        # Verify leg1 schedule was updated
        assert result["data"]["leg1"]["schedule"]["end_date"] == "2026-01-01"
        # Verify leg1 schedule preserved other fields
        assert result["data"]["leg1"]["schedule"]["start_date"] == "2024-01-01"
        assert result["data"]["leg1"]["schedule"]["frequency"] == "quarterly"
        # Verify leg1 notional was preserved
        assert result["data"]["leg1"]["notional"] == 1000000
        # Verify leg2 was completely preserved
        assert result["data"]["leg2"]["schedule"]["end_date"] == "2025-01-01"
        assert result["data"]["leg2"]["schedule"]["frequency"] == "semi-annual"
        # Verify top-level fields preserved
        assert result["data"]["counterparty"] == "BANK_A"
        assert result["data"]["notional"] == 1000000
    
    def test_bulk_operations_workflow(self):
        """Test workflow with bulk save, load, and delete operations."""
        # Step 1: Save multiple trades
        trades = []
        for i in range(5):
            save_request = {
                "context": {
                    "user": f"trader_{i}",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "bulk_trade_booking"
                },
                "trade": {
                    "id": f"bulk-trade-{i:03d}",
                    "data": {
                        "trade_type": "IR_SWAP",
                        "counterparty": f"BANK_{chr(65 + i)}",
                        "notional": (i + 1) * 1000000
                    }
                }
            }
            
            response = client.post("/save/new", json=save_request)
            assert response.status_code == 201
            trades.append(save_request["trade"]["id"])
        
        # Step 2: Load multiple trades
        load_group_request = {
            "context": {
                "user": "admin",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "bulk_review"
            },
            "ids": trades
        }
        
        load_response = client.post("/load/group", json=load_group_request)
        assert load_response.status_code == 200
        load_result = load_response.json()
        assert len(load_result["trades"]) == 5
        assert len(load_result["missing_ids"]) == 0
        
        # Step 3: Load with some missing IDs
        mixed_ids = trades[:3] + ["non-existent-1", "non-existent-2"]
        mixed_load_request = {
            "context": {
                "user": "admin",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "bulk_review"
            },
            "ids": mixed_ids
        }
        
        mixed_response = client.post("/load/group", json=mixed_load_request)
        assert mixed_response.status_code == 200
        mixed_result = mixed_response.json()
        assert len(mixed_result["trades"]) == 3
        assert len(mixed_result["missing_ids"]) == 2
        assert "non-existent-1" in mixed_result["missing_ids"]
        assert "non-existent-2" in mixed_result["missing_ids"]
        
        # Step 4: Delete multiple trades
        delete_group_request = {
            "context": {
                "user": "admin",
                "agent": "trading_platform",
                "action": "delete_group",
                "intent": "bulk_cleanup"
            },
            "ids": trades[:3]
        }
        
        delete_response = client.post("/delete/group", json=delete_group_request)
        assert delete_response.status_code == 200
        delete_result = delete_response.json()
        assert delete_result["deleted_count"] == 3
        assert len(delete_result["missing_ids"]) == 0
        
        # Step 5: Verify remaining trades
        remaining_request = {
            "context": {
                "user": "admin",
                "agent": "trading_platform",
                "action": "load_group",
                "intent": "verify_deletion"
            },
            "ids": trades
        }
        remaining_response = client.post("/load/group", json=remaining_request)
        assert remaining_response.status_code == 200
        remaining_result = remaining_response.json()
        assert len(remaining_result["trades"]) == 2
        assert len(remaining_result["missing_ids"]) == 3
    
    def test_filter_workflow(self):
        """Test workflow with filtering operations."""
        # Step 1: Save trades with different attributes
        trades_data = [
            {
                "id": "filter-trade-001",
                "trade_type": "IR_SWAP",
                "counterparty": "BANK_A",
                "notional": 1000000,
                "trade_date": "2024-01-15"
            },
            {
                "id": "filter-trade-002",
                "trade_type": "IR_SWAP",
                "counterparty": "BANK_B",
                "notional": 2000000,
                "trade_date": "2024-02-20"
            },
            {
                "id": "filter-trade-003",
                "trade_type": "FX_SWAP",
                "counterparty": "BANK_A",
                "notional": 1500000,
                "trade_date": "2024-03-10"
            },
            {
                "id": "filter-trade-004",
                "trade_type": "IR_SWAP",
                "counterparty": "BANK_C",
                "notional": 3000000,
                "trade_date": "2024-04-05"
            }
        ]
        
        for trade_data in trades_data:
            save_request = {
                "context": {
                    "user": "trader_filter",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "test_data_setup"
                },
                "trade": {
                    "id": trade_data["id"],
                    "data": {k: v for k, v in trade_data.items() if k != "id"}
                }
            }
            response = client.post("/save/new", json=save_request)
            assert response.status_code == 201
        
        # Step 2: Filter by trade type
        filter_request = {
            "context": {
                "user": "trader_filter",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"}
                }
            }
        }
        
        filter_response = client.post("/load/filter", json=filter_request)
        assert filter_response.status_code == 200
        filter_result = filter_response.json()
        assert len(filter_result) == 3
        assert all(t["data"]["trade_type"] == "IR_SWAP" for t in filter_result)
        
        # Step 3: Filter by counterparty
        counterparty_filter = {
            "context": {
                "user": "trader_filter",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.counterparty": {"eq": "BANK_A"}
                }
            }
        }
        
        counterparty_response = client.post("/load/filter", json=counterparty_filter)
        assert counterparty_response.status_code == 200
        counterparty_result = counterparty_response.json()
        assert len(counterparty_result) == 2
        
        # Step 4: Filter by notional range
        range_filter = {
            "context": {
                "user": "trader_filter",
                "agent": "trading_platform",
                "action": "load_filter",
                "intent": "search_trades"
            },
            "filter": {
                "filter": {
                    "data.notional": {"gte": 1500000, "lte": 2500000}
                }
            }
        }
        
        range_response = client.post("/load/filter", json=range_filter)
        assert range_response.status_code == 200
        range_result = range_response.json()
        assert len(range_result) == 2
        
        # Step 5: Count trades matching filter
        count_request = {
            "context": {
                "user": "trader_filter",
                "agent": "trading_platform",
                "action": "count",
                "intent": "get_count"
            },
            "filter": {
                "filter": {
                    "data.trade_type": {"eq": "IR_SWAP"}
                }
            }
        }
        
        count_response = client.post("/list/count", json=count_request)
        assert count_response.status_code == 200
        count_result = count_response.json()
        assert count_result["count"] == 3
        
        # Step 6: List trades matching filter
        list_request = {
            "context": {
                "user": "trader_filter",
                "agent": "trading_platform",
                "action": "list",
                "intent": "list_trades"
            },
            "filter": {
                "filter": {
                    "data.counterparty": {"eq": "BANK_A"}
                }
            }
        }
        
        list_response = client.post("/list", json=list_request)
        assert list_response.status_code == 200
        list_result = list_response.json()
        assert len(list_result) == 2
    
    def test_realistic_trade_workflow(self):
        """Test workflow with realistic trade payloads."""
        # Step 1: Save a realistic IR swap trade
        realistic_trade = {
            "context": {
                "user": "trader_john_doe",
                "agent": "bloomberg_terminal",
                "action": "save_new",
                "intent": "client_trade_booking"
            },
            "trade": {
                "id": "IR-SWAP-2024-001-ABC123",
                "data": {
                    "trade_type": "IR_SWAP",
                    "trade_date": "2024-01-15",
                    "effective_date": "2024-01-17",
                    "maturity_date": "2029-01-17",
                    "counterparty": "JPMORGAN_CHASE",
                    "notional": 50000000,
                    "currency": "USD",
                    "leg1": {
                        "type": "fixed",
                        "notional": 50000000,
                        "rate": 0.0425,
                        "day_count": "30/360",
                        "payment_frequency": "semi-annual",
                        "schedule": {
                            "start_date": "2024-01-17",
                            "end_date": "2029-01-17",
                            "payment_dates": [
                                "2024-07-17", "2025-01-17", "2025-07-17",
                                "2026-01-17", "2026-07-17", "2027-01-17",
                                "2027-07-17", "2028-01-17", "2028-07-17",
                                "2029-01-17"
                            ]
                        }
                    },
                    "leg2": {
                        "type": "floating",
                        "notional": 50000000,
                        "index": "USD-LIBOR-3M",
                        "spread": 0.0025,
                        "day_count": "ACT/360",
                        "payment_frequency": "quarterly",
                        "schedule": {
                            "start_date": "2024-01-17",
                            "end_date": "2029-01-17",
                            "reset_dates": [
                                "2024-01-17", "2024-04-17", "2024-07-17",
                                "2024-10-17", "2025-01-17"
                                # ... more dates
                            ]
                        }
                    },
                    "collateral": {
                        "type": "CSA",
                        "threshold": 1000000,
                        "minimum_transfer": 500000
                    },
                    "booking_system": "Murex",
                    "trader": "John Doe",
                    "sales": "Jane Smith",
                    "desk": "USD Rates"
                }
            }
        }
        
        save_response = client.post("/save/new", json=realistic_trade)
        assert save_response.status_code == 201
        
        # Step 2: Partial update - adjust collateral terms
        collateral_update = {
            "context": {
                "user": "risk_manager",
                "agent": "risk_system",
                "action": "save_partial",
                "intent": "collateral_adjustment"
            },
            "id": "IR-SWAP-2024-001-ABC123",
            "updates": {
                "data": {
                    "collateral": {
                        "threshold": 500000,
                        "minimum_transfer": 250000
                    }
                }
            }
        }
        
        update_response = client.post("/save/partial", json=collateral_update)
        assert update_response.status_code == 200
        
        # Step 3: Verify update preserved all other fields
        load_request = {
            "context": {
                "user": "risk_manager",
                "agent": "risk_system",
                "action": "load",
                "intent": "verify_update"
            },
            "id": "IR-SWAP-2024-001-ABC123"
        }
        load_response = client.post("/load/id", json=load_request)
        assert load_response.status_code == 200
        
        result = load_response.json()
        # Verify collateral was updated
        assert result["data"]["collateral"]["threshold"] == 500000
        assert result["data"]["collateral"]["minimum_transfer"] == 250000
        assert result["data"]["collateral"]["type"] == "CSA"  # Preserved
        # Verify legs were preserved
        assert result["data"]["leg1"]["rate"] == 0.0425
        assert result["data"]["leg2"]["index"] == "USD-LIBOR-3M"
        # Verify other fields preserved
        assert result["data"]["notional"] == 50000000
        assert result["data"]["trader"] == "John Doe"


class TestOperationLogTracking:
    """Test that context metadata is logged for lifecycle tracing."""
    
    def test_operation_log_contains_context(self):
        """Test that mutating operations log context metadata."""
        # Clear operation log
        store.clear()
        
        # Step 1: Save a trade
        save_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "log-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        client.post("/save/new", json=save_request)
        
        # Step 2: Update the trade
        update_request = {
            "context": {
                "user": "trader_bob",
                "agent": "trading_platform",
                "action": "save_update",
                "intent": "trade_correction"
            },
            "trade": {
                "id": "log-trade-001",
                "data": {"trade_type": "FX_SWAP"}
            }
        }
        
        client.post("/save/update", json=update_request)
        
        # Step 3: Partial update
        partial_request = {
            "context": {
                "user": "trader_charlie",
                "agent": "risk_system",
                "action": "save_partial",
                "intent": "risk_adjustment"
            },
            "id": "log-trade-001",
            "updates": {
                "data": {"notional": 1000000}
            }
        }
        
        client.post("/save/partial", json=partial_request)
        
        # Step 4: Delete the trade
        delete_request = {
            "context": {
                "user": "admin",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "trade_cancellation"
            },
            "id": "log-trade-001"
        }
        
        client.post("/delete/id", json=delete_request)
        
        # Step 5: Verify operation log
        operation_log = store.get_operation_log()
        
        # Should have 4 operations logged
        assert len(operation_log) >= 4
        
        # Verify each operation has context metadata
        for operation in operation_log:
            assert "timestamp" in operation
            assert "context" in operation
            assert "operation" in operation
            assert "trade_id" in operation
            
            # Verify context has all required fields
            context = operation["context"]
            assert "user" in context
            assert "agent" in context
            assert "action" in context
            assert "intent" in context
        
        # Verify specific operations
        save_ops = [op for op in operation_log if op["operation"] == "save"]
        assert len(save_ops) >= 3  # Initial save, full update, and partial update
        
        # Verify first save operation
        first_save = save_ops[0]
        assert first_save["context"]["user"] == "trader_alice"
        assert first_save["context"]["intent"] == "new_trade_booking"
        assert first_save["trade_id"] == "log-trade-001"
        
        # Verify update operations (also logged as "save")
        if len(save_ops) >= 2:
            second_save = save_ops[1]
            assert second_save["context"]["user"] == "trader_bob"
            assert second_save["context"]["intent"] == "trade_correction"
        
        if len(save_ops) >= 3:
            third_save = save_ops[2]
            assert third_save["context"]["user"] == "trader_charlie"
            assert third_save["context"]["intent"] == "risk_adjustment"
        
        delete_op = next(op for op in operation_log if op["operation"] == "delete")
        assert delete_op["context"]["user"] == "admin"
        assert delete_op["context"]["intent"] == "trade_cancellation"
    
    def test_read_operations_do_not_log_context(self):
        """Test that read operations don't require or log context."""
        # Save a trade first
        save_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "read-trade-001",
                "data": {"trade_type": "IR_SWAP"}
            }
        }
        
        client.post("/save/new", json=save_request)
        
        # Get initial log count
        initial_log = store.get_operation_log()
        initial_count = len(initial_log)
        
        # Perform read operations (with context as currently required)
        load_response = client.post("/load/id", json={
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "load",
                "intent": "view_trade"
            },
            "id": "read-trade-001"
        })
        assert load_response.status_code == 200
        
        list_response = client.post("/list", json={
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "list",
                "intent": "list_trades"
            },
            "filter": {}
        })
        assert list_response.status_code == 200
        
        count_response = client.post("/list/count", json={
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "count",
                "intent": "count_trades"
            },
            "filter": {}
        })
        assert count_response.status_code == 200
        
        # Verify operation log didn't grow (read operations don't log)
        final_log = store.get_operation_log()
        assert len(final_log) == initial_count


class TestMultipleOperationsSequence:
    """Test sequences of multiple operations."""
    
    def test_multiple_updates_sequence(self):
        """Test multiple sequential updates to the same trade."""
        # Save initial trade
        save_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": "seq-trade-001",
                "data": {
                    "version": 1,
                    "notional": 1000000,
                    "counterparty": "BANK_A"
                }
            }
        }
        
        client.post("/save/new", json=save_request)
        
        # Perform multiple partial updates
        for i in range(2, 6):
            partial_request = {
                "context": {
                    "user": f"trader_{i}",
                    "agent": "trading_platform",
                    "action": "save_partial",
                    "intent": f"update_version_{i}"
                },
                "id": "seq-trade-001",
                "updates": {
                    "data": {
                        "version": i,
                        "notional": i * 1000000
                    }
                }
            }
            
            response = client.post("/save/partial", json=partial_request)
            assert response.status_code == 200
        
        # Verify final state
        load_request = {
            "context": {
                "user": "admin",
                "agent": "trading_platform",
                "action": "load",
                "intent": "verify_updates"
            },
            "id": "seq-trade-001"
        }
        load_response = client.post("/load/id", json=load_request)
        assert load_response.status_code == 200
        
        result = load_response.json()
        assert result["data"]["version"] == 5
        assert result["data"]["notional"] == 5000000
        assert result["data"]["counterparty"] == "BANK_A"  # Preserved through all updates
    
    def test_save_delete_save_sequence(self):
        """Test saving, deleting, then saving again with same ID."""
        trade_id = "reuse-trade-001"
        
        # Save trade
        save_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": trade_id,
                "data": {"version": 1}
            }
        }
        
        response1 = client.post("/save/new", json=save_request)
        assert response1.status_code == 201
        
        # Delete trade
        delete_request = {
            "context": {
                "user": "trader_alice",
                "agent": "trading_platform",
                "action": "delete",
                "intent": "trade_cancellation"
            },
            "id": trade_id
        }
        
        delete_response = client.post("/delete/id", json=delete_request)
        assert delete_response.status_code == 200
        
        # Save trade again with same ID (should succeed)
        save_request2 = {
            "context": {
                "user": "trader_bob",
                "agent": "trading_platform",
                "action": "save_new",
                "intent": "new_trade_booking"
            },
            "trade": {
                "id": trade_id,
                "data": {"version": 2}
            }
        }
        
        response2 = client.post("/save/new", json=save_request2)
        assert response2.status_code == 201
        
        # Verify new trade
        load_request = {
            "context": {
                "user": "trader_bob",
                "agent": "trading_platform",
                "action": "load",
                "intent": "verify_save"
            },
            "id": trade_id
        }
        load_response = client.post("/load/id", json=load_request)
        assert load_response.status_code == 200
        assert load_response.json()["data"]["version"] == 2
