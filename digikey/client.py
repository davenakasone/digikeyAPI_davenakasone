"""
Unified master client for DigiKey API SDK.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from digikey.auth.credentials import DigiKeyCredentials, resolve_credentials
from digikey.auth.oauth import OAuthHandler
from digikey.core.base_client import BaseClient
from digikey.models.barcode import BarcodeData
from digikey.models.category import Category
from digikey.models.common import SearchResultsPage
from digikey.models.product import Product
from digikey.services.barcode import BarcodeService
from digikey.services.doctor import DiagnosticResult, HealthInspector
from digikey.services.mylists import MyListsService
from digikey.services.orders import OrderService
from digikey.services.products import ProductService
from digikey.services.quotes import QuoteService
from digikey.services.reference import ReferenceService


class DigiKey:
    """
    Main entry point for the DigiKey Python SDK.

    Usage:
        >>> from digikey import DigiKey
        >>> dk = DigiKey()  # Auto-discovers credentials from environment, throttles to 10 req/s
        >>> results = dk.products.search("STM32F407VGT6")
        >>> for prod in results.items:
        ...     print(prod.manufacturer.name, prod.manufacturer_part_number, prod.unit_price)
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        environment: Optional[str] = None,
        env_file_path: Optional[Union[str, Path]] = None,
        tokens_cache_file: Optional[Path] = None,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_per_second: Optional[float] = 10.0,
    ):
        self.credentials = resolve_credentials(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            environment=environment,
            env_file_path=env_file_path,
        )

        self.oauth_handler = OAuthHandler(
            credentials=self.credentials,
            tokens_cache_file=tokens_cache_file,
        )

        self.base_client = BaseClient(
            credentials=self.credentials,
            oauth_handler=self.oauth_handler,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_per_second=rate_limit_per_second,
        )

        # Dedicated API Services
        self.products = ProductService(self.base_client)
        self.reference = ReferenceService(self.base_client)
        self.barcode = BarcodeService(self.base_client)
        self.orders = OrderService(self.base_client)
        self.mylists = MyListsService(self.base_client)
        self.quotes = QuoteService(self.base_client)
        self.doctor = HealthInspector(self.base_client)

    @property
    def rate_limit_remaining(self) -> Optional[int]:
        """Returns the remaining requests in the current DigiKey rate limit window."""
        return self.base_client.rate_limit_remaining

    @property
    def rate_limit_limit(self) -> Optional[int]:
        """Returns the total quota limit in the current DigiKey rate limit window."""
        return self.base_client.rate_limit_limit

    # High-level convenience shortcuts
    def search(self, keywords: str, limit: int = 10, **kwargs) -> SearchResultsPage:
        """Shortcut for `dk.products.search(keywords, limit=limit, **kwargs)`"""
        return self.products.search(keywords=keywords, limit=limit, **kwargs)

    def get_details(self, part_number: str) -> Product:
        """Shortcut for `dk.products.get_details(part_number)`"""
        return self.products.get_details(part_number=part_number)

    def get_categories(self) -> List[Category]:
        """Shortcut for `dk.reference.get_categories()`"""
        return self.reference.get_categories()

    def decode_barcode(self, barcode_string: str) -> BarcodeData:
        """Shortcut for `dk.barcode.decode(barcode_string)`"""
        return self.barcode.decode(barcode_string=barcode_string)
