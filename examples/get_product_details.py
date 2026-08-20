#!/usr/bin/env python3
"""
Example: Fetching detailed component specifications, parametric attributes,
and datasheet links for a specific part.
"""
import sys
from pathlib import Path

# Allow running directly from repository root or examples directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from digikey import DigiKey

def main():
    dk = DigiKey()
    part = "NE555P"
    print(f"📦 Fetching full product details for '{part}'...")

    product = dk.products.get_details(part)

    print("\n" + "=" * 60)
    print(f"{product.manufacturer.name} - {product.manufacturer_part_number}")
    print("=" * 60)
    print(f"DigiKey Part #:    {product.digikey_part_number}")
    print(f"Description:       {product.description}")
    print(f"Status:            {product.product_status}")
    print(f"Stock Available:   {product.quantity_available:,} units")
    print(f"Datasheet:         {product.datasheet_url or 'N/A'}")
    print(f"Photo:             {product.photo_url or 'N/A'}")

    if product.parameters:
        print("\nParametric Specifications (Top 6):")
        for p in product.parameters[:6]:
            print(f"  • {p.parameter:<30}: {p.value}")

if __name__ == "__main__":
    main()
