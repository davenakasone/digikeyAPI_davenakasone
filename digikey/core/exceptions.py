"""
Custom exceptions for the DigiKey API client.
"""
from typing import Any, Optional


class DigiKeyError(Exception):
    """Base exception for all DigiKey SDK errors."""
    pass


class DigiKeyAPIError(DigiKeyError):
    """Exception raised when DigiKey API returns an HTTP error status code."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_id = request_id

    def __str__(self) -> str:
        code_str = f"[{self.status_code}] " if self.status_code else ""
        req_str = f" (Request ID: {self.request_id})" if self.request_id else ""
        return f"{code_str}{super().__str__()}{req_str}"


class AuthenticationError(DigiKeyAPIError):
    """Raised when OAuth authentication or token refresh fails (HTTP 401/403)."""
    pass


class NotFoundError(DigiKeyAPIError):
    """Raised when a requested part, category, or order is not found (HTTP 404)."""
    pass


class RateLimitExceededError(DigiKeyAPIError):
    """Raised when the API rate limit has been exceeded (HTTP 429)."""
    pass


class ValidationError(DigiKeyAPIError):
    """Raised when the request payload is malformed or invalid (HTTP 400)."""
    pass


class ServerError(DigiKeyAPIError):
    """Raised when DigiKey experiences an internal server error (HTTP 5xx)."""
    pass
