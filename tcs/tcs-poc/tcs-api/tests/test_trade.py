"""Tests for Trade class."""

import pytest
from trade_api.models import Trade


def test_trade_initialization():
    """Test basic Trade initialization."""
    data = {
        "tradeId": "SWAP-20260114-IRS-0001",
        "tradeType": "InterestRateSwap",
        "version": 1
    }
    trade = Trade(data)
    
    assert trade.trade_id == "SWAP-20260114-IRS-0001"
    assert trade.trade_type == "InterestRateSwap"
    assert trade.version == 1


def test_trade_data_access():
    """Test direct data property access."""
    data = {"tradeId": "TEST-001", "tradeType": "TestType"}
    trade = Trade(data)
    
    assert trade.data == data
    assert trade.data is trade._data  # Direct reference


def test_trade_get_simple_property():
    """Test getting simple properties."""
    data = {
        "tradeId": "SWAP-001",
        "tradeType": "InterestRateSwap",
        "notional": 1000000
    }
    trade = Trade(data)
    
    assert trade.get("tradeId") == "SWAP-001"
    assert trade.get("tradeType") == "InterestRateSwap"
    assert trade.get("notional") == 1000000


def test_trade_get_nested_property():
    """Test getting nested properties with dot notation."""
    data = {
        "tradeId": "SWAP-001",
        "specific": {
            "rateFamily": "VanillaIRS",
            "compounding": "None"
        },
        "legs": [
            {"legId": "FIXED", "legType": "Fixed"},
            {"legId": "FLOAT", "legType": "Floating"}
        ]
    }
    trade = Trade(data)
    
    assert trade.get("specific.rateFamily") == "VanillaIRS"
    assert trade.get("specific.compounding") == "None"
    assert trade.get("legs.0.legId") == "FIXED"
    assert trade.get("legs.1.legType") == "Floating"


def test_trade_get_with_default():
    """Test getting properties with default values."""
    data = {"tradeId": "SWAP-001"}
    trade = Trade(data)
    
    assert trade.get("nonexistent") is None
    assert trade.get("nonexistent", "default") == "default"
    assert trade.get("nested.property", 42) == 42


def test_trade_set_simple_property():
    """Test setting simple properties."""
    data = {"tradeId": "SWAP-001"}
    trade = Trade(data)
    
    trade.set("tradeType", "InterestRateSwap")
    assert trade.get("tradeType") == "InterestRateSwap"
    assert trade.data["tradeType"] == "InterestRateSwap"


def test_trade_set_nested_property():
    """Test setting nested properties with dot notation."""
    data = {"tradeId": "SWAP-001"}
    trade = Trade(data)
    
    trade.set("specific.rateFamily", "VanillaIRS")
    assert trade.get("specific.rateFamily") == "VanillaIRS"
    assert "specific" in trade.data
    assert trade.data["specific"]["rateFamily"] == "VanillaIRS"


def test_trade_set_list_property():
    """Test setting properties in existing lists."""
    data = {
        "tradeId": "SWAP-001",
        "legs": [
            {"legId": "FIXED"},
            {"legId": "FLOAT"}
        ]
    }
    trade = Trade(data)
    
    trade.set("legs.0.legType", "Fixed")
    assert trade.get("legs.0.legType") == "Fixed"


def test_trade_equality():
    """Test Trade equality comparison."""
    data1 = {"tradeId": "SWAP-001", "tradeType": "IRS"}
    data2 = {"tradeId": "SWAP-001", "tradeType": "IRS"}
    data3 = {"tradeId": "SWAP-002", "tradeType": "IRS"}
    
    trade1 = Trade(data1)
    trade2 = Trade(data2)
    trade3 = Trade(data3)
    
    assert trade1 == trade2
    assert trade1 != trade3


def test_trade_repr():
    """Test Trade string representation."""
    data = {"tradeId": "SWAP-001", "tradeType": "InterestRateSwap"}
    trade = Trade(data)
    
    repr_str = repr(trade)
    assert "SWAP-001" in repr_str
    assert "InterestRateSwap" in repr_str


def test_trade_preserves_json_flexibility():
    """Test that Trade preserves arbitrary JSON structures."""
    # Complex nested structure with various types
    data = {
        "tradeId": "SWAP-001",
        "customField": "custom_value",
        "nested": {
            "deep": {
                "property": "value"
            }
        },
        "array": [1, 2, 3],
        "mixed": {
            "numbers": [10, 20],
            "strings": ["a", "b"]
        }
    }
    trade = Trade(data)
    
    # All properties should be accessible
    assert trade.get("customField") == "custom_value"
    assert trade.get("nested.deep.property") == "value"
    assert trade.get("array.0") == 1
    assert trade.get("mixed.numbers.1") == 20
    
    # Original structure preserved
    assert trade.data == data