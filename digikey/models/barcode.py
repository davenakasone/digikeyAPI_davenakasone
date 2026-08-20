"""
Data models for DigiKey 2D Barcode parser responses.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BarcodeData:
    digikey_part_number: str
    manufacturer_part_number: Optional[str] = None
    quantity: int = 1
    invoice_id: Optional[str] = None
    sales_order_id: Optional[str] = None
    purchase_order: Optional[str] = None
    lot_code: Optional[str] = None
    country_of_origin: Optional[str] = None
    raw_barcode: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], raw_barcode: Optional[str] = None) -> "BarcodeData":
        return cls(
            digikey_part_number=data.get("DigiKeyPartNumber", data.get("PartNumber", "")),
            manufacturer_part_number=data.get("ManufacturerPartNumber", data.get("MPN")),
            quantity=int(data.get("Quantity", 1)),
            invoice_id=data.get("InvoiceId"),
            sales_order_id=data.get("SalesOrderId"),
            purchase_order=data.get("PurchaseOrder"),
            lot_code=data.get("LotCode"),
            country_of_origin=data.get("CountryOfOrigin"),
            raw_barcode=raw_barcode or data.get("RawBarcode"),
        )
