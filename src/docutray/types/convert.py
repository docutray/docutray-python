"""Types for document conversion operations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from ..resources.convert import AsyncConvert, Convert

ConversionStatusType = Literal["ENQUEUED", "PROCESSING", "SUCCESS", "ERROR"]


class ConversionResult(BaseModel):
    """Result of a synchronous document conversion."""

    model_config = ConfigDict(extra="allow")

    data: dict[str, Any]
    """Extracted data according to the document type JSON schema."""


class ConversionStatus(BaseModel):
    """Status of an asynchronous document conversion."""

    model_config = ConfigDict(extra="allow")

    conversion_id: str
    """Unique conversion ID."""

    status: ConversionStatusType
    """Current conversion status."""

    request_timestamp: datetime | None = None
    """Timestamp when conversion was started."""

    response_timestamp: datetime | None = None
    """Timestamp when conversion was completed (only for SUCCESS/ERROR)."""

    document_type_code: str | None = None
    """Document type code used for conversion."""

    original_filename: str | None = None
    """Original filename of the processed file."""

    data: dict[str, Any] | None = None
    """Extracted data (only present when status is SUCCESS)."""

    error: str | None = None
    """Error message (only present when status is ERROR)."""

    # Internal reference to the resource for polling
    _resource: Convert | AsyncConvert | None = None

    def is_complete(self) -> bool:
        """Check if the conversion has completed (success or error)."""
        return self.status in ("SUCCESS", "ERROR")

    def is_success(self) -> bool:
        """Check if the conversion completed successfully."""
        return self.status == "SUCCESS"

    def is_error(self) -> bool:
        """Check if the conversion failed."""
        return self.status == "ERROR"

    def wait(
        self,
        *,
        poll_interval: float | None = None,
        timeout: float | None = None,
    ) -> ConversionStatus:
        """Wait for the conversion to complete by polling.

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).

        Returns:
            The final conversion status with data or error.

        Raises:
            APITimeoutError: If the conversion doesn't complete within timeout.
            ValueError: If this status wasn't created by run_async().

        Example:
            >>> status = client.convert.run_async(file=path, document_type_code="invoice")
            >>> final = status.wait(timeout=60)
            >>> if final.is_success():
            ...     print(final.data)
        """
        from .._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
        from .._polling import wait_for_completion

        return wait_for_completion(
            self,
            poll_interval=poll_interval or DEFAULT_POLL_INTERVAL,
            timeout=timeout or DEFAULT_POLL_TIMEOUT,
        )

    async def wait_async(
        self,
        *,
        poll_interval: float | None = None,
        timeout: float | None = None,
    ) -> ConversionStatus:
        """Wait for the conversion to complete by polling (async version).

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).

        Returns:
            The final conversion status with data or error.

        Raises:
            APITimeoutError: If the conversion doesn't complete within timeout.
        """
        from .._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
        from .._polling import wait_for_completion_async

        return await wait_for_completion_async(
            self,
            poll_interval=poll_interval or DEFAULT_POLL_INTERVAL,
            timeout=timeout or DEFAULT_POLL_TIMEOUT,
        )
