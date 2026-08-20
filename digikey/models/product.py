"""
Data models for DigiKey Product Information V4.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from digikey.models.common import PriceBreak


@dataclass
class Manufacturer:
    id: Optional[int] = None
    name: str = "Unknown"

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Manufacturer":
        if not data:
            return cls()
        return cls(
            id=data.get("Id"),
            name=data.get("Name", "Unknown"),
        )


@dataclass
class ParametricAttribute:
    parameter_id: Optional[int] = None
    parameter: str = ""
    value_id: Optional[str] = None
    value: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParametricAttribute":
        return cls(
            parameter_id=data.get("ParameterId"),
            parameter=data.get("ParameterText", data.get("Parameter", "")),
            value_id=data.get("ValueId"),
            value=data.get("ValueText", data.get("Value", "")),
        )


@dataclass
class MediaLink:
    media_type: str
    title: str
    url: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaLink":
        return cls(
            media_type=data.get("MediaType", ""),
            title=data.get("Title", ""),
            url=data.get("Url", ""),
        )


@dataclass
class Product:
    """Represents a component/product in the DigiKey catalog."""
    digikey_part_number: str
    manufacturer_part_number: str
    description: str
    manufacturer: Manufacturer
    quantity_available: int = 0
    unit_price: float = 0.0
    detailed_description: str = ""
    datasheet_url: Optional[str] = None
    photo_url: Optional[str] = None
    product_status: str = "Active"
    lead_time_weeks: Optional[int] = None
    minimum_order_quantity: int = 1
    standard_package: int = 1
    price_breaks: List[PriceBreak] = field(default_factory=list)
    parameters: List[ParametricAttribute] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def in_stock(self) -> bool:
        return self.quantity_available > 0

    def unit_price_at(self, quantity: int) -> float:
        """Calculates applicable tiered unit price for a given quantity order."""
        if not self.price_breaks:
            return self.unit_price

        # Sort price breaks descending by break_quantity
        sorted_breaks = sorted(self.price_breaks, key=lambda pb: pb.break_quantity, reverse=True)
        for pb in sorted_breaks:
            if quantity >= pb.break_quantity:
                return pb.unit_price

        return self.unit_price

    def get_parameter(self, param_name: str) -> Optional[str]:
        """Looks up a specific parametric attribute by name (case-insensitive)."""
        target = param_name.lower().strip()
        for p in self.parameters:
            if p.parameter.lower().strip() == target:
                return p.value
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        desc_obj = data.get("Description", {})
        desc = (
            desc_obj.get("ProductDescription")
            if isinstance(desc_obj, dict)
            else str(desc_obj or data.get("ProductDescription", ""))
        )
        detailed_desc = (
            desc_obj.get("DetailedDescription", "")
            if isinstance(desc_obj, dict)
            else data.get("DetailedDescription", "")
        )

        mfg = Manufacturer.from_dict(data.get("Manufacturer"))

        # Parse price breaks
        raw_breaks = (
            data.get("ProductVariations", [{}])[0].get("StandardPricing", [])
            if data.get("ProductVariations")
            else data.get("StandardPricing", [])
        )
        if not raw_breaks and data.get("PriceBreaks"):
            raw_breaks = data.get("PriceBreaks", [])
        price_breaks = [PriceBreak.from_dict(pb) for pb in raw_breaks]

        # Parse parameters
        raw_params = data.get("Parameters", [])
        parameters = [ParametricAttribute.from_dict(p) for p in raw_params]

        # Extract primary photo and datasheet
        photo_url = data.get("PrimaryPhoto") or data.get("PhotoUrl")
        datasheet_url = data.get("PrimaryDatasheet") or data.get("DatasheetUrl")

        # Extract DigiKey part number with fallback to variations
        dkpn = (
            data.get("DigiKeyPartNumber")
            or data.get("DigiKeyProductNumber")
            or (data.get("ProductVariations", [{}])[0].get("DigiKeyProductNumber") if data.get("ProductVariations") else "")
            or ""
        )

        return cls(
            digikey_part_number=dkpn,
            manufacturer_part_number=data.get("ManufacturerProductNumber", data.get("ManufacturerPartNumber", "")),
            description=desc,
            detailed_description=detailed_desc,
            manufacturer=mfg,
            quantity_available=int(data.get("QuantityAvailable", data.get("Quantity", 0))),
            unit_price=float(data.get("UnitPrice", 0.0)),
            datasheet_url=datasheet_url,
            photo_url=photo_url,
            product_status=data.get("ProductStatus", {}).get("Status", "Active")
            if isinstance(data.get("ProductStatus"), dict)
            else str(data.get("ProductStatus", "Active")),
            minimum_order_quantity=int(data.get("MinimumOrderQuantity", 1)),
            standard_package=int(data.get("StandardPackage", 1)),
            price_breaks=price_breaks,
            parameters=parameters,
            raw_data=data,
        )
