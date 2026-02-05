"""Steps resource for step execution operations."""

from __future__ import annotations

import json
from functools import cached_property
from typing import TYPE_CHECKING, Any

from .._files import prepare_base64_upload, prepare_file_upload, prepare_url_upload
from .._types import FileInput
from ..types.step import StepExecutionStatus

if TYPE_CHECKING:
    from .._base_client import BaseAsyncClient, BaseClient


class Steps:
    """Synchronous step execution operations.

    Steps allow executing predefined document processing workflows.

    Example:
        >>> client = Client(api_key="...")
        >>> status = client.steps.run_async(
        ...     step_id="step_extraction",
        ...     file=Path("document.pdf")
        ... )
        >>> result = status.wait()
        >>> print(result.data)
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the Steps resource.

        Args:
            client: The parent client instance.
        """
        self._client = client

    def run_async(
        self,
        step_id: str,
        *,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> StepExecutionStatus:
        """Execute a step asynchronously.

        Initiates step execution and returns immediately with an execution ID.
        Use get_status() to poll for completion.

        Args:
            step_id: The ID of the step to execute.
            file: File to process (Path, bytes, or file-like object).
            url: URL of the document to process (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.
            document_metadata: Additional metadata to include with the document.

        Returns:
            The initial execution status with execution_id.

        Raises:
            ValueError: If no file input is provided.
            BadRequestError: If the request is invalid.
            NotFoundError: If the step doesn't exist.

        Example:
            >>> status = client.steps.run_async(
            ...     "step_invoice_extraction",
            ...     file=Path("invoice.pdf")
            ... )
            >>> print(f"Execution ID: {status.execution_id}")
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            data: dict[str, Any] = {}
            if document_metadata:
                # Multipart form data requires JSON-stringified metadata
                data["document_metadata"] = json.dumps(document_metadata)

            response = self._client._request(
                "POST", f"/api/steps-async/{step_id}", files=files, data=data if data else None
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = self._client._request("POST", f"/api/steps-async/{step_id}", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = self._client._request("POST", f"/api/steps-async/{step_id}", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        status = StepExecutionStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    def get_status(self, execution_id: str) -> StepExecutionStatus:
        """Get the status of a step execution.

        Args:
            execution_id: The execution ID returned by run_async().

        Returns:
            The current execution status.

        Example:
            >>> status = client.steps.get_status("exec_abc123")
            >>> if status.is_success():
            ...     print(status.data)
        """
        response = self._client._request(
            "GET", f"/api/steps-async/status/{execution_id}"
        )
        status = StepExecutionStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    @cached_property
    def with_raw_response(self) -> StepsWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = client.steps.with_raw_response.run_async(
            ...     step_id="step_extraction",
            ...     file=Path("document.pdf")
            ... )
            >>> print(response.status_code)
            >>> print(response.headers)
            >>> result = response.parse()
        """
        return StepsWithRawResponse(self)


class AsyncSteps:
    """Asynchronous step execution operations.

    Example:
        >>> async with AsyncClient(api_key="...") as client:
        ...     status = await client.steps.run_async(
        ...         step_id="step_extraction",
        ...         file=Path("document.pdf")
        ...     )
        ...     result = await status.wait()
        ...     print(result.data)
    """

    def __init__(self, client: BaseAsyncClient) -> None:
        """Initialize the AsyncSteps resource.

        Args:
            client: The parent async client instance.
        """
        self._client = client

    async def run_async(
        self,
        step_id: str,
        *,
        file: FileInput | None = None,
        url: str | None = None,
        file_base64: str | None = None,
        content_type: str | None = None,
        document_metadata: dict[str, Any] | None = None,
    ) -> StepExecutionStatus:
        """Execute a step asynchronously.

        Args:
            step_id: The ID of the step to execute.
            file: File to process (Path, bytes, or file-like object).
            url: URL of the document to process (alternative to file).
            file_base64: Base64-encoded document (alternative to file).
            content_type: Content type of the file. Auto-detected if not provided.
            document_metadata: Additional metadata to include with the document.

        Returns:
            The initial execution status with execution_id.
        """
        if file is not None:
            field_name, file_tuple = prepare_file_upload(file, content_type=content_type)
            files = {field_name: file_tuple}
            data: dict[str, Any] = {}
            if document_metadata:
                # Multipart form data requires JSON-stringified metadata
                data["document_metadata"] = json.dumps(document_metadata)

            response = await self._client._request(
                "POST", f"/api/steps-async/{step_id}", files=files, data=data if data else None
            )
        elif url is not None:
            body = prepare_url_upload(url, content_type=content_type)
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = await self._client._request("POST", f"/api/steps-async/{step_id}", json=body)
        elif file_base64 is not None:
            body = prepare_base64_upload(file_base64, content_type=content_type)
            if document_metadata:
                body["document_metadata"] = document_metadata

            response = await self._client._request("POST", f"/api/steps-async/{step_id}", json=body)
        else:
            raise ValueError("Must provide one of: file, url, or file_base64")

        status = StepExecutionStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    async def get_status(self, execution_id: str) -> StepExecutionStatus:
        """Get the status of a step execution.

        Args:
            execution_id: The execution ID returned by run_async().

        Returns:
            The current execution status.
        """
        response = await self._client._request(
            "GET", f"/api/steps-async/status/{execution_id}"
        )
        status = StepExecutionStatus.model_validate(response.json())
        object.__setattr__(status, "_resource", self)
        return status

    @cached_property
    def with_raw_response(self) -> AsyncStepsWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = await client.steps.with_raw_response.run_async(
            ...     step_id="step_extraction",
            ...     file=Path("document.pdf")
            ... )
            >>> print(response.status_code)
            >>> result = response.parse()
        """
        return AsyncStepsWithRawResponse(self)


# Import here to avoid circular imports
from .._response import (  # noqa: E402
    AsyncStepsWithRawResponse,
    StepsWithRawResponse,
)
