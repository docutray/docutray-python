"""Types for step execution operations."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from .document_type import ValidationErrorInfo, ValidationWarningInfo

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from ..resources.steps import AsyncSteps, Steps

StepExecutionStatusType = Literal["ENQUEUED", "PROCESSING", "SUCCESS", "ERROR"]


class StepIdentification(BaseModel):
    """Identification result of a step execution."""

    model_config = ConfigDict(extra="allow")

    success: bool | None = None
    """Whether identification succeeded (``True`` even for ``"other"`` documents)."""

    documentTypeCode: str | None = None
    """Identified document type code; ``"other"`` when no configured type matched."""

    confidence: float | None = None
    """Confidence score for automatic identification (omitted for fixed types)."""


class StepValidationSummary(BaseModel):
    """Summarized validation of a step's conversion (informational only).

    Never changes step success. Empty summaries mean validation was skipped.
    """

    model_config = ConfigDict(extra="allow")

    errors: ValidationErrorInfo = Field(default_factory=ValidationErrorInfo)
    """Validation errors summary."""

    warnings: ValidationWarningInfo = Field(default_factory=ValidationWarningInfo)
    """Validation warnings summary."""


class StepExecutionStatus(BaseModel):
    """Status of an asynchronous step execution."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    execution_id: str = Field(
        validation_alias=AliasChoices("execution_id", "id", "conversion_id")
    )
    """Unique execution ID.

    Read from ``execution_id`` (status endpoint), ``id`` (run response) or the
    deprecated ``conversion_id`` alias.
    """

    status: StepExecutionStatusType
    """Current execution status."""

    request_timestamp: datetime | None = None
    """Timestamp when execution was started."""

    response_timestamp: datetime | None = None
    """Timestamp when execution was completed (only for SUCCESS/ERROR)."""

    step_id: str | None = None
    """Step ID that was executed."""

    step_name: str | None = None
    """Name of the step (returned when the execution is started)."""

    original_filename: str | None = None
    """Original filename of the processed file."""

    data: dict[str, Any] | None = None
    """Result data (only present when status is SUCCESS)."""

    error: str | dict[str, Any] | None = None
    """Error message or details (only present when status is ERROR)."""

    identification: StepIdentification | None = None
    """Identification result (only present when status is SUCCESS)."""

    validation: StepValidationSummary | None = None
    """Validation summary (only present when status is SUCCESS)."""

    document_metadata: dict[str, Any] | None = None
    """Metadata sent with the original request (only for SUCCESS/ERROR)."""

    # Internal reference to the resource for polling
    _resource: Steps | AsyncSteps | None = None

    def is_complete(self) -> bool:
        """Check if the execution has completed (success or error)."""
        return self.status in ("SUCCESS", "ERROR")

    def is_success(self) -> bool:
        """Check if the execution completed successfully."""
        return self.status == "SUCCESS"

    def is_error(self) -> bool:
        """Check if the execution failed."""
        return self.status == "ERROR"

    def wait(
        self,
        *,
        poll_interval: float | None = None,
        timeout: float | None = None,
        on_status: Callable[[StepExecutionStatus], None] | None = None,
    ) -> StepExecutionStatus:
        """Wait for the step execution to complete by polling.

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).
            on_status: Optional callback invoked with each status update.
                Called with the current status after each poll for progress tracking.

        Returns:
            The final execution status with data or error. A failed
            execution is returned with ``status == "ERROR"`` (check
            ``is_error()``); it is not raised as an exception.

        Raises:
            APITimeoutError: If the execution doesn't complete within timeout.
            ValueError: If this status wasn't created by run_async().

        Example:
            >>> status = client.steps.run_async(step_id="step_123", file=path)
            >>> final = status.wait(timeout=120, on_status=lambda s: print(s.status))
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
        on_status: Callable[[StepExecutionStatus], None]
        | Callable[[StepExecutionStatus], Awaitable[None]]
        | None = None,
    ) -> StepExecutionStatus:
        """Wait for the step execution to complete by polling (async version).

        Args:
            poll_interval: Seconds between status checks. Defaults to 2.0.
            timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).
            on_status: Optional callback invoked with each status update.
                Can be sync or async. Called with the current status after each poll.

        Returns:
            The final execution status with data or error. A failed
            execution is returned with ``status == "ERROR"`` (check
            ``is_error()``); it is not raised as an exception.

        Raises:
            APITimeoutError: If the execution doesn't complete within timeout.
        """
        from .._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
        from .._polling import wait_for_completion_async

        return await wait_for_completion_async(
            self,
            poll_interval=poll_interval or DEFAULT_POLL_INTERVAL,
            timeout=timeout or DEFAULT_POLL_TIMEOUT,
            on_status=on_status,
        )
