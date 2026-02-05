"""Document Types resource for document type catalog operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..types.document_type import DocumentType, ValidationResult
from ..types.shared import PaginatedResponse, Pagination

if TYPE_CHECKING:
    from .._base_client import BaseAsyncClient, BaseClient


class DocumentTypesListResponse(PaginatedResponse[DocumentType]):
    """Response from listing document types."""

    pass


class DocumentTypes:
    """Synchronous document type operations.

    Example:
        >>> client = Client(api_key="...")
        >>> types = client.document_types.list()
        >>> for doc_type in types.data:
        ...     print(f"{doc_type.codeType}: {doc_type.name}")
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the DocumentTypes resource.

        Args:
            client: The parent client instance.
        """
        self._client = client

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> DocumentTypesListResponse:
        """List available document types.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page. Defaults to server default.
            search: Search term to filter document types by name.

        Returns:
            Paginated list of document types.

        Example:
            >>> # List all document types
            >>> response = client.document_types.list()
            >>> for doc_type in response.data:
            ...     print(doc_type.name)
            >>>
            >>> # Search for specific types
            >>> response = client.document_types.list(search="invoice")
        """
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = self._client._request("GET", "/api/document-types", params=params)
        data = response.json()

        return DocumentTypesListResponse(
            data=[DocumentType.model_validate(item) for item in data.get("data", [])],
            pagination=Pagination.model_validate(data.get("pagination", {})),
        )

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


class AsyncDocumentTypes:
    """Asynchronous document type operations.

    Example:
        >>> async with AsyncClient(api_key="...") as client:
        ...     types = await client.document_types.list()
        ...     for doc_type in types.data:
        ...         print(f"{doc_type.codeType}: {doc_type.name}")
    """

    def __init__(self, client: BaseAsyncClient) -> None:
        """Initialize the AsyncDocumentTypes resource.

        Args:
            client: The parent async client instance.
        """
        self._client = client

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> DocumentTypesListResponse:
        """List available document types.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page. Defaults to server default.
            search: Search term to filter document types by name.

        Returns:
            Paginated list of document types.
        """
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = await self._client._request("GET", "/api/document-types", params=params)
        data = response.json()

        return DocumentTypesListResponse(
            data=[DocumentType.model_validate(item) for item in data.get("data", [])],
            pagination=Pagination.model_validate(data.get("pagination", {})),
        )

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
