"""Tests for the Steps resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from docutray import Client, StepExecutionStatus


class TestStepsRunAsync:
    """Tests for Steps.run_async()."""

    def test_run_async_with_url(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Execute step with URL input."""
        mock_api.post("/api/steps-async/step_123").mock(
            return_value=httpx.Response(
                202,
                json={
                    "execution_id": "exec_xyz789",
                    "status": "ENQUEUED",
                    "step_id": "step_123",
                },
            )
        )

        status = client.steps.run_async(
            "step_123",
            url="https://example.com/document.pdf",
        )

        assert isinstance(status, StepExecutionStatus)
        assert status.execution_id == "exec_xyz789"
        assert status.status == "ENQUEUED"
        assert not status.is_complete()

    def test_run_async_with_bytes(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Execute step with bytes input."""
        mock_api.post("/api/steps-async/step_456").mock(
            return_value=httpx.Response(
                202,
                json={
                    "execution_id": "exec_abc123",
                    "status": "ENQUEUED",
                    "step_id": "step_456",
                },
            )
        )

        status = client.steps.run_async(
            "step_456",
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert status.execution_id == "exec_abc123"
        assert status.status == "ENQUEUED"

    def test_run_async_with_metadata(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Execute step with document metadata."""
        mock_api.post("/api/steps-async/step_789").mock(
            return_value=httpx.Response(
                202,
                json={
                    "execution_id": "exec_meta",
                    "status": "ENQUEUED",
                },
            )
        )

        status = client.steps.run_async(
            "step_789",
            url="https://example.com/doc.pdf",
            document_metadata={"customer_id": "cust_123"},
        )

        assert status.execution_id == "exec_meta"

    def test_run_async_requires_input(self, client: Client) -> None:
        """Execute step raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.steps.run_async("step_123")


class TestStepsGetStatus:
    """Tests for Steps.get_status()."""

    def test_get_status_processing(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get status returns PROCESSING state."""
        mock_api.get("/api/steps-async/status/exec_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "execution_id": "exec_123",
                    "status": "PROCESSING",
                    "step_id": "step_invoice",
                    "request_timestamp": "2024-01-15T10:30:00.000Z",
                },
            )
        )

        status = client.steps.get_status("exec_123")

        assert status.status == "PROCESSING"
        assert not status.is_complete()
        assert not status.is_success()

    def test_get_status_success(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get status returns SUCCESS state with data."""
        mock_api.get("/api/steps-async/status/exec_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "execution_id": "exec_123",
                    "status": "SUCCESS",
                    "step_id": "step_invoice",
                    "request_timestamp": "2024-01-15T10:30:00.000Z",
                    "response_timestamp": "2024-01-15T10:30:05.000Z",
                    "data": {"invoice_number": "INV-001", "total": 1500.00},
                },
            )
        )

        status = client.steps.get_status("exec_123")

        assert status.status == "SUCCESS"
        assert status.is_complete()
        assert status.is_success()
        assert status.data == {"invoice_number": "INV-001", "total": 1500.00}

    def test_get_status_error(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get status returns ERROR state with message."""
        mock_api.get("/api/steps-async/status/exec_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "execution_id": "exec_123",
                    "status": "ERROR",
                    "error": "Step execution failed: invalid document format",
                },
            )
        )

        status = client.steps.get_status("exec_123")

        assert status.status == "ERROR"
        assert status.is_complete()
        assert status.is_error()
        assert "invalid document format" in status.error


class TestStepExecutionStatusHelpers:
    """Tests for StepExecutionStatus helper methods."""

    def test_is_complete_for_enqueued(self) -> None:
        """is_complete returns False for ENQUEUED."""
        status = StepExecutionStatus(execution_id="test", status="ENQUEUED")
        assert not status.is_complete()

    def test_is_complete_for_processing(self) -> None:
        """is_complete returns False for PROCESSING."""
        status = StepExecutionStatus(execution_id="test", status="PROCESSING")
        assert not status.is_complete()

    def test_is_complete_for_success(self) -> None:
        """is_complete returns True for SUCCESS."""
        status = StepExecutionStatus(execution_id="test", status="SUCCESS")
        assert status.is_complete()
        assert status.is_success()
        assert not status.is_error()

    def test_is_complete_for_error(self) -> None:
        """is_complete returns True for ERROR."""
        status = StepExecutionStatus(execution_id="test", status="ERROR")
        assert status.is_complete()
        assert not status.is_success()
        assert status.is_error()
