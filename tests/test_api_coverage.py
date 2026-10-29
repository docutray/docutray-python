"""Tests for API coverage gaps closed before release (#27).

Response bodies mirror what the API builds in its route handlers.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from docutray import (
    APITimeoutError,
    AsyncClient,
    Client,
    InternalServerError,
    NotFoundError,
    ValidationOutcome,
)
from docutray.types import (
    ConversionResult,
    ConversionStatus,
    IdentificationStatus,
    KnowledgeBaseDocument,
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

        client.identify.run(
            document_type_code_options=["invoice"], **kwargs, document_metadata=METADATA
        )

        assert json.loads(route.calls[0].request.content)["document_metadata"] == (
            METADATA
        )

    def test_multipart_body(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        client.identify.run(
            document_type_code_options=["invoice"],
            file=b"%PDF-1.4",
            content_type="application/pdf",
            document_metadata=METADATA,
        )

        sent = _form_field(route.calls[0].request, "document_metadata")
        assert json.loads(sent) == METADATA

    def test_omitted_by_default(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        client.identify.run(
            document_type_code_options=["invoice"], url="https://example.com/a.pdf"
        )

        assert "document_metadata" not in json.loads(route.calls[0].request.content)

    def test_run_async(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/identify-async").mock(
            return_value=httpx.Response(202, json=IDENTIFY_ASYNC_RESULT)
        )

        client.identify.run_async(
            document_type_code_options=["invoice"],
            url="https://example.com/a.pdf",
            document_metadata=METADATA,
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
            document_type_code_options=["invoice"],
            file=b"%PDF-1.4",
            content_type="application/pdf",
            document_metadata=METADATA,
        )

        sent = _form_field(route.calls[0].request, "document_metadata")
        assert json.loads(sent) == METADATA

    def test_raw_response(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        raw = client.identify.with_raw_response.run(
            document_type_code_options=["invoice"],
            url="https://example.com/a.pdf",
            document_metadata=METADATA,
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
            document_type_code_options=["invoice"],
            url="https://example.com/a.pdf",
            document_metadata=METADATA,
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

        client.knowledge_bases.sync("kb_1", force=True, regenerate_embeddings=True)

        assert json.loads(route.calls[0].request.content) == {
            "force": True,
            "regenerateEmbeddings": True,
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

        client.knowledge_bases.with_raw_response.sync("kb_1", force=False)

        assert json.loads(route.calls[0].request.content) == {"force": False}

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
        assert issue.code == ""
        assert issue.message == ""
        assert issue.details == ["a", "b"]

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            (["items", 0, "total"], "items[0].total"),
            (["total"], "total"),
            ([0, "name"], "[0].name"),
            (["items", None, "total"], "items.total"),
            ("items[0].total", "items[0].total"),
            (None, None),
        ],
    )
    def test_field_path_is_canonical(self, raw: object, expected: str | None) -> None:
        issue = ValidationOutcome.model_validate(
            {"valid": False, "errors": [{"field": raw, "code": "X", "message": "m"}]}
        ).errors[0]

        assert issue.field == expected

    def test_non_string_scalars_keep_outcome(self) -> None:
        outcome = ValidationOutcome.model_validate(
            {
                "valid": False,
                "errors": [
                    {"code": 400, "message": 1, "severity": 2, "source": 3, "rule": 4}
                ],
            }
        )

        issue = outcome.errors[0]
        assert (
            issue.code,
            issue.message,
            issue.severity,
            issue.source,
            issue.rule,
        ) == (
            "400",
            "1",
            "2",
            "3",
            "4",
        )

    def test_empty_summary_parses_but_is_not_valid(self) -> None:
        # An empty summary must not read as "no errors" when valid is unknown.
        result = ValidationResult.model_validate(
            {"valid": None, "errors": {}, "warnings": {}}
        )

        assert result.is_valid() is False

    def test_valid_flag_wins_over_empty_summary(self) -> None:
        result = ValidationResult.model_validate(
            {"valid": True, "issues": [], "errors": {}, "warnings": {}}
        )

        assert result.is_valid() is True

    def test_legacy_zero_count_is_valid(self) -> None:
        result = ValidationResult.model_validate(
            {
                "errors": {"count": 0, "messages": []},
                "warnings": {"count": 0, "messages": []},
            }
        )

        assert result.is_valid() is True

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


def test_step_webhook_identification_is_typed() -> None:
    payload = StepWebhookPayload.model_validate(
        {
            "step_execution_id": "se_1",
            "step_id": "st_1",
            "status": "completed",
            "identification": {"documentTypeCode": "invoice"},
        }
    )

    assert payload.identification is not None
    assert payload.identification.documentTypeCode == "invoice"


class TestGetByCode:
    """document_types.get_by_code() resolves a codeType to the full type."""

    @staticmethod
    def _mock_pages(mock_api: respx.MockRouter) -> respx.Route:
        pages = {
            "1": [
                {"id": "dt_1", "name": "Invoice v2", "codeType": "acme_invoice_v2"},
            ],
            "2": [
                {"id": "dt_2", "name": "Invoice", "codeType": "acme_invoice"},
            ],
        }

        def handler(request: httpx.Request) -> httpx.Response:
            page = request.url.params["page"]
            return httpx.Response(
                200,
                json={
                    "data": pages[page],
                    "pagination": {"total": 2, "page": int(page), "limit": 1},
                },
            )

        return mock_api.get("/api/document-types").mock(side_effect=handler)

    def test_exact_match_on_a_later_page(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        listing = self._mock_pages(mock_api)
        mock_api.get("/api/document-types/dt_2").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "dt_2",
                        "name": "Invoice",
                        "codeType": "acme_invoice",
                        "jsonSchema": {"type": "object"},
                    }
                },
            )
        )

        doc_type = client.document_types.get_by_code("acme_invoice")

        assert doc_type.id == "dt_2"
        assert doc_type.jsonSchema == {"type": "object"}
        assert listing.calls[0].request.url.params["search"] == "acme_invoice"
        assert listing.calls[0].request.url.params["limit"] == "100"
        assert len(listing.calls) == 2

    def test_not_found(self, client: Client, mock_api: respx.MockRouter) -> None:
        self._mock_pages(mock_api)

        with pytest.raises(NotFoundError, match="acme_receipt") as exc_info:
            client.document_types.get_by_code("acme_receipt")

        assert exc_info.value.status_code == 404

    def test_substring_is_not_a_match(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        self._mock_pages(mock_api)

        with pytest.raises(NotFoundError):
            client.document_types.get_by_code("acme_invoice_v")

    async def test_async(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        self._mock_pages(mock_api)
        mock_api.get("/api/document-types/dt_2").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "dt_2",
                        "name": "Invoice",
                        "codeType": "acme_invoice",
                    }
                },
            )
        )

        doc_type = await async_client.document_types.get_by_code("acme_invoice")

        assert doc_type.codeType == "acme_invoice"

    async def test_async_not_found(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        self._mock_pages(mock_api)

        with pytest.raises(NotFoundError):
            await async_client.document_types.get_by_code("missing")


def test_knowledge_base_document_null_document_id() -> None:
    doc = KnowledgeBaseDocument.model_validate(
        {"id": "kbd_1", "documentId": None, "content": {"title": "Legacy"}}
    )

    assert doc.documentId == ""


class TestIdentifyRequiresCodeOptions:
    """document_type_code_options is required, as in the API and Node SDK."""

    MESSAGE = "document_type_code_options"

    @pytest.mark.parametrize("options", [None, []])
    @pytest.mark.parametrize("method", ["run", "run_async"])
    @pytest.mark.parametrize("raw", [False, True])
    def test_sync_rejects_missing_or_empty(
        self,
        client: Client,
        mock_api: respx.MockRouter,
        options: list[str] | None,
        method: str,
        raw: bool,
    ) -> None:
        route = mock_api.post(url__regex=r"/api/identify.*")
        resource = client.identify.with_raw_response if raw else client.identify

        with pytest.raises(ValueError, match=self.MESSAGE):
            getattr(resource, method)(
                url="https://example.com/a.pdf", document_type_code_options=options
            )

        assert not route.called

    @pytest.mark.parametrize("options", [None, []])
    @pytest.mark.parametrize("method", ["run", "run_async"])
    @pytest.mark.parametrize("raw", [False, True])
    async def test_async_rejects_missing_or_empty(
        self,
        async_client: AsyncClient,
        mock_api: respx.MockRouter,
        options: list[str] | None,
        method: str,
        raw: bool,
    ) -> None:
        route = mock_api.post(url__regex=r"/api/identify.*")
        resource = (
            async_client.identify.with_raw_response if raw else async_client.identify
        )

        with pytest.raises(ValueError, match=self.MESSAGE):
            await getattr(resource, method)(
                file=b"%PDF-1.4",
                content_type="application/pdf",
                document_type_code_options=options,
            )

        assert not route.called

    def test_omitted_is_a_type_error(self, client: Client) -> None:
        with pytest.raises(TypeError, match=self.MESSAGE):
            client.identify.run(url="https://example.com/a.pdf")  # type: ignore[call-arg]

    def test_options_always_sent_in_multipart(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/identify").mock(
            return_value=httpx.Response(200, json=IDENTIFY_RESULT)
        )

        client.identify.run(
            file=b"%PDF-1.4",
            content_type="application/pdf",
            document_type_code_options=["acme_invoice"],
        )

        sent = _form_field(route.calls[0].request, "document_type_code_options")
        assert json.loads(sent) == ["acme_invoice"]


SYNC_OK = httpx.Response(200, json={"data": {"status": "completed"}})


@pytest.fixture
def no_retry_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip backoff delays between retries."""
    import docutray._http as http_module

    async def _no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(http_module.time, "sleep", lambda _delay: None)
    monkeypatch.setattr(http_module.asyncio, "sleep", _no_sleep)


