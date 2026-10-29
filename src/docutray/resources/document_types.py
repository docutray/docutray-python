"""Document Types resource for document type catalog operations."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from .._exceptions import NotFoundError
from .._pagination import AsyncPage, Page
from .._types import NOT_GIVEN, NotGiven
from ..types.document_type import ConversionMode, DocumentType, ValidationResult
from ..types.shared import Pagination

if TYPE_CHECKING:
    from .._base_client import BaseAsyncClient, BaseClient


def _create_body(
    *,
    name: str,
    code_type: str,
    description: str,
    json_schema: dict[str, Any],
    is_draft: bool | None,
    prompt_hints: str | None,
    identify_prompt_hints: str | None,
    conversion_mode: ConversionMode | None,
    keep_property_ordering: bool | None,
    bounding_boxes_enabled: bool | None,
    conversion_spec: dict[str, Any] | None,
    dsl_rules: str | None,
    is_public: bool | None,
) -> dict[str, Any]:
    """Build the JSON body for POST /api/document-types."""
    body: dict[str, Any] = {
        "name": name,
        "codeType": code_type,
        "description": description,
        "jsonSchema": json_schema,
    }
    optional = {
        "isDraft": is_draft,
        "promptHints": prompt_hints,
        "identifyPromptHints": identify_prompt_hints,
        "conversionMode": conversion_mode,
        "keepPropertyOrdering": keep_property_ordering,
        "boundingBoxesEnabled": bounding_boxes_enabled,
        "conversionSpec": conversion_spec,
        "dslRules": dsl_rules,
        "isPublic": is_public,
    }
    body.update({key: value for key, value in optional.items() if value is not None})
    return body


def _update_body(
    *,
    name: str | None,
    description: str | None,
    json_schema: dict[str, Any] | None,
    is_draft: bool | None,
    prompt_hints: str | None,
    identify_prompt_hints: str | None,
    conversion_mode: ConversionMode | None,
    keep_property_ordering: bool | None,
    bounding_boxes_enabled: bool | None,
    conversion_spec: dict[str, Any] | None | NotGiven,
    dsl_rules: str | None | NotGiven,
    is_public: bool | None,
) -> dict[str, Any]:
    """Build the JSON body for ``PUT /api/document-types/{id}``.

    ``None`` omits most fields; ``conversion_spec`` and ``dsl_rules`` are
    omitted only when ``NOT_GIVEN`` so that ``None`` can clear them.
    """
    optional = {
        "name": name,
        "description": description,
        "jsonSchema": json_schema,
        "isDraft": is_draft,
        "promptHints": prompt_hints,
        "identifyPromptHints": identify_prompt_hints,
        "conversionMode": conversion_mode,
        "keepPropertyOrdering": keep_property_ordering,
        "boundingBoxesEnabled": bounding_boxes_enabled,
        "isPublic": is_public,
    }
    body: dict[str, Any] = {k: v for k, v in optional.items() if v is not None}
    if not isinstance(conversion_spec, NotGiven):
        body["conversionSpec"] = conversion_spec
    if not isinstance(dsl_rules, NotGiven):
        body["dslRules"] = dsl_rules
    return body


def _validate_body(data: Any, dsl_rules: str | None | NotGiven) -> Any:
    """Build the JSON body for ``POST /api/document-types/{id}/validate``.

    With ``dsl_rules`` the dry-run envelope ``{data, dslRules}`` is sent;
    otherwise the data itself is the body and the stored rules run.
    """
    if isinstance(dsl_rules, NotGiven):
        return data
    return {"data": data, "dslRules": dsl_rules}


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
            search: Search term matched against name, ``codeType`` and description.

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
            search: Search term matched against name, ``codeType`` and description.

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
            type_id: The document type's internal ID (not its ``codeType``).

        Returns:
            The document type details including schema.

        Raises:
            NotFoundError: If the document type doesn't exist.

        Example:
            >>> doc_type = client.document_types.get("cm0example0000000000000id")
            >>> print(f"Name: {doc_type.name}")
            >>> print(f"Schema: {doc_type.jsonSchema}")
        """
        response = self._client._request("GET", f"/api/document-types/{type_id}")
        return DocumentType.model_validate(response.json().get("data", response.json()))

    def get_by_code(self, code: str) -> DocumentType:
        """Get a document type by its ``codeType``.

        Looks the code up with ``list(search=code)`` across all pages and fetches
        the match with ``get()``. Codes of your organization's own types carry its
        slug as a prefix, so pass the full code (e.g. ``"acme_invoice"``).

        Args:
            code: The exact ``codeType`` of the document type.

        Returns:
            The document type details including schema.

        Raises:
            NotFoundError: If no accessible document type has this exact code.

        Example:
            >>> doc_type = client.document_types.get_by_code("acme_invoice")
            >>> print(doc_type.id)
        """
        page = self.list(search=code)
        for doc_type in page.auto_paging_iter():
            if doc_type.codeType == code:
                return self.get(doc_type.id)
        raise NotFoundError(
            f"Document type with code {code!r} not found", status_code=404
        )

    def validate(
        self,
        type_id: str,
        data: dict[str, Any],
        *,
        dsl_rules: str | None | NotGiven = NOT_GIVEN,
    ) -> ValidationResult:
        """Validate JSON data against a document type's schema.

        This validates extracted data to check if it conforms to the
        document type's expected structure and requirements.

        Args:
            type_id: The document type's internal ID (not its ``codeType``) to validate against.
            data: The JSON data to validate.
            dsl_rules: Temporary DSL rules for a dry run. They replace the stored
                rules for this call only (JSON Schema still runs); ``None`` or
                ``""`` validates without DSL. Omit to use the stored rules.

        Returns:
            Validation result with errors and warnings.

        Example:
            >>> result = client.document_types.validate(
            ...     "cm0example0000000000000id",
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
            json=_validate_body(data, dsl_rules),
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
        bounding_boxes_enabled: bool | None = None,
        conversion_spec: dict[str, Any] | None = None,
        dsl_rules: str | None = None,
        is_public: bool | None = None,
    ) -> DocumentType:
        """Create a new document type.

        Args:
            name: Document type name (min 2 characters).
            code_type: Unique code identifier (lowercase alphanumeric and underscores).
                The API prefixes it with the organization slug when missing
                (``"invoice"`` is stored as ``"acme_invoice"``).
            description: Document type description (min 1 character).
            json_schema: JSON Schema for document validation.
            is_draft: Whether the document type is a draft. Defaults to True.
            prompt_hints: Hints for OCR prompt processing.
            identify_prompt_hints: Hints for document identification prompt.
            conversion_mode: Processing mode ("json", "toon", or "multi_prompt").
            keep_property_ordering: Preserve property ordering in schema.
            bounding_boxes_enabled: Also return per-field locations (admin API keys only).
            conversion_spec: Spec mapping extracted JSON to CSV/Excel export columns.
            dsl_rules: DSL validation rules (64 KiB max). Invalid syntax raises
                DSLValidationError.
            is_public: Whether the document type is publicly available.

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
        body = _create_body(
            name=name,
            code_type=code_type,
            description=description,
            json_schema=json_schema,
            is_draft=is_draft,
            prompt_hints=prompt_hints,
            identify_prompt_hints=identify_prompt_hints,
            conversion_mode=conversion_mode,
            keep_property_ordering=keep_property_ordering,
            bounding_boxes_enabled=bounding_boxes_enabled,
            conversion_spec=conversion_spec,
            dsl_rules=dsl_rules,
            is_public=is_public,
        )

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
        bounding_boxes_enabled: bool | None = None,
        conversion_spec: dict[str, Any] | None | NotGiven = NOT_GIVEN,
        dsl_rules: str | None | NotGiven = NOT_GIVEN,
        is_public: bool | None = None,
    ) -> DocumentType:
        """Update an existing document type.

        All fields are optional; only provided fields will be updated.

        Args:
            type_id: The document type's internal ID (not its ``codeType``) to update.
            name: New document type name.
            description: New description.
            json_schema: New JSON Schema for document validation.
            is_draft: New draft status.
            prompt_hints: New OCR prompt hints.
            identify_prompt_hints: New identification prompt hints.
            conversion_mode: New processing mode.
            keep_property_ordering: New property ordering setting.
            bounding_boxes_enabled: Also return per-field locations (admin API keys only).
            conversion_spec: New export spec. ``None`` clears it; omit to keep it.
            dsl_rules: New DSL validation rules (64 KiB max). ``None`` or ``""``
                clears them; omit to keep the saved rules. Invalid syntax raises
                DSLValidationError.
            is_public: New public/private flag.

        Returns:
            The updated document type.

        Raises:
            NotFoundError: If the document type doesn't exist.
            PermissionDeniedError: If insufficient permissions.

        Example:
            >>> doc_type = client.document_types.update(
            ...     "cm0example0000000000000id",
            ...     name="Updated Invoice",
            ...     is_draft=False,
            ... )
            >>> print(f"Updated: {doc_type.name}")
        """
        body = _update_body(
            name=name,
            description=description,
            json_schema=json_schema,
            is_draft=is_draft,
            prompt_hints=prompt_hints,
            identify_prompt_hints=identify_prompt_hints,
            conversion_mode=conversion_mode,
            keep_property_ordering=keep_property_ordering,
            bounding_boxes_enabled=bounding_boxes_enabled,
            conversion_spec=conversion_spec,
            dsl_rules=dsl_rules,
            is_public=is_public,
        )

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
            search: Search term matched against name, ``codeType`` and description.

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
            search: Search term matched against name, ``codeType`` and description.

        Returns:
            An AsyncPage of document types with pagination support.
        """
        return await self._fetch_page(page or 1, limit=limit, search=search)

    async def get(self, type_id: str) -> DocumentType:
        """Get a specific document type by ID.

        Args:
            type_id: The document type's internal ID (not its ``codeType``).

        Returns:
            The document type details including schema.
        """
        response = await self._client._request("GET", f"/api/document-types/{type_id}")
        return DocumentType.model_validate(response.json().get("data", response.json()))

    async def get_by_code(self, code: str) -> DocumentType:
        """Get a document type by its ``codeType``.

        Looks the code up with ``list(search=code)`` across all pages and fetches
        the match with ``get()``. Codes of your organization's own types carry its
        slug as a prefix, so pass the full code (e.g. ``"acme_invoice"``).

        Args:
            code: The exact ``codeType`` of the document type.

        Returns:
            The document type details including schema.

        Raises:
            NotFoundError: If no accessible document type has this exact code.

        Example:
            >>> doc_type = await client.document_types.get_by_code("acme_invoice")
            >>> print(doc_type.id)
        """
        page = await self.list(search=code)
        async for doc_type in page.auto_paging_iter_async():
            if doc_type.codeType == code:
                return await self.get(doc_type.id)
        raise NotFoundError(
            f"Document type with code {code!r} not found", status_code=404
        )

    async def validate(
        self,
        type_id: str,
        data: dict[str, Any],
        *,
        dsl_rules: str | None | NotGiven = NOT_GIVEN,
    ) -> ValidationResult:
        """Validate JSON data against a document type's schema.

        Args:
            type_id: The document type's internal ID (not its ``codeType``) to validate against.
            data: The JSON data to validate.
            dsl_rules: Temporary DSL rules for a dry run. They replace the stored
                rules for this call only (JSON Schema still runs); ``None`` or
                ``""`` validates without DSL. Omit to use the stored rules.

        Returns:
            Validation result with errors and warnings.
        """
        response = await self._client._request(
            "POST",
            f"/api/document-types/{type_id}/validate",
            json=_validate_body(data, dsl_rules),
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
        bounding_boxes_enabled: bool | None = None,
        conversion_spec: dict[str, Any] | None = None,
        dsl_rules: str | None = None,
        is_public: bool | None = None,
    ) -> DocumentType:
        """Create a new document type.

        Args:
            name: Document type name (min 2 characters).
            code_type: Unique code identifier (lowercase alphanumeric and underscores).
                The API prefixes it with the organization slug when missing
                (``"invoice"`` is stored as ``"acme_invoice"``).
            description: Document type description (min 1 character).
            json_schema: JSON Schema for document validation.
            is_draft: Whether the document type is a draft. Defaults to True.
            prompt_hints: Hints for OCR prompt processing.
            identify_prompt_hints: Hints for document identification prompt.
            conversion_mode: Processing mode ("json", "toon", or "multi_prompt").
            keep_property_ordering: Preserve property ordering in schema.
            bounding_boxes_enabled: Also return per-field locations (admin API keys only).
            conversion_spec: Spec mapping extracted JSON to CSV/Excel export columns.
            dsl_rules: DSL validation rules (64 KiB max). Invalid syntax raises
                DSLValidationError.
            is_public: Whether the document type is publicly available.

        Returns:
            The created document type.
        """
        body = _create_body(
            name=name,
            code_type=code_type,
            description=description,
            json_schema=json_schema,
            is_draft=is_draft,
            prompt_hints=prompt_hints,
            identify_prompt_hints=identify_prompt_hints,
            conversion_mode=conversion_mode,
            keep_property_ordering=keep_property_ordering,
            bounding_boxes_enabled=bounding_boxes_enabled,
            conversion_spec=conversion_spec,
            dsl_rules=dsl_rules,
            is_public=is_public,
        )

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
        bounding_boxes_enabled: bool | None = None,
        conversion_spec: dict[str, Any] | None | NotGiven = NOT_GIVEN,
        dsl_rules: str | None | NotGiven = NOT_GIVEN,
        is_public: bool | None = None,
    ) -> DocumentType:
        """Update an existing document type.

        All fields are optional; only provided fields will be updated.

        Args:
            type_id: The document type's internal ID (not its ``codeType``) to update.
            name: New document type name.
            description: New description.
            json_schema: New JSON Schema for document validation.
            is_draft: New draft status.
            prompt_hints: New OCR prompt hints.
            identify_prompt_hints: New identification prompt hints.
            conversion_mode: New processing mode.
            keep_property_ordering: New property ordering setting.
            bounding_boxes_enabled: Also return per-field locations (admin API keys only).
            conversion_spec: New export spec. ``None`` clears it; omit to keep it.
            dsl_rules: New DSL validation rules (64 KiB max). ``None`` or ``""``
                clears them; omit to keep the saved rules. Invalid syntax raises
                DSLValidationError.
            is_public: New public/private flag.

        Returns:
            The updated document type.
        """
        body = _update_body(
            name=name,
            description=description,
            json_schema=json_schema,
            is_draft=is_draft,
            prompt_hints=prompt_hints,
            identify_prompt_hints=identify_prompt_hints,
            conversion_mode=conversion_mode,
            keep_property_ordering=keep_property_ordering,
            bounding_boxes_enabled=bounding_boxes_enabled,
            conversion_spec=conversion_spec,
            dsl_rules=dsl_rules,
            is_public=is_public,
        )

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
