"""Base client classes for the DocuTray SDK."""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from ._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
)
from ._exceptions import make_authentication_error
from ._http import AsyncHTTPClient, SyncHTTPClient
from ._utils import get_api_key_from_env, mask_api_key


class BaseClient(ABC):
    """Abstract base class for synchronous DocuTray clients."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            api_key: The API key for authentication. If not provided,
                reads from DOCUTRAY_API_KEY environment variable.
            base_url: The base URL for API requests.
            timeout: Request timeout configuration. Can be a single float
                (seconds) or an httpx.Timeout for granular control.
            max_retries: Maximum number of retry attempts for failed requests.
                Defaults to 2.

        Raises:
            AuthenticationError: If no API key is provided or found.
        """
        resolved_api_key = api_key if api_key is not None else get_api_key_from_env()
        if resolved_api_key is None:
            raise make_authentication_error(
                "No API key provided. Either pass api_key to the constructor "
                "or set the DOCUTRAY_API_KEY environment variable."
            )

        self._api_key = resolved_api_key
        self._base_url = base_url if base_url is not None else DEFAULT_BASE_URL
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES

        if self._max_retries < 0:
            raise ValueError("max_retries must be >= 0")

        self._retry_config = DEFAULT_RETRY_CONFIG.with_max_retries(self._max_retries)
        self._http_client: SyncHTTPClient | None = None

    @property
    def _client(self) -> SyncHTTPClient:
        """Get the HTTP client, creating it if necessary."""
        if self._http_client is None:
            self._http_client = SyncHTTPClient(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout,
                retry_config=self._retry_config,
            )
        return self._http_client

    def close(self) -> None:
        """Close the client and release resources."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"api_key={mask_api_key(self._api_key)}, "
            f"base_url={self._base_url!r})"
        )

    @abstractmethod
    def __enter__(self) -> BaseClient:
        """Enter the context manager."""
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the context manager."""
        ...


class BaseAsyncClient(ABC):
    """Abstract base class for asynchronous DocuTray clients."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Initialize the async client.

        Args:
            api_key: The API key for authentication. If not provided,
                reads from DOCUTRAY_API_KEY environment variable.
            base_url: The base URL for API requests.
            timeout: Request timeout configuration. Can be a single float
                (seconds) or an httpx.Timeout for granular control.
            max_retries: Maximum number of retry attempts for failed requests.
                Defaults to 2.

        Raises:
            AuthenticationError: If no API key is provided or found.
        """
        resolved_api_key = api_key if api_key is not None else get_api_key_from_env()
        if resolved_api_key is None:
            raise make_authentication_error(
                "No API key provided. Either pass api_key to the constructor "
                "or set the DOCUTRAY_API_KEY environment variable."
            )

        self._api_key = resolved_api_key
        self._base_url = base_url if base_url is not None else DEFAULT_BASE_URL
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES

        if self._max_retries < 0:
            raise ValueError("max_retries must be >= 0")

        self._retry_config = DEFAULT_RETRY_CONFIG.with_max_retries(self._max_retries)
        self._http_client: AsyncHTTPClient | None = None

    @property
    def _client(self) -> AsyncHTTPClient:
        """Get the async HTTP client, creating it if necessary."""
        if self._http_client is None:
            self._http_client = AsyncHTTPClient(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout,
                retry_config=self._retry_config,
            )
        return self._http_client

    async def close(self) -> None:
        """Close the client and release resources."""
        if self._http_client is not None:
            await self._http_client.close()
            self._http_client = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"api_key={mask_api_key(self._api_key)}, "
            f"base_url={self._base_url!r})"
        )

    @abstractmethod
    async def __aenter__(self) -> BaseAsyncClient:
        """Enter the async context manager."""
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the async context manager."""
        ...
