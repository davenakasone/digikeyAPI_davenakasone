#!/usr/bin/env python3
"""
Example: Browsing DigiKey product taxonomy and categories.
"""
import sys
from pathlib import Path

# Allow running directly from repository root or examples directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from digikey import DigiKey

def main():
    dk = DigiKey()
    print("📁 Fetching top-level categories from DigiKey Reference API...")

    categories = dk.reference.get_categories()
    print(f"✅ Found {len(categories)} top-level categories:\n")

    for cat in categories[:10]:
        print(f" • [ID {cat.category_id:>5}] {cat.name} ({cat.product_count:,} products)")
        for child in cat.children[:3]:
            print(f"     └─ [ID {child.category_id:>5}] {child.name} ({child.product_count:,} products)")

if __name__ == "__main__":
    main()
