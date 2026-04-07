"""Document Types resource for document type catalog operations."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from .._pagination import AsyncPage, Page
from ..types.document_type import ConversionMode, DocumentType, ValidationResult
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

    def create(
        self,
        *,
        name: str,
        code_type: str,
        description: str,
        json_schema: dict[str, Any],
        is_draft: bool | None = None,
        prompt_hints: str | None = None,
        identify_prompt_hints: str | None = None,
        conversion_mode: ConversionMode | None = None,
        keep_property_ordering: bool | None = None,
    ) -> DocumentType:
        """Create a new document type.

        Args:
            name: Document type name (min 2 characters).
            code_type: Unique code identifier (lowercase alphanumeric and underscores).
            description: Document type description (min 1 character).
            json_schema: JSON Schema for document validation.
            is_draft: Whether the document type is a draft. Defaults to True.
            prompt_hints: Hints for OCR prompt processing.
            identify_prompt_hints: Hints for document identification prompt.
            conversion_mode: Processing mode ("json", "toon", or "multi_prompt").
            keep_property_ordering: Preserve property ordering in schema.

        Returns:
            The created document type.

        Raises:
            ConflictError: If a document type with that code_type already exists.

        Example:
            >>> doc_type = client.document_types.create(
            ...     name="Invoice",
            ...     code_type="invoice",
            ...     description="Invoice documents with line items",
            ...     json_schema={
            ...         "type": "object",
            ...         "properties": {
            ...             "invoice_number": {"type": "string"},
            ...             "total": {"type": "number"},
            ...         },
            ...     },
            ... )
            >>> print(f"Created: {doc_type.id}")
        """
        body: dict[str, Any] = {
            "name": name,
            "codeType": code_type,
            "description": description,
            "jsonSchema": json_schema,
        }
        if is_draft is not None:
            body["isDraft"] = is_draft
        if prompt_hints is not None:
            body["promptHints"] = prompt_hints
        if identify_prompt_hints is not None:
            body["identifyPromptHints"] = identify_prompt_hints
        if conversion_mode is not None:
            body["conversionMode"] = conversion_mode
        if keep_property_ordering is not None:
            body["keepPropertyOrdering"] = keep_property_ordering

        response = self._client._request("POST", "/api/document-types", json=body)
        return DocumentType.model_validate(response.json().get("data", response.json()))

    def update(
        self,
        type_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        json_schema: dict[str, Any] | None = None,
        is_draft: bool | None = None,
        prompt_hints: str | None = None,
        identify_prompt_hints: str | None = None,
        conversion_mode: ConversionMode | None = None,
        keep_property_ordering: bool | None = None,
    ) -> DocumentType:
        """Update an existing document type.

        All fields are optional; only provided fields will be updated.

        Args:
            type_id: The document type ID to update.
            name: New document type name.
            description: New description.
            json_schema: New JSON Schema for document validation.
            is_draft: New draft status.
            prompt_hints: New OCR prompt hints.
            identify_prompt_hints: New identification prompt hints.
            conversion_mode: New processing mode.
            keep_property_ordering: New property ordering setting.

        Returns:
            The updated document type.

        Raises:
            NotFoundError: If the document type doesn't exist.
            PermissionDeniedError: If insufficient permissions.

        Example:
            >>> doc_type = client.document_types.update(
            ...     "dt_123",
            ...     name="Updated Invoice",
            ...     is_draft=False,
            ... )
            >>> print(f"Updated: {doc_type.name}")
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if json_schema is not None:
            body["jsonSchema"] = json_schema
        if is_draft is not None:
            body["isDraft"] = is_draft
        if prompt_hints is not None:
            body["promptHints"] = prompt_hints
        if identify_prompt_hints is not None:
            body["identifyPromptHints"] = identify_prompt_hints
        if conversion_mode is not None:
            body["conversionMode"] = conversion_mode
        if keep_property_ordering is not None:
            body["keepPropertyOrdering"] = keep_property_ordering

        response = self._client._request(
            "PUT",
            f"/api/document-types/{type_id}",
            json=body,
        )
        return DocumentType.model_validate(response.json().get("data", response.json()))

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

        response = await self._client._request(
            "GET", "/api/document-types", params=params
        )
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

    async def create(
        self,
        *,
        name: str,
        code_type: str,
        description: str,
        json_schema: dict[str, Any],
        is_draft: bool | None = None,
        prompt_hints: str | None = None,
        identify_prompt_hints: str | None = None,
        conversion_mode: ConversionMode | None = None,
        keep_property_ordering: bool | None = None,
    ) -> DocumentType:
        """Create a new document type.

        Args:
            name: Document type name (min 2 characters).
            code_type: Unique code identifier (lowercase alphanumeric and underscores).
            description: Document type description (min 1 character).
            json_schema: JSON Schema for document validation.
            is_draft: Whether the document type is a draft. Defaults to True.
            prompt_hints: Hints for OCR prompt processing.
            identify_prompt_hints: Hints for document identification prompt.
            conversion_mode: Processing mode ("json", "toon", or "multi_prompt").
            keep_property_ordering: Preserve property ordering in schema.

        Returns:
            The created document type.
        """
        body: dict[str, Any] = {
            "name": name,
            "codeType": code_type,
            "description": description,
            "jsonSchema": json_schema,
        }
        if is_draft is not None:
            body["isDraft"] = is_draft
        if prompt_hints is not None:
            body["promptHints"] = prompt_hints
        if identify_prompt_hints is not None:
            body["identifyPromptHints"] = identify_prompt_hints
        if conversion_mode is not None:
            body["conversionMode"] = conversion_mode
        if keep_property_ordering is not None:
            body["keepPropertyOrdering"] = keep_property_ordering

        response = await self._client._request("POST", "/api/document-types", json=body)
        return DocumentType.model_validate(response.json().get("data", response.json()))

    async def update(
        self,
        type_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        json_schema: dict[str, Any] | None = None,
        is_draft: bool | None = None,
        prompt_hints: str | None = None,
        identify_prompt_hints: str | None = None,
        conversion_mode: ConversionMode | None = None,
        keep_property_ordering: bool | None = None,
    ) -> DocumentType:
        """Update an existing document type.

        All fields are optional; only provided fields will be updated.

        Args:
            type_id: The document type ID to update.
            name: New document type name.
            description: New description.
            json_schema: New JSON Schema for document validation.
            is_draft: New draft status.
            prompt_hints: New OCR prompt hints.
            identify_prompt_hints: New identification prompt hints.
            conversion_mode: New processing mode.
            keep_property_ordering: New property ordering setting.

        Returns:
            The updated document type.
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if json_schema is not None:
            body["jsonSchema"] = json_schema
        if is_draft is not None:
            body["isDraft"] = is_draft
        if prompt_hints is not None:
            body["promptHints"] = prompt_hints
        if identify_prompt_hints is not None:
            body["identifyPromptHints"] = identify_prompt_hints
        if conversion_mode is not None:
            body["conversionMode"] = conversion_mode
        if keep_property_ordering is not None:
            body["keepPropertyOrdering"] = keep_property_ordering

        response = await self._client._request(
            "PUT",
            f"/api/document-types/{type_id}",
            json=body,
        )
        return DocumentType.model_validate(response.json().get("data", response.json()))

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
