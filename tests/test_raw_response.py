"""Tests for WithRawResponse wrappers."""

from __future__ import annotations

import httpx
import pytest
import respx

from docutray import AsyncClient, Client, ConversionResult, ConversionStatus


class TestConvertWithRawResponse:
    """Tests for Convert.with_raw_response."""

    def test_run_returns_status_code(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run returns status_code."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"invoice_number": "INV-001"}},
                headers={"x-request-id": "req_123"},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 200

    def test_run_with_file_bytes(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run works with file bytes."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"invoice_number": "INV-002"}},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert response.status_code == 200
        result = response.parse()
        assert result.data == {"invoice_number": "INV-002"}

    def test_run_with_file_base64(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run works with base64 file."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"invoice_number": "INV-003"}},
            )
        )

        import base64

        file_base64 = base64.b64encode(b"fake pdf content").decode()
        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            file_base64=file_base64,
            content_type="application/pdf",
        )

        assert response.status_code == 200

    def test_run_with_metadata(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run works with document_metadata."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {}},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
            document_metadata={"customer_id": "cust_123"},
        )

        assert response.status_code == 200

    def test_run_requires_input(self, client: Client) -> None:
        """with_raw_response.run raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.convert.with_raw_response.run(document_type_code="invoice")

    def test_run_async_with_file_bytes(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async works with file bytes."""
        mock_api.post("/api/convert-async").mock(
            return_value=httpx.Response(
                202,
                json={"conversion_id": "conv_123", "status": "ENQUEUED"},
            )
        )

        response = client.convert.with_raw_response.run_async(
            document_type_code="invoice",
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert response.status_code == 202

    def test_run_async_with_file_base64(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async works with base64 file."""
        mock_api.post("/api/convert-async").mock(
            return_value=httpx.Response(
                202,
                json={"conversion_id": "conv_123", "status": "ENQUEUED"},
            )
        )

        import base64

        file_base64 = base64.b64encode(b"fake pdf content").decode()
        response = client.convert.with_raw_response.run_async(
            document_type_code="invoice",
            file_base64=file_base64,
            content_type="application/pdf",
        )

        assert response.status_code == 202

    def test_run_async_requires_input(self, client: Client) -> None:
        """with_raw_response.run_async raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.convert.with_raw_response.run_async(document_type_code="invoice")

    def test_run_returns_headers(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run returns headers."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"invoice_number": "INV-001"}},
                headers={"x-request-id": "req_abc123", "content-type": "application/json"},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert response.headers["x-request-id"] == "req_abc123"
        assert "application/json" in response.headers["content-type"]

    def test_run_parse_returns_model(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run.parse() returns typed model."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"invoice_number": "INV-001", "total": 500.00}},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        result = response.parse()
        assert isinstance(result, ConversionResult)
        assert result.data == {"invoice_number": "INV-001", "total": 500.00}

    def test_run_async_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async returns raw HTTP response."""
        mock_api.post("/api/convert-async").mock(
            return_value=httpx.Response(
                202,
                json={"conversion_id": "conv_123", "status": "ENQUEUED"},
                headers={"x-request-id": "req_456"},
            )
        )

        response = client.convert.with_raw_response.run_async(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 202
        assert response.headers["x-request-id"] == "req_456"
        result = response.parse()
        assert isinstance(result, ConversionStatus)
        assert result.conversion_id == "conv_123"

    def test_get_status_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.get_status returns raw HTTP response."""
        mock_api.get("/api/convert-async/status/conv_123").mock(
            return_value=httpx.Response(
                200,
                json={"conversion_id": "conv_123", "status": "SUCCESS", "data": {}},
                headers={"x-request-id": "req_789"},
            )
        )

        response = client.convert.with_raw_response.get_status("conv_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.status == "SUCCESS"

    def test_content_property(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response provides content property."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {}},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert isinstance(response.content, bytes)
        assert b"data" in response.content

    def test_text_property(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response provides text property."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {}},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert isinstance(response.text, str)
        assert "data" in response.text

    def test_json_method(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response provides json() method."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"field": "value"}},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        json_data = response.json()
        assert json_data == {"data": {"field": "value"}}

    def test_http_response_property(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response provides http_response property."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {}},
            )
        )

        response = client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert isinstance(response.http_response, httpx.Response)


class TestIdentifyWithRawResponse:
    """Tests for Identify.with_raw_response."""

    def test_run_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run returns raw HTTP response."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {"code": "invoice", "name": "Invoice", "confidence": 0.95},
                    "alternatives": [],
                },
                headers={"x-request-id": "req_identify"},
            )
        )

        response = client.identify.with_raw_response.run(
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 200
        assert response.headers["x-request-id"] == "req_identify"
        result = response.parse()
        assert result.document_type.code == "invoice"

    def test_run_with_file_bytes(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run works with file bytes."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {"code": "contract", "name": "Contract", "confidence": 0.9},
                    "alternatives": [],
                },
            )
        )

        response = client.identify.with_raw_response.run(
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert response.status_code == 200

    def test_run_with_file_base64(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run works with base64 file."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {"code": "receipt", "name": "Receipt", "confidence": 0.85},
                    "alternatives": [],
                },
            )
        )

        import base64

        file_base64 = base64.b64encode(b"fake pdf content").decode()
        response = client.identify.with_raw_response.run(
            file_base64=file_base64,
            content_type="application/pdf",
        )

        assert response.status_code == 200

    def test_run_requires_input(self, client: Client) -> None:
        """with_raw_response.run raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.identify.with_raw_response.run()

    def test_run_async_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async returns raw HTTP response."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={"identification_id": "id_123", "status": "ENQUEUED"},
                headers={"x-request-id": "req_456"},
            )
        )

        response = client.identify.with_raw_response.run_async(
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 202
        result = response.parse()
        assert result.identification_id == "id_123"

    def test_run_async_with_file_bytes(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async works with file bytes."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={"identification_id": "id_456", "status": "ENQUEUED"},
            )
        )

        response = client.identify.with_raw_response.run_async(
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert response.status_code == 202

    def test_run_async_with_file_base64(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async works with base64 file."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={"identification_id": "id_789", "status": "ENQUEUED"},
            )
        )

        import base64

        file_base64 = base64.b64encode(b"fake pdf content").decode()
        response = client.identify.with_raw_response.run_async(
            file_base64=file_base64,
            content_type="application/pdf",
        )

        assert response.status_code == 202

    def test_run_async_requires_input(self, client: Client) -> None:
        """with_raw_response.run_async raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.identify.with_raw_response.run_async()

    def test_get_status_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.get_status returns raw HTTP response."""
        mock_api.get("/api/identify-async/status/id_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "identification_id": "id_123",
                    "status": "SUCCESS",
                    "document_type": {"code": "receipt", "name": "Receipt", "confidence": 0.88},
                    "alternatives": [],
                },
            )
        )

        response = client.identify.with_raw_response.get_status("id_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.is_success()


class TestDocumentTypesWithRawResponse:
    """Tests for DocumentTypes.with_raw_response."""

    def test_list_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.list returns raw HTTP response."""
        mock_api.get("/api/document-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "dt_1", "name": "Invoice", "codeType": "invoice"}],
                    "pagination": {"total": 1, "page": 1, "limit": 10},
                },
                headers={"x-request-id": "req_list"},
            )
        )

        response = client.document_types.with_raw_response.list()

        assert response.status_code == 200
        assert response.headers["x-request-id"] == "req_list"
        page = response.parse()
        assert len(page.data) == 1
        assert page.data[0].codeType == "invoice"

    def test_get_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.get returns raw HTTP response."""
        mock_api.get("/api/document-types/dt_123").mock(
            return_value=httpx.Response(
                200,
                json={"id": "dt_123", "name": "Invoice", "codeType": "invoice"},
            )
        )

        response = client.document_types.with_raw_response.get("dt_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.id == "dt_123"

    def test_validate_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.validate returns raw HTTP response."""
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        response = client.document_types.with_raw_response.validate(
            "dt_123", {"invoice_number": "INV-001"}
        )

        assert response.status_code == 200
        result = response.parse()
        assert result.is_valid()


