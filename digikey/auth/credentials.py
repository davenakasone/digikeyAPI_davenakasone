"""
Credential resolution and configuration for DigiKey SDK.
"""
import os
from pathlib import Path
from typing import NamedTuple, Optional, Union
from dotenv import load_dotenv


class DigiKeyCredentials(NamedTuple):
    client_id: str
    client_secret: str
    redirect_uri: str = "https://localhost"
    environment: str = "production"  # 'production' or 'sandbox'


def resolve_credentials(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    environment: Optional[str] = None,
    env_file_path: Optional[Union[str, Path]] = None,
) -> DigiKeyCredentials:
    """
    Discovers and resolves DigiKey API credentials in order of priority:
    1. Explicit parameters passed to function
    2. Path specified by `DIGIKEY_ENV_PATH` or `VAULT_ENV_PATH` environment variable
    3. Custom `env_file_path` passed to function
    4. Project-local `.env` file
    5. Environment variables (DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET)
    """
    # 1. Check custom path or environment variable path
    target_env = env_file_path or os.getenv("DIGIKEY_ENV_PATH") or os.getenv("VAULT_ENV_PATH")
    if target_env:
        resolved_path = Path(target_env).expanduser()
        if resolved_path.exists():
            load_dotenv(dotenv_path=resolved_path, override=False)

    # 2. Check local project .env file
    local_env = Path.cwd() / ".env"
    if local_env.exists():
        load_dotenv(dotenv_path=local_env, override=False)

    resolved_client_id = (
        client_id
        or os.getenv("DIGIKEY_CLIENT_ID")
        or os.getenv("DIGI_KEY_CLIENT_ID")
    )
    resolved_client_secret = (
        client_secret
        or os.getenv("DIGIKEY_CLIENT_SECRET")
        or os.getenv("DIGI_KEY_CLIENT_SECRET")
    )
    resolved_redirect_uri = (
        redirect_uri
        or os.getenv("DIGIKEY_REDIRECT_URI")
        or "https://localhost"
    )
    resolved_environment = (
        environment
        or os.getenv("DIGIKEY_ENVIRONMENT")
        or "production"
    ).lower().strip()

    if not resolved_client_id or not resolved_client_secret:
        raise ValueError(
            "Missing DigiKey credentials. Please provide client_id and client_secret, "
            "set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET in your environment, "
            "or specify DIGIKEY_ENV_PATH pointing to your credentials file."
        )

    return DigiKeyCredentials(
        client_id=resolved_client_id,
        client_secret=resolved_client_secret,
        redirect_uri=resolved_redirect_uri,
        environment=resolved_environment,
    )
