"""Tests for API coverage gaps closed before release (#27).

Response bodies mirror what the API builds in its route handlers.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from docutray import AsyncClient, Client, ValidationOutcome
from docutray.types import (
    ConversionResult,
    ConversionStatus,
    IdentificationStatus,
    StepExecutionStatus,
    StepWebhookPayload,
    ValidationResult,
)

METADATA = {"customer_id": "12345", "reference": "INV-001"}

IDENTIFY_RESULT = {
    "document_type": {"code": "invoice", "name": "Invoice", "confidence": 0.95},
    "alternatives": [],
}

IDENTIFY_ASYNC_RESULT = {"id": "idf_1", "status": "ENQUEUED"}


def _form_field(request: httpx.Request, name: str) -> str:
    """Extract a text field from a multipart body."""
    body = request.content.decode("latin-1")
    marker = f'name="{name}"\r\n\r\n'
    start = body.index(marker) + len(marker)
    return body[start : body.index("\r\n--", start)]


class TestIdentifyDocumentMetadata:
    """document_metadata on identify.run / run_async."""

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"url": "https://example.com/a.pdf"},
            {"file_base64": "data:application/pdf;base64,JVBERi0="},
        ],
    )
    def test_json_body(
        self, client: Client, mock_api: respx.MockRouter, kwargs: dict[str, str]
    ) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        client.identify.run(**kwargs, document_metadata=METADATA)

        assert json.loads(route.calls[0].request.content)["document_metadata"] == (
            METADATA
        )

    def test_multipart_body(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        client.identify.run(
            file=b"%PDF-1.4", content_type="application/pdf", document_metadata=METADATA
        )

        sent = _form_field(route.calls[0].request, "document_metadata")
        assert json.loads(sent) == METADATA

    def test_omitted_by_default(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        client.identify.run(url="https://example.com/a.pdf")

        assert "document_metadata" not in json.loads(route.calls[0].request.content)

    def test_run_async(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(202, json=IDENTIFY_ASYNC_RESULT)
        )

        client.identify.run_async(
            url="https://example.com/a.pdf", document_metadata=METADATA
        )

        assert json.loads(route.calls[0].request.content)["document_metadata"] == (
            METADATA
        )

    async def test_async_client_multipart(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(202, json=IDENTIFY_ASYNC_RESULT)
        )

        await async_client.identify.run_async(
            file=b"%PDF-1.4", content_type="application/pdf", document_metadata=METADATA
        )

        sent = _form_field(route.calls[0].request, "document_metadata")
        assert json.loads(sent) == METADATA

    def test_raw_response(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        raw = client.identify.with_raw_response.run(
            url="https://example.com/a.pdf", document_metadata=METADATA
        )

        assert raw.parse().document_type.code == "invoice"
        assert json.loads(route.calls[0].request.content)["document_metadata"] == (
            METADATA
        )

    async def test_async_raw_response(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        await async_client.identify.with_raw_response.run(
            url="https://example.com/a.pdf", document_metadata=METADATA
        )

        assert json.loads(route.calls[0].request.content)["document_metadata"] == (
            METADATA
        )


class TestStatusModels:
    """Typed fields on status responses."""

    def test_step_status_reads_execution_id(self) -> None:
        # Shape built by GET /api/steps-async/status/{executionId}; a future API
        # version may drop the deprecated conversion_id alias.
        status = StepExecutionStatus.model_validate(
            {
                "execution_id": "se_1",
                "status": "SUCCESS",
                "request_timestamp": "2026-10-28T10:30:00.000Z",
                "response_timestamp": "2026-10-28T10:30:05.000Z",
                "data": {"total": 100},
                "identification": {
                    "success": True,
                    "documentTypeCode": "invoice",
                    "confidence": 0.95,
                },
                "validation": {
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 0, "messages": []},
                },
                "document_metadata": METADATA,
            }
        )

        assert status.execution_id == "se_1"
        assert status.identification is not None
        assert status.identification.documentTypeCode == "invoice"
        assert status.identification.confidence == 0.95
        assert status.document_metadata == METADATA

    def test_step_status_prefers_execution_id(self) -> None:
        status = StepExecutionStatus.model_validate(
            {"execution_id": "se_1", "conversion_id": "se_1", "status": "ERROR"}
        )

        assert status.execution_id == "se_1"

    @pytest.mark.parametrize("key", ["id", "conversion_id"])
    def test_step_status_legacy_keys(self, key: str) -> None:
        status = StepExecutionStatus.model_validate({key: "se_1", "status": "ENQUEUED"})

        assert status.execution_id == "se_1"

    def test_step_run_response_step_name(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        # Shape returned by POST /api/steps-async/{stepId}
        mock_api.post("/api/steps-async/st_1").mock(
            return_value=httpx.Response(
                202,
                json={
                    "id": "se_1",
                    "status": "ENQUEUED",
                    "step_id": "st_1",
                    "step_name": "Invoices",
                },
            )
        )

        status = client.steps.run_async("st_1", url="https://example.com/a.pdf")

        assert status.execution_id == "se_1"
        assert status.step_name == "Invoices"

    def test_step_identification_other(self) -> None:
        status = StepExecutionStatus.model_validate(
            {
                "execution_id": "se_1",
                "status": "SUCCESS",
                "data": None,
                "identification": {"success": True, "documentTypeCode": "other"},
            }
        )

        assert status.identification is not None
        assert status.identification.documentTypeCode == "other"
        assert status.identification.confidence is None

    def test_conversion_status_document_metadata(self) -> None:
        status = ConversionStatus.model_validate(
            {
                "conversion_id": "c_1",
                "status": "PROCESSING",
                "request_timestamp": "2026-10-28T10:30:00.000Z",
                "document_type_code": "invoice",
                "original_filename": "a.pdf",
                "document_metadata": METADATA,
            }
        )

        assert status.document_metadata == METADATA

    def test_identification_status_code_options(self) -> None:
        status = IdentificationStatus.model_validate(
            {
                "id": "idf_1",
                "status": "SUCCESS",
                "document_type_code_options": ["invoice", "receipt"],
                "request_timestamp": "2026-10-28T10:30:00.000Z",
                "response_timestamp": "2026-10-28T10:30:05.000Z",
                "document_type": {
                    "code": "invoice",
                    "name": "Invoice",
                    "confidence": 0.95,
                },
                "alternatives": [],
            }
        )

        assert status.document_type_code_options == ["invoice", "receipt"]


class TestKnowledgeBaseParams:
    """Knowledge base parameters accepted by the API."""

    KB = {"id": "kb_1", "name": "Docs", "isActive": True}
    DOC = {"id": "kbd_1", "documentId": "guide", "content": {"title": "Guide"}}

    def test_update_schema_and_indexing_preferences(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.put("/api/knowledge-bases/kb_1").mock(
            return_value=httpx.Response(200, json={"data": self.KB})
        )
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}

        client.knowledge_bases.update(
            "kb_1", schema=schema, indexing_preferences={"fields": ["title"]}
        )

        assert json.loads(route.calls[0].request.content) == {
            "schema": schema,
            "indexingPreferences": {"fields": ["title"]},
        }

    async def test_async_update(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.put("/api/knowledge-bases/kb_1").mock(
            return_value=httpx.Response(200, json={"data": self.KB})
        )

        await async_client.knowledge_bases.update("kb_1", schema={"type": "object"})

        assert json.loads(route.calls[0].request.content) == {
            "schema": {"type": "object"}
        }

    def test_sync_options(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/knowledge-bases/kb_1/sync").mock(
            return_value=httpx.Response(200, json={"data": {"status": "completed"}})
        )

        client.knowledge_bases.sync("kb_1", force=True, sync_external_sources=False)

        assert json.loads(route.calls[0].request.content) == {
            "force": True,
            "syncExternalSources": False,
        }

    def test_sync_without_options_sends_no_body(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/knowledge-bases/kb_1/sync").mock(
            return_value=httpx.Response(200, json={"data": {"status": "completed"}})
        )

        client.knowledge_bases.sync("kb_1")

        assert route.calls[0].request.content == b""

    @pytest.mark.parametrize("raw", [False, True])
    async def test_async_sync_options(
        self, async_client: AsyncClient, mock_api: respx.MockRouter, raw: bool
    ) -> None:
        route = mock_api.post("/api/knowledge-bases/kb_1/sync").mock(
            return_value=httpx.Response(200, json={"data": {"status": "completed"}})
        )
        resource = (
            async_client.knowledge_bases.with_raw_response
            if raw
            else async_client.knowledge_bases
        )

        await resource.sync("kb_1", force=True)

        assert json.loads(route.calls[0].request.content) == {"force": True}

    def test_raw_sync_options(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/knowledge-bases/kb_1/sync").mock(
            return_value=httpx.Response(200, json={"data": {"status": "completed"}})
        )

        client.knowledge_bases.with_raw_response.sync(
            "kb_1", sync_external_sources=False
        )

        assert json.loads(route.calls[0].request.content) == {
            "syncExternalSources": False
        }

    def test_documents_list_document_id(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.get("/api/knowledge-bases/kb_1/documents").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [self.DOC],
                    "pagination": {"total": 2, "page": 1, "limit": 1, "pages": 2},
                },
            )
        )

        page = client.knowledge_bases.documents("kb_1").list(
            document_id="guide", limit=1
        )
        page.next_page()

        for call in route.calls:
            assert call.request.url.params["documentId"] == "guide"
        assert len(route.calls) == 2

    async def test_async_documents_list_document_id(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.get("/api/knowledge-bases/kb_1/documents").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [self.DOC],
                    "pagination": {"total": 1, "page": 1, "limit": 20, "pages": 1},
                },
            )
        )

        await async_client.knowledge_bases.documents("kb_1").list(document_id="guide")

        assert route.calls[0].request.url.params["documentId"] == "guide"

    def test_documents_create_sends_document_id(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/knowledge-bases/kb_1/documents").mock(
            return_value=httpx.Response(201, json={"data": self.DOC})
        )

        client.knowledge_bases.documents("kb_1").create(
            document_id="guide", content={"title": "Guide"}
        )

        body = json.loads(route.calls[0].request.content)
        assert body["documentId"] == "guide"

    def test_documents_create_requires_document_id(self, client: Client) -> None:
        create = client.knowledge_bases.documents("kb_1").create

        with pytest.raises(TypeError, match="document_id"):
            create(content={"title": "Guide"})  # type: ignore[call-arg]

    async def test_async_documents_create_requires_document_id(
        self, async_client: AsyncClient
    ) -> None:
        create = async_client.knowledge_bases.documents("kb_1").create

        with pytest.raises(TypeError, match="document_id"):
            await create(content={"title": "Guide"})  # type: ignore[call-arg]


class TestValidationHardening:
    """Malformed issues and partial summaries (#23)."""

    def test_malformed_issue_keeps_outcome(self) -> None:
        result = ConversionResult.model_validate(
            {
                "data": {},
                "validation": {
                    "valid": False,
                    "errors": [
                        {
                            "field": 3,
                            "code": None,
                            "message": None,
                            "severity": "error",
                            "source": "schema",
                            "details": ["a", "b"],
                        }
                    ],
                    "warnings": [],
                },
            }
        )

        assert isinstance(result.validation, ValidationOutcome)
        assert result.validation.valid is False
        issue = result.validation.errors[0]
        assert issue.field == "3"
        assert issue.code is None
        assert issue.message is None
        assert issue.details == ["a", "b"]

    def test_validation_result_requires_summary_counts(self) -> None:
        # An empty summary must not read as "no errors" when valid is unknown.
        with pytest.raises(ValueError):
            ValidationResult.model_validate(
                {"valid": None, "errors": {}, "warnings": {}}
            )

    def test_validation_result_legacy_shape(self) -> None:
        result = ValidationResult.model_validate(
            {
                "errors": {"count": 1, "messages": ["total: must be > 0"]},
                "warnings": {"count": 0, "messages": []},
            }
        )

        assert result.is_valid() is False

    def test_step_summary_still_lenient(self) -> None:
        payload = StepWebhookPayload.model_validate(
            {
                "step_execution_id": "se_1",
                "step_id": "st_1",
                "status": "completed",
                "validation": {"errors": {"count": 1}},
            }
        )

        assert payload.validation is not None
        assert payload.validation.errors.count == 1
        assert payload.validation.errors.messages == []
        assert payload.validation.warnings.count == 0
