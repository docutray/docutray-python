"""Tests for DSL validation rules and validation results."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from docutray import (
    AsyncClient,
    BadRequestError,
    Client,
    ConversionWebhookPayload,
    DSLValidationError,
    ValidationOutcome,
    ValidationSystemFailure,
)
from docutray.types import (
    IdentificationWebhookPayload,
    StepValidationSummary,
    StepWebhookPayload,
)

DSL_RULES = "field.total greaterThan(0)"

DOCUMENT_TYPE = {
    "id": "dt_123",
    "codeType": "acme_invoice",
    "name": "Invoice",
    "description": "Invoices",
    "isPublic": False,
    "isDraft": True,
    "status": "DRAFT",
    "dslRules": DSL_RULES,
    "boundingBoxesEnabled": False,
    "conversionSpec": None,
}

ISSUE = {
    "field": "total",
    "value": -5,
    "rule": "greaterThan",
    "message": "El campo 'total' debe ser mayor que 0",
    "code": "VALIDATION_ERROR",
    "severity": "error",
    "source": "rule",
}

VALIDATE_RESPONSE = {
    "valid": False,
    "issues": [ISSUE],
    "errors": {"count": 1, "messages": [ISSUE["message"]]},
    "warnings": {"count": 0, "messages": []},
}

DSL_ERROR_BODY = {
    "error": "Reglas DSL inválidas",
    "errors": [{"line": 2, "column": 7, "message": "Se esperaba un operador"}],
}


def sent_json(route: respx.Route) -> object:
    return json.loads(route.calls.last.request.content)


class TestDocumentTypeDslRules:
    """dsl_rules on DocumentType, create() and update()."""

    def test_model_exposes_dsl_rules(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.get("/api/document-types/dt_123").mock(
            return_value=httpx.Response(200, json={"data": DOCUMENT_TYPE})
        )

        doc_type = client.document_types.get("dt_123")

        assert doc_type.dslRules == DSL_RULES
        assert doc_type.boundingBoxesEnabled is False

    def test_create_sends_new_fields(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/document-types").mock(
            return_value=httpx.Response(201, json={"data": DOCUMENT_TYPE})
        )

        doc_type = client.document_types.create(
            name="Invoice",
            code_type="acme_invoice",
            description="Invoices",
            json_schema={"type": "object"},
            dsl_rules=DSL_RULES,
            bounding_boxes_enabled=False,
            conversion_spec={"columns": [{"header": "Total", "jsonPath": "$.total"}]},
        )

        body = sent_json(route)
        assert body["dslRules"] == DSL_RULES
        assert body["boundingBoxesEnabled"] is False
        assert body["conversionSpec"] == {
            "columns": [{"header": "Total", "jsonPath": "$.total"}]
        }
        assert doc_type.dslRules == DSL_RULES

    def test_create_omits_unset_fields(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/document-types").mock(
            return_value=httpx.Response(201, json={"data": DOCUMENT_TYPE})
        )

        client.document_types.create(
            name="Invoice",
            code_type="acme_invoice",
            description="Invoices",
            json_schema={"type": "object"},
        )

        body = sent_json(route)
        assert "dslRules" not in body
        assert "conversionSpec" not in body
        assert "boundingBoxesEnabled" not in body

    def test_update_omitted_dsl_rules_preserves(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.put("/api/document-types/dt_123").mock(
            return_value=httpx.Response(200, json={"data": DOCUMENT_TYPE})
        )

        client.document_types.update("dt_123", name="Invoice v2")

        assert sent_json(route) == {"name": "Invoice v2"}

    @pytest.mark.parametrize("value", [None, ""])
    def test_update_clears_dsl_rules(
        self, client: Client, mock_api: respx.MockRouter, value: str | None
    ) -> None:
        route = mock_api.put("/api/document-types/dt_123").mock(
            return_value=httpx.Response(
                200, json={"data": {**DOCUMENT_TYPE, "dslRules": None}}
            )
        )

        doc_type = client.document_types.update("dt_123", dsl_rules=value)

        assert sent_json(route) == {"dslRules": value}
        assert doc_type.dslRules is None

    def test_update_clears_conversion_spec(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.put("/api/document-types/dt_123").mock(
            return_value=httpx.Response(200, json={"data": DOCUMENT_TYPE})
        )

        client.document_types.update("dt_123", conversion_spec=None)

        assert sent_json(route) == {"conversionSpec": None}

    async def test_async_update_sets_dsl_rules(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.put("/api/document-types/dt_123").mock(
            return_value=httpx.Response(200, json={"data": DOCUMENT_TYPE})
        )

        doc_type = await async_client.document_types.update(
            "dt_123", dsl_rules=DSL_RULES
        )

        assert sent_json(route) == {"dslRules": DSL_RULES}
        assert doc_type.dslRules == DSL_RULES

    def test_raw_update_sets_dsl_rules(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.put("/api/document-types/dt_123").mock(
            return_value=httpx.Response(200, json={"data": DOCUMENT_TYPE})
        )

        raw = client.document_types.with_raw_response.update("dt_123", dsl_rules=None)

        assert sent_json(route) == {"dslRules": None}
        assert raw.parse().dslRules == DSL_RULES


class TestValidate:
    """document_types.validate() with stored rules and dry-run DSL."""

    def test_validate_with_stored_rules(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(200, json=VALIDATE_RESPONSE)
        )

        result = client.document_types.validate("dt_123", {"total": -5})

        assert sent_json(route) == {"total": -5}
        assert result.valid is False
        assert not result.is_valid()
        assert result.issues[0].field == "total"
        assert result.issues[0].rule == "greaterThan"
        assert result.issues[0].value == -5
        assert result.issues[0].severity == "error"
        assert result.issues[0].source == "rule"
        assert result.errors.count == 1

    def test_validate_dry_run(self, client: Client, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(200, json=VALIDATE_RESPONSE)
        )

        client.document_types.validate("dt_123", {"total": -5}, dsl_rules=DSL_RULES)

        assert sent_json(route) == {"data": {"total": -5}, "dslRules": DSL_RULES}

    def test_validate_dry_run_without_dsl(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "valid": True,
                    "issues": [],
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        result = client.document_types.validate("dt_123", {"total": -5}, dsl_rules=None)

        assert sent_json(route) == {"data": {"total": -5}, "dslRules": None}
        assert result.is_valid()

    def test_valid_is_authoritative(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "valid": True,
                    "issues": [{**ISSUE, "severity": "warning"}],
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 1, "messages": [ISSUE["message"]]},
                },
            )
        )

        result = client.document_types.validate("dt_123", {"total": -5})

        assert result.is_valid()
        assert result.has_warnings()

    def test_legacy_response_without_valid(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {"count": 1, "messages": ["bad"]},
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        result = client.document_types.validate("dt_123", {})

        assert result.valid is None
        assert result.issues == []
        assert not result.is_valid()

    async def test_async_validate_dry_run(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(200, json=VALIDATE_RESPONSE)
        )

        result = await async_client.document_types.validate(
            "dt_123", {"total": -5}, dsl_rules=DSL_RULES
        )

        assert sent_json(route) == {"data": {"total": -5}, "dslRules": DSL_RULES}
        assert result.issues[0].code == "VALIDATION_ERROR"

    async def test_async_raw_validate_dry_run(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        route = mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(200, json=VALIDATE_RESPONSE)
        )

        raw = await async_client.document_types.with_raw_response.validate(
            "dt_123", {"total": -5}, dsl_rules=""
        )

        assert sent_json(route) == {"data": {"total": -5}, "dslRules": ""}
        assert raw.parse().valid is False


class TestDSLValidationError:
    """400 responses with DSL diagnostics."""

    def test_update_invalid_dsl(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.put("/api/document-types/dt_123").mock(
            return_value=httpx.Response(400, json=DSL_ERROR_BODY)
        )

        with pytest.raises(DSLValidationError) as exc_info:
            client.document_types.update("dt_123", dsl_rules="field.total >")

        error = exc_info.value
        assert isinstance(error, BadRequestError)
        assert error.status_code == 400
        assert error.message == "Reglas DSL inválidas"
        assert len(error.diagnostics) == 1
        assert error.diagnostics[0].line == 2
        assert error.diagnostics[0].column == 7
        assert error.diagnostics[0].message == "Se esperaba un operador"

    def test_validate_dry_run_invalid_dsl(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(400, json=DSL_ERROR_BODY)
        )

        with pytest.raises(DSLValidationError):
            client.document_types.validate("dt_123", {}, dsl_rules="field.total >")

    async def test_async_create_invalid_dsl(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/document-types").mock(
            return_value=httpx.Response(400, json=DSL_ERROR_BODY)
        )

        with pytest.raises(DSLValidationError) as exc_info:
            await async_client.document_types.create(
                name="Invoice",
                code_type="acme_invoice",
                description="Invoices",
                json_schema={"type": "object"},
                dsl_rules="field.total >",
            )

        assert exc_info.value.diagnostics[0].line == 2

    def test_plain_bad_request_is_not_dsl_error(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                400, json={"error": "El dry-run solo acepta data y dslRules"}
            )
        )

        with pytest.raises(BadRequestError) as exc_info:
            client.document_types.validate("dt_123", {})

        assert not isinstance(exc_info.value, DSLValidationError)
        assert exc_info.value.message == "El dry-run solo acepta data y dslRules"

    def test_string_errors_are_not_dsl_error(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                400, json={"message": "Validation error", "errors": ["bad url"]}
            )
        )

        with pytest.raises(BadRequestError) as exc_info:
            client.convert.run(url="https://example.com/a.pdf", document_type_code="x")

        assert not isinstance(exc_info.value, DSLValidationError)


class TestConversionValidation:
    """validation and field_locations on conversion results."""

    def test_sync_conversion_with_outcome(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {"total": -5},
                    "validation": {"valid": False, "errors": [ISSUE], "warnings": []},
                    "field_locations": {
                        "coordinate_space": "page-relative",
                        "pages": [
                            {"page": 1, "width": 612, "height": 792, "unit": "pt"}
                        ],
                        "fields": [
                            {
                                "path": "$.total",
                                "page": 1,
                                "box": {"x0": 0.1, "y0": 0.2, "x1": 0.3, "y1": 0.25},
                                "confidence": None,
                            }
                        ],
                    },
                },
            )
        )

        result = client.convert.run(
            url="https://example.com/a.pdf", document_type_code="x"
        )

        assert isinstance(result.validation, ValidationOutcome)
        assert result.validation.valid is False
        assert result.validation.errors[0].rule == "greaterThan"
        assert result.field_locations is not None
        assert result.field_locations.fields[0].box.x1 == 0.3
        assert result.field_locations.pages[0].width == 612

    def test_sync_conversion_with_system_failure(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200, json={"data": {"total": 1}, "validation": {"status": "error"}}
            )
        )

        result = client.convert.run(
            url="https://example.com/a.pdf", document_type_code="x"
        )

        assert isinstance(result.validation, ValidationSystemFailure)
        assert result.validation.status == "error"
        assert result.field_locations is None

    def test_sync_conversion_with_skipped_validation(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.post("/api/convert").mock(
            return_value=httpx.Response(
                200, json={"data": {"total": 1}, "validation": None}
            )
        )

        result = client.convert.run(
            url="https://example.com/a.pdf", document_type_code="x"
        )

        assert result.validation is None

    def test_async_status_with_validation(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.get("/api/convert-async/status/conv_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "conversion_id": "conv_123",
                    "status": "SUCCESS",
                    "data": {"total": 1},
                    "validation": {
                        "valid": True,
                        "errors": [],
                        "warnings": [{**ISSUE, "severity": "warning", "field": ""}],
                    },
                },
            )
        )

        status = client.convert.get_status("conv_123")

        assert isinstance(status.validation, ValidationOutcome)
        assert status.validation.valid is True
        assert status.validation.warnings[0].field == ""

    def test_step_status_validation_summary(
        self, client: Client, mock_api: respx.MockRouter
    ) -> None:
        mock_api.get("/api/steps-async/status/exec_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "execution_id": "exec_123",
                    "status": "SUCCESS",
                    "data": {"total": -5},
                    "validation": {
                        "errors": {"count": 1, "messages": [ISSUE["message"]]},
                        "warnings": {"count": 0, "messages": []},
                    },
                },
            )
        )

        status = client.steps.get_status("exec_123")

        assert isinstance(status.validation, StepValidationSummary)
        assert status.validation.errors.count == 1


class TestWebhookPayloads:
    """Parsing webhook delivery bodies."""

    def test_conversion_completed(self) -> None:
        body = json.dumps(
            {
                "conversion_id": "conv_123",
                "status": "SUCCESS",
                "request_timestamp": "2024-01-15T10:30:00.000Z",
                "response_timestamp": "2024-01-15T10:30:15.000Z",
                "document_type_code": "invoice",
                "data": {"total": -5},
                "validation": {"valid": False, "errors": [ISSUE], "warnings": []},
            }
        )

        payload = ConversionWebhookPayload.model_validate_json(body)

        assert payload.conversion_id == "conv_123"
        assert isinstance(payload.validation, ValidationOutcome)
        assert payload.validation.errors[0].message == ISSUE["message"]

    def test_conversion_completed_system_failure(self) -> None:
        payload = ConversionWebhookPayload.model_validate(
            {
                "conversion_id": "conv_123",
                "status": "SUCCESS",
                "validation": {"status": "error"},
            }
        )

        assert isinstance(payload.validation, ValidationSystemFailure)

    def test_conversion_failed(self) -> None:
        payload = ConversionWebhookPayload.model_validate(
            {"conversion_id": "conv_123", "status": "ERROR", "error": "OCR failed"}
        )

        assert payload.validation is None
        assert payload.error == "OCR failed"

    def test_identification_completed(self) -> None:
        payload = IdentificationWebhookPayload.model_validate(
            {
                "identification_id": "idn_1",
                "status": "SUCCESS",
                "document_type": {
                    "code": "invoice",
                    "name": "Invoice",
                    "confidence": 0.95,
                },
                "alternatives": [],
            }
        )

        assert payload.document_type is not None
        assert payload.document_type.code == "invoice"

    def test_step_completed(self) -> None:
        payload = StepWebhookPayload.model_validate(
            {
                "step_execution_id": "exec_1",
                "step_id": "step_1",
                "step_name": "Convert",
                "status": "completed",
                "data": {"total": 1},
                "identification": None,
                "validation": {
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 1, "messages": ["check"]},
                },
            }
        )

        assert payload.validation is not None
        assert payload.validation.warnings.messages == ["check"]