@pytest.mark.usefixtures("no_retry_sleep")
class TestSyncRetries:
    """knowledge_bases.sync() is not retried by default: every attempt is billed."""

    PATH = "/api/knowledge-bases/kb_1/sync"

    @pytest.mark.parametrize("raw", [False, True])
    def test_sync_is_not_retried_by_default(
        self, client: Client, mock_api: respx.MockRouter, raw: bool
    ) -> None:
        route = mock_api.post(self.PATH).mock(return_value=httpx.Response(503))
        resource = (
            client.knowledge_bases.with_raw_response if raw else client.knowledge_bases
        )

        with pytest.raises(InternalServerError):
            resource.sync("kb_1")

        assert route.call_count == 1

    def test_sync_timeout_is_not_retried(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post(self.PATH).mock(
            side_effect=httpx.ReadTimeout("timed out")
        )

        with pytest.raises(APITimeoutError):
            client.knowledge_bases.sync("kb_1")

        assert route.call_count == 1

    def test_sync_max_retries_override(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post(self.PATH).mock(
            side_effect=[httpx.Response(503), httpx.Response(503), SYNC_OK]
        )

        result = client.knowledge_bases.sync("kb_1", max_retries=2)

        assert result.status == "completed"
        assert route.call_count == 3

    @pytest.mark.parametrize("raw", [False, True])
    async def test_async_sync_is_not_retried_by_default(
        self, async_client: AsyncClient, mock_api: respx.MockRouter, raw: bool
    ) -> None:
        route = mock_api.post(self.PATH).mock(
            side_effect=httpx.ReadTimeout("timed out")
        )
        resource = (
            async_client.knowledge_bases.with_raw_response
            if raw
            else async_client.knowledge_bases
        )

        with pytest.raises(APITimeoutError):
            await resource.sync("kb_1")

        assert route.call_count == 1

    async def test_async_sync_max_retries_override(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post(self.PATH).mock(
            side_effect=[httpx.Response(503), SYNC_OK]
        )

        result = await async_client.knowledge_bases.sync("kb_1", max_retries=1)

        assert result.status == "completed"
        assert route.call_count == 2

    def test_other_requests_keep_client_retries(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.get("/api/knowledge-bases/kb_1").mock(
            side_effect=[
                httpx.Response(503),
                httpx.Response(200, json={"data": TestKnowledgeBaseParams.KB}),
            ]
        )

        client.knowledge_bases.get("kb_1")

        assert route.call_count == 2

    def test_negative_max_retries_is_rejected(self, client: Client) -> None:
        with pytest.raises(ValueError, match="max_retries"):
            client.knowledge_bases.sync("kb_1", max_retries=-1)


class TestPathEncoding:
    """Ids are percent-encoded as single path segments, as in docutray-node."""

    RAW_ID = "a/b c?d#e"
    ENCODED = "a%2Fb%20c%3Fd%23e"

    def _capture(self, mock_api: respx.MockRouter) -> list[str]:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paths.append(request.url.raw_path.decode())
            return httpx.Response(404, json={"error": "not found"})

        mock_api.route().mock(side_effect=handler)
        return paths

    def test_sync_resources(self, client: Client, mock_api: respx.MockRouter) -> None:
        paths = self._capture(mock_api)
        calls = [
            lambda: client.document_types.get(self.RAW_ID),
            lambda: client.document_types.update(self.RAW_ID, name="x"),
            lambda: client.document_types.validate(self.RAW_ID, {}),
            lambda: client.knowledge_bases.get(self.RAW_ID),
            lambda: client.knowledge_bases.sync(self.RAW_ID),
            lambda: client.knowledge_bases.search(self.RAW_ID, query="q"),
            lambda: client.knowledge_bases.documents(self.RAW_ID).get(self.RAW_ID),
            lambda: client.knowledge_bases.documents(self.RAW_ID).list(),
            lambda: client.convert.get_status(self.RAW_ID),
            lambda: client.identify.get_status(self.RAW_ID),
            lambda: client.steps.get_status(self.RAW_ID),
            lambda: client.document_types.with_raw_response.get(self.RAW_ID),
        ]
        for call in calls:
            try:
                call()
            except NotFoundError:
                pass

        assert paths == [
            f"/api/document-types/{self.ENCODED}",
            f"/api/document-types/{self.ENCODED}",
            f"/api/document-types/{self.ENCODED}/validate",
            f"/api/knowledge-bases/{self.ENCODED}",
            f"/api/knowledge-bases/{self.ENCODED}/sync",
            f"/api/knowledge-bases/{self.ENCODED}/search",
            f"/api/knowledge-bases/{self.ENCODED}/documents/{self.ENCODED}",
            f"/api/knowledge-bases/{self.ENCODED}/documents?page=1",
            f"/api/convert-async/status/{self.ENCODED}",
            f"/api/identify-async/status/{self.ENCODED}",
            f"/api/steps-async/status/{self.ENCODED}",
            f"/api/document-types/{self.ENCODED}",
        ]

    async def test_async_resources(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        paths = self._capture(mock_api)

        for call in (
            lambda: async_client.document_types.get(self.RAW_ID),
            lambda: async_client.knowledge_bases.documents(self.RAW_ID).delete(
                self.RAW_ID
            ),
            lambda: async_client.steps.run_async(
                self.RAW_ID, url="https://e.com/a.pdf"
            ),
        ):
            with pytest.raises(NotFoundError):
                await call()

        assert paths == [
            f"/api/document-types/{self.ENCODED}",
            f"/api/knowledge-bases/{self.ENCODED}/documents/{self.ENCODED}",
            f"/api/steps-async/{self.ENCODED}",
        ]
