"""
Command-line interface (CLI) for DigiKey Python SDK.
Usage:
    python -m digikey search "STM32F407" --in-stock
    python -m digikey details "NE555P"
    python -m digikey categories
    python -m digikey alternates "STM32F407VGT6"
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List

from digikey.client import DigiKey
from digikey.core.exceptions import DigiKeyError


def format_currency(val: float) -> str:
    return f"${val:.4f}" if val < 1.0 else f"${val:.2f}"


def handle_search(args, dk: DigiKey):
    print(f"🔍 Searching DigiKey for '{args.query}' (in_stock_only={args.in_stock})...")
    page = dk.products.search(
        keywords=args.query,
        limit=args.limit,
        in_stock_only=args.in_stock,
        sort_by=args.sort,
    )
    print(f"✅ Found {page.total_count} matching product(s):\n")

    if not page.items:
        print("  No products found matching the criteria.")
        return

    for idx, p in enumerate(page.items, 1):
        print(f"[{idx}] {p.manufacturer.name} - {p.manufacturer_part_number}")
        print(f"    DigiKey Part #: {p.digikey_part_number or 'N/A'}")
        print(f"    Description:    {p.description}")
        print(f"    In Stock:       {p.quantity_available:,} units")
        print(f"    Base Price:     {format_currency(p.unit_price)}")
        if p.price_breaks:
            breaks_str = ", ".join(f"@{pb.break_quantity}: {format_currency(pb.unit_price)}" for pb in p.price_breaks[:3])
            print(f"    Price Breaks:   {breaks_str}")
        print()


def handle_details(args, dk: DigiKey):
    print(f"📦 Fetching details for '{args.part}'...")
    p = dk.products.get_details(args.part)

    print("\n" + "=" * 65)
    print(f"{p.manufacturer.name} - {p.manufacturer_part_number}")
    print("=" * 65)
    print(f"DigiKey Part #:  {p.digikey_part_number or 'N/A'}")
    print(f"Status:          {p.product_status}")
    print(f"In Stock:        {p.quantity_available:,} units")
    print(f"Unit Price:      {format_currency(p.unit_price)}")
    print(f"Description:     {p.description}")
    if p.detailed_description:
        print(f"Detailed:        {p.detailed_description}")
    print(f"Datasheet:       {p.datasheet_url or 'N/A'}")
    print(f"Photo:           {p.photo_url or 'N/A'}")

    if p.price_breaks:
        print("\nTiered Pricing:")
        for pb in p.price_breaks:
            print(f"  • Qty {pb.break_quantity:>6,}: {format_currency(pb.unit_price)}/unit")

    if p.parameters:
        print("\nParametric Specifications (Top 8):")
        for param in p.parameters[:8]:
            print(f"  • {param.parameter:<30}: {param.value}")
    print()


def handle_categories(args, dk: DigiKey):
    print("📁 Fetching DigiKey product taxonomy...")
    categories = dk.reference.get_categories()
    print(f"✅ Found {len(categories)} root categories:\n")

    for cat in categories[: args.limit]:
        print(f" • [ID {cat.category_id:>5}] {cat.name} ({cat.product_count:,} products)")
        for child in cat.children[:3]:
            print(f"     └─ [ID {child.category_id:>5}] {child.name} ({child.product_count:,} products)")


def handle_alternates(args, dk: DigiKey):
    print(f"🔄 Searching in-stock alternates for '{args.part}'...")
    alternates = dk.products.find_alternates(args.part, limit=args.limit, in_stock_only=True)

    print(f"✅ Found {len(alternates)} in-stock candidate(s):\n")
    for idx, p in enumerate(alternates, 1):
        print(f"[{idx}] {p.manufacturer.name} - {p.manufacturer_part_number}")
        print(f"    DigiKey Part #: {p.digikey_part_number or 'N/A'}")
        print(f"    In Stock:       {p.quantity_available:,} units")
        print(f"    Price:          {format_currency(p.unit_price)}")
        print(f"    Description:    {p.description}")
        print()


def handle_bom(args, dk: DigiKey):
    bom_file = Path(args.file)
    if not bom_file.exists():
        print(f"❌ File not found: {bom_file}", file=sys.stderr)
        sys.exit(1)

    print(f"📋 Scrubbing & Enriching BOM from '{bom_file.name}'...")
    enriched_rows = []

    with open(bom_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])

        # Detect part number column
        part_col = None
        for col in fieldnames:
            if col.lower().strip() in ("mpn", "part_number", "part", "mfg_part", "manufacturer part number", "partnumber"):
                part_col = col
                break
        if not part_col and fieldnames:
            part_col = fieldnames[0]

        qty_col = None
        for col in fieldnames:
            if col.lower().strip() in ("qty", "quantity", "count"):
                qty_col = col
                break

        print(f"   Using Part Column: '{part_col}', Qty Column: '{qty_col or 'Default: 1'}'\n")

        for row in reader:
            part_num = row.get(part_col, "").strip()
            if not part_num:
                continue

            qty = int(row.get(qty_col, 1)) if qty_col and row.get(qty_col) else 1

            try:
                prod = dk.products.get_details(part_num)
                row["DigiKey_Part_Number"] = prod.digikey_part_number
                row["DigiKey_Stock"] = prod.quantity_available
                row["DigiKey_Unit_Price"] = prod.unit_price
                row["DigiKey_Extended_Price"] = round(prod.unit_price_at(qty) * qty, 4)
                row["DigiKey_Status"] = prod.product_status
                row["DigiKey_Datasheet"] = prod.datasheet_url or ""
                status_icon = "🟢" if prod.in_stock else "🔴"
                print(f" {status_icon} {part_num:<25} | Stock: {prod.quantity_available:>7,} | Price: {format_currency(prod.unit_price)}")
            except Exception as e:
                row["DigiKey_Part_Number"] = "NOT_FOUND"
                row["DigiKey_Stock"] = 0
                row["DigiKey_Unit_Price"] = 0.0
                row["DigiKey_Status"] = "NOT_FOUND"
                print(f" ⚠️ {part_num:<25} | Not found in DigiKey")

            enriched_rows.append(row)

    # Save enriched BOM
    out_file = bom_file.with_name(f"{bom_file.stem}_enriched.csv")
    if enriched_rows:
        all_headers = list(enriched_rows[0].keys())
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_headers)
            writer.writeheader()
            writer.writerows(enriched_rows)
        print(f"\n💾 Enriched BOM saved to: {out_file}")


def handle_doctor(args, dk: DigiKey):
    print("🩺 Running DigiKey API Health Audit & Diagnostic Suite...")
    print("=" * 65)

    checks = dk.doctor.run_all_checks()
    all_passed = True

    for c in checks:
        icon = "✅" if c.passed else "❌"
        latency_str = f"({c.latency_ms:>5.1f}ms)" if c.latency_ms > 0 else "        "
        print(f" {icon} {c.check_name:<42} {latency_str} : {c.message}")
        if not c.passed:
            all_passed = False

    print("=" * 65)
    if all_passed:
        print("🎉 ALL SYSTEMS HEALTHY. DigiKey API endpoints and credentials verified.")
    else:
        print("⚠️ SOME DIAGNOSTIC CHECKS FAILED. Please review the errors above.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="digikey",
        description="DigiKey Python SDK CLI - Part search, details, alternates, BOM enrichment, and health diagnostics.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # doctor
    subparsers.add_parser("doctor", help="Run comprehensive API and credentials health audit")

    # search
    p_search = subparsers.add_parser("search", help="Search DigiKey catalog")
    p_search.add_argument("query", help="Keyword, MPN, or DKPN to search")
    p_search.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    p_search.add_argument("--in-stock", action="store_true", help="Only show in-stock products")
    p_search.add_argument("--sort", help="Sort field (e.g. UnitPrice)")

    # details
    p_details = subparsers.add_parser("details", help="Get full specifications & datasheet for a part")
    p_details.add_argument("part", help="MPN or DigiKey part number")

    # categories
    p_cats = subparsers.add_parser("categories", help="Browse product taxonomy")
    p_cats.add_argument("--limit", type=int, default=10, help="Number of top categories (default: 10)")

    # alternates
    p_alt = subparsers.add_parser("alternates", help="Find in-stock alternate parts")
    p_alt.add_argument("part", help="Target part number")
    p_alt.add_argument("--limit", type=int, default=5, help="Max alternates (default: 5)")

    # bom
    p_bom = subparsers.add_parser("bom", help="Scrub and enrich a CSV BOM file with pricing and stock")
    p_bom.add_argument("file", help="Path to BOM CSV file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        dk = DigiKey()
        if args.command == "doctor":
            handle_doctor(args, dk)
        elif args.command == "search":
            handle_search(args, dk)
        elif args.command == "details":
            handle_details(args, dk)
        elif args.command == "categories":
            handle_categories(args, dk)
        elif args.command == "alternates":
            handle_alternates(args, dk)
        elif args.command == "bom":
            handle_bom(args, dk)
    except DigiKeyError as e:
        print(f"❌ DigiKey API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
