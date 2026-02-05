"""Tests for the Identify resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from docutray import (
    AsyncClient,
    Client,
    DocumentTypeMatch,
    IdentificationResult,
    IdentificationStatus,
)


class TestIdentifyRun:
    """Tests for Identify.run() synchronous identification."""

    def test_identify_with_url(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Identify document from URL."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "invoice",
                        "name": "Invoice",
                        "confidence": 0.95,
                    },
                    "alternatives": [
                        {"code": "receipt", "name": "Receipt", "confidence": 0.30},
                    ],
                },
            )
        )

        result = client.identify.run(url="https://example.com/document.pdf")

        assert isinstance(result, IdentificationResult)
        assert result.document_type.code == "invoice"
        assert result.document_type.confidence == 0.95
        assert len(result.alternatives) == 1
        assert result.alternatives[0].code == "receipt"

    def test_identify_with_bytes(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Identify document from bytes."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "contract",
                        "name": "Contract",
                        "confidence": 0.88,
                    },
                    "alternatives": [],
                },
            )
        )

        result = client.identify.run(
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert result.document_type.code == "contract"
        assert result.alternatives == []

    def test_identify_requires_input(self, client: Client) -> None:
        """Identify raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.identify.run()

    def test_identify_with_document_type_code_options_url(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """Identify with document_type_code_options via URL."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "cartola_cc",
                        "name": "Cartola Cuenta Corriente",
                        "confidence": 0.95,
                    },
                    "alternatives": [],
                },
            )
        )

        result = client.identify.run(
            url="https://example.com/statement.pdf",
            document_type_code_options=["cartola_cc", "cartola_tc"],
        )

        assert result.document_type.code == "cartola_cc"
        # Verify the request body contains document_type_code_options
        request = mock_api.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["document_type_code_options"] == ["cartola_cc", "cartola_tc"]

    def test_identify_with_document_type_code_options_file(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """Identify with document_type_code_options via file (multipart)."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "invoice",
                        "name": "Invoice",
                        "confidence": 0.88,
                    },
                    "alternatives": [],
                },
            )
        )

        result = client.identify.run(
            file=b"fake pdf content",
            content_type="application/pdf",
            document_type_code_options=["invoice", "receipt"],
        )

        assert result.document_type.code == "invoice"
        # Verify the multipart request contains document_type_code_options as JSON
        request = mock_api.calls.last.request
        content = request.content.decode("utf-8")
        assert "document_type_code_options" in content
        # The value should be JSON encoded in multipart
        assert '["invoice", "receipt"]' in content or '["invoice","receipt"]' in content

    def test_identify_with_document_type_code_options_base64(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """Identify with document_type_code_options via base64."""
        import base64

        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "contract",
                        "name": "Contract",
                        "confidence": 0.92,
                    },
                    "alternatives": [],
                },
            )
        )

        result = client.identify.run(
            file_base64=base64.b64encode(b"fake content").decode(),
            content_type="application/pdf",
            document_type_code_options=["contract"],
        )

        assert result.document_type.code == "contract"
        request = mock_api.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["document_type_code_options"] == ["contract"]


class TestIdentifyRunAsync:
    """Tests for Identify.run_async() asynchronous identification."""

    def test_run_async_returns_status(self, client: Client, mock_api: respx.MockRouter) -> None:
        """run_async returns IdentificationStatus with identification_id."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={
                    "identification_id": "id_xyz789",
                    "status": "ENQUEUED",
                },
            )
        )

        status = client.identify.run_async(url="https://example.com/doc.pdf")

        assert isinstance(status, IdentificationStatus)
        assert status.identification_id == "id_xyz789"
        assert status.status == "ENQUEUED"

    def test_run_async_accepts_id_alias(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """run_async accepts 'id' field as alias for identification_id."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={
                    "id": "id_from_api",  # API returns 'id' instead of 'identification_id'
                    "status": "ENQUEUED",
                },
            )
        )

        status = client.identify.run_async(url="https://example.com/doc.pdf")

        assert status.identification_id == "id_from_api"

    def test_run_async_with_document_type_code_options(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """run_async with document_type_code_options."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={
                    "id": "id_abc123",
                    "status": "ENQUEUED",
                },
            )
        )

        status = client.identify.run_async(
            url="https://example.com/doc.pdf",
            document_type_code_options=["invoice", "receipt"],
        )

        assert status.identification_id == "id_abc123"
        request = mock_api.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["document_type_code_options"] == ["invoice", "receipt"]


class TestIdentifyGetStatus:
    """Tests for Identify.get_status() polling."""

    def test_get_status_success(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get status returns SUCCESS state with results."""
        mock_api.get("/api/identify-async/status/id_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "identification_id": "id_123",
                    "status": "SUCCESS",
                    "document_type": {
                        "code": "invoice",
                        "name": "Invoice",
                        "confidence": 0.92,
                    },
                    "alternatives": [],
                },
            )
        )

        status = client.identify.get_status("id_123")

        assert status.is_success()
        assert status.document_type is not None
        assert status.document_type.code == "invoice"


