"""Convert resource for document conversion operations."""

from __future__ import annotations

import json
from functools import cached_property
from typing import TYPE_CHECKING, Any

from .._files import prepare_base64_upload, prepare_file_upload, prepare_url_upload
from .._types import FileInput
from ..types.convert import ConversionResult, ConversionStatus

if TYPE_CHECKING:
    from .._base_client import BaseAsyncClient, BaseClient


class Convert:
    """Synchronous document conversion operations.

    Example:
        >>> client = Client(api_key="...")
        >>> result = client.convert.run(
        ...     file=Path("invoice.pdf"),
        ...     document_type_code="invoice"
        ... )
        >>> print(result.data)
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the Convert resource.

        Args:
            client: The parent client instance.
        """
        self._client = client

    def run(
        self,
        *,
        document_type_code: str,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> ConversionResult:
        """Convert a document synchronously.

        Sends a document to the API and waits for the conversion result.
        This is suitable for small documents that process quickly.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.
            document_metadata: Additional metadata to include with the document.

        Returns:
            The conversion result with extracted data.

        Raises:
            ValueError: If no file input is provided.
            BadRequestError: If the request is invalid.
            AuthenticationError: If the API key is invalid.

        Example:
            >>> result = client.convert.run(
            ...     file=Path("invoice.pdf"),
            ...     document_type_code="invoice"
            ... )
            >>> print(result.data["total"])
        """
        if file is not None:
            # Multipart upload
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                # Multipart form data requires JSON-stringified metadata
                data["document_metadata"] = json.dumps(document_metadata)

            response = self._client._request("POST", "/api/convert", files=files, data=data)
        elif url is not None:
            # JSON with URL
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = self._client._request("POST", "/api/convert", json=body)
        elif file_base64 is not None:
            # JSON with base64
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = self._client._request("POST", "/api/convert", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return ConversionResult.model_validate(response.json())

    def run_async(
        self,
        *,
        document_type_code: str,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> ConversionStatus:
        """Start an asynchronous document conversion.

        Initiates a conversion job and returns immediately with a conversion ID.
        Use get_status() to poll for completion, or call wait() on the result.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.
            document_metadata: Additional metadata to include with the document.

        Returns:
            The initial conversion status with conversion_id.

        Example:
            >>> status = client.convert.run_async(
            ...     file=Path("large_document.pdf"),
            ...     document_type_code="invoice"
            ... )
            >>> print(f"Conversion ID: {status.conversion_id}")
            >>> # Poll for completion
            >>> final = status.wait()
        """
        if file is not None:
            # Multipart upload
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                # Multipart form data requires JSON-stringified metadata
                data["document_metadata"] = json.dumps(document_metadata)

            response = self._client._request("POST", "/api/convert-async", files=files, data=data)
        elif url is not None:
            # JSON with URL
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = self._client._request("POST", "/api/convert-async", json=body)
        elif file_base64 is not None:
            # JSON with base64
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = self._client._request("POST", "/api/convert-async", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        status = ConversionStatus.model_validate(response.json())
        # Store reference for polling
        object.__setattr__(status, "_resource", self)
        return status

    def get_status(self, conversion_id: str) -> ConversionStatus:
        """Get the status of an asynchronous conversion.

        Args:
            conversion_id: The conversion ID returned by run_async().

        Returns:
            The current conversion status.

        Example:
            >>> status = client.convert.get_status("conv_abc123")
            >>> if status.is_success():
            ...     print(status.data)
        """
        response = self._client._request(
            "GET", f"/api/convert-async/status/{conversion_id}"
        )
        status = ConversionStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    @cached_property
    def with_raw_response(self) -> ConvertWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = client.convert.with_raw_response.run(
            ...     file=Path("invoice.pdf"),
            ...     document_type_code="invoice"
            ... )
            >>> print(response.status_code)
            >>> print(response.headers)
            >>> result = response.parse()
        """
        return ConvertWithRawResponse(self)


class AsyncConvert:
    """Asynchronous document conversion operations.

    Example:
        >>> async with AsyncClient(api_key="...") as client:
        ...     result = await client.convert.run(
        ...         file=Path("invoice.pdf"),
        ...         document_type_code="invoice"
        ...     )
        ...     print(result.data)
    """

    def __init__(self, client: BaseAsyncClient) -> None:
        """Initialize the AsyncConvert resource.

        Args:
            client: The parent async client instance.
        """
        self._client = client

    async def run(
        self,
        *,
        document_type_code: str,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> ConversionResult:
        """Convert a document asynchronously.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.
            document_metadata: Additional metadata to include with the document.

        Returns:
            The conversion result with extracted data.
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                # Multipart form data requires JSON-stringified metadata
                data["document_metadata"] = json.dumps(document_metadata)

            response = await self._client._request("POST", "/api/convert", files=files, data=data)
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = await self._client._request("POST", "/api/convert", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = await self._client._request("POST", "/api/convert", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return ConversionResult.model_validate(response.json())

    async def run_async(
        self,
        *,
        document_type_code: str,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> ConversionStatus:
        """Start an asynchronous document conversion.

        Args:
            document_type_code: The document type code to use for conversion.
            file: File to convert (Path, bytes, or file-like object).
            url: URL of the document to convert (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.
            document_metadata: Additional metadata to include with the document.

        Returns:
            The initial conversion status with conversion_id.
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            data: dict[str, Any] = {"document_type_code": document_type_code}
            if document_metadata:
                # Multipart form data requires JSON-stringified metadata
                data["document_metadata"] = json.dumps(document_metadata)

            response = await self._client._request("POST", "/api/convert-async", files=files, data=data)
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = await self._client._request("POST", "/api/convert-async", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            body["document_type_code"] = document_type_code
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = await self._client._request("POST", "/api/convert-async", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        status = ConversionStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    async def get_status(self, conversion_id: str) -> ConversionStatus:
        """Get the status of an asynchronous conversion.

        Args:
            conversion_id: The conversion ID returned by run_async().

        Returns:
            The current conversion status.
        """
        response = await self._client._request(
            "GET", f"/api/convert-async/status/{conversion_id}"
        )
        status = ConversionStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    @cached_property
    def with_raw_response(self) -> AsyncConvertWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = await client.convert.with_raw_response.run(
            ...     file=Path("invoice.pdf"),
            ...     document_type_code="invoice"
            ... )
            >>> print(response.status_code)
            >>> result = response.parse()
        """
        return AsyncConvertWithRawResponse(self)


# Import here to avoid circular imports
from .._response import (  # noqa: E402
    AsyncConvertWithRawResponse,
    ConvertWithRawResponse,
)
