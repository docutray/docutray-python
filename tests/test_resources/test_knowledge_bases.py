"""Tests for the KnowledgeBases resource."""

from __future__ import annotations

import httpx
import respx

from docutray import (
    AsyncClient,
    Client,
    KnowledgeBase,
    KnowledgeBaseDocument,
    SearchResult,
    SyncResult,
)


class TestKnowledgeBasesList:
    """Tests for KnowledgeBases.list()."""

    def test_list_knowledge_bases(self, client: Client, mock_api: respx.MockRouter) -> None:
        """List all knowledge bases."""
        mock_api.get("/api/knowledge-bases").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "kb_1",
                            "name": "User Documentation",
                            "description": "Product guides",
                            "isActive": True,
                            "documentCount": 50,
                        },
                        {
                            "id": "kb_2",
                            "name": "API Reference",
                            "description": "API docs",
                            "isActive": True,
                            "documentCount": 100,
                        },
                    ],
                    "pagination": {
                        "total": 2,
                        "page": 1,
                        "limit": 20,
                    },
                },
            )
        )

        page = client.knowledge_bases.list()

        assert len(page.data) == 2
        assert page.data[0].name == "User Documentation"
        assert page.data[0].documentCount == 50
        assert page.data[1].name == "API Reference"
        assert page.total == 2

    def test_list_with_search(self, client: Client, mock_api: respx.MockRouter) -> None:
        """List knowledge bases with search filter."""
        route = mock_api.get("/api/knowledge-bases").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"id": "kb_1", "name": "User Documentation"}],
                    "pagination": {"total": 1, "page": 1, "limit": 20},
                },
            )
        )

        page = client.knowledge_bases.list(search="user")

        assert len(page.data) == 1
        assert "search=user" in str(route.calls[0].request.url)


class TestKnowledgeBasesGet:
    """Tests for KnowledgeBases.get()."""

    def test_get_knowledge_base(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get a specific knowledge base."""
        mock_api.get("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "kb_123",
                        "name": "User Documentation",
                        "description": "Complete product documentation",
                        "isActive": True,
                        "documentCount": 75,
                        "createdAt": "2024-01-01T00:00:00.000Z",
                    }
                },
            )
        )

        kb = client.knowledge_bases.get("kb_123")

        assert isinstance(kb, KnowledgeBase)
        assert kb.id == "kb_123"
        assert kb.name == "User Documentation"
        assert kb.documentCount == 75


class TestKnowledgeBasesCreate:
    """Tests for KnowledgeBases.create()."""

    def test_create_knowledge_base(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Create a new knowledge base."""
        mock_api.post("/api/knowledge-bases").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": {
                        "id": "kb_new",
                        "name": "New KB",
                        "description": "A new knowledge base",
                        "isActive": True,
                    }
                },
            )
        )

        kb = client.knowledge_bases.create(
            name="New KB",
            description="A new knowledge base",
            schema={"type": "object"},
        )

        assert isinstance(kb, KnowledgeBase)
        assert kb.id == "kb_new"
        assert kb.name == "New KB"


