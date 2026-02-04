"""HTTP transport layer for the DocuTray SDK."""

from __future__ import annotations

from typing import Any

import httpx

from ._constants import DEFAULT_TIMEOUT
from ._version import __version__


def build_headers(api_key: str) -> dict[str, str]:
    """Build the default headers for API requests.

    Args:
        api_key: The API key for authentication.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": f"docutray-python/{__version__}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


class SyncHTTPClient:
    """Synchronous HTTP client wrapper around httpx."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float | None = None,
    ) -> None:
        """Initialize the sync HTTP client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for API requests.
            timeout: Request timeout in seconds.
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._client: httpx.Client | None = None

    def _ensure_client(self) -> httpx.Client:
        """Ensure the httpx client is initialized.

        Returns:
            The httpx client instance.
        """
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._base_url,
                headers=build_headers(self._api_key),
                timeout=self._timeout,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an HTTP request.

        Args:
            method: The HTTP method.
            path: The request path.
            **kwargs: Additional arguments to pass to httpx.

        Returns:
            The HTTP response.
        """
        client = self._ensure_client()
        return client.request(method, path, **kwargs)


class AsyncHTTPClient:
    """Asynchronous HTTP client wrapper around httpx."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float | None = None,
    ) -> None:
        """Initialize the async HTTP client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for API requests.
            timeout: Request timeout in seconds.
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._client: httpx.AsyncClient | None = None

    def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the httpx async client is initialized.

        Returns:
            The httpx async client instance.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=build_headers(self._api_key),
                timeout=self._timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async HTTP request.

        Args:
            method: The HTTP method.
            path: The request path.
            **kwargs: Additional arguments to pass to httpx.

        Returns:
            The HTTP response.
        """
        client = self._ensure_client()
        return await client.request(method, path, **kwargs)
