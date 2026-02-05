"""Polling utilities for async operations."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, TypeVar

from ._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
from ._exceptions import APITimeoutError

if TYPE_CHECKING:
    from .types.convert import ConversionStatus
    from .types.identify import IdentificationStatus
    from .types.step import StepExecutionStatus

T = TypeVar("T", "ConversionStatus", "IdentificationStatus", "StepExecutionStatus")


def wait_for_completion(
    status: T,
    *,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    timeout: float = DEFAULT_POLL_TIMEOUT,
) -> T:
    """Wait for an async operation to complete by polling.

    Args:
        status: The initial status object with a _resource reference.
        poll_interval: Seconds between status checks. Defaults to 2.0.
        timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).

    Returns:
        The final status with completion data.

    Raises:
        APITimeoutError: If the operation doesn't complete within timeout.
        ValueError: If the status object doesn't have a resource reference.
    """
    from .types.convert import ConversionStatus
    from .types.identify import IdentificationStatus
    from .types.step import StepExecutionStatus

    resource = getattr(status, "_resource", None)
    if resource is None:
        raise ValueError(
            "Status object doesn't have a resource reference. "
            "Use get_status() to create a pollable status."
        )

    start_time = time.monotonic()
    current_status = status

    # Check completion first, then sleep if needed (avoids latency for fast ops)
    while True:
        if current_status.is_complete():
            return current_status

        elapsed = time.monotonic() - start_time
        if elapsed >= timeout:
            if isinstance(current_status, ConversionStatus):
                raise APITimeoutError(
                    f"Conversion {current_status.conversion_id} did not complete "
                    f"within {timeout} seconds"
                )
            elif isinstance(current_status, IdentificationStatus):
                raise APITimeoutError(
                    f"Identification {current_status.identification_id} did not complete "
                    f"within {timeout} seconds"
                )
            elif isinstance(current_status, StepExecutionStatus):
                raise APITimeoutError(
                    f"Step execution {current_status.execution_id} did not complete "
                    f"within {timeout} seconds"
                )
            else:
                raise APITimeoutError(
                    f"Operation did not complete within {timeout} seconds"
                )

        # Sleep before polling for new status
        time.sleep(poll_interval)

        # Get fresh status
        if isinstance(current_status, ConversionStatus):
            current_status = resource.get_status(current_status.conversion_id)
        elif isinstance(current_status, IdentificationStatus):
            current_status = resource.get_status(current_status.identification_id)
        elif isinstance(current_status, StepExecutionStatus):
            current_status = resource.get_status(current_status.execution_id)


async def wait_for_completion_async(
    status: T,
    *,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    timeout: float = DEFAULT_POLL_TIMEOUT,
) -> T:
    """Wait for an async operation to complete by polling (async version).

    Args:
        status: The initial status object with a _resource reference.
        poll_interval: Seconds between status checks. Defaults to 2.0.
        timeout: Maximum seconds to wait. Defaults to 300.0 (5 minutes).

    Returns:
        The final status with completion data.

    Raises:
        APITimeoutError: If the operation doesn't complete within timeout.
        ValueError: If the status object doesn't have a resource reference.
    """
    from .types.convert import ConversionStatus
    from .types.identify import IdentificationStatus
    from .types.step import StepExecutionStatus

    resource = getattr(status, "_resource", None)
    if resource is None:
        raise ValueError(
            "Status object doesn't have a resource reference. "
            "Use get_status() to create a pollable status."
        )

    start_time = time.monotonic()
    current_status = status

    # Check completion first, then sleep if needed (avoids latency for fast ops)
    while True:
        if current_status.is_complete():
            return current_status

        elapsed = time.monotonic() - start_time
        if elapsed >= timeout:
            if isinstance(current_status, ConversionStatus):
                raise APITimeoutError(
                    f"Conversion {current_status.conversion_id} did not complete "
                    f"within {timeout} seconds"
                )
            elif isinstance(current_status, IdentificationStatus):
                raise APITimeoutError(
                    f"Identification {current_status.identification_id} did not complete "
                    f"within {timeout} seconds"
                )
            elif isinstance(current_status, StepExecutionStatus):
                raise APITimeoutError(
                    f"Step execution {current_status.execution_id} did not complete "
                    f"within {timeout} seconds"
                )
            else:
                raise APITimeoutError(
                    f"Operation did not complete within {timeout} seconds"
                )

        # Sleep before polling for new status
        await asyncio.sleep(poll_interval)

        # Get fresh status
        if isinstance(current_status, ConversionStatus):
            current_status = await resource.get_status(current_status.conversion_id)
        elif isinstance(current_status, IdentificationStatus):
            current_status = await resource.get_status(current_status.identification_id)
        elif isinstance(current_status, StepExecutionStatus):
            current_status = await resource.get_status(current_status.execution_id)
