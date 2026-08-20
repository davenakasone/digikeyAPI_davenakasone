"""
Common data models and helper structures for the DigiKey SDK.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PriceBreak:
    """Represents a quantity-tiered price point."""
    break_quantity: int
    unit_price: float
    total_price: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PriceBreak":
        qty = int(data.get("BreakQuantity", data.get("Quantity", 1)))
        unit = float(data.get("UnitPrice", data.get("Price", 0.0)))
        total = float(data.get("TotalPrice", round(qty * unit, 4)))
        return cls(break_quantity=qty, unit_price=unit, total_price=total)


@dataclass
class SearchResultsPage:
    """Wrapper for paginated search results."""
    total_count: int
    items: List[Any] = field(default_factory=list)
    limit: int = 10
    offset: int = 0