class TestKnowledgeBasesUpdate:
    """Tests for KnowledgeBases.update()."""

    def test_update_knowledge_base(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Update a knowledge base."""
        mock_api.put("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "kb_123",
                        "name": "Updated KB",
                        "description": "Updated description",
                        "isActive": True,
                    }
                },
            )
        )

        kb = client.knowledge_bases.update(
            "kb_123",
            description="Updated description",
        )

        assert kb.description == "Updated description"


class TestKnowledgeBasesDelete:
    """Tests for KnowledgeBases.delete()."""

    def test_delete_knowledge_base(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Delete a knowledge base."""
        mock_api.delete("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        # Should not raise
        client.knowledge_bases.delete("kb_123")


class TestKnowledgeBasesDocuments:
    """Tests for KnowledgeBases.documents()."""

    def test_list_documents(self, client: Client, mock_api: respx.MockRouter) -> None:
        """List documents in a knowledge base."""
        mock_api.get("/api/knowledge-bases/kb_123/documents").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "doc_1",
                            "documentId": "external_1",
                            "content": {"title": "Getting Started"},
                            "metadata": {"category": "guide"},
                        },
                        {
                            "id": "doc_2",
                            "documentId": "external_2",
                            "content": {"title": "Advanced Usage"},
                            "metadata": {"category": "guide"},
                        },
                    ],
                    "pagination": {"total": 2, "page": 1, "limit": 20},
                },
            )
        )

        docs = client.knowledge_bases.documents("kb_123")
        page = docs.list()

        assert len(page.data) == 2
        assert page.data[0].content["title"] == "Getting Started"

    def test_get_document(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Get a specific document."""
        mock_api.get("/api/knowledge-bases/kb_123/documents/doc_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "doc_456",
                        "documentId": "external_456",
                        "content": {"title": "Test Document", "body": "Content here"},
                        "metadata": {"author": "Test"},
                    }
                },
            )
        )

        docs = client.knowledge_bases.documents("kb_123")
        doc = docs.get("doc_456")

        assert isinstance(doc, KnowledgeBaseDocument)
        assert doc.id == "doc_456"
        assert doc.content["title"] == "Test Document"

    def test_create_document(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Add a document to a knowledge base."""
        mock_api.post("/api/knowledge-bases/kb_123/documents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": {
                        "id": "doc_new",
                        "documentId": "external_new",
                        "content": {"title": "New Doc"},
                    }
                },
            )
        )

        docs = client.knowledge_bases.documents("kb_123")
        doc = docs.create(
            content={"title": "New Doc"},
            document_id="external_new",
        )

        assert doc.id == "doc_new"

    def test_update_document(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Update a document."""
        mock_api.put("/api/knowledge-bases/kb_123/documents/doc_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "doc_456",
                        "content": {"title": "Updated Doc"},
                    }
                },
            )
        )

        docs = client.knowledge_bases.documents("kb_123")
        doc = docs.update("doc_456", content={"title": "Updated Doc"})

        assert doc.content["title"] == "Updated Doc"

    def test_delete_document(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Delete a document."""
        mock_api.delete("/api/knowledge-bases/kb_123/documents/doc_456").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        docs = client.knowledge_bases.documents("kb_123")
        docs.delete("doc_456")


class TestKnowledgeBasesSearch:
    """Tests for KnowledgeBases.search()."""

    def test_search(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Perform semantic search in a knowledge base."""
        mock_api.post("/api/knowledge-bases/kb_123/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "document": {
                                "id": "doc_1",
                                "content": {"title": "Authentication Guide"},
                            },
                            "similarity": 0.92,
                        },
                        {
                            "document": {
                                "id": "doc_2",
                                "content": {"title": "Security Best Practices"},
                            },
                            "similarity": 0.85,
                        },
                    ],
                    "query": "how to authenticate",
                    "resultsCount": 2,
                },
            )
        )

        results = client.knowledge_bases.search(
            "kb_123",
            query="how to authenticate",
            limit=5,
        )

        assert isinstance(results, SearchResult)
        assert results.resultsCount == 2
        assert len(results.data) == 2
        assert results.data[0].similarity == 0.92
        assert results.data[0].document.content["title"] == "Authentication Guide"

    def test_search_with_threshold(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Search with similarity threshold."""
        route = mock_api.post("/api/knowledge-bases/kb_123/search").mock(
            return_value=httpx.Response(
                200,
                json={"data": [], "query": "test", "resultsCount": 0},
            )
        )

        client.knowledge_bases.search(
            "kb_123",
            query="test",
            similarity_threshold=0.8,
        )

        # Verify request body contains threshold
        request = route.calls[0].request
        import json

        body = json.loads(request.content)
        assert body["similarityThreshold"] == 0.8


class TestKnowledgeBasesSync:
    """Tests for KnowledgeBases.sync()."""

    def test_sync(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Trigger knowledge base synchronization."""
        mock_api.post("/api/knowledge-bases/kb_123/sync").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "syncId": "sync_abc",
                        "status": "started",
                        "documentsProcessed": 0,
                    }
                },
            )
        )

        result = client.knowledge_bases.sync("kb_123")

        assert isinstance(result, SyncResult)
        assert result.status == "started"
        assert result.syncId == "sync_abc"

    def test_sync_with_regenerate(self, client: Client, mock_api: respx.MockRouter) -> None:
        """Sync with embedding regeneration."""
        route = mock_api.post("/api/knowledge-bases/kb_123/sync").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "syncId": "sync_def",
                        "status": "started",
                    }
                },
            )
        )

        client.knowledge_bases.sync("kb_123", regenerate_embeddings=True)

        # Verify request body
        request = route.calls[0].request
        import json

        body = json.loads(request.content)
        assert body["regenerateEmbeddings"] is True


class TestKnowledgeBaseModel:
    """Tests for KnowledgeBase model."""

    def test_knowledge_base_fields(self) -> None:
        """KnowledgeBase has expected fields."""
        kb = KnowledgeBase(
            id="kb_1",
            name="Test KB",
            description="Test description",
            isActive=True,
            documentCount=42,
        )
        assert kb.id == "kb_1"
        assert kb.name == "Test KB"
        assert kb.description == "Test description"
        assert kb.isActive is True
        assert kb.documentCount == 42


class TestKnowledgeBaseDocumentModel:
    """Tests for KnowledgeBaseDocument model."""

    def test_document_fields(self) -> None:
        """KnowledgeBaseDocument has expected fields."""
        doc = KnowledgeBaseDocument(
            id="doc_1",
            documentId="external_1",
            content={"title": "Test", "body": "Content"},
            metadata={"source": "manual"},
        )
        assert doc.id == "doc_1"
        assert doc.documentId == "external_1"
        assert doc.content["title"] == "Test"
        assert doc.metadata["source"] == "manual"


class TestAsyncKnowledgeBasesList:
    """Tests for AsyncKnowledgeBases.list()."""

    async def test_async_list_knowledge_bases(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async list all knowledge bases."""
        mock_api.get("/api/knowledge-bases").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "kb_1",
                            "name": "User Documentation",
                            "description": "Product guides",
                            "isActive": True,
                            "documentCount": 50,
                        },
                    ],
                    "pagination": {"total": 1, "page": 1, "limit": 20},
                },
            )
        )

        page = await async_client.knowledge_bases.list()

        assert len(page.data) == 1
        assert page.data[0].name == "User Documentation"


