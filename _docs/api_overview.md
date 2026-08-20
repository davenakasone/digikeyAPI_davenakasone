# DigiKey API Overview

This document provides a detailed breakdown of DigiKey's API products, base URLs, required headers, and environment configurations.

---

## 1. Environments & Base URLs

| Environment | Base URL | Purpose |
| :--- | :--- | :--- |
| **Production** | `https://api.digikey.com` | Live production API requests |
| **Sandbox** | `https://sandbox-api.digikey.com` | Testing without impacting live inventory/orders |

> **Requirement:** All HTTP requests must use TLS v1.2 or higher.

---

## 2. API Products Breakdown

### 1. Product Information V4 (`/products/product-information-v4`)
* **APIs Included:** 2
* **Capabilities:** 
  * Keyword search across millions of components.
  * Search by manufacturer part number (MPN) or DigiKey part number (DKPN).
  * Retrieve component specifications, parametric data, datasheets, stock counts, and tiered pricing.
* **Common Use Cases:** Inventory lookup, ERP component sync, automated BOM pricing.

### 2. Order Status (`/products/order-status`)
* **APIs Included:** 1
* **Capabilities:** 
  * Retrieve list of past orders within a specified date range.
  * Get real-time status, line items, and tracking numbers for specific order IDs.
* **Authentication:** Supports 2-Legged and 3-Legged OAuth.

### 3. Quote (`/products/quote`)
* **APIs Included:** 1
* **Capabilities:** 
  * Submit a batch list of products for custom pricing quotes.
  * Lock in quoted prices for a specified validity period.

### 4. Ordering (`/products/ordering`)
* **APIs Included:** 2
* **Capabilities:** 
  * Programmatically place orders and manage existing orders.
* **Requirement:** Company must have an active **DigiKey Credit Account**.

### 5. MyLists (`/products/mylists`)
* **APIs Included:** 1
* **Capabilities:** 
  * Retrieve existing saved part lists / BOMs.
  * Create, update, or delete lists programmatically.

### 6. Barcode (`/products/barcode`)
* **APIs Included:** 2
* **Capabilities:** 
  * Decode 2D DataMatrix barcodes printed on DigiKey product bags and packing slips.
  * Extract part numbers, quantities, order numbers, and lot info directly from raw scan strings.

### 7. SupplyChain (`/products/supplychain`)
* **APIs Included:** 1
* **Capabilities:** 
  * Monitor bonded/consigned stock levels by location or part number.

### 8. Reference APIs (`/products/reference-apis`)
* **APIs Included:** 1
* **Capabilities:** 
  * Fetch reference metadata such as product categories, manufacturers, packaging types, and parametric field definitions used across other DigiKey API endpoints.

---

## 3. Required Headers for API Calls

For all standard API endpoints (post-authentication):

```http
Authorization: Bearer <access_token>
X-DIGIKEY-Client-Id: <your_client_id>
Content-Type: application/json
Accept: application/json
```

---

## 4. Rate Limiting & Best Practices

- Rate limits vary by API subscription tier. Standard limits typically enforce requests-per-minute (RPM) and daily quotas.
- Cache reference data (e.g., categories, manufacturers) locally to minimize redundant API calls.
- Always implement exponential backoff when handling `429 Too Many Requests` responses.
