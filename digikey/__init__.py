"""
DigiKey Python SDK - Modern, type-safe API client for DigiKey v4 APIs.
"""
from digikey.auth.credentials import DigiKeyCredentials, resolve_credentials
from digikey.auth.oauth import OAuthHandler
from digikey.client import DigiKey
from digikey.core.base_client import BaseClient
from digikey.core.exceptions import (
    AuthenticationError,
    DigiKeyAPIError,
    DigiKeyError,
    NotFoundError,
    RateLimitExceededError,
    ServerError,
    ValidationError,
)
from digikey.models.barcode import BarcodeData
from digikey.models.category import Category
from digikey.models.common import PriceBreak, SearchResultsPage
from digikey.models.order import LineItem, OrderStatus
from digikey.models.product import (
    Manufacturer,
    MediaLink,
    ParametricAttribute,
    Product,
)

__version__ = "1.0.0"

__all__ = [
    "DigiKey",
    "BaseClient",
    "DigiKeyCredentials",
    "resolve_credentials",
    "OAuthHandler",
    # Exceptions
    "DigiKeyError",
    "DigiKeyAPIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitExceededError",
    "ValidationError",
    "ServerError",
    # Models
    "Product",
    "PriceBreak",
    "SearchResultsPage",
    "Manufacturer",
    "ParametricAttribute",
    "MediaLink",
    "Category",
    "BarcodeData",
    "OrderStatus",
    "LineItem",
]
