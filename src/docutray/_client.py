"""Client classes for the DocuTray SDK."""

from __future__ import annotations

import httpx
from typing_extensions import Self

from ._base_client import BaseAsyncClient, BaseClient


class Client(BaseClient):
    """Synchronous client for the DocuTray API.

    Example:
        >>> client = Client(api_key="sk_test_123")
        >>> # Use the client...
        >>> client.close()

        Or using a context manager:
        >>> with Client(api_key="sk_test_123") as client:
        ...     # Use the client...

    Args:
        api_key: The API key for authentication. If not provided,
            reads from DOCUTRAY_API_KEY environment variable.
        base_url: The base URL for API requests. Defaults to
            https://api.docutray.com.
        timeout: Request timeout configuration. Can be a single float
            (seconds) or an httpx.Timeout for granular control.
            Default: connect=5s, read=60s, write=60s, pool=10s.
        max_retries: Maximum number of retry attempts for failed requests.
            Retries use exponential backoff with jitter.
            Defaults to 2.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Initialize the synchronous client."""
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    def __enter__(self) -> Self:
        """Enter the context manager.

        Returns:
            The client instance.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the context manager and close the client."""
        self.close()


class AsyncClient(BaseAsyncClient):
    """Asynchronous client for the DocuTray API.

    Example:
        >>> client = AsyncClient(api_key="sk_test_123")
        >>> # Use the client...
        >>> await client.close()

        Or using an async context manager:
        >>> async with AsyncClient(api_key="sk_test_123") as client:
        ...     # Use the client...

    Args:
        api_key: The API key for authentication. If not provided,
            reads from DOCUTRAY_API_KEY environment variable.
        base_url: The base URL for API requests. Defaults to
            https://api.docutray.com.
        timeout: Request timeout configuration. Can be a single float
            (seconds) or an httpx.Timeout for granular control.
            Default: connect=5s, read=60s, write=60s, pool=10s.
        max_retries: Maximum number of retry attempts for failed requests.
            Retries use exponential backoff with jitter.
            Defaults to 2.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Initialize the asynchronous client."""
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Returns:
            The client instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the async context manager and close the client."""
        await self.close()
