"""Tests for polling utilities."""

from __future__ import annotations

from unittest.mock import MagicMock

from docutray._polling import wait_for_completion
from docutray.types.convert import ConversionStatus


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
