# DigiKey Python SDK (`digikey-python`)

A type-safe, production-grade Python SDK for DigiKey API v4 with automated OAuth 2.0 token management, hierarchical credential discovery, parametric search, and structured data models.

---

## Features

- **Automated OAuth 2.0:** Handles 2-legged (`client_credentials`) token acquisition, caching, and auto-refresh before expiration. Also supports 3-legged (`authorization_code`) flows.
- **Hierarchical Credential Discovery:** Discovers credentials seamlessly from explicit arguments, centralized vault (`~/___СОВЕРШННО_СЕКРЕТНО/digikey.env`), local `.env`, or environment variables.
- **Dedicated Services:**
  - `dk.products`: Keyword search, MPN lookup, DKPN lookup, auto-complete suggestions.
  - `dk.reference`: Taxonomy & category trees, manufacturers, packaging types.
  - `dk.barcode`: 2D DataMatrix packaging barcode decoding.
  - `dk.orders`: Order status and tracking numbers.
  - `dk.mylists`: BOM and saved lists management.
  - `dk.quotes`: Custom pricing quote requests.
- **Strongly-Typed Models:** Returns structured dataclasses with helper utilities (`.unit_price_at(qty)`, `.in_stock`, `.get_parameter()`).
- **Resilient Transport:** Built-in retries with exponential backoff on `429 Too Many Requests` and network drops.

---

## Installation

```bash
pip install -e .
```

---

## Quickstart

```python
from digikey import DigiKey

# Initialize client (automatically finds credentials)
dk = DigiKey()

# 1. Search for parts
results = dk.products.search("STM32F407", limit=5)
for prod in results.items:
    print(f"{prod.manufacturer.name} - {prod.manufacturer_part_number}")
    print(f"  In Stock:   {prod.quantity_available:,}")
    print(f"  Base Price: ${prod.unit_price}")
    print(f"  Price @ 100 qty: ${prod.unit_price_at(100)}")

# 2. Get full part specifications & datasheet
details = dk.products.get_details("NE555P")
print(f"Datasheet: {details.datasheet_url}")
print(f"Frequency: {details.get_parameter('Frequency')}")

# 3. Explore category taxonomy
categories = dk.reference.get_categories()
for cat in categories[:5]:
    print(f"Category: {cat.name} ({cat.product_count:,} products)")
```

---

## Running Examples

```bash
python examples/search_parts.py
python examples/get_product_details.py
python examples/category_browser.py
```

---

## Running Unit Tests

```bash
python -m unittest discover tests
```

---

## License

MIT
