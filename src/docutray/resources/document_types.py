"""Document Types resource for document type catalog operations."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from .._pagination import AsyncPage, Page
from ..types.document_type import DocumentType, ValidationResult
from ..types.shared import Pagination

if TYPE_CHECKING:
    from .._base_client import BaseAsyncClient, BaseClient


class DocumentTypes:
    """Synchronous document type operations.

    Example:
        >>> client = Client(api_key="...")
        >>> page = client.document_types.list()
        >>> for doc_type in page.data:
        ...     print(f"{doc_type.codeType}: {doc_type.name}")
        >>>
        >>> # Iterate through all document types across pages
        >>> for doc_type in client.document_types.list().auto_paging_iter():
        ...     print(doc_type.name)
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the DocumentTypes resource.

        Args:
            client: The parent client instance.
        """
        self._client = client

    def _fetch_page(
        self,
        page_num: int,
        *,
        limit: int | None = None,
        search: str | None = None,
    ) -> Page[DocumentType]:
        """Fetch a specific page of document types.

        Args:
            page_num: The page number to fetch.
            limit: Number of items per page.
            search: Search term to filter document types.

        Returns:
            The requested page of document types.
        """
        params: dict[str, Any] = {"page": page_num}
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = self._client._request("GET", "/api/document-types", params=params)
        data = response.json()

        pagination = Pagination.model_validate(data.get("pagination", {}))
        items = [DocumentType.model_validate(item) for item in data.get("data", [])]

        return Page(
            data=items,
            pagination=pagination,
            fetch_page=lambda p: self._fetch_page(p, limit=limit, search=search),
        )

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> Page[DocumentType]:
        """List available document types.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page. Defaults to server default.
            search: Search term to filter document types by name.

        Returns:
            A Page of document types with pagination support.

        Example:
            >>> # List all document types
            >>> page = client.document_types.list()
            >>> for doc_type in page.data:
            ...     print(doc_type.name)
            >>>
            >>> # Iterate through all pages
            >>> for page in client.document_types.list().iter_pages():
            ...     print(f"Page {page.page}: {len(page.data)} items")
            >>>
            >>> # Iterate through all items automatically
            >>> for doc_type in client.document_types.list().auto_paging_iter():
            ...     print(doc_type.name)
            >>>
            >>> # Search for specific types
            >>> page = client.document_types.list(search="invoice")
        """
        return self._fetch_page(page or 1, limit=limit, search=search)

    def get(self, type_id: str) -> DocumentType:
        """Get a specific document type by ID.

        Args:
            type_id: The document type ID.

        Returns:
            The document type details including schema.

        Raises:
            NotFoundError: If the document type doesn't exist.

        Example:
            >>> doc_type = client.document_types.get("dt_abc123")
            >>> print(f"Name: {doc_type.name}")
            >>> print(f"Schema: {doc_type.schema_}")
        """
        response = self._client._request("GET", f"/api/document-types/{type_id}")
        return DocumentType.model_validate(response.json())

    def validate(
        self,
        type_id: str,
        data: dict[str, Any],
    ) -> ValidationResult:
        """Validate JSON data against a document type's schema.

        This validates extracted data to check if it conforms to the
        document type's expected structure and requirements.

        Args:
            type_id: The document type ID to validate against.
            data: The JSON data to validate.

        Returns:
            Validation result with errors and warnings.

        Example:
            >>> result = client.document_types.validate(
            ...     "dt_invoice",
            ...     {"invoice_number": "INV-001", "total": 100}
            ... )
            >>> if result.is_valid():
            ...     print("Data is valid!")
            >>> else:
            ...     for error in result.errors.messages:
            ...         print(f"Error: {error}")
        """
        response = self._client._request(
            "POST",
            f"/api/document-types/{type_id}/validate",
            json=data,
        )
        return ValidationResult.model_validate(response.json())

    @cached_property
    def with_raw_response(self) -> DocumentTypesWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = client.document_types.with_raw_response.list()
            >>> print(response.status_code)
            >>> print(response.headers)
            >>> page = response.parse()
        """
        return DocumentTypesWithRawResponse(self)


class AsyncDocumentTypes:
    """Asynchronous document type operations.

    Example:
        >>> async with AsyncClient(api_key="...") as client:
        ...     page = await client.document_types.list()
        ...     for doc_type in page.data:
        ...         print(f"{doc_type.codeType}: {doc_type.name}")
        >>>
        >>> # Iterate through all document types across pages
        >>> async for doc_type in (await client.document_types.list()).auto_paging_iter_async():
        ...     print(doc_type.name)
    """

    def __init__(self, client: BaseAsyncClient) -> None:
        """Initialize the AsyncDocumentTypes resource.

        Args:
            client: The parent async client instance.
        """
        self._client = client

    async def _fetch_page(
        self,
        page_num: int,
        *,
        limit: int | None = None,
        search: str | None = None,
    ) -> AsyncPage[DocumentType]:
        """Fetch a specific page of document types.

        Args:
            page_num: The page number to fetch.
            limit: Number of items per page.
            search: Search term to filter document types.

        Returns:
            The requested page of document types.
        """
        params: dict[str, Any] = {"page": page_num}
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = await self._client._request("GET", "/api/document-types", params=params)
        data = response.json()

        pagination = Pagination.model_validate(data.get("pagination", {}))
        items = [DocumentType.model_validate(item) for item in data.get("data", [])]

        return AsyncPage(
            data=items,
            pagination=pagination,
            fetch_page=lambda p: self._fetch_page(p, limit=limit, search=search),
        )

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> AsyncPage[DocumentType]:
        """List available document types.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page. Defaults to server default.
            search: Search term to filter document types by name.

        Returns:
            An AsyncPage of document types with pagination support.
        """
        return await self._fetch_page(page or 1, limit=limit, search=search)

    async def get(self, type_id: str) -> DocumentType:
        """Get a specific document type by ID.

        Args:
            type_id: The document type ID.

        Returns:
            The document type details including schema.
        """
        response = await self._client._request("GET", f"/api/document-types/{type_id}")
        return DocumentType.model_validate(response.json())

    async def validate(
        self,
        type_id: str,
        data: dict[str, Any],
    ) -> ValidationResult:
        """Validate JSON data against a document type's schema.

        Args:
            type_id: The document type ID to validate against.
            data: The JSON data to validate.

        Returns:
            Validation result with errors and warnings.
        """
        response = await self._client._request(
            "POST",
            f"/api/document-types/{type_id}/validate",
            json=data,
        )
        return ValidationResult.model_validate(response.json())

    @cached_property
    def with_raw_response(self) -> AsyncDocumentTypesWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = await client.document_types.with_raw_response.list()
            >>> print(response.status_code)
            >>> page = response.parse()
        """
        return AsyncDocumentTypesWithRawResponse(self)


# Import here to avoid circular imports
from .._response import (  # noqa: E402
    AsyncDocumentTypesWithRawResponse,
    DocumentTypesWithRawResponse,
)
