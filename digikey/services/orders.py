"""
Order Status service for DigiKey SDK.
"""
from typing import Any, Dict, List, Optional, Union
from digikey.core.base_client import BaseClient
from digikey.models.order import OrderStatus


class OrderService:
    """
    Service wrapper for DigiKey Order Status API.
    """

    def __init__(self, client: BaseClient):
        self._client = client

    def get_order_status(self, salesorder_id: Union[int, str]) -> OrderStatus:
        """
        Retrieves status, tracking numbers, and line items for a specific order.
        """
        url = f"/orderstatus/v4/orders/{salesorder_id}"
        resp = self._client.get(url)
        return OrderStatus.from_dict(resp)

    def list_orders(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[OrderStatus]:
        """
        Retrieves orders within a specified date range.
        """
        url = "/orderstatus/v4/orders"
        params: Dict[str, Any] = {}
        if start_date:
            params["StartDate"] = start_date
        if end_date:
            params["EndDate"] = end_date

        resp = self._client.get(url, params=params)
        raw_orders = resp.get("Orders", resp if isinstance(resp, list) else [])
        return [OrderStatus.from_dict(o) for o in raw_orders]
