"""Identify resource for document type identification operations."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from .._files import prepare_base64_upload, prepare_file_upload, prepare_url_upload
from .._types import FileInput
from ..types.identify import IdentificationResult, IdentificationStatus

if TYPE_CHECKING:
    from .._base_client import BaseAsyncClient, BaseClient


class Identify:
    """Synchronous document identification operations.

    Example:
        >>> client = Client(api_key="...")
        >>> result = client.identify.run(file=Path("document.pdf"))
        >>> print(f"Type: {result.document_type.code}")
        >>> print(f"Confidence: {result.document_type.confidence}")
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the Identify resource.

        Args:
            client: The parent client instance.
        """
        self._client = client

    def run(
        self,
        *,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
    ) -> IdentificationResult:
        """Identify the type of a document synchronously.

        Sends a document to the API and returns the identified document type
        with confidence scores.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.

        Returns:
            The identification result with document type and alternatives.

        Raises:
            ValueError: If no file input is provided.
            BadRequestError: If the request is invalid.
            AuthenticationError: If the API key is invalid.

        Example:
            >>> result = client.identify.run(file=Path("unknown.pdf"))
            >>> print(f"Identified as: {result.document_type.name}")
            >>> for alt in result.alternatives:
            ...     print(f"  Alternative: {alt.name} ({alt.confidence:.2%})")
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            response = self._client._request("POST", "/api/identify", files=files)
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            response = self._client._request("POST", "/api/identify", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            response = self._client._request("POST", "/api/identify", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return IdentificationResult.model_validate(response.json())

    def run_async(
        self,
        *,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
    ) -> IdentificationStatus:
        """Start an asynchronous document identification.

        Initiates an identification job and returns immediately with an ID.
        Use get_status() to poll for completion.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.

        Returns:
            The initial identification status with identification_id.

        Example:
            >>> status = client.identify.run_async(file=Path("document.pdf"))
            >>> final = status.wait()
            >>> print(f"Type: {final.document_type.code}")
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            response = self._client._request("POST", "/api/identify-async", files=files)
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            response = self._client._request("POST", "/api/identify-async", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            response = self._client._request("POST", "/api/identify-async", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        status = IdentificationStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    def get_status(self, identification_id: str) -> IdentificationStatus:
        """Get the status of an asynchronous identification.

        Args:
            identification_id: The identification ID returned by run_async().

        Returns:
            The current identification status.

        Example:
            >>> status = client.identify.get_status("id_abc123")
            >>> if status.is_success():
            ...     print(status.document_type.name)
        """
        response = self._client._request(
            "GET", f"/api/identify-async/status/{identification_id}"
        )
        status = IdentificationStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    @cached_property
    def with_raw_response(self) -> IdentifyWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = client.identify.with_raw_response.run(
            ...     file=Path("document.pdf")
            ... )
            >>> print(response.status_code)
            >>> print(response.headers)
            >>> result = response.parse()
        """
        return IdentifyWithRawResponse(self)


class AsyncIdentify:
    """Asynchronous document identification operations.

    Example:
        >>> async with AsyncClient(api_key="...") as client:
        ...     result = await client.identify.run(file=Path("document.pdf"))
        ...     print(f"Type: {result.document_type.code}")
    """

    def __init__(self, client: BaseAsyncClient) -> None:
        """Initialize the AsyncIdentify resource.

        Args:
            client: The parent async client instance.
        """
        self._client = client

    async def run(
        self,
        *,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
    ) -> IdentificationResult:
        """Identify the type of a document asynchronously.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.

        Returns:
            The identification result with document type and alternatives.
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            response = await self._client._request("POST", "/api/identify", files=files)
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            response = await self._client._request("POST", "/api/identify", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            response = await self._client._request("POST", "/api/identify", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        return IdentificationResult.model_validate(response.json())

    async def run_async(
        self,
        *,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
    ) -> IdentificationStatus:
        """Start an asynchronous document identification.

        Args:
            file: File to identify (Path, bytes, or file-like object).
            url: URL of the document to identify (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.

        Returns:
            The initial identification status with identification_id.
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            response = await self._client._request("POST", "/api/identify-async", files=files)
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            response = await self._client._request("POST", "/api/identify-async", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            response = await self._client._request("POST", "/api/identify-async", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        status = IdentificationStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    async def get_status(self, identification_id: str) -> IdentificationStatus:
        """Get the status of an asynchronous identification.

        Args:
            identification_id: The identification ID returned by run_async().

        Returns:
            The current identification status.
        """
        response = await self._client._request(
            "GET", f"/api/identify-async/status/{identification_id}"
        )
        status = IdentificationStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    @cached_property
    def with_raw_response(self) -> AsyncIdentifyWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = await client.identify.with_raw_response.run(
            ...     file=Path("document.pdf")
            ... )
            >>> print(response.status_code)
            >>> result = response.parse()
        """
        return AsyncIdentifyWithRawResponse(self)


# Import here to avoid circular imports
from .._response import (  # noqa: E402
    AsyncIdentifyWithRawResponse,
    IdentifyWithRawResponse,
)
