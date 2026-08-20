"""
Health Inspector and Diagnostic Subsystem for DigiKey API SDK.
Audits credentials, OAuth handshake, endpoints health, latency, and quota limits.
"""
import time
from typing import Any, Dict, List, NamedTuple, Optional
from digikey.core.base_client import BaseClient
from digikey.core.exceptions import DigiKeyError


class DiagnosticResult(NamedTuple):
    check_name: str
    passed: bool
    latency_ms: float
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthInspector:
    """
    Automated health audit for DigiKey API endpoints and credentials.
    """

    def __init__(self, client: BaseClient):
        self._client = client

    def run_all_checks(self) -> List[DiagnosticResult]:
        """
        Runs comprehensive suite of connectivity, auth, and endpoint health checks.
        """
        results: List[DiagnosticResult] = []

        # 1. Auth & Token Acquisition
        results.append(self._check_auth())

        # If auth failed, abort remaining endpoint checks
        if not results[0].passed:
            return results

        # 2. Product Search V4
        results.append(self._check_product_search())

        # 3. Product Details V4
        results.append(self._check_product_details())

        # 4. Categories Reference Taxonomy
        results.append(self._check_categories())

        # 5. Manufacturers Reference API
        results.append(self._check_manufacturers())

        # 6. Rate Limit & Quota Telemetry
        results.append(self._check_quota())

        return results

    def _check_auth(self) -> DiagnosticResult:
        t0 = time.monotonic()
        try:
            token = self._client.oauth_handler.get_valid_token()
            latency = (time.monotonic() - t0) * 1000
            token_preview = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "Valid"
            return DiagnosticResult(
                check_name="OAuth2 Token Handshake",
                passed=True,
                latency_ms=latency,
                message=f"Authenticated successfully (Token: {token_preview})",
            )
        except Exception as e:
            latency = (time.monotonic() - t0) * 1000
            return DiagnosticResult(
                check_name="OAuth2 Token Handshake",
                passed=False,
                latency_ms=latency,
                message=f"Authentication failed: {e}",
            )

    def _check_product_search(self) -> DiagnosticResult:
        t0 = time.monotonic()
        try:
            resp = self._client.post(
                "/products/v4/search/keyword",
                json_data={"Keywords": "resistor", "Limit": 1},
            )
            latency = (time.monotonic() - t0) * 1000
            count = resp.get("ProductsCount", 0)
            return DiagnosticResult(
                check_name="Product Search V4 (/products/v4/search/keyword)",
                passed=True,
                latency_ms=latency,
                message=f"Healthy (Status 200, matching catalog size: {count:,} parts)",
            )
        except Exception as e:
            latency = (time.monotonic() - t0) * 1000
            return DiagnosticResult(
                check_name="Product Search V4 (/products/v4/search/keyword)",
                passed=False,
                latency_ms=latency,
                message=f"Failed: {e}",
            )

    def _check_product_details(self) -> DiagnosticResult:
        t0 = time.monotonic()
        try:
            resp = self._client.get("/products/v4/search/NE555P/productdetails")
            latency = (time.monotonic() - t0) * 1000
            prod = resp.get("Product", resp)
            mpn = prod.get("ManufacturerProductNumber", "NE555P")
            return DiagnosticResult(
                check_name="Product Details V4 (/products/v4/search/{part}/productdetails)",
                passed=True,
                latency_ms=latency,
                message=f"Healthy (Status 200, successfully resolved MPN '{mpn}')",
            )
        except Exception as e:
            latency = (time.monotonic() - t0) * 1000
            return DiagnosticResult(
                check_name="Product Details V4 (/products/v4/search/{part}/productdetails)",
                passed=False,
                latency_ms=latency,
                message=f"Failed: {e}",
            )

    def _check_categories(self) -> DiagnosticResult:
        t0 = time.monotonic()
        try:
            resp = self._client.get("/products/v4/search/categories")
            latency = (time.monotonic() - t0) * 1000
            cats = resp.get("Categories", [])
            return DiagnosticResult(
                check_name="Category Taxonomy (/products/v4/search/categories)",
                passed=True,
                latency_ms=latency,
                message=f"Healthy (Status 200, {len(cats)} root taxonomy trees)",
            )
        except Exception as e:
            latency = (time.monotonic() - t0) * 1000
            return DiagnosticResult(
                check_name="Category Taxonomy (/products/v4/search/categories)",
                passed=False,
                latency_ms=latency,
                message=f"Failed: {e}",
            )

    def _check_manufacturers(self) -> DiagnosticResult:
        t0 = time.monotonic()
        try:
            resp = self._client.get("/products/v4/search/manufacturers")
            latency = (time.monotonic() - t0) * 1000
            mfgs = resp.get("Manufacturers", [])
            return DiagnosticResult(
                check_name="Manufacturers Directory (/products/v4/search/manufacturers)",
                passed=True,
                latency_ms=latency,
                message=f"Healthy (Status 200, {len(mfgs):,} authorized manufacturers)",
            )
        except Exception as e:
            latency = (time.monotonic() - t0) * 1000
            return DiagnosticResult(
                check_name="Manufacturers Directory (/products/v4/search/manufacturers)",
                passed=False,
                latency_ms=latency,
                message=f"Failed: {e}",
            )

    def _check_quota(self) -> DiagnosticResult:
        rem = self._client.rate_limit_remaining
        lim = self._client.rate_limit_limit
        if rem is not None and lim is not None:
            pct = (rem / lim) * 100
            status_ok = rem > 50
            msg = f"Quota: {rem:,} / {lim:,} requests remaining ({pct:.1f}% capacity)"
            return DiagnosticResult(
                check_name="Rate Limit & Quota Capacity",
                passed=status_ok,
                latency_ms=0.0,
                message=msg if status_ok else f"WARNING Low Quota: {msg}",
            )
        return DiagnosticResult(
            check_name="Rate Limit & Quota Capacity",
            passed=True,
            latency_ms=0.0,
            message="No rate limit headers intercepted yet",
        )
