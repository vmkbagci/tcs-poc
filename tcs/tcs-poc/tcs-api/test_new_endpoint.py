"""Quick test script for /new endpoint."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trade_api.models import TradeTemplateFactory

# Test factory directly
print("Testing TradeTemplateFactory...")
factory = TradeTemplateFactory(template_dir="templates", schema_version="v1")

print(f"Factory: {factory}")
print(f"Available types: {factory.get_available_types()}")
print(f"Available IRS subtypes: {factory.get_available_subtypes('irs')}")
print(f"Available leg types: {factory.get_available_leg_types()}")

# Test creating assembler
print("\nCreating assembler for Vanilla EUR IRS...")
assembler = factory.create_assembler(
    trade_type="irs",
    subtype="vanilla",
    currency="eur",
    leg_configs=[
        {"type": "fixed", "legType": "Pay"},
        {"type": "floating-ibor", "legType": "Receive"}
    ]
)

print(f"Assembler: {assembler}")

# Assemble trade
print("\nAssembling trade...")
trade_dict = assembler.assemble()

print(f"Trade keys: {list(trade_dict.keys())}")
print(f"Trade type: {trade_dict.get('tradeType')}")
print(f"Asset class: {trade_dict.get('assetClass')}")
print(f"Leg count: {len(trade_dict.get('legs', []))}")

if 'legs' in trade_dict:
    for i, leg in enumerate(trade_dict['legs']):
        print(f"  Leg {i}: type={leg.get('rateType')}, legType={leg.get('legType')}")

print("\n✅ Factory test successful!")