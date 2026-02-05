"""Tests for the DocumentTypes resource."""

from __future__ import annotations

import httpx
import respx

from docutray import AsyncClient, Client, DocumentType, ValidationResult


class TestDocumentTypesList:
    """Tests for DocumentTypes.list()."""

    def test_list_document_types(self, client: Client, mock_api: respx.MockRouter) -> None:
        """List all document types."""
        mock_api.get("/api/document-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "dt_1",
                            "name": "Invoice",
                            "codeType": "invoice",
                            "description": "Invoice documents",
                            "isPublic": True,
                            "isDraft": False,
                        },
                        {
                            "id": "dt_2",
                            "name": "Receipt",
                            "codeType": "receipt",
                            "description": "Receipt documents",
                            "isPublic": True,
                            "isDraft": False,
                        },
                    ],
                    "pagination": {
                        "total": 2,
                        "page": 1,
                        "limit": 10,
                    },
                },
            )
        )

        response = client.document_types.list()

        assert len(response.data) == 2
        assert response.data[0].codeType == "invoice"
        assert response.data[1].codeType == "receipt"
        assert response.total == 2
        assert response.page == 1

    def test_list_with_pagination(self, client: Client, mock_api: respx.MockRouter) -> None:
        """List document types with pagination parameters."""
        mock_api.get("/api/document-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "dt_3", "name": "Contract", "codeType": "contract"}],
                    "pagination": {"total": 15, "page": 2, "limit": 5},
                },
            )
        )

        response = client.document_types.list(page=2, limit=5)

        assert response.page == 2
        assert response.limit == 5

    def test_list_with_search(self, client: Client, mock_api: respx.MockRouter) -> None:
        """List document types with search filter."""
        route = mock_api.get("/api/document-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "dt_1", "name": "Invoice", "codeType": "invoice"}],
                    "pagination": {"total": 1, "page": 1, "limit": 10},
                },
            )
        )

        response = client.document_types.list(search="invoice")

        assert len(response.data) == 1
        # Verify search param was sent
        assert "search=invoice" in str(route.calls[0].request.url)


class TestDocumentTypesGet:
    """Tests for DocumentTypes.get()."""

    def test_get_document_type(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get a specific document type."""
        mock_api.get("/api/document-types/dt_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "dt_123",
                    "name": "Invoice",
                    "codeType": "invoice",
                    "description": "Invoice documents with line items",
                    "isPublic": True,
                    "isDraft": False,
                    "createdAt": "2024-01-01T00:00:00.000Z",
                },
            )
        )

        doc_type = client.document_types.get("dt_123")

        assert isinstance(doc_type, DocumentType)
        assert doc_type.id == "dt_123"
        assert doc_type.name == "Invoice"
        assert doc_type.codeType == "invoice"


class TestDocumentTypesValidate:
    """Tests for DocumentTypes.validate()."""

    def test_validate_valid_data(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Validate data that passes validation."""
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        result = client.document_types.validate(
            "dt_123",
            {"invoice_number": "INV-001", "total": 100},
        )

        assert isinstance(result, ValidationResult)
        assert result.is_valid()
        assert not result.has_warnings()

    def test_validate_invalid_data(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Validate data that fails validation."""
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {
                        "count": 2,
                        "messages": [
                            "Missing required field: invoice_number",
                            "Invalid type for field: total",
                        ],
                    },
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        result = client.document_types.validate("dt_123", {"total": "not-a-number"})

        assert not result.is_valid()
        assert result.errors.count == 2
        assert "invoice_number" in result.errors.messages[0]

    def test_validate_with_warnings(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Validate data that has warnings but passes."""
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {"count": 0, "messages": []},
                    "warnings": {
                        "count": 1,
                        "messages": ["Field 'notes' is deprecated"],
                    },
                },
            )
        )

        result = client.document_types.validate("dt_123", {"invoice_number": "INV-001"})

        assert result.is_valid()
        assert result.has_warnings()
        assert result.warnings.count == 1


class TestDocumentTypeModel:
    """Tests for DocumentType model."""

    def test_document_type_fields(self) -> None:
        """DocumentType has expected fields."""
        doc_type = DocumentType(
            id="dt_1",
            name="Invoice",
            codeType="invoice",
            isPublic=True,
        )
        assert doc_type.id == "dt_1"
        assert doc_type.name == "Invoice"
        assert doc_type.codeType == "invoice"
        assert doc_type.isPublic is True


class TestAsyncDocumentTypesList:
    """Tests for AsyncDocumentTypes.list()."""

    async def test_async_list_document_types(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async list all document types."""
        mock_api.get("/api/document-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "dt_1",
                            "name": "Invoice",
                            "codeType": "invoice",
                            "description": "Invoice documents",
                            "isPublic": True,
                            "isDraft": False,
                        },
                        {
                            "id": "dt_2",
                            "name": "Receipt",
                            "codeType": "receipt",
                            "description": "Receipt documents",
                            "isPublic": True,
                            "isDraft": False,
                        },
                    ],
                    "pagination": {
                        "total": 2,
                        "page": 1,
                        "limit": 10,
                    },
                },
            )
        )

        response = await async_client.document_types.list()

        assert len(response.data) == 2
        assert response.data[0].codeType == "invoice"
        assert response.data[1].codeType == "receipt"
        assert response.total == 2

    async def test_async_list_with_pagination(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async list document types with pagination parameters."""
        mock_api.get("/api/document-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "dt_3", "name": "Contract", "codeType": "contract"}],
                    "pagination": {"total": 15, "page": 2, "limit": 5},
                },
            )
        )

        response = await async_client.document_types.list(page=2, limit=5)

        assert response.page == 2
        assert response.limit == 5


class TestAsyncDocumentTypesGet:
    """Tests for AsyncDocumentTypes.get()."""

    async def test_async_get_document_type(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async get a specific document type."""
        mock_api.get("/api/document-types/dt_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "dt_123",
                    "name": "Invoice",
                    "codeType": "invoice",
                    "description": "Invoice documents with line items",
                    "isPublic": True,
                    "isDraft": False,
                    "createdAt": "2024-01-01T00:00:00.000Z",
                },
            )
        )

        doc_type = await async_client.document_types.get("dt_123")

        assert isinstance(doc_type, DocumentType)
        assert doc_type.id == "dt_123"
        assert doc_type.name == "Invoice"
        assert doc_type.codeType == "invoice"


class TestAsyncDocumentTypesValidate:
    """Tests for AsyncDocumentTypes.validate()."""

    async def test_async_validate_valid_data(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async validate data that passes validation."""
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {"count": 0, "messages": []},
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        result = await async_client.document_types.validate(
            "dt_123",
            {"invoice_number": "INV-001", "total": 100},
        )

        assert isinstance(result, ValidationResult)
        assert result.is_valid()
        assert not result.has_warnings()

    async def test_async_validate_invalid_data(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async validate data that fails validation."""
        mock_api.post("/api/document-types/dt_123/validate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "errors": {
                        "count": 2,
                        "messages": [
                            "Missing required field: invoice_number",
                            "Invalid type for field: total",
                        ],
                    },
                    "warnings": {"count": 0, "messages": []},
                },
            )
        )

        result = await async_client.document_types.validate(
            "dt_123", {"total": "not-a-number"}
        )

        assert not result.is_valid()
        assert result.errors.count == 2