class TestAsyncKnowledgeBasesGet:
    """Tests for AsyncKnowledgeBases.get()."""

    async def test_async_get_knowledge_base(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async get a specific knowledge base."""
        mock_api.get("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "kb_123",
                        "name": "User Documentation",
                        "description": "Complete product documentation",
                        "isActive": True,
                        "documentCount": 75,
                    }
                },
            )
        )

        kb = await async_client.knowledge_bases.get("kb_123")

        assert isinstance(kb, KnowledgeBase)
        assert kb.id == "kb_123"
        assert kb.name == "User Documentation"


class TestAsyncKnowledgeBasesCreate:
    """Tests for AsyncKnowledgeBases.create()."""

    async def test_async_create_knowledge_base(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async create a new knowledge base."""
        mock_api.post("/api/knowledge-bases").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": {
                        "id": "kb_new",
                        "name": "New KB",
                        "description": "A new knowledge base",
                        "isActive": True,
                    }
                },
            )
        )

        kb = await async_client.knowledge_bases.create(
            name="New KB",
            description="A new knowledge base",
            schema={"type": "object"},
        )

        assert isinstance(kb, KnowledgeBase)
        assert kb.id == "kb_new"


class TestAsyncKnowledgeBasesUpdate:
    """Tests for AsyncKnowledgeBases.update()."""

    async def test_async_update_knowledge_base(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async update a knowledge base."""
        mock_api.put("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "kb_123",
                        "name": "Updated KB",
                        "description": "Updated description",
                        "isActive": True,
                    }
                },
            )
        )

        kb = await async_client.knowledge_bases.update(
            "kb_123", description="Updated description"
        )

        assert kb.description == "Updated description"


class TestAsyncKnowledgeBasesDelete:
    """Tests for AsyncKnowledgeBases.delete()."""

    async def test_async_delete_knowledge_base(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async delete a knowledge base."""
        mock_api.delete("/api/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        # Should not raise
        await async_client.knowledge_bases.delete("kb_123")


class TestAsyncKnowledgeBasesDocuments:
    """Tests for AsyncKnowledgeBases.documents()."""

    async def test_async_list_documents(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async list documents in a knowledge base."""
        mock_api.get("/api/knowledge-bases/kb_123/documents").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "doc_1",
                            "documentId": "external_1",
                            "content": {"title": "Getting Started"},
                            "metadata": {"category": "guide"},
                        },
                    ],
                    "pagination": {"total": 1, "page": 1, "limit": 20},
                },
            )
        )

        docs = async_client.knowledge_bases.documents("kb_123")
        page = await docs.list()

        assert len(page.data) == 1
        assert page.data[0].content["title"] == "Getting Started"

    async def test_async_get_document(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async get a specific document."""
        mock_api.get("/api/knowledge-bases/kb_123/documents/doc_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "doc_456",
                        "documentId": "external_456",
                        "content": {"title": "Test Document"},
                        "metadata": {"author": "Test"},
                    }
                },
            )
        )

        docs = async_client.knowledge_bases.documents("kb_123")
        doc = await docs.get("doc_456")

        assert isinstance(doc, KnowledgeBaseDocument)
        assert doc.id == "doc_456"

    async def test_async_create_document(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async add a document to a knowledge base."""
        mock_api.post("/api/knowledge-bases/kb_123/documents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": {
                        "id": "doc_new",
                        "documentId": "external_new",
                        "content": {"title": "New Doc"},
                    }
                },
            )
        )

        docs = async_client.knowledge_bases.documents("kb_123")
        doc = await docs.create(
            content={"title": "New Doc"},
            document_id="external_new",
        )

        assert doc.id == "doc_new"

    async def test_async_update_document(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async update a document."""
        mock_api.put("/api/knowledge-bases/kb_123/documents/doc_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "id": "doc_456",
                        "content": {"title": "Updated Doc"},
                    }
                },
            )
        )

        docs = async_client.knowledge_bases.documents("kb_123")
        doc = await docs.update("doc_456", content={"title": "Updated Doc"})

        assert doc.content["title"] == "Updated Doc"

    async def test_async_delete_document(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async delete a document."""
        mock_api.delete("/api/knowledge-bases/kb_123/documents/doc_456").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        docs = async_client.knowledge_bases.documents("kb_123")
        await docs.delete("doc_456")


class TestAsyncKnowledgeBasesSearch:
    """Tests for AsyncKnowledgeBases.search()."""

    async def test_async_search(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async perform semantic search in a knowledge base."""
        mock_api.post("/api/knowledge-bases/kb_123/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "document": {
                                "id": "doc_1",
                                "content": {"title": "Authentication Guide"},
                            },
                            "similarity": 0.92,
                        },
                    ],
                    "query": "how to authenticate",
                    "resultsCount": 1,
                },
            )
        )

        results = await async_client.knowledge_bases.search(
            "kb_123",
            query="how to authenticate",
            limit=5,
        )

        assert isinstance(results, SearchResult)
        assert results.resultsCount == 1
        assert results.data[0].similarity == 0.92


class TestAsyncKnowledgeBasesSync:
    """Tests for AsyncKnowledgeBases.sync()."""

    async def test_async_sync(
        self, async_client: AsyncClient, mock_api: respx.MockRouter
    ) -> None:
        """Async trigger knowledge base synchronization."""
        mock_api.post("/api/knowledge-bases/kb_123/sync").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "syncId": "sync_abc",
                        "status": "started",
                        "documentsProcessed": 0,
                    }
                },
            )
        )

        result = await async_client.knowledge_bases.sync("kb_123")

        assert isinstance(result, SyncResult)
        assert result.status == "started"
        assert result.syncId == "sync_abc"
