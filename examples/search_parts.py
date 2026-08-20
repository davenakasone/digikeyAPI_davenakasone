#!/usr/bin/env python3
"""
Example: Searching the DigiKey catalog by keyword, inspecting stock,
and calculating tiered quantity pricing.
"""
import sys
from pathlib import Path

# Allow running directly from repository root or examples directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from digikey import DigiKey

def main():
    dk = DigiKey()
    keyword = "STM32F407"
    print(f"🔍 Searching DigiKey catalog for '{keyword}'...")

    results = dk.products.search(keyword, limit=3)
    print(f"✅ Found {results.total_count} total matching products:\n")

    for idx, prod in enumerate(results.items, 1):
        print(f"[{idx}] {prod.manufacturer.name} - {prod.manufacturer_part_number}")
        print(f"    DigiKey Part #: {prod.digikey_part_number}")
        print(f"    Description:    {prod.description}")
        print(f"    In Stock:       {prod.quantity_available:,} units")
        print(f"    Base Price:     ${prod.unit_price:.4f}")

        # Test tiered price calculator method
        print("    Tiered Pricing:")
        for qty in [1, 10, 100, 1000]:
            print(f"      • Qty {qty:>4}: ${prod.unit_price_at(qty):.4f}/unit")
        print()

if __name__ == "__main__":
    main()
