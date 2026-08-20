"""
Reference APIs service for DigiKey SDK.
"""
from typing import Any, Dict, List, Optional
from digikey.core.base_client import BaseClient
from digikey.models.category import Category


class ReferenceService:
    """
    Service wrapper for DigiKey Reference APIs (Taxonomy, Categories, Manufacturers, Packaging).
    """

    def __init__(self, client: BaseClient):
        self._client = client

    def get_categories(self) -> List[Category]:
        """Fetches top-level product category taxonomy."""
        url = "/products/v4/search/categories"
        resp = self._client.get(url)
        raw_categories = resp.get("Categories", resp.get("RootCategories", []))
        if isinstance(raw_categories, list):
            return [Category.from_dict(c) for c in raw_categories]
        return [Category.from_dict(resp)]

    def get_category(self, category_id: int) -> Category:
        """Fetches a specific category and its child subcategories."""
        url = f"/products/v4/search/categories/{category_id}"
        resp = self._client.get(url)
        return Category.from_dict(resp)

    def get_manufacturers(self) -> List[Dict[str, Any]]:
        """Fetches list of all authorized manufacturers."""
        url = "/products/v4/search/manufacturers"
        resp = self._client.get(url)
        return resp.get("Manufacturers", [])

    def get_packaging_types(self) -> List[Dict[str, Any]]:
        """Fetches list of packaging types (Cut Tape, Reel, Tube, Tray, Bulk, etc.)."""
        url = "/products/v4/search/packagingtypes"
        resp = self._client.get(url)
        return resp.get("PackagingTypes", [])
