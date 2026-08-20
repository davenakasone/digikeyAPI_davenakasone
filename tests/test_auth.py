"""
Unit tests for DigiKey Auth and Credential Discovery.
"""
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from digikey.auth.credentials import DigiKeyCredentials, resolve_credentials
from digikey.auth.oauth import OAuthHandler
from digikey.core.exceptions import AuthenticationError


class TestAuth(unittest.TestCase):

    def test_resolve_credentials_explicit(self):
        creds = resolve_credentials(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="https://localhost:8080",
            environment="sandbox",
        )
        self.assertEqual(creds.client_id, "test_id")
        self.assertEqual(creds.client_secret, "test_secret")
        self.assertEqual(creds.redirect_uri, "https://localhost:8080")
        self.assertEqual(creds.environment, "sandbox")

    def test_resolve_credentials_from_env_path_var(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write("DIGIKEY_CLIENT_ID=env_var_id\nDIGIKEY_CLIENT_SECRET=env_var_secret\n")
            tmp_path = tmp.name

        try:
            with patch.dict(os.environ, {"DIGIKEY_ENV_PATH": tmp_path}, clear=True):
                creds = resolve_credentials()
                self.assertEqual(creds.client_id, "env_var_id")
                self.assertEqual(creds.client_secret, "env_var_secret")
        finally:
            os.remove(tmp_path)

    def test_resolve_credentials_from_home_dir(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write("DIGIKEY_CLIENT_ID=home_user_id\nDIGIKEY_CLIENT_SECRET=home_user_sec\n")
            tmp_path = Path(tmp.name)

        try:
            with patch("digikey.auth.credentials.Path.home", return_value=tmp_path.parent):
                with patch("digikey.auth.credentials.Path.exists", side_effect=lambda self: str(self) == str(tmp_path)):
                    with patch.dict(os.environ, {}, clear=True):
                        # Should find the mock home config
                        pass
        finally:
            if tmp_path.exists():
                os.remove(tmp_path)

    def test_resolve_credentials_missing_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                resolve_credentials(
                    client_id=None,
                    client_secret=None,
                    env_file_path=Path("/non/existent/path.env"),
                )

    def test_2legged_token_request_success(self):
        creds = DigiKeyCredentials(client_id="id123", client_secret="sec123")
        session_mock = MagicMock()
        response_mock = MagicMock()
        response_mock.ok = True
        response_mock.json.return_value = {
            "access_token": "mock_token_abc",
            "expires_in": 600,
            "token_type": "Bearer",
        }
        session_mock.post.return_value = response_mock

        handler = OAuthHandler(credentials=creds, session=session_mock)
        token = handler.request_2legged_token()

        self.assertEqual(token, "mock_token_abc")
        session_mock.post.assert_called_once()
        call_args = session_mock.post.call_args
        self.assertIn("https://api.digikey.com/v1/oauth2/token", call_args[0])
        self.assertEqual(call_args[1]["data"]["grant_type"], "client_credentials")

    def test_2legged_token_request_failure_raises(self):
        creds = DigiKeyCredentials(client_id="id123", client_secret="sec123")
        session_mock = MagicMock()
        response_mock = MagicMock()
        response_mock.ok = False
        response_mock.status_code = 401
        response_mock.text = "Unauthorized Client"
        session_mock.post.return_value = response_mock

        handler = OAuthHandler(credentials=creds, session=session_mock)
        with self.assertRaises(AuthenticationError):
            handler.request_2legged_token()

    def test_token_caching_and_expiry(self):
        creds = DigiKeyCredentials(client_id="id123", client_secret="sec123")
        session_mock = MagicMock()
        response_mock = MagicMock()
        response_mock.ok = True
        response_mock.json.return_value = {
            "access_token": "token_1",
            "expires_in": 1000,
            "token_type": "Bearer",
        }
        session_mock.post.return_value = response_mock

        handler = OAuthHandler(credentials=creds, session=session_mock)
        t1 = handler.get_valid_token()
        self.assertEqual(t1, "token_1")
        self.assertEqual(session_mock.post.call_count, 1)

        # Second call should use cache without calling network
        t2 = handler.get_valid_token()
        self.assertEqual(t2, "token_1")
        self.assertEqual(session_mock.post.call_count, 1)


if __name__ == "__main__":
    unittest.main()
