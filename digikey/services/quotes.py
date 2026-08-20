"""
Quote Request service for DigiKey SDK.
"""
from typing import Any, Dict, List, Optional
from digikey.core.base_client import BaseClient


class QuoteService:
    """
    Service wrapper for DigiKey Quote API.
    """

    def __init__(self, client: BaseClient):
        self._client = client

    def create_quote(self, line_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Submits a batch list of parts for custom pricing quotes.
        `line_items` format: `[{"DigiKeyPartNumber": "...", "Quantity": 1000}]`
        """
        url = "/quote/v1/quotes"
        payload = {"QuoteLineItems": line_items}
        return self._client.post(url, json_data=payload)

    def get_quote(self, quote_id: str) -> Dict[str, Any]:
        """Retrieves details of an existing quote."""
        url = f"/quote/v1/quotes/{quote_id}"
        return self._client.get(url)
