"""
Unit tests for DigiKey BaseClient HTTP transport and error handling.
"""
import unittest
from unittest.mock import MagicMock, patch

from digikey.auth.credentials import DigiKeyCredentials
from digikey.core.base_client import BaseClient
from digikey.core.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitExceededError,
    ValidationError,
)


class TestCoreBaseClient(unittest.TestCase):

    def setUp(self):
        self.creds = DigiKeyCredentials(client_id="dk_test_id", client_secret="dk_secret")
        self.oauth_mock = MagicMock()
        self.oauth_mock.get_valid_token.return_value = "valid_test_token"

    def test_headers_construction(self):
        client = BaseClient(credentials=self.creds, oauth_handler=self.oauth_mock)
        headers = client._build_headers()

        self.assertEqual(headers["Authorization"], "Bearer valid_test_token")
        self.assertEqual(headers["X-DIGIKEY-Client-Id"], "dk_test_id")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Accept"], "application/json")

    def test_successful_get_json(self):
        client = BaseClient(credentials=self.creds, oauth_handler=self.oauth_mock)
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.content = b'{"result": "ok"}'
        mock_resp.json.return_value = {"result": "ok"}
        client.session.request = MagicMock(return_value=mock_resp)

        data = client.get("/test/path", params={"q": "foo"})
        self.assertEqual(data, {"result": "ok"})
        client.session.request.assert_called_once()
        args, kwargs = client.session.request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], "https://api.digikey.com/test/path")
        self.assertEqual(kwargs["params"], {"q": "foo"})

    def test_404_raises_not_found(self):
        client = BaseClient(credentials=self.creds, oauth_handler=self.oauth_mock)
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 404
        mock_resp.text = '{"ErrorMessage": "Part not found"}'
        mock_resp.json.return_value = {"ErrorMessage": "Part not found"}
        client.session.request = MagicMock(return_value=mock_resp)

        with self.assertRaises(NotFoundError):
            client.get("/products/v4/search/unknown/productdetails")

    def test_400_raises_validation_error(self):
        client = BaseClient(credentials=self.creds, oauth_handler=self.oauth_mock)
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 400
        mock_resp.text = '{"ErrorMessage": "Keywords required"}'
        mock_resp.json.return_value = {"ErrorMessage": "Keywords required"}
        client.session.request = MagicMock(return_value=mock_resp)

        with self.assertRaises(ValidationError):
            client.post("/products/v4/search/keyword", json_data={})

    @patch("time.sleep", return_value=None)
    def test_429_rate_limit_retry_and_exhaustion(self, sleep_mock):
        client = BaseClient(
            credentials=self.creds,
            oauth_handler=self.oauth_mock,
            max_retries=2,
        )
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 429
        mock_resp.headers = {"Retry-After": "1"}
        mock_resp.text = "Rate Limit Exceeded"
        mock_resp.json.side_effect = ValueError("Not JSON")
        client.session.request = MagicMock(return_value=mock_resp)

        with self.assertRaises(RateLimitExceededError):
            client.get("/test/rate/limited")

        # Initial try + 2 retries = 3 calls
        self.assertEqual(client.session.request.call_count, 3)

    def test_rate_limit_headers_captured(self):
        client = BaseClient(credentials=self.creds, oauth_handler=self.oauth_mock)
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.content = b'{"ok": true}'
        mock_resp.json.return_value = {"ok": True}
        mock_resp.headers = {
            "x-ratelimit-limit": "1000",
            "x-ratelimit-remaining": "850",
        }
        client.session.request = MagicMock(return_value=mock_resp)

        client.get("/test/path")
        self.assertEqual(client.rate_limit_limit, 1000)
        self.assertEqual(client.rate_limit_remaining, 850)

    def test_rate_limiter_logic(self):
        from digikey.core.rate_limiter import RateLimiter
        limiter = RateLimiter(rate_per_second=10.0, burst_capacity=2)
        # First 2 acquires should be immediate
        w1 = limiter.acquire()
        w2 = limiter.acquire()
        self.assertEqual(w1, 0.0)
        self.assertEqual(w2, 0.0)


if __name__ == "__main__":
    unittest.main()

