"""
OAuth 2.0 token lifecycle manager for DigiKey API.
"""
import json
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional
import requests

from digikey.auth.credentials import DigiKeyCredentials
from digikey.core.exceptions import AuthenticationError

PRODUCTION_BASE_URL = "https://api.digikey.com"
SANDBOX_BASE_URL = "https://sandbox-api.digikey.com"


class OAuthHandler:
    """
    Manages OAuth 2.0 token acquisition, caching, expiration detection,
    and automatic renewal for both 2-legged (client credentials) and
    3-legged (authorization code) flows.
    """

    TOKEN_ENDPOINT = "/v1/oauth2/token"
    AUTHORIZE_ENDPOINT = "/v1/oauth2/authorize"

    def __init__(
        self,
        credentials: DigiKeyCredentials,
        tokens_cache_file: Optional[Path] = None,
        session: Optional[requests.Session] = None,
    ):
        self.credentials = credentials
        self.base_url = (
            SANDBOX_BASE_URL
            if credentials.environment == "sandbox"
            else PRODUCTION_BASE_URL
        )
        self.tokens_cache_file = tokens_cache_file
        self._session = session or requests.Session()
        self._lock = threading.Lock()

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: float = 0.0

        if self.tokens_cache_file and self.tokens_cache_file.exists():
            self._load_cached_tokens()

    def _load_cached_tokens(self) -> None:
        try:
            with open(self.tokens_cache_file, "r") as f:
                data = json.load(f)
                self._access_token = data.get("access_token")
                self._refresh_token = data.get("refresh_token")
                self._expires_at = float(data.get("expires_at", 0.0))
        except Exception:
            pass

    def _save_cached_tokens(self, data: Dict[str, Any]) -> None:
        if not self.tokens_cache_file:
            return
        try:
            self.tokens_cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tokens_cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_authorization_url(self) -> str:
        """Generates the 3-legged OAuth browser login URL."""
        params = {
            "response_type": "code",
            "client_id": self.credentials.client_id,
            "redirect_uri": self.credentials.redirect_uri,
        }
        return f"{self.base_url}{self.AUTHORIZE_ENDPOINT}?{urllib.parse.urlencode(params)}"

    def request_2legged_token(self) -> str:
        """
        Requests an OAuth 2.0 Bearer access token using Client Credentials grant.
        This is the default flow for part search and product data.
        """
        with self._lock:
            url = f"{self.base_url}{self.TOKEN_ENDPOINT}"
            payload = {
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "grant_type": "client_credentials",
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            try:
                resp = self._session.post(url, data=payload, headers=headers, timeout=15)
            except requests.RequestException as e:
                raise AuthenticationError(f"Network error during OAuth token request: {e}") from e

            if not resp.ok:
                raise AuthenticationError(
                    f"DigiKey 2-legged OAuth failed: {resp.text}",
                    status_code=resp.status_code,
                    response_body=resp.text,
                )

            data = resp.json()
            self._access_token = data["access_token"]
            expires_in = int(data.get("expires_in", 600))
            self._expires_at = time.time() + expires_in

            data_to_cache = {
                "access_token": self._access_token,
                "expires_at": self._expires_at,
                "token_type": data.get("token_type", "Bearer"),
            }
            self._save_cached_tokens(data_to_cache)
            return self._access_token

    def exchange_authorization_code(self, code: str) -> Dict[str, Any]:
        """
        Exchanges a 3-legged authorization code for access and refresh tokens.
        """
        with self._lock:
            url = f"{self.base_url}{self.TOKEN_ENDPOINT}"
            payload = {
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "code": code.strip(),
                "grant_type": "authorization_code",
                "redirect_uri": self.credentials.redirect_uri,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            try:
                resp = self._session.post(url, data=payload, headers=headers, timeout=15)
            except requests.RequestException as e:
                raise AuthenticationError(f"Network error during authorization code exchange: {e}") from e

            if not resp.ok:
                raise AuthenticationError(
                    f"DigiKey authorization code exchange failed: {resp.text}",
                    status_code=resp.status_code,
                    response_body=resp.text,
                )

            data = resp.json()
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token")
            expires_in = int(data.get("expires_in", 1800))
            self._expires_at = time.time() + expires_in

            data["expires_at"] = self._expires_at
            self._save_cached_tokens(data)
            return data

    def refresh_3legged_token(self) -> str:
        """
        Refreshes a 3-legged access token using the stored refresh token.
        """
        with self._lock:
            if not self._refresh_token:
                raise AuthenticationError("No refresh token available to renew 3-legged session.")

            url = f"{self.base_url}{self.TOKEN_ENDPOINT}"
            payload = {
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            try:
                resp = self._session.post(url, data=payload, headers=headers, timeout=15)
            except requests.RequestException as e:
                raise AuthenticationError(f"Network error during token refresh: {e}") from e

            if not resp.ok:
                raise AuthenticationError(
                    f"DigiKey token refresh failed: {resp.text}",
                    status_code=resp.status_code,
                    response_body=resp.text,
                )

            data = resp.json()
            self._access_token = data["access_token"]
            if "refresh_token" in data:
                self._refresh_token = data["refresh_token"]
            expires_in = int(data.get("expires_in", 1800))
            self._expires_at = time.time() + expires_in

            data["expires_at"] = self._expires_at
            data["refresh_token"] = self._refresh_token
            self._save_cached_tokens(data)
            return self._access_token

    def get_valid_token(self, proactive_buffer_seconds: int = 60) -> str:
        """
        Returns a valid access token. Automatically requests a fresh token or
        refreshes an existing session before expiry.
        """
        now = time.time()
        if self._access_token and (now < self._expires_at - proactive_buffer_seconds):
            return self._access_token

        # If we have a refresh token (3-legged session), use refresh
        if self._refresh_token:
            return self.refresh_3legged_token()

        # Otherwise standard 2-legged flow
        return self.request_2legged_token()