class TestStepsWithRawResponse:
    """Tests for Steps.with_raw_response."""

    def test_run_async_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async returns raw HTTP response."""
        mock_api.post("/api/steps-async/step_123").mock(
            return_value=httpx.Response(
                202,
                json={"execution_id": "exec_123", "status": "ENQUEUED"},
                headers={"x-request-id": "req_step"},
            )
        )

        response = client.steps.with_raw_response.run_async(
            step_id="step_123",
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 202
        assert response.headers["x-request-id"] == "req_step"
        result = response.parse()
        assert result.execution_id == "exec_123"

    def test_run_async_with_file_bytes(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async works with file bytes."""
        mock_api.post("/api/steps-async/step_456").mock(
            return_value=httpx.Response(
                202,
                json={"execution_id": "exec_456", "status": "ENQUEUED"},
            )
        )

        response = client.steps.with_raw_response.run_async(
            step_id="step_456",
            file=b"fake pdf content",
            content_type="application/pdf",
        )

        assert response.status_code == 202

    def test_run_async_with_file_base64(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.run_async works with base64 file."""
        mock_api.post("/api/steps-async/step_789").mock(
            return_value=httpx.Response(
                202,
                json={"execution_id": "exec_789", "status": "ENQUEUED"},
            )
        )

        import base64

        file_base64 = base64.b64encode(b"fake pdf content").decode()
        response = client.steps.with_raw_response.run_async(
            step_id="step_789",
            file_base64=file_base64,
            content_type="application/pdf",
        )

        assert response.status_code == 202

    def test_run_async_requires_input(self, client: Client) -> None:
        """with_raw_response.run_async raises error when no input provided."""
        with pytest.raises(ValueError, match="Must provide one of"):
            client.steps.with_raw_response.run_async(step_id="step_123")

    def test_get_status_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.get_status returns raw HTTP response."""
        mock_api.get("/api/steps-async/status/exec_123").mock(
            return_value=httpx.Response(
                200,
                json={"execution_id": "exec_123", "status": "SUCCESS", "data": {}},
            )
        )

        response = client.steps.with_raw_response.get_status("exec_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.is_success()


class TestKnowledgeBasesWithRawResponse:
    """Tests for KnowledgeBases.with_raw_response."""

    def test_list_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.list returns raw HTTP response."""
        mock_api.get("/api/knowledge-bases").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "kb_1", "name": "Test KB", "isActive": True}],
                    "pagination": {"total": 1, "page": 1, "limit": 10},
                },
                headers={"x-request-id": "req_kb"},
            )
        )

        response = client.knowledge_bases.with_raw_response.list()

        assert response.status_code == 200
        assert response.headers["x-request-id"] == "req_kb"
        page = response.parse()
        assert len(page.data) == 1

    def test_get_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.get returns raw HTTP response."""
        mock_api.get("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"id": "kb_123", "name": "Test KB"}},
            )
        )

        response = client.knowledge_bases.with_raw_response.get("kb_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.id == "kb_123"

    def test_search_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.search returns raw HTTP response."""
        mock_api.post("/api/knowledge-bases/kb_123/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "document": {
                                "id": "doc_1",
                                "name": "Doc 1",
                                "content": {"text": "Sample content"},
                            },
                            "similarity": 0.95,
                        }
                    ],
                    "query": "test query",
                    "resultsCount": 1,
                },
            )
        )

        response = client.knowledge_bases.with_raw_response.search(
            "kb_123", query="test query"
        )

        assert response.status_code == 200
        result = response.parse()
        assert result.resultsCount == 1

    def test_sync_returns_raw_response(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        """with_raw_response.sync returns raw HTTP response."""
        mock_api.post("/api/knowledge-bases/kb_123/sync").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "status": "COMPLETED",
                        "documentsProcessed": 10,
                        "documentsAdded": 2,
                        "documentsUpdated": 1,
                        "documentsRemoved": 0,
                    }
                },
            )
        )

        response = client.knowledge_bases.with_raw_response.sync("kb_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.status == "COMPLETED"


# ============================================================================
# Async WithRawResponse Tests
# ============================================================================


class TestAsyncConvertWithRawResponse:
    """Tests for AsyncConvert.with_raw_response."""

    async def test_async_run_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.run returns raw HTTP response."""
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"invoice_number": "INV-001"}},
                headers={"x-request-id": "req_async"},
            )
        )

        response = await async_client.convert.with_raw_response.run(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 200
        assert response.headers["x-request-id"] == "req_async"
        result = response.parse()
        assert isinstance(result, ConversionResult)

    async def test_async_run_async_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.run_async returns raw HTTP response."""
        mock_api.post("/api/convert-async").mock(
            return_value=httpx.Response(
                202,
                json={"conversion_id": "conv_123", "status": "ENQUEUED"},
            )
        )

        response = await async_client.convert.with_raw_response.run_async(
            document_type_code="invoice",
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 202
        result = response.parse()
        assert result.conversion_id == "conv_123"

    async def test_async_get_status_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.get_status returns raw HTTP response."""
        mock_api.get("/api/convert-async/status/conv_123").mock(
            return_value=httpx.Response(
                200,
                json={"conversion_id": "conv_123", "status": "SUCCESS", "data": {}},
            )
        )

        response = await async_client.convert.with_raw_response.get_status("conv_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.is_success()


class TestAsyncIdentifyWithRawResponse:
    """Tests for AsyncIdentify.with_raw_response."""

    async def test_async_run_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.run returns raw HTTP response."""
        mock_api.post("/api/identify").mock(
            return_value=httpx.Response(
                200,
                json={
                    "document_type": {"code": "invoice", "name": "Invoice", "confidence": 0.95},
                    "alternatives": [],
                },
            )
        )

        response = await async_client.identify.with_raw_response.run(
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 200
        result = response.parse()
        assert result.document_type.code == "invoice"

    async def test_async_run_async_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.run_async returns raw HTTP response."""
        mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(
                202,
                json={"identification_id": "id_123", "status": "ENQUEUED"},
            )
        )

        response = await async_client.identify.with_raw_response.run_async(
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 202
        result = response.parse()
        assert result.identification_id == "id_123"

    async def test_async_get_status_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.get_status returns raw HTTP response."""
        mock_api.get("/api/identify-async/status/id_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "identification_id": "id_123",
                    "status": "SUCCESS",
                    "document_type": {"code": "invoice", "name": "Invoice", "confidence": 0.9},
                    "alternatives": [],
                },
            )
        )

        response = await async_client.identify.with_raw_response.get_status("id_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.is_success()


class TestAsyncDocumentTypesWithRawResponse:
    """Tests for AsyncDocumentTypes.with_raw_response."""

    async def test_async_list_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.list returns raw HTTP response."""
        mock_api.get("/api/document-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "dt_1", "name": "Invoice", "codeType": "invoice"}],
                    "pagination": {"total": 1, "page": 1, "limit": 10},
                },
            )
        )

        response = await async_client.document_types.with_raw_response.list()

        assert response.status_code == 200
        page = response.parse()
        assert len(page.data) == 1

    async def test_async_get_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.get returns raw HTTP response."""
        mock_api.get("/api/document-types/dt_123").mock(
            return_value=httpx.Response(
                200,
                json={"id": "dt_123", "name": "Invoice", "codeType": "invoice"},
            )
        )

        response = await async_client.document_types.with_raw_response.get("dt_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.id == "dt_123"

    async def test_async_validate_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.validate returns raw HTTP response."""
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        response = await async_client.document_types.with_raw_response.validate(
            "dt_123", {"invoice_number": "INV-001"}
        )

        assert response.status_code == 200
        result = response.parse()
        assert result.is_valid()


