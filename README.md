# DigiKey Python SDK (`digikey-python`)

A type-safe, production-grade Python SDK for **DigiKey API v4** with automated OAuth 2.0 token management, hierarchical cross-platform credential discovery, token-bucket rate limiting, interactive CLI tools, automated health diagnostics, and structured hardware data models.

---

## ⚡ Features

- **Automated OAuth 2.0:** Handles 2-legged (`client_credentials`) token acquisition, caching, and auto-refresh before expiration. Also supports 3-legged (`authorization_code`) flows.
- **Cross-Platform Credential Discovery:** Discovers credentials seamlessly from explicit arguments, `$DIGIKEY_ENV_PATH`, local `./.env`, standard user home files (`~/.digikey.env`, `~/.config/digikey/.env`), or Windows `%APPDATA%\digikey\.env` / environment variables.
- **Client-Side Token Bucket Rate Limiter:** Built-in rate limiting (default: 10 req/s) prevents accidental quota burn and Apigee WAF throttling, with live quota tracking (`dk.rate_limit_remaining`).
- **Dedicated Services:**
  - `dk.products`: Keyword search, MPN lookup, DKPN direct details, parametric filtering, and in-stock alternate finder.
  - `dk.reference`: Taxonomy & category trees, manufacturers directory (3,700+ suppliers).
  - `dk.doctor`: Comprehensive API health auditor and diagnostic suite.
  - `dk.barcode`: 2D DataMatrix packaging barcode decoding.
  - `dk.orders`: Order status and tracking numbers.
  - `dk.mylists`: BOM and saved lists management.
  - `dk.quotes`: Custom pricing quote requests.
- **PCB Design & BOM Workflow Tooling:**
  - Automated CSV BOM scrubber and enricher (`python -m digikey bom <file.csv>`).
  - Datasheet auto-downloader (`prod.download_datasheet()`).
  - Diagnostic auditor (`python -m digikey doctor`).
- **Autonomous Health Inspector:** Includes scheduled GitHub Actions CI workflow for continuous API and endpoint drift audits.
- **Strict Grounding Rule:** Adheres to a strict "I don't know" policy on ambiguous or unverified API responses to prevent LLM hallucinations in hardware design.

---

## 📦 Installation

Install in editable mode for development or directly into your virtual environment:

```bash
pip install -e .
```

---

## 🔑 Credential Setup

You only need to set your credentials once. The SDK auto-detects them in any of the following locations:

### macOS / Linux
Add to `~/.zshrc` or `~/.bashrc`:
```bash
export DIGIKEY_CLIENT_ID="your_client_id_here"
export DIGIKEY_CLIENT_SECRET="your_client_secret_here"
# Or point to a central vault file:
export DIGIKEY_ENV_PATH="$HOME/.secrets/digikey.env"
```

### Windows (PowerShell)
```powershell
[System.Environment]::SetEnvironmentVariable('DIGIKEY_CLIENT_ID', 'your_client_id_here', 'User')
[System.Environment]::SetEnvironmentVariable('DIGIKEY_CLIENT_SECRET', 'your_client_secret_here', 'User')
```

---

## 🚀 Quickstart (Python SDK)

```python
from digikey import DigiKey

# Initialize client (auto-discovers credentials and throttles safely)
dk = DigiKey()

# 1. Search for in-stock parts
results = dk.products.search("STM32F407", limit=5, in_stock_only=True)
for prod in results.items:
    print(f"{prod.manufacturer.name} - {prod.manufacturer_part_number}")
    print(f"  In Stock:   {prod.quantity_available:,} units")
    print(f"  Base Price: ${prod.unit_price}")
    print(f"  Price @ 100 qty: ${prod.unit_price_at(100)}")

# 2. Get full part specifications & download datasheet
details = dk.products.get_details("NE555P")
print(f"Status:    {details.product_status}")
print(f"Datasheet: {details.datasheet_url}")
pdf_path = details.download_datasheet("./datasheets")
print(f"Saved to:  {pdf_path}")

# 3. Find in-stock alternate parts
alternates = dk.products.find_alternates("STM32F407VGT6", limit=3)
for alt in alternates:
    print(f"Alternate: {alt.manufacturer.name} {alt.manufacturer_part_number} (Stock: {alt.quantity_available:,})")

# 4. Check API health & live quota telemetry
print(f"Quota Remaining: {dk.rate_limit_remaining} / {dk.rate_limit_limit}")
```

---

## 🛠️ Command-Line Interface (CLI)

The package includes a rich CLI for human and agent interactive use:

```bash
# Run comprehensive health and diagnostics check
python -m digikey doctor

# Search DigiKey catalog with filters
python -m digikey search "0.1uF 0402 16V X7R" --in-stock --limit 5

# Fetch full part specifications and tiered pricing
python -m digikey details "NE555P"

# Find in-stock alternate parts
python -m digikey alternates "STM32F407VGT6"

# Browse product taxonomy categories
python -m digikey categories --limit 10

# Scrub and enrich a PCB schematic BOM (KiCad / Altium CSV)
python -m digikey bom my_board_bom.csv
```

---

## 🧪 Testing

Run the full unit test suite:

```bash
python -m unittest discover tests
```

---

## 📄 License

MIT License.
