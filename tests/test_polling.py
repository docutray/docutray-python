"""Tests for polling utilities."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from docutray._exceptions import APITimeoutError
from docutray._polling import wait_for_completion, wait_for_completion_async
from docutray.types.convert import ConversionStatus
from docutray.types.identify import IdentificationStatus
from docutray.types.step import StepExecutionStatus


class TestOnStatusCallback:
    """Tests for on_status callback in polling."""

    def test_callback_not_invoked_on_initial_status(self) -> None:
        """Callback should not be invoked with initial status."""
        # Create a status that is already complete
        status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
            data={"field": "value"},
        )
        # Mock the resource
        mock_resource = MagicMock()
        status._resource = mock_resource

        # Track callback invocations
        callback = MagicMock()

        # Call wait - should return immediately since already complete
        result = wait_for_completion(status, on_status=callback)

        # Callback should NOT have been called (not on initial status per spec)
        callback.assert_not_called()
        assert result.status == "SUCCESS"

    def test_callback_invoked_after_each_poll(self) -> None:
        """Callback should be invoked after each poll."""
        # Create initial status that is processing
        initial_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )

        # Create sequence of statuses
        processing_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        success_status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
            data={"field": "value"},
        )

        # Mock the resource to return statuses in sequence
        mock_resource = MagicMock()
        mock_resource.get_status = MagicMock(
            side_effect=[processing_status, success_status]
        )
        initial_status._resource = mock_resource

        # Track callback invocations
        callback_statuses: list[str] = []

        def track_status(s: ConversionStatus) -> None:
            callback_statuses.append(s.status)

        # Call wait with very short poll interval
        result = wait_for_completion(
            initial_status,
            poll_interval=0.01,
            on_status=track_status,
        )

        # Callback should have been called twice (once per poll after initial)
        assert callback_statuses == ["PROCESSING", "SUCCESS"]
        assert result.status == "SUCCESS"

    def test_callback_not_required(self) -> None:
        """Polling works without callback."""
        status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
            data={"field": "value"},
        )
        mock_resource = MagicMock()
        status._resource = mock_resource

        # Call wait without callback
        result = wait_for_completion(status)

        assert result.status == "SUCCESS"


class TestPollingTimeout:
    """Tests for polling timeout behavior."""

    def test_timeout_raises_api_timeout_error(self) -> None:
        """Polling raises APITimeoutError when timeout is reached."""
        status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        mock_resource = MagicMock()
        mock_resource.get_status = MagicMock(
            return_value=ConversionStatus(
                conversion_id="conv_123",
                status="PROCESSING",
            )
        )
        status._resource = mock_resource

        with pytest.raises(APITimeoutError) as exc_info:
            wait_for_completion(status, poll_interval=0.01, timeout=0.05)

        assert "conv_123" in str(exc_info.value)
        assert "did not complete" in str(exc_info.value)

    def test_timeout_with_identification_status(self) -> None:
        """Polling timeout includes identification_id in error."""
        status = IdentificationStatus(
            identification_id="id_abc",
            status="PROCESSING",
        )
        mock_resource = MagicMock()
        mock_resource.get_status = MagicMock(
            return_value=IdentificationStatus(
                identification_id="id_abc",
                status="PROCESSING",
            )
        )
        status._resource = mock_resource

        with pytest.raises(APITimeoutError) as exc_info:
            wait_for_completion(status, poll_interval=0.01, timeout=0.05)

        assert "id_abc" in str(exc_info.value)

    def test_timeout_with_step_execution_status(self) -> None:
        """Polling timeout includes execution_id in error."""
        status = StepExecutionStatus(
            execution_id="exec_xyz",
            status="PROCESSING",
        )
        mock_resource = MagicMock()
        mock_resource.get_status = MagicMock(
            return_value=StepExecutionStatus(
                execution_id="exec_xyz",
                status="PROCESSING",
            )
        )
        status._resource = mock_resource

        with pytest.raises(APITimeoutError) as exc_info:
            wait_for_completion(status, poll_interval=0.01, timeout=0.05)

        assert "exec_xyz" in str(exc_info.value)


class TestPollingNoResource:
    """Tests for polling without resource reference."""

    def test_raises_value_error_without_resource(self) -> None:
        """Polling raises ValueError when status has no resource."""
        status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        # No _resource set

        with pytest.raises(ValueError, match="doesn't have a resource reference"):
            wait_for_completion(status)


class TestAsyncPolling:
    """Tests for async polling with wait_for_completion_async."""

    async def test_async_wait_success_path(self) -> None:
        """Async polling returns when status is complete."""
        initial_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        success_status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
            data={"field": "value"},
        )

        mock_resource = AsyncMock()
        mock_resource.get_status = AsyncMock(return_value=success_status)
        initial_status._resource = mock_resource

        result = await wait_for_completion_async(initial_status, poll_interval=0.01)

        assert result.status == "SUCCESS"
        assert result.data == {"field": "value"}
        mock_resource.get_status.assert_called_once_with("conv_123")

    async def test_async_wait_multiple_polls(self) -> None:
        """Async polling polls multiple times until complete."""
        initial_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        processing_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        success_status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
            data={"result": "done"},
        )

        mock_resource = AsyncMock()
        mock_resource.get_status = AsyncMock(
            side_effect=[processing_status, processing_status, success_status]
        )
        initial_status._resource = mock_resource

        result = await wait_for_completion_async(initial_status, poll_interval=0.01)

        assert result.status == "SUCCESS"
        assert mock_resource.get_status.call_count == 3

    async def test_async_wait_timeout(self) -> None:
        """Async polling raises APITimeoutError on timeout."""
        status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        mock_resource = AsyncMock()
        mock_resource.get_status = AsyncMock(
            return_value=ConversionStatus(
                conversion_id="conv_123",
                status="PROCESSING",
            )
        )
        status._resource = mock_resource

        with pytest.raises(APITimeoutError) as exc_info:
            await wait_for_completion_async(status, poll_interval=0.01, timeout=0.05)

        assert "conv_123" in str(exc_info.value)

    async def test_async_on_status_sync_callback(self) -> None:
        """Async polling works with sync on_status callback."""
        initial_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        success_status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
        )

        mock_resource = AsyncMock()
        mock_resource.get_status = AsyncMock(return_value=success_status)
        initial_status._resource = mock_resource

        callback_statuses: list[str] = []

        def track_status(s: ConversionStatus) -> None:
            callback_statuses.append(s.status)

        result = await wait_for_completion_async(
            initial_status,
            poll_interval=0.01,
            on_status=track_status,
        )

        assert result.status == "SUCCESS"
        assert callback_statuses == ["SUCCESS"]

    async def test_async_on_status_async_callback(self) -> None:
        """Async polling works with async on_status callback."""
        initial_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        processing_status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        success_status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
        )

        mock_resource = AsyncMock()
        mock_resource.get_status = AsyncMock(
            side_effect=[processing_status, success_status]
        )
        initial_status._resource = mock_resource

        callback_statuses: list[str] = []

        async def track_status(s: ConversionStatus) -> None:
            callback_statuses.append(s.status)

        result = await wait_for_completion_async(
            initial_status,
            poll_interval=0.01,
            on_status=track_status,
        )

        assert result.status == "SUCCESS"
        assert callback_statuses == ["PROCESSING", "SUCCESS"]

    async def test_async_callback_not_invoked_on_initial_complete(self) -> None:
        """Async callback not invoked when status is already complete."""
        status = ConversionStatus(
            conversion_id="conv_123",
            status="SUCCESS",
            data={"field": "value"},
        )
        mock_resource = AsyncMock()
        status._resource = mock_resource

        callback = MagicMock()

        result = await wait_for_completion_async(status, on_status=callback)

        callback.assert_not_called()
        assert result.status == "SUCCESS"

    async def test_async_no_resource_raises_error(self) -> None:
        """Async polling raises ValueError without resource."""
        status = ConversionStatus(
            conversion_id="conv_123",
            status="PROCESSING",
        )
        # No _resource set

        with pytest.raises(ValueError, match="doesn't have a resource reference"):
            await wait_for_completion_async(status)

    async def test_async_wait_identification_status(self) -> None:
        """Async polling works with IdentificationStatus."""
        initial_status = IdentificationStatus(
            identification_id="id_abc",
            status="PROCESSING",
        )
        success_status = IdentificationStatus(
            identification_id="id_abc",
            status="SUCCESS",
            document_type={"code": "invoice", "name": "Invoice", "confidence": 0.95},
        )

        mock_resource = AsyncMock()
        mock_resource.get_status = AsyncMock(return_value=success_status)
        initial_status._resource = mock_resource

        result = await wait_for_completion_async(initial_status, poll_interval=0.01)

        assert result.status == "SUCCESS"
        mock_resource.get_status.assert_called_once_with("id_abc")

    async def test_async_wait_step_execution_status(self) -> None:
        """Async polling works with StepExecutionStatus."""
        initial_status = StepExecutionStatus(
            execution_id="exec_xyz",
            status="ENQUEUED",
        )
        success_status = StepExecutionStatus(
            execution_id="exec_xyz",
            status="SUCCESS",
            data={"output": "result"},
        )

        mock_resource = AsyncMock()
        mock_resource.get_status = AsyncMock(return_value=success_status)
        initial_status._resource = mock_resource

        result = await wait_for_completion_async(initial_status, poll_interval=0.01)

        assert result.status == "SUCCESS"
        mock_resource.get_status.assert_called_once_with("exec_xyz")
