"""Client classes for the DocuTray SDK."""

from __future__ import annotations

from functools import cached_property

import httpx
from typing_extensions import Self

from ._base_client import BaseAsyncClient, BaseClient
from .resources.convert import AsyncConvert, Convert
from .resources.document_types import AsyncDocumentTypes, DocumentTypes
from .resources.identify import AsyncIdentify, Identify
from .resources.steps import AsyncSteps, Steps


class Client(BaseClient):
    """Synchronous client for the DocuTray API.

    Example:
        >>> client = Client(api_key="sk_test_123")
        >>> # Convert a document
        >>> result = client.convert.run(
        ...     file=Path("invoice.pdf"),
        ...     document_type_code="invoice"
        ... )
        >>> print(result.data)
        >>> client.close()

        Or using a context manager:
        >>> with Client(api_key="sk_test_123") as client:
        ...     result = client.identify.run(file=Path("document.pdf"))
        ...     print(f"Type: {result.document_type.name}")

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

    @cached_property
    def convert(self) -> Convert:
        """Document conversion operations.

        Example:
            >>> result = client.convert.run(
            ...     file=Path("invoice.pdf"),
            ...     document_type_code="invoice"
            ... )
        """
        return Convert(self)

    @cached_property
    def identify(self) -> Identify:
        """Document identification operations.

        Example:
            >>> result = client.identify.run(file=Path("document.pdf"))
            >>> print(f"Type: {result.document_type.name}")
        """
        return Identify(self)

    @cached_property
    def document_types(self) -> DocumentTypes:
        """Document type catalog operations.

        Example:
            >>> types = client.document_types.list()
            >>> for t in types.data:
            ...     print(t.name)
        """
        return DocumentTypes(self)

    @cached_property
    def steps(self) -> Steps:
        """Step execution operations.

        Example:
            >>> status = client.steps.run_async(
            ...     step_id="step_123",
            ...     file=Path("document.pdf")
            ... )
        """
        return Steps(self)

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
        >>> async with AsyncClient(api_key="sk_test_123") as client:
        ...     result = await client.convert.run(
        ...         file=Path("invoice.pdf"),
        ...         document_type_code="invoice"
        ...     )
        ...     print(result.data)

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

    @cached_property
    def convert(self) -> AsyncConvert:
        """Document conversion operations (async).

        Example:
            >>> result = await client.convert.run(
            ...     file=Path("invoice.pdf"),
            ...     document_type_code="invoice"
            ... )
        """
        return AsyncConvert(self)

    @cached_property
    def identify(self) -> AsyncIdentify:
        """Document identification operations (async).

        Example:
            >>> result = await client.identify.run(file=Path("document.pdf"))
            >>> print(f"Type: {result.document_type.name}")
        """
        return AsyncIdentify(self)

    @cached_property
    def document_types(self) -> AsyncDocumentTypes:
        """Document type catalog operations (async).

        Example:
            >>> types = await client.document_types.list()
            >>> for t in types.data:
            ...     print(t.name)
        """
        return AsyncDocumentTypes(self)

    @cached_property
    def steps(self) -> AsyncSteps:
        """Step execution operations (async).

        Example:
            >>> status = await client.steps.run_async(
            ...     step_id="step_123",
            ...     file=Path("document.pdf")
            ... )
        """
        return AsyncSteps(self)

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
