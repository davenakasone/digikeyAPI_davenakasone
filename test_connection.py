#!/usr/bin/env python3
"""
Verification script for DigiKey API connection using the digikey package.
"""
import sys
from digikey import DigiKey, DigiKeyError

def main():
    print("=" * 65)
    print("DigiKey Python SDK - Live Integration & Verification Test")
    print("=" * 65)

    try:
        dk = DigiKey()
        masked_id = f"{dk.credentials.client_id[:6]}...{dk.credentials.client_id[-4:]}"
        print(f" Loaded Client ID: {masked_id}")
        print(" Acquiring OAuth 2.0 access token...")

        token = dk.oauth_handler.get_valid_token()
        masked_token = f"{token[:8]}...{token[-4:]}"
        print(f" OAuth Token active! ({masked_token})")

        # 1. Test Keyword Search
        query = "STM32F407VGT6"
        print(f"\n1. Testing Product Search for '{query}'...")
        page = dk.products.search(keywords=query, limit=3)
        print(f"   Found {page.total_count} matching products. Showing top {len(page.items)}:")

        for idx, p in enumerate(page.items, 1):
            print(f"   [{idx}] {p.manufacturer.name} - {p.manufacturer_part_number}")
            print(f"       Description: {p.description}")
            print(f"       In Stock:    {p.quantity_available:,} units")
            print(f"       Unit Price:  ${p.unit_price:.4f}")

        # 2. Test Categories Reference API
        print(f"\n2. Testing Reference API (Categories)...")
        categories = dk.reference.get_categories()
        print(f"   Successfully fetched {len(categories)} root categories from DigiKey.")
        if categories:
            sample_cat = categories[0]
            print(f"   Sample: ID {sample_cat.category_id} - '{sample_cat.name}'")

        print("\n" + "=" * 65)
        print(" ALL VERIFICATION TESTS PASSED! DigiKey SDK is ready for use.")
        print("=" * 65)

    except DigiKeyError as e:
        print(f"\n❌ DigiKey SDK Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
