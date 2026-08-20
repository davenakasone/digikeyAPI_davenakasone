"""
Barcode decoding service for DigiKey SDK.
"""
from typing import Any, Dict, Optional
from digikey.core.base_client import BaseClient
from digikey.models.barcode import BarcodeData


class BarcodeService:
    """
    Service wrapper for DigiKey Barcode API.
    Decodes 2D DataMatrix barcodes from DigiKey product packaging.
    """

    def __init__(self, client: BaseClient):
        self._client = client

    def decode(self, barcode_string: str) -> BarcodeData:
        """
        Decodes a raw 2D barcode scan string into structured part and packaging metadata.
        """
        url = "/barcode/v4/barcodedetails"
        payload = {"Barcode": barcode_string.strip()}
        resp = self._client.post(url, json_data=payload)
        return BarcodeData.from_dict(resp, raw_barcode=barcode_string)
