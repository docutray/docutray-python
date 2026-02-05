"""Tests for the Convert resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from docutray import Client, ConversionResult, ConversionStatus


class TestConvertRun:
    """Tests for Convert.run() synchronous conversion."""

    def test_convert_with_url(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Convert document from URL."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "invoice_number": "INV-001",
                        "total": 1500.00,
                    }
                },
            )
        )

        result = client.convert.run(
            url="https://example.com/invoice.pdf",
            document_type_code="invoice",
        )

        assert isinstance(result, ConversionResult)
        assert result.data["invoice_number"] == "INV-001"
        assert result.data["total"] == 1500.00

    def test_convert_with_bytes(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Convert document from bytes."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"field": "value"}},
            )
        )

        result = client.convert.run(
            file=b"fake pdf content",
            document_type_code="generic",
            content_type="application/pdf",
        )

        assert isinstance(result, ConversionResult)
        assert result.data["field"] == "value"

    def test_convert_with_metadata(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Convert document with metadata."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"processed": True}},
            )
        )

        result = client.convert.run(
            url="https://example.com/doc.pdf",
            document_type_code="invoice",
            document_metadata={"customer_id": "cust_123"},
        )

        assert result.data["processed"] is True

    def test_convert_requires_input(self, client: Client) -> None:
        """Convert raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.convert.run(document_type_code="invoice")


class TestConvertRunAsync:
    """Tests for Convert.run_async() asynchronous conversion."""

    def test_run_async_returns_status(self, client: Client, mock_api: respx.MockRouter) -> None:
        """run_async returns ConversionStatus with conversion_id."""
        mock_api.post("/api/convert-async").mock(
            return_value=httpx.Response(
                202,
                json={
                    "conversion_id": "conv_abc123",
                    "status": "ENQUEUED",
                    "status_url": "https://api.docutray.com/api/convert-async/status/conv_abc123",
                },
            )
        )

        status = client.convert.run_async(
            url="https://example.com/large.pdf",
            document_type_code="invoice",
        )

        assert isinstance(status, ConversionStatus)
        assert status.conversion_id == "conv_abc123"
        assert status.status == "ENQUEUED"
        assert not status.is_complete()


class TestConvertGetStatus:
    """Tests for Convert.get_status() polling."""

    def test_get_status_processing(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get status returns PROCESSING state."""
        mock_api.get("/api/convert-async/status/conv_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "conversion_id": "conv_123",
                    "status": "PROCESSING",
                    "request_timestamp": "2024-01-15T10:30:00.000Z",
                },
            )
        )

        status = client.convert.get_status("conv_123")

        assert status.status == "PROCESSING"
        assert not status.is_complete()
        assert not status.is_success()

    def test_get_status_success(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get status returns SUCCESS state with data."""
        mock_api.get("/api/convert-async/status/conv_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "conversion_id": "conv_123",
                    "status": "SUCCESS",
                    "request_timestamp": "2024-01-15T10:30:00.000Z",
                    "response_timestamp": "2024-01-15T10:30:05.000Z",
                    "data": {"invoice_number": "INV-001"},
                },
            )
        )

        status = client.convert.get_status("conv_123")

        assert status.status == "SUCCESS"
        assert status.is_complete()
        assert status.is_success()
        assert status.data == {"invoice_number": "INV-001"}

    def test_get_status_error(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get status returns ERROR state with message."""
        mock_api.get("/api/convert-async/status/conv_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "conversion_id": "conv_123",
                    "status": "ERROR",
                    "error": "Processing timeout after 60 minutes",
                },
            )
        )

        status = client.convert.get_status("conv_123")

        assert status.status == "ERROR"
        assert status.is_complete()
        assert status.is_error()
        assert "timeout" in status.error.lower()


class TestConversionStatusHelpers:
    """Tests for ConversionStatus helper methods."""

    def test_is_complete_for_enqueued(self) -> None:
        """is_complete returns False for ENQUEUED."""
        status = ConversionStatus(conversion_id="test", status="ENQUEUED")
        assert not status.is_complete()

    def test_is_complete_for_processing(self) -> None:
        """is_complete returns False for PROCESSING."""
        status = ConversionStatus(conversion_id="test", status="PROCESSING")
        assert not status.is_complete()

    def test_is_complete_for_success(self) -> None:
        """is_complete returns True for SUCCESS."""
        status = ConversionStatus(conversion_id="test", status="SUCCESS")
        assert status.is_complete()

    def test_is_complete_for_error(self) -> None:
        """is_complete returns True for ERROR."""
        status = ConversionStatus(conversion_id="test", status="ERROR")
        assert status.is_complete()
