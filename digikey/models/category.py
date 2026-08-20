"""
Data models for DigiKey Product Taxonomy and Categories.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Category:
    category_id: int
    name: str
    product_count: int = 0
    parent_id: Optional[int] = None
    children: List["Category"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent_id: Optional[int] = None) -> "Category":
        cat_id = int(data.get("CategoryId", data.get("Id", 0)))
        name = data.get("Name", data.get("CategoryName", "Unknown"))
        count = int(data.get("ProductCount", 0))

        raw_children = data.get("ChildCategories", data.get("Children", []))
        children = [cls.from_dict(c, parent_id=cat_id) for c in raw_children]

        return cls(
            category_id=cat_id,
            name=name,
            product_count=count,
            parent_id=parent_id or data.get("ParentId"),
            children=children,
        )
