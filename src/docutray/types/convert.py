"""Types for document conversion operations."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict

from .validation import ConversionValidation

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from ..resources.convert import AsyncConvert, Convert

ConversionStatusType = Literal["ENQUEUED", "PROCESSING", "SUCCESS", "ERROR"]


class BoundingBox(BaseModel):
    """Bounding box of a value, as floats in 0..1 relative to its page (origin top-left)."""

    model_config = ConfigDict(extra="allow")

    x0: float
    y0: float
    x1: float
    y1: float


class PageDimensions(BaseModel):
    """Real dimensions of a source document page."""

    model_config = ConfigDict(extra="allow")

    page: int
    """1-based page number."""

    width: float
    height: float

    unit: str = "pt"
    """Unit of ``width`` and ``height``."""


class FieldLocation(BaseModel):
    """Location of one extracted leaf field in the source document."""

    model_config = ConfigDict(extra="allow")

    path: str
    """Restricted JSONPath of the field inside ``data`` (e.g. ``"$.items[0].total"``)."""

    page: int
    """1-based page the value appears on."""

    box: BoundingBox
    """Bounding box of the printed value."""

    confidence: float | None = None
    """Reserved; currently always ``None``."""


class FieldLocations(BaseModel):
    """Per-field locations, present when the document type has ``boundingBoxesEnabled``.

    Best-effort: fields the model could not locate are absent.
    """

    model_config = ConfigDict(extra="allow")

    coordinate_space: str = "page-relative"
    """Coordinate space of the boxes."""

    pages: list[PageDimensions] = []
    """Real page dimensions. Empty for non-PDF documents."""

    fields: list[FieldLocation] = []
    """Located fields."""


class ConversionResult(BaseModel):
    """Result of a synchronous document conversion."""

    model_config = ConfigDict(extra="allow")

    data: dict[str, Any]
    """Extracted data according to the document type JSON schema."""

    validation: ConversionValidation = None
    """Validation of ``data`` against the JSON Schema and DSL rules.

    Informational only. ``None`` when validation was skipped.
    """

    field_locations: FieldLocations | None = None
    """Per-field locations (only when the document type has bounding boxes enabled)."""


class ConversionStatus(BaseModel):
    """Status of an asynchronous document conversion."""

    model_config = ConfigDict(extra="allow")

    conversion_id: str
    """Unique conversion ID."""

    status: ConversionStatusType
    """Current conversion status."""

    status_url: str | None = None
    """URL to check conversion status."""

    request_timestamp: datetime | None = None
    """Timestamp when conversion was started."""

    response_timestamp: datetime | None = None
    """Timestamp when conversion was completed (only for SUCCESS/ERROR)."""

    document_type_code: str | None = None
    """Document type code used for conversion."""

    original_filename: str | None = None
    """Original filename of the processed file."""

    document_metadata: dict[str, Any] | None = None
    """Metadata sent with the original request."""

    data: dict[str, Any] | None = None
    """Extracted data (only present when status is SUCCESS)."""

    error: str | None = None
    """Error message (only present when status is ERROR)."""

    validation: ConversionValidation = None
    """Validation of ``data`` (only meaningful when status is SUCCESS).

    Informational only. ``None`` when validation was skipped or not yet available.
    """

    field_locations: FieldLocations | None = None
    """Per-field locations (only when the document type has bounding boxes enabled)."""

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
        on_status: Callable[[ConversionStatus], None] | None = None,
    ) -> ConversionStatus:
        """Wait for the conversion to complete by polling.

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).
            on_status: Optional callback invoked with each status update.
                Called with the current status after each poll for progress tracking.

        Returns:
            The final conversion status with data or error. A failed
            conversion is returned with ``status == "ERROR"`` (check
            ``is_error()``); it is not raised as an exception.

        Raises:
            APITimeoutError: If the conversion doesn't complete within timeout.
            ValueError: If this status wasn't created by run_async().

        Example:
            >>> status = client.convert.run_async(file=path, document_type_code="invoice")
            >>> final = status.wait(timeout=60, on_status=lambda s: print(s.status))
            >>> if final.is_success():
            ...     print(final.data)
        """
        from .._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
        from .._polling import wait_for_completion

        return wait_for_completion(
            self,
            poll_interval=poll_interval or DEFAULT_POLL_INTERVAL,
            timeout=timeout or DEFAULT_POLL_TIMEOUT,
            on_status=on_status,
        )

    async def wait_async(
        self,
        *,
        poll_interval: float | None = None,
        timeout: float | None = None,
        on_status: Callable[[ConversionStatus], None]
        | Callable[[ConversionStatus], Awaitable[None]]
        | None = None,
    ) -> ConversionStatus:
        """Wait for the conversion to complete by polling (async version).

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).
            on_status: Optional callback invoked with each status update.
                Can be sync or async. Called with the current status after each poll.

        Returns:
            The final conversion status with data or error. A failed
            conversion is returned with ``status == "ERROR"`` (check
            ``is_error()``); it is not raised as an exception.

        Raises:
            APITimeoutError: If the conversion doesn't complete within timeout.
        """
        from .._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
        from .._polling import wait_for_completion_async

        return await wait_for_completion_async(
            self,
            poll_interval=poll_interval or DEFAULT_POLL_INTERVAL,
            timeout=timeout or DEFAULT_POLL_TIMEOUT,
            on_status=on_status,
        )
