"""Client classes for the DocuTray SDK."""

from __future__ import annotations

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
    """

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
    """

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
