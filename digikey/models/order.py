"""
Data models for DigiKey Order Status and Tracking.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LineItem:
    line_number: int
    digikey_part_number: str
    manufacturer_part_number: str
    quantity: int
    unit_price: float
    total_price: float
    status: str = "Shipped"
    tracking_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineItem":
        return cls(
            line_number=int(data.get("LineNumber", data.get("LineItemId", 1))),
            digikey_part_number=data.get("DigiKeyPartNumber", ""),
            manufacturer_part_number=data.get("ManufacturerPartNumber", ""),
            quantity=int(data.get("Quantity", data.get("QuantityOrdered", 1))),
            unit_price=float(data.get("UnitPrice", 0.0)),
            total_price=float(data.get("TotalPrice", 0.0)),
            status=data.get("Status", "Shipped"),
            tracking_number=data.get("TrackingNumber"),
        )


@dataclass
class OrderStatus:
    order_id: str
    status: str
    order_date: str
    total: float
    currency: str = "USD"
    customer_id: Optional[str] = None
    line_items: List[LineItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderStatus":
        raw_items = data.get("LineItems", data.get("Items", []))
        line_items = [LineItem.from_dict(item) for item in raw_items]
        return cls(
            order_id=str(data.get("SalesorderId", data.get("OrderId", ""))),
            status=data.get("Status", "Completed"),
            order_date=data.get("OrderDate", data.get("CreatedDate", "")),
            total=float(data.get("TotalPrice", data.get("Total", 0.0))),
            currency=data.get("Currency", "USD"),
            customer_id=data.get("CustomerId"),
            line_items=line_items,
        )
