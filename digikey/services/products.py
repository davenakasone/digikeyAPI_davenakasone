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
        in_stock_only: bool = False,
        category_id: Optional[int] = None,
        manufacturer_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
    ) -> SearchResultsPage:
        """
        Search DigiKey product catalog by keyword, MPN, or DKPN.

        Args:
            keywords: Search query string (e.g. "STM32F407", "0.1uF 0402", "NE555P")
            limit: Number of results to return (default: 10, max: 50)
            offset: Pagination offset
            in_stock_only: If True, only returns products currently in stock
            category_id: Restricts search to a specific category taxonomy ID
            manufacturer_id: Restricts search to a specific manufacturer ID
            filters: Custom raw filter dictionary for advanced parametric queries
            sort_by: Field to sort by (e.g. "UnitPrice", "QuantityAvailable")

        Returns:
            SearchResultsPage containing parsed Product objects.
        """
        url = "/products/v4/search/keyword"
        payload: Dict[str, Any] = {
            "Keywords": keywords.strip(),
            "Limit": limit,
            "Offset": offset,
        }

        # Build filter dictionary
        applied_filters: Dict[str, Any] = {}
        if filters:
            applied_filters.update(filters)
        if in_stock_only:
            applied_filters["InStock"] = True
        if category_id is not None:
            applied_filters["TaxonomyIds"] = [category_id]
        if manufacturer_id is not None:
            applied_filters["ManufacturerIds"] = [manufacturer_id]

        if applied_filters:
            payload["Filters"] = applied_filters

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
        Retrieves full specifications, price tiers, stock, and datasheets for a part.
        `part_number` can be a DigiKey part number (e.g. `296-NE555P-ND`)
        or a manufacturer part number (e.g. `NE555P`).
        """
        clean_part = part_number.strip()
        url = f"/products/v4/search/{clean_part}/productdetails"
        resp = self._client.get(url)
        product_data = resp.get("Product", resp)
        return Product.from_dict(product_data)

    def search_by_mpn(self, mpn: str, limit: int = 10) -> SearchResultsPage:
        """
        Searches by Manufacturer Part Number (MPN).
        """
        return self.search(keywords=mpn, limit=limit)

    def search_by_dkpn(self, dkpn: str) -> Product:
        """
        Retrieves product details directly using DigiKey Part Number (DKPN).
        """
        return self.get_details(part_number=dkpn)

    def find_alternates(
        self,
        part_or_query: Union[str, Product],
        limit: int = 5,
        in_stock_only: bool = True,
    ) -> List[Product]:
        """
        Finds spec-compatible alternate parts (e.g. when the target part is out of stock).
        """
        if isinstance(part_or_query, Product):
            target = part_or_query
        else:
            try:
                target = self.get_details(part_or_query)
            except Exception:
                # Fallback to searching the query string directly
                page = self.search(keywords=part_or_query, limit=limit, in_stock_only=in_stock_only)
                return page.items

        # Search by description / base part or MPN
        search_term = target.manufacturer_part_number
        page = self.search(keywords=search_term, limit=limit + 1, in_stock_only=in_stock_only)
        # Exclude exact same part if possible to prioritize alternates
        alternates = [p for p in page.items if p.manufacturer_part_number != target.manufacturer_part_number]
        return alternates[:limit] if alternates else page.items[:limit]