class TestAsyncStepsWithRawResponse:
    """Tests for AsyncSteps.with_raw_response."""

    async def test_async_run_async_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.run_async returns raw HTTP response."""
        mock_api.post("/api/steps-async/step_123").mock(
            return_value=httpx.Response(
                202,
                json={"execution_id": "exec_123", "status": "ENQUEUED"},
            )
        )

        response = await async_client.steps.with_raw_response.run_async(
            step_id="step_123",
            url="https://example.com/doc.pdf",
        )

        assert response.status_code == 202
        result = response.parse()
        assert result.execution_id == "exec_123"

    async def test_async_get_status_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.get_status returns raw HTTP response."""
        mock_api.get("/api/steps-async/status/exec_123").mock(
            return_value=httpx.Response(
                200,
                json={"execution_id": "exec_123", "status": "SUCCESS", "data": {}},
            )
        )

        response = await async_client.steps.with_raw_response.get_status("exec_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.is_success()


class TestAsyncKnowledgeBasesWithRawResponse:
    """Tests for AsyncKnowledgeBases.with_raw_response."""

    async def test_async_list_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.list returns raw HTTP response."""
        mock_api.get("/api/knowledge-bases").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "kb_1", "name": "Test KB", "isActive": True}],
                    "pagination": {"total": 1, "page": 1, "limit": 10},
                },
            )
        )

        response = await async_client.knowledge_bases.with_raw_response.list()

        assert response.status_code == 200
        page = response.parse()
        assert len(page.data) == 1

    async def test_async_get_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.get returns raw HTTP response."""
        mock_api.get("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"id": "kb_123", "name": "Test KB"}},
            )
        )

        response = await async_client.knowledge_bases.with_raw_response.get("kb_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.id == "kb_123"

    async def test_async_search_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.search returns raw HTTP response."""
        mock_api.post("/api/knowledge-bases/kb_123/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "document": {
                                "id": "doc_1",
                                "name": "Doc 1",
                                "content": {"text": "Sample content"},
                            },
                            "similarity": 0.95,
                        }
                    ],
                    "query": "test query",
                    "resultsCount": 1,
                },
            )
        )

        response = await async_client.knowledge_bases.with_raw_response.search(
            "kb_123", query="test query"
        )

        assert response.status_code == 200
        result = response.parse()
        assert result.resultsCount == 1

    async def test_async_sync_returns_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async with_raw_response.sync returns raw HTTP response."""
        mock_api.post("/api/knowledge-bases/kb_123/sync").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "status": "COMPLETED",
                        "documentsProcessed": 10,
                        "documentsAdded": 2,
                        "documentsUpdated": 1,
                        "documentsRemoved": 0,
                    }
                },
            )
        )

        response = await async_client.knowledge_bases.with_raw_response.sync("kb_123")

        assert response.status_code == 200
        result = response.parse()
        assert result.status == "COMPLETED"
