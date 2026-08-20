"""
Base HTTP client transport for DigiKey API SDK.
"""
import time
from typing import Any, Dict, Optional
import requests

from digikey.auth.credentials import DigiKeyCredentials, resolve_credentials
from digikey.auth.oauth import OAuthHandler
from digikey.core.exceptions import (
    AuthenticationError,
    DigiKeyAPIError,
    NotFoundError,
    RateLimitExceededError,
    ServerError,
    ValidationError,
)

PRODUCTION_BASE_URL = "https://api.digikey.com"
SANDBOX_BASE_URL = "https://sandbox-api.digikey.com"


class BaseClient:
    """
    HTTP Transport Layer for DigiKey API.
    Handles headers, OAuth token injection, exponential backoff retries, and error mapping.
    """

    def __init__(
        self,
        credentials: Optional[DigiKeyCredentials] = None,
        oauth_handler: Optional[OAuthHandler] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        self.credentials = credentials or resolve_credentials()
        self.base_url = (
            SANDBOX_BASE_URL
            if self.credentials.environment == "sandbox"
            else PRODUCTION_BASE_URL
        )
        self.session = requests.Session()
        self.oauth_handler = oauth_handler or OAuthHandler(
            credentials=self.credentials, session=self.session
        )
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _build_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        token = self.oauth_handler.get_valid_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-DIGIKEY-Client-Id": self.credentials.client_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DigiKey-Python-SDK/1.0.0",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Executes an HTTP request against the DigiKey API with automatic retry for rate limits.
        """
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        retries = 0

        while True:
            request_headers = self._build_headers(headers)

            try:
                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json_data,
                    data=data,
                    headers=request_headers,
                    timeout=self.timeout,
                )
            except requests.RequestException as e:
                if retries < self.max_retries:
                    retries += 1
                    time.sleep(self.backoff_factor * (2 ** (retries - 1)))
                    continue
                raise DigiKeyAPIError(f"Network request failed: {e}") from e

            # Handle Rate Limiting (HTTP 429)
            if response.status_code == 429:
                if retries < self.max_retries:
                    retries += 1
                    retry_after = int(response.headers.get("Retry-After", 2 * retries))
                    time.sleep(retry_after)
                    continue
                raise RateLimitExceededError(
                    "Rate limit exceeded (HTTP 429)",
                    status_code=429,
                    response_body=response.text,
                )

            # Handle Successful Responses
            if response.ok:
                if not response.content:
                    return None
                try:
                    return response.json()
                except ValueError:
                    return response.text

            # Handle Errors
            self._handle_error_response(response)

    def _handle_error_response(self, response: requests.Response) -> None:
        status = response.status_code
        body = response.text
        req_id = response.headers.get("X-Request-Id") or response.headers.get("apigee.edge.execution.id")

        try:
            err_json = response.json()
            msg = err_json.get("ErrorMessage") or err_json.get("message") or body
        except Exception:
            msg = body

        if status in (401, 403):
            raise AuthenticationError(msg, status_code=status, response_body=body, request_id=req_id)
        elif status == 404:
            raise NotFoundError(msg, status_code=status, response_body=body, request_id=req_id)
        elif status == 400:
            raise ValidationError(msg, status_code=status, response_body=body, request_id=req_id)
        elif 500 <= status < 600:
            raise ServerError(msg, status_code=status, response_body=body, request_id=req_id)
        else:
            raise DigiKeyAPIError(msg, status_code=status, response_body=body, request_id=req_id)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path: str, json_data: Optional[Any] = None, **kwargs) -> Any:
        return self.request("POST", path, json_data=json_data, **kwargs)

    def put(self, path: str, json_data: Optional[Any] = None, **kwargs) -> Any:
        return self.request("PUT", path, json_data=json_data, **kwargs)

    def delete(self, path: str, **kwargs) -> Any:
        return self.request("DELETE", path, **kwargs)
