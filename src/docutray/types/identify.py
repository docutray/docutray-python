"""Types for document identification operations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from ..resources.identify import AsyncIdentify, Identify

IdentificationStatusType = Literal["ENQUEUED", "PROCESSING", "SUCCESS", "ERROR"]


class DocumentTypeMatch(BaseModel):
    """A matched document type with confidence score."""

    model_config = ConfigDict(extra="allow")

    code: str
    """Document type code."""

    name: str
    """Document type name."""

    confidence: float
    """Confidence score (0-1)."""


class IdentificationResult(BaseModel):
    """Result of a synchronous document identification."""

    model_config = ConfigDict(extra="allow")

    document_type: DocumentTypeMatch
    """Primary identified document type."""

    alternatives: list[DocumentTypeMatch]
    """Alternative document types with their confidence levels."""


class IdentificationStatus(BaseModel):
    """Status of an asynchronous document identification."""

    model_config = ConfigDict(extra="allow")

    identification_id: str
    """Unique identification ID."""

    status: IdentificationStatusType
    """Current identification status."""

    status_url: str | None = None
    """URL to check identification status."""

    request_timestamp: datetime | None = None
    """Timestamp when identification was started."""

    response_timestamp: datetime | None = None
    """Timestamp when identification was completed (only for SUCCESS/ERROR)."""

    original_filename: str | None = None
    """Original filename of the processed file."""

    document_type: DocumentTypeMatch | None = None
    """Primary identified document type (only present when status is SUCCESS)."""

    alternatives: list[DocumentTypeMatch] | None = None
    """Alternative document types (only present when status is SUCCESS)."""

    error: str | None = None
    """Error message (only present when status is ERROR)."""

    # Internal reference to the resource for polling
    _resource: Identify | AsyncIdentify | None = None

    def is_complete(self) -> bool:
        """Check if the identification has completed (success or error)."""
        return self.status in ("SUCCESS", "ERROR")

    def is_success(self) -> bool:
        """Check if the identification completed successfully."""
        return self.status == "SUCCESS"

    def is_error(self) -> bool:
        """Check if the identification failed."""
        return self.status == "ERROR"

    def wait(
        self,
        *,
        poll_interval: float | None = None,
        timeout: float | None = None,
    ) -> IdentificationStatus:
        """Wait for the identification to complete by polling.

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).

        Returns:
            The final identification status with results or error.

        Raises:
            APITimeoutError: If the identification doesn't complete within timeout.
            ValueError: If this status wasn't created by run_async().

        Example:
            >>> status = client.identify.run_async(file=path)
            >>> final = status.wait(timeout=60)
            >>> if final.is_success():
            ...     print(final.document_type.name)
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
    ) -> IdentificationStatus:
        """Wait for the identification to complete by polling (async version).

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).

        Returns:
            The final identification status with results or error.

        Raises:
            APITimeoutError: If the identification doesn't complete within timeout.
        """
        from .._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
        from .._polling import wait_for_completion_async

        return await wait_for_completion_async(
            self,
            poll_interval=poll_interval or DEFAULT_POLL_INTERVAL,
            timeout=timeout or DEFAULT_POLL_TIMEOUT,
        )