class TestDocumentTypeMatch:
    """Tests for DocumentTypeMatch model."""

    def test_document_type_match_fields(self) -> None:
        """DocumentTypeMatch has expected fields."""
        match = DocumentTypeMatch(code="invoice", name="Invoice", confidence=0.95)
        assert match.code == "invoice"
        assert match.name == "Invoice"
        assert match.confidence == 0.95


class TestIdentificationStatusHelpers:
    """Tests for IdentificationStatus helper methods."""

    def test_is_complete_for_success(self) -> None:
        """is_complete returns True for SUCCESS."""
        status = IdentificationStatus(identification_id="test", status="SUCCESS")
        assert status.is_complete()
        assert status.is_success()
        assert not status.is_error()

    def test_is_complete_for_error(self) -> None:
        """is_complete returns True for ERROR."""
        status = IdentificationStatus(identification_id="test", status="ERROR")
        assert status.is_complete()
        assert not status.is_success()
        assert status.is_error()


class TestAsyncIdentifyRun:
    """Tests for AsyncIdentify.run() asynchronous identification."""

    async def test_async_identify_with_url(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async identify document from URL."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "invoice",
                        "name": "Invoice",
                        "confidence": 0.95,
                    },
                    "alternatives": [
                        {"code": "receipt", "name": "Receipt", "confidence": 0.30},
                    ],
                },
            )
        )

        result = await async_client.identify.run(url="https://example.com/document.pdf")

        assert isinstance(result, IdentificationResult)
        assert result.document_type.code == "invoice"
        assert result.document_type.confidence == 0.95
        assert len(result.alternatives) == 1

    async def test_async_identify_with_bytes(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async identify document from bytes."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "contract",
                        "name": "Contract",
                        "confidence": 0.88,
                    },
                    "alternatives": [],
                },
            )
        )

        result = await async_client.identify.run(
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert result.document_type.code == "contract"
        assert result.alternatives == []

    async def test_async_identify_requires_input(
        self, async_client: AsyncClient
    ) -> None:
        """Async identify raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            await async_client.identify.run()

    async def test_async_identify_with_document_type_code_options_url(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async identify with document_type_code_options via URL."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "cartola_cc",
                        "name": "Cartola Cuenta Corriente",
                        "confidence": 0.95,
                    },
                    "alternatives": [],
                },
            )
        )

        result = await async_client.identify.run(
            url="https://example.com/statement.pdf",
            document_type_code_options=["cartola_cc", "cartola_tc"],
        )

        assert result.document_type.code == "cartola_cc"
        request = mock_api.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["document_type_code_options"] == ["cartola_cc", "cartola_tc"]

    async def test_async_identify_with_document_type_code_options_file(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async identify with document_type_code_options via file (multipart)."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {
                        "code": "invoice",
                        "name": "Invoice",
                        "confidence": 0.88,
                    },
                    "alternatives": [],
                },
            )
        )

        result = await async_client.identify.run(
            file=b"fake pdf content",
            content_type="application/pdf",
            document_type_code_options=["invoice", "receipt"],
        )

        assert result.document_type.code == "invoice"
        request = mock_api.calls.last.request
        content = request.content.decode("utf-8")
        assert "document_type_code_options" in content


class TestAsyncIdentifyRunAsync:
    """Tests for AsyncIdentify.run_async() method."""

    async def test_async_run_async_returns_status(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """run_async returns IdentificationStatus with identification_id."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={
                    "identification_id": "id_xyz789",
                    "status": "ENQUEUED",
                },
            )
        )

        status = await async_client.identify.run_async(
            url="https://example.com/doc.pdf"
        )

        assert isinstance(status, IdentificationStatus)
        assert status.identification_id == "id_xyz789"
        assert status.status == "ENQUEUED"


class TestAsyncIdentifyGetStatus:
    """Tests for AsyncIdentify.get_status() polling."""

    async def test_async_get_status_success(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async get status returns SUCCESS state with results."""
        mock_api.get("/api/identify-async/status/id_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "identification_id": "id_123",
                    "status": "SUCCESS",
                    "document_type": {
                        "code": "invoice",
                        "name": "Invoice",
                        "confidence": 0.92,
                    },
                    "alternatives": [],
                },
            )
        )

        status = await async_client.identify.get_status("id_123")

        assert status.is_success()
        assert status.document_type is not None
        assert status.document_type.code == "invoice"

    async def test_async_get_status_processing(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async get status returns PROCESSING state."""
        mock_api.get("/api/identify-async/status/id_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "identification_id": "id_456",
                    "status": "PROCESSING",
                },
            )
        )

        status = await async_client.identify.get_status("id_456")

        assert not status.is_complete()
        assert status.status == "PROCESSING"

    async def test_async_get_status_error(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async get status returns ERROR state."""
        mock_api.get("/api/identify-async/status/id_789").mock(
            return_value=httpx.Response(
                200,
                json={
                    "identification_id": "id_789",
                    "status": "ERROR",
                    "error": "Failed to process document",
                },
            )
        )

        status = await async_client.identify.get_status("id_789")

        assert status.is_error()
        assert status.error == "Failed to process document"
