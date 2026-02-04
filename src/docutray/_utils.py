"""Internal utilities for the DocuTray SDK."""

from __future__ import annotations

import os

from ._constants import ENV_VAR_API_KEY


def get_api_key_from_env() -> str | None:
    """Get the API key from the environment variable.

    Returns:
        The API key if set, otherwise None.
    """
    return os.environ.get(ENV_VAR_API_KEY)


def mask_api_key(api_key: str | None) -> str:
    """Mask an API key for safe display in repr/logs.

    Args:
        api_key: The API key to mask.

    Returns:
        A masked version of the API key showing only first 5 characters.
    """
    if api_key is None:
        return "None"
    if len(api_key) <= 5:
        return "***"
    return f"{api_key[:5]}***"
