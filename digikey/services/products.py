"""
Product Information V4 Service for DigiKey SDK.
"""
from typing import Any, Dict, List, Optional, Union
from digikey.core.base_client import BaseClient
from digikey.models.common import SearchResultsPage
from digikey.models.product import Product


class ProductService:
    """
    Service wrapper for DigiKey Product Information V4 APIs.
    """

    def __init__(self, client: BaseClient):
        self._client = client

    def search(
        self,
        keywords: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
    ) -> SearchResultsPage:
        """
        Search DigiKey product catalog by keyword or part number.
        Returns a paginated SearchResultsPage containing parsed Product models.
        """
        url = "/products/v4/search/keyword"
        payload: Dict[str, Any] = {
            "Keywords": keywords,
            "Limit": limit,
            "Offset": offset,
        }
        if filters:
            payload["Filters"] = filters
        if sort_by:
            payload["Sort"] = {"SortBy": sort_by}

        resp = self._client.post(url, json_data=payload)
        raw_products = resp.get("Products", [])
        total_count = int(resp.get("ProductsCount", len(raw_products)))
        products = [Product.from_dict(p) for p in raw_products]

        return SearchResultsPage(
            total_count=total_count,
            items=products,
            limit=limit,
            offset=offset,
        )

    def get_details(self, part_number: str) -> Product:
        """
        Retrieves full specifications, price tiers, and stock for a part.
        `part_number` can be a DigiKey part number or manufacturer part number.
        """
        clean_part = part_number.strip()
        url = f"/products/v4/search/{clean_part}/productdetails"
        resp = self._client.get(url)
        product_data = resp.get("Product", resp)
        return Product.from_dict(product_data)

    def search_by_mpn(self, mpn: str) -> List[Product]:
        """
        Searches explicitly by Manufacturer Product Number.
        """
        url = f"/products/v4/search/manufacturerproduct/{mpn.strip()}"
        resp = self._client.get(url)
        raw_products = resp.get("Products", [])
        return [Product.from_dict(p) for p in raw_products]

    def search_by_dkpn(self, dkpn: str) -> Product:
        """
        Searches explicitly by DigiKey Part Number.
        """
        url = f"/products/v4/search/digikeyproduct/{dkpn.strip()}"
        resp = self._client.get(url)
        product_data = resp.get("Product", resp)
        return Product.from_dict(product_data)

    def get_suggestions(self, keyword: str) -> List[str]:
        """
        Fetches search auto-complete keyword suggestions.
        """
        url = f"/products/v4/search/keyword/{keyword.strip()}/suggestions"
        resp = self._client.get(url)
        return resp.get("Suggestions", [])
