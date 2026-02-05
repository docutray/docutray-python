"""Raw response wrappers for HTTP debugging access."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import httpx

if TYPE_CHECKING:
    from ._pagination import AsyncPage, Page
    from .resources.convert import AsyncConvert, Convert
    from .resources.document_types import AsyncDocumentTypes, DocumentTypes
    from .resources.identify import AsyncIdentify, Identify
    from .resources.knowledge_bases import AsyncKnowledgeBases, KnowledgeBases
    from .resources.steps import AsyncSteps, Steps
    from .types.convert import ConversionResult, ConversionStatus
    from .types.document_type import DocumentType, ValidationResult
    from .types.identify import IdentificationResult, IdentificationStatus
    from .types.knowledge_base import KnowledgeBase, SearchResult, SyncResult
    from .types.step import StepExecutionStatus

T = TypeVar("T")


class RawResponse(Generic[T]):
    """A wrapper around an HTTP response providing access to raw details.

    This class wraps an httpx.Response and provides convenient access to
    status code, headers, and the ability to parse the response body
    into a typed model.

    Example:
        >>> response = client.convert.with_raw_response.run(
        ...     file=Path("invoice.pdf"),
        ...     document_type_code="invoice"
        ... )
        >>> print(f"Status: {response.status_code}")
        >>> print(f"Request ID: {response.headers.get('x-request-id')}")
        >>> result = response.parse()
        >>> print(result.data)
    """

    def __init__(
        self,
        response: httpx.Response,
        parse_func: Callable[[httpx.Response], T],
    ) -> None:
        """Initialize a RawResponse.

        Args:
            response: The underlying httpx.Response.
            parse_func: Function or callable to parse the response into typed model.
        """
        self._response = response
        self._parse_func = parse_func

    @property
    def status_code(self) -> int:
        """The HTTP status code of the response."""
        return self._response.status_code

    @property
    def headers(self) -> httpx.Headers:
        """The HTTP headers of the response."""
        return self._response.headers

    @property
    def http_response(self) -> httpx.Response:
        """The underlying httpx.Response object."""
        return self._response

    @property
    def content(self) -> bytes:
        """The raw response body as bytes."""
        return self._response.content

    @property
    def text(self) -> str:
        """The response body as a string."""
        return self._response.text

    def json(self) -> Any:
        """Parse the response body as JSON."""
        return self._response.json()

    def parse(self) -> T:
        """Parse the response body into the appropriate typed model.

        Returns:
            The parsed response model.
        """
        return self._parse_func(self._response)


# ============================================================================
# Convert Resource Raw Response Wrappers
# ============================================================================


class ConvertWithRawResponse:
    """Wrapper for Convert resource that returns raw HTTP responses."""

    def __init__(self, convert: Convert) -> None:
        """Initialize the wrapper.

        Args:
            convert: The Convert resource instance.
        """
        self._convert = convert

    def run(
        self,
        *,
        document_type_code: str,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> RawResponse[ConversionResult]:
        """Convert a document and return the raw HTTP response.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file.
            document_metadata: Additional metadata to include.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.convert import ConversionResult

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)

            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                data["document_metadata"] = json.dumps(document_metadata)
            response = self._convert._client._request(
                "POST", "/api/convert", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = self._convert._client._request("POST", "/api/convert", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = self._convert._client._request("POST", "/api/convert", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: ConversionResult.model_validate(r.json()),
        )

    def run_async(
        self,
        *,
        document_type_code: str,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> RawResponse[ConversionStatus]:
        """Start async conversion and return the raw HTTP response.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file.
            document_metadata: Additional metadata to include.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.convert import ConversionStatus

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)

            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                data["document_metadata"] = json.dumps(document_metadata)
            response = self._convert._client._request(
                "POST", "/api/convert-async", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = self._convert._client._request(
                "POST", "/api/convert-async", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = self._convert._client._request(
                "POST", "/api/convert-async", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: ConversionStatus.model_validate(r.json()),
        )

    def get_status(self, conversion_id: str) -> RawResponse[ConversionStatus]:
        """Get conversion status and return the raw HTTP response.

        Args:
            conversion_id: The conversion ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.convert import ConversionStatus

        response = self._convert._client._request(
            "GET", f"/api/convert-async/status/{conversion_id}"
        )
        return RawResponse(
            response,
            lambda r: ConversionStatus.model_validate(r.json()),
        )


class AsyncConvertWithRawResponse:
    """Wrapper for AsyncConvert resource that returns raw HTTP responses."""

    def __init__(self, convert: AsyncConvert) -> None:
        """Initialize the wrapper.

        Args:
            convert: The AsyncConvert resource instance.
        """
        self._convert = convert

    async def run(
        self,
        *,
        document_type_code: str,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> RawResponse[ConversionResult]:
        """Convert a document and return the raw HTTP response.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file.
            document_metadata: Additional metadata to include.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.convert import ConversionResult

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)

            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                data["document_metadata"] = json.dumps(document_metadata)
            response = await self._convert._client._request(
                "POST", "/api/convert", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = await self._convert._client._request(
                "POST", "/api/convert", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = await self._convert._client._request(
                "POST", "/api/convert", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: ConversionResult.model_validate(r.json()),
        )

    async def run_async(
        self,
        *,
        document_type_code: str,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> RawResponse[ConversionStatus]:
        """Start async conversion and return the raw HTTP response.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file.
            document_metadata: Additional metadata to include.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.convert import ConversionStatus

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)

            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                data["document_metadata"] = json.dumps(document_metadata)
            response = await self._convert._client._request(
                "POST", "/api/convert-async", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = await self._convert._client._request(
                "POST", "/api/convert-async", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata
            response = await self._convert._client._request(
                "POST", "/api/convert-async", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: ConversionStatus.model_validate(r.json()),
        )

    async def get_status(self, conversion_id: str) -> RawResponse[ConversionStatus]:
        """Get conversion status and return the raw HTTP response.

        Args:
            conversion_id: The conversion ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.convert import ConversionStatus

        response = await self._convert._client._request(
            "GET", f"/api/convert-async/status/{conversion_id}"
        )
        return RawResponse(
            response,
            lambda r: ConversionStatus.model_validate(r.json()),
        )


# ============================================================================
# Identify Resource Raw Response Wrappers
# ============================================================================


class IdentifyWithRawResponse:
    """Wrapper for Identify resource that returns raw HTTP responses."""

    def __init__(self, identify: Identify) -> None:
        """Initialize the wrapper.

        Args:
            identify: The Identify resource instance.
        """
        self._identify = identify

    def run(
        self,
        *,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_type_code_options: list[str] | None = None,
    ) -> RawResponse[IdentificationResult]:
        """Identify a document and return the raw HTTP response.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify.
            file_base64: Base64-encoded document.
            content_type: Content type of the file.
            document_type_code_options: List of document type codes to limit
                identification to.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.identify import IdentificationResult

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)
            data: dict[str, Any] = {"image_content_type": upload.content_type}
            if document_type_code_options:
                data["document_type_code_options"] = json.dumps(
                    document_type_code_options
                )
            response = self._identify._client._request(
                "POST", "/api/identify", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = self._identify._client._request(
                "POST", "/api/identify", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = self._identify._client._request(
                "POST", "/api/identify", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: IdentificationResult.model_validate(r.json()),
        )

    def run_async(
        self,
        *,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_type_code_options: list[str] | None = None,
    ) -> RawResponse[IdentificationStatus]:
        """Start async identification and return the raw HTTP response.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify.
            file_base64: Base64-encoded document.
            content_type: Content type of the file.
            document_type_code_options: List of document type codes to limit
                identification to.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.identify import IdentificationStatus

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)
            data: dict[str, Any] = {"image_content_type": upload.content_type}
            if document_type_code_options:
                data["document_type_code_options"] = json.dumps(
                    document_type_code_options
                )
            response = self._identify._client._request(
                "POST", "/api/identify-async", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = self._identify._client._request(
                "POST", "/api/identify-async", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = self._identify._client._request(
                "POST", "/api/identify-async", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: IdentificationStatus.model_validate(r.json()),
        )

    def get_status(self, identification_id: str) -> RawResponse[IdentificationStatus]:
        """Get identification status and return the raw HTTP response.

        Args:
            identification_id: The identification ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.identify import IdentificationStatus

        response = self._identify._client._request(
            "GET", f"/api/identify-async/status/{identification_id}"
        )
        return RawResponse(
            response,
            lambda r: IdentificationStatus.model_validate(r.json()),
        )


class AsyncIdentifyWithRawResponse:
    """Wrapper for AsyncIdentify resource that returns raw HTTP responses."""

    def __init__(self, identify: AsyncIdentify) -> None:
        """Initialize the wrapper.

        Args:
            identify: The AsyncIdentify resource instance.
        """
        self._identify = identify

    async def run(
        self,
        *,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_type_code_options: list[str] | None = None,
    ) -> RawResponse[IdentificationResult]:
        """Identify a document and return the raw HTTP response.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify.
            file_base64: Base64-encoded document.
            content_type: Content type of the file.
            document_type_code_options: List of document type codes to limit
                identification to.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.identify import IdentificationResult

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)
            data: dict[str, Any] = {"image_content_type": upload.content_type}
            if document_type_code_options:
                data["document_type_code_options"] = json.dumps(
                    document_type_code_options
                )
            response = await self._identify._client._request(
                "POST", "/api/identify", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = await self._identify._client._request(
                "POST", "/api/identify", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = await self._identify._client._request(
                "POST", "/api/identify", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: IdentificationResult.model_validate(r.json()),
        )

    async def run_async(
        self,
        *,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_type_code_options: list[str] | None = None,
    ) -> RawResponse[IdentificationStatus]:
        """Start async identification and return the raw HTTP response.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify.
            file_base64: Base64-encoded document.
            content_type: Content type of the file.
            document_type_code_options: List of document type codes to limit
                identification to.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.identify import IdentificationStatus

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)
            data: dict[str, Any] = {"image_content_type": upload.content_type}
            if document_type_code_options:
                data["document_type_code_options"] = json.dumps(
                    document_type_code_options
                )
            response = await self._identify._client._request(
                "POST", "/api/identify-async", files=upload.files, data=data
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = await self._identify._client._request(
                "POST", "/api/identify-async", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if document_type_code_options:
                body["document_type_code_options"] = document_type_code_options
            response = await self._identify._client._request(
                "POST", "/api/identify-async", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: IdentificationStatus.model_validate(r.json()),
        )

    async def get_status(
        self, identification_id: str
    ) -> RawResponse[IdentificationStatus]:
        """Get identification status and return the raw HTTP response.

        Args:
            identification_id: The identification ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.identify import IdentificationStatus

        response = await self._identify._client._request(
            "GET", f"/api/identify-async/status/{identification_id}"
        )
        return RawResponse(
            response,
            lambda r: IdentificationStatus.model_validate(r.json()),
        )


# ============================================================================
# DocumentTypes Resource Raw Response Wrappers
# ============================================================================


class DocumentTypesWithRawResponse:
    """Wrapper for DocumentTypes resource that returns raw HTTP responses."""

    def __init__(self, document_types: DocumentTypes) -> None:
        """Initialize the wrapper.

        Args:
            document_types: The DocumentTypes resource instance.
        """
        self._document_types = document_types

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> RawResponse[Page[DocumentType]]:
        """List document types and return the raw HTTP response.

        Args:
            page: Page number (1-indexed).
            limit: Number of items per page.
            search: Search term to filter document types.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._pagination import Page
        from .types.document_type import DocumentType
        from .types.shared import Pagination

        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = self._document_types._client._request(
            "GET", "/api/document-types", params=params
        )

        def parse_page(r: httpx.Response) -> Page[DocumentType]:
            data = r.json()
            pagination = Pagination.model_validate(data.get("pagination", {}))
            items = [DocumentType.model_validate(item) for item in data.get("data", [])]
            return Page(
                data=items,
                pagination=pagination,
                fetch_page=lambda p: self._document_types._fetch_page(
                    p, limit=limit, search=search
                ),
            )

        return RawResponse(response, parse_page)

    def get(self, type_id: str) -> RawResponse[DocumentType]:
        """Get a document type and return the raw HTTP response.

        Args:
            type_id: The document type ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.document_type import DocumentType

        response = self._document_types._client._request(
            "GET", f"/api/document-types/{type_id}"
        )
        return RawResponse(
            response,
            lambda r: DocumentType.model_validate(r.json()),
        )

    def validate(
        self,
        type_id: str,
        data: dict[str, Any],
    ) -> RawResponse[ValidationResult]:
        """Validate data against a document type and return the raw HTTP response.

        Args:
            type_id: The document type ID.
            data: The JSON data to validate.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.document_type import ValidationResult

        response = self._document_types._client._request(
            "POST",
            f"/api/document-types/{type_id}/validate",
            json=data,
        )
        return RawResponse(
            response,
            lambda r: ValidationResult.model_validate(r.json()),
        )


class AsyncDocumentTypesWithRawResponse:
    """Wrapper for AsyncDocumentTypes resource that returns raw HTTP responses."""

    def __init__(self, document_types: AsyncDocumentTypes) -> None:
        """Initialize the wrapper.

        Args:
            document_types: The AsyncDocumentTypes resource instance.
        """
        self._document_types = document_types

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> RawResponse[AsyncPage[DocumentType]]:
        """List document types and return the raw HTTP response.

        Args:
            page: Page number (1-indexed).
            limit: Number of items per page.
            search: Search term to filter document types.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._pagination import AsyncPage
        from .types.document_type import DocumentType
        from .types.shared import Pagination

        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = await self._document_types._client._request(
            "GET", "/api/document-types", params=params
        )

        def parse_page(r: httpx.Response) -> AsyncPage[DocumentType]:
            data = r.json()
            pagination = Pagination.model_validate(data.get("pagination", {}))
            items = [DocumentType.model_validate(item) for item in data.get("data", [])]
            return AsyncPage(
                data=items,
                pagination=pagination,
                fetch_page=lambda p: self._document_types._fetch_page(
                    p, limit=limit, search=search
                ),
            )

        return RawResponse(response, parse_page)

    async def get(self, type_id: str) -> RawResponse[DocumentType]:
        """Get a document type and return the raw HTTP response.

        Args:
            type_id: The document type ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.document_type import DocumentType

        response = await self._document_types._client._request(
            "GET", f"/api/document-types/{type_id}"
        )
        return RawResponse(
            response,
            lambda r: DocumentType.model_validate(r.json()),
        )

    async def validate(
        self,
        type_id: str,
        data: dict[str, Any],
    ) -> RawResponse[ValidationResult]:
        """Validate data against a document type and return the raw HTTP response.

        Args:
            type_id: The document type ID.
            data: The JSON data to validate.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.document_type import ValidationResult

        response = await self._document_types._client._request(
            "POST",
            f"/api/document-types/{type_id}/validate",
            json=data,
        )
        return RawResponse(
            response,
            lambda r: ValidationResult.model_validate(r.json()),
        )


# ============================================================================
# Steps Resource Raw Response Wrappers
# ============================================================================


class StepsWithRawResponse:
    """Wrapper for Steps resource that returns raw HTTP responses."""

    def __init__(self, steps: Steps) -> None:
        """Initialize the wrapper.

        Args:
            steps: The Steps resource instance.
        """
        self._steps = steps

    def run_async(
        self,
        *,
        step_id: str,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        input_data: dict[str, Any] | None = None,
    ) -> RawResponse[StepExecutionStatus]:
        """Execute a step and return the raw HTTP response.

        Args:
            step_id: The step ID to execute.
            file: File to process (Path, bytes, or file-like object).
            url: URL of the document to process.
            file_base64: Base64-encoded document.
            content_type: Content type of the file.
            input_data: Additional input data for the step.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.step import StepExecutionStatus

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)

            data: dict[str, Any] = {}
            if input_data:
                data["input_data"] = json.dumps(input_data)
            response = self._steps._client._request(
                "POST",
                f"/api/steps-async/{step_id}",
                files=upload.files,
                data=data if data else None,
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if input_data:
                body["input_data"] = input_data
            response = self._steps._client._request(
                "POST", f"/api/steps-async/{step_id}", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if input_data:
                body["input_data"] = input_data
            response = self._steps._client._request(
                "POST", f"/api/steps-async/{step_id}", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: StepExecutionStatus.model_validate(r.json()),
        )

    def get_status(self, execution_id: str) -> RawResponse[StepExecutionStatus]:
        """Get step execution status and return the raw HTTP response.

        Args:
            execution_id: The execution ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.step import StepExecutionStatus

        response = self._steps._client._request(
            "GET", f"/api/steps-async/status/{execution_id}"
        )
        return RawResponse(
            response,
            lambda r: StepExecutionStatus.model_validate(r.json()),
        )


class AsyncStepsWithRawResponse:
    """Wrapper for AsyncSteps resource that returns raw HTTP responses."""

    def __init__(self, steps: AsyncSteps) -> None:
        """Initialize the wrapper.

        Args:
            steps: The AsyncSteps resource instance.
        """
        self._steps = steps

    async def run_async(
        self,
        *,
        step_id: str,
        file: Any = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        input_data: dict[str, Any] | None = None,
    ) -> RawResponse[StepExecutionStatus]:
        """Execute a step and return the raw HTTP response.

        Args:
            step_id: The step ID to execute.
            file: File to process (Path, bytes, or file-like object).
            url: URL of the document to process.
            file_base64: Base64-encoded document.
            content_type: Content type of the file.
            input_data: Additional input data for the step.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._files import (
            prepare_base64_upload,
            prepare_file_upload,
            prepare_url_upload,
        )
        from .types.step import StepExecutionStatus

        if file is not None:
            upload = prepare_file_upload(file, content_type=content_type)

            data: dict[str, Any] = {}
            if input_data:
                data["input_data"] = json.dumps(input_data)
            response = await self._steps._client._request(
                "POST",
                f"/api/steps-async/{step_id}",
                files=upload.files,
                data=data if data else None,
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if input_data:
                body["input_data"] = input_data
            response = await self._steps._client._request(
                "POST", f"/api/steps-async/{step_id}", json=body
            )
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if input_data:
                body["input_data"] = input_data
            response = await self._steps._client._request(
                "POST", f"/api/steps-async/{step_id}", json=body
            )
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return RawResponse(
            response,
            lambda r: StepExecutionStatus.model_validate(r.json()),
        )

    async def get_status(self, execution_id: str) -> RawResponse[StepExecutionStatus]:
        """Get step execution status and return the raw HTTP response.

        Args:
            execution_id: The execution ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.step import StepExecutionStatus

        response = await self._steps._client._request(
            "GET", f"/api/steps-async/status/{execution_id}"
        )
        return RawResponse(
            response,
            lambda r: StepExecutionStatus.model_validate(r.json()),
        )


# ============================================================================
# KnowledgeBases Resource Raw Response Wrappers
# ============================================================================


class KnowledgeBasesWithRawResponse:
    """Wrapper for KnowledgeBases resource that returns raw HTTP responses."""

    def __init__(self, knowledge_bases: KnowledgeBases) -> None:
        """Initialize the wrapper.

        Args:
            knowledge_bases: The KnowledgeBases resource instance.
        """
        self._knowledge_bases = knowledge_bases

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> RawResponse[Page[KnowledgeBase]]:
        """List knowledge bases and return the raw HTTP response.

        Args:
            page: Page number (1-indexed).
            limit: Number of items per page.
            search: Search term to filter by name or description.
            is_active: Filter by active status.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._pagination import Page
        from .types.knowledge_base import KnowledgeBase
        from .types.shared import Pagination

        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if is_active is not None:
            params["isActive"] = is_active

        response = self._knowledge_bases._client._request(
            "GET", "/api/knowledge-bases", params=params
        )

        def parse_page(r: httpx.Response) -> Page[KnowledgeBase]:
            data = r.json()
            pagination = Pagination.model_validate(data.get("pagination", {}))
            items = [
                KnowledgeBase.model_validate(item) for item in data.get("data", [])
            ]
            return Page(
                data=items,
                pagination=pagination,
                fetch_page=lambda p: self._knowledge_bases._fetch_page(
                    p, limit=limit, search=search, is_active=is_active
                ),
            )

        return RawResponse(response, parse_page)

    def get(self, knowledge_base_id: str) -> RawResponse[KnowledgeBase]:
        """Get a knowledge base and return the raw HTTP response.

        Args:
            knowledge_base_id: The knowledge base ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.knowledge_base import KnowledgeBase

        response = self._knowledge_bases._client._request(
            "GET", f"/api/knowledge-bases/{knowledge_base_id}"
        )
        return RawResponse(
            response,
            lambda r: KnowledgeBase.model_validate(r.json().get("data", r.json())),
        )

    def search(
        self,
        knowledge_base_id: str,
        *,
        query: str,
        limit: int | None = None,
        similarity_threshold: float | None = None,
        include_metadata: bool | None = None,
    ) -> RawResponse[SearchResult]:
        """Search a knowledge base and return the raw HTTP response.

        Args:
            knowledge_base_id: The knowledge base ID.
            query: Search query text.
            limit: Maximum number of results.
            similarity_threshold: Minimum similarity score.
            include_metadata: Include document metadata.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.knowledge_base import (
            KnowledgeBaseDocument,
            SearchResult,
            SearchResultItem,
        )

        body: dict[str, Any] = {"query": query}
        if limit is not None:
            body["limit"] = limit
        if similarity_threshold is not None:
            body["similarityThreshold"] = similarity_threshold
        if include_metadata is not None:
            body["includeMetadata"] = include_metadata

        response = self._knowledge_bases._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/search",
            json=body,
        )

        def parse_search(r: httpx.Response) -> SearchResult:
            data = r.json()
            items = []
            for item_data in data.get("data", []):
                doc = KnowledgeBaseDocument.model_validate(
                    item_data.get("document", {})
                )
                items.append(
                    SearchResultItem(
                        document=doc, similarity=item_data.get("similarity", 0)
                    )
                )
            return SearchResult(
                data=items,
                query=data.get("query"),
                resultsCount=data.get("resultsCount", len(items)),
            )

        return RawResponse(response, parse_search)

    def sync(
        self,
        knowledge_base_id: str,
        *,
        regenerate_embeddings: bool | None = None,
    ) -> RawResponse[SyncResult]:
        """Sync a knowledge base and return the raw HTTP response.

        Args:
            knowledge_base_id: The knowledge base ID.
            regenerate_embeddings: Whether to regenerate all embeddings.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.knowledge_base import SyncResult

        body: dict[str, Any] = {}
        if regenerate_embeddings is not None:
            body["regenerateEmbeddings"] = regenerate_embeddings

        response = self._knowledge_bases._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/sync",
            json=body if body else None,
        )
        return RawResponse(
            response,
            lambda r: SyncResult.model_validate(r.json().get("data", r.json())),
        )


class AsyncKnowledgeBasesWithRawResponse:
    """Wrapper for AsyncKnowledgeBases resource that returns raw HTTP responses."""

    def __init__(self, knowledge_bases: AsyncKnowledgeBases) -> None:
        """Initialize the wrapper.

        Args:
            knowledge_bases: The AsyncKnowledgeBases resource instance.
        """
        self._knowledge_bases = knowledge_bases

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> RawResponse[AsyncPage[KnowledgeBase]]:
        """List knowledge bases and return the raw HTTP response.

        Args:
            page: Page number (1-indexed).
            limit: Number of items per page.
            search: Search term to filter by name or description.
            is_active: Filter by active status.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from ._pagination import AsyncPage
        from .types.knowledge_base import KnowledgeBase
        from .types.shared import Pagination

        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if is_active is not None:
            params["isActive"] = is_active

        response = await self._knowledge_bases._client._request(
            "GET", "/api/knowledge-bases", params=params
        )

        def parse_page(r: httpx.Response) -> AsyncPage[KnowledgeBase]:
            data = r.json()
            pagination = Pagination.model_validate(data.get("pagination", {}))
            items = [
                KnowledgeBase.model_validate(item) for item in data.get("data", [])
            ]
            return AsyncPage(
                data=items,
                pagination=pagination,
                fetch_page=lambda p: self._knowledge_bases._fetch_page(
                    p, limit=limit, search=search, is_active=is_active
                ),
            )

        return RawResponse(response, parse_page)

    async def get(self, knowledge_base_id: str) -> RawResponse[KnowledgeBase]:
        """Get a knowledge base and return the raw HTTP response.

        Args:
            knowledge_base_id: The knowledge base ID.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.knowledge_base import KnowledgeBase

        response = await self._knowledge_bases._client._request(
            "GET", f"/api/knowledge-bases/{knowledge_base_id}"
        )
        return RawResponse(
            response,
            lambda r: KnowledgeBase.model_validate(r.json().get("data", r.json())),
        )

    async def search(
        self,
        knowledge_base_id: str,
        *,
        query: str,
        limit: int | None = None,
        similarity_threshold: float | None = None,
        include_metadata: bool | None = None,
    ) -> RawResponse[SearchResult]:
        """Search a knowledge base and return the raw HTTP response.

        Args:
            knowledge_base_id: The knowledge base ID.
            query: Search query text.
            limit: Maximum number of results.
            similarity_threshold: Minimum similarity score.
            include_metadata: Include document metadata.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.knowledge_base import (
            KnowledgeBaseDocument,
            SearchResult,
            SearchResultItem,
        )

        body: dict[str, Any] = {"query": query}
        if limit is not None:
            body["limit"] = limit
        if similarity_threshold is not None:
            body["similarityThreshold"] = similarity_threshold
        if include_metadata is not None:
            body["includeMetadata"] = include_metadata

        response = await self._knowledge_bases._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/search",
            json=body,
        )

        def parse_search(r: httpx.Response) -> SearchResult:
            data = r.json()
            items = []
            for item_data in data.get("data", []):
                doc = KnowledgeBaseDocument.model_validate(
                    item_data.get("document", {})
                )
                items.append(
                    SearchResultItem(
                        document=doc, similarity=item_data.get("similarity", 0)
                    )
                )
            return SearchResult(
                data=items,
                query=data.get("query"),
                resultsCount=data.get("resultsCount", len(items)),
            )

        return RawResponse(response, parse_search)

    async def sync(
        self,
        knowledge_base_id: str,
        *,
        regenerate_embeddings: bool | None = None,
    ) -> RawResponse[SyncResult]:
        """Sync a knowledge base and return the raw HTTP response.

        Args:
            knowledge_base_id: The knowledge base ID.
            regenerate_embeddings: Whether to regenerate all embeddings.

        Returns:
            RawResponse wrapping the HTTP response.
        """
        from .types.knowledge_base import SyncResult

        body: dict[str, Any] = {}
        if regenerate_embeddings is not None:
            body["regenerateEmbeddings"] = regenerate_embeddings

        response = await self._knowledge_bases._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/sync",
            json=body if body else None,
        )
        return RawResponse(
            response,
            lambda r: SyncResult.model_validate(r.json().get("data", r.json())),
        )
