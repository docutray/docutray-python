"""Knowledge Bases resource for semantic document search operations."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from .._pagination import AsyncPage, Page
from ..types.knowledge_base import (
    KnowledgeBase,
    KnowledgeBaseDocument,
    SearchResult,
    SearchResultItem,
    SyncResult,
)
from ..types.shared import Pagination

if TYPE_CHECKING:
    from .._base_client import BaseAsyncClient, BaseClient


class KnowledgeBaseDocuments:
    """Synchronous document operations for a knowledge base."""

    def __init__(self, client: BaseClient, knowledge_base_id: str) -> None:
        """Initialize the KnowledgeBaseDocuments resource.

        Args:
            client: The parent client instance.
            knowledge_base_id: The knowledge base ID.
        """
        self._client = client
        self._knowledge_base_id = knowledge_base_id

    def _fetch_page(
        self,
        page_num: int,
        *,
        limit: int | None = None,
        search: str | None = None,
    ) -> Page[KnowledgeBaseDocument]:
        """Fetch a specific page of documents."""
        params: dict[str, Any] = {"page": page_num}
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = self._client._request(
            "GET",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents",
            params=params,
        )
        data = response.json()

        pagination = Pagination.model_validate(data.get("pagination", {}))
        items = [KnowledgeBaseDocument.model_validate(item) for item in data.get("data", [])]

        return Page(
            data=items,
            pagination=pagination,
            fetch_page=lambda p: self._fetch_page(p, limit=limit, search=search),
        )

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> Page[KnowledgeBaseDocument]:
        """List documents in the knowledge base.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page.
            search: Search term to filter documents.

        Returns:
            A Page of documents with pagination support.

        Example:
            >>> docs = client.knowledge_bases.documents("kb_123").list()
            >>> for doc in docs.auto_paging_iter():
            ...     print(doc.id)
        """
        return self._fetch_page(page or 1, limit=limit, search=search)

    def get(self, document_id: str) -> KnowledgeBaseDocument:
        """Get a specific document by ID.

        Args:
            document_id: The document ID.

        Returns:
            The document details.

        Raises:
            NotFoundError: If the document doesn't exist.

        Example:
            >>> doc = client.knowledge_bases.documents("kb_123").get("doc_456")
            >>> print(doc.content)
        """
        response = self._client._request(
            "GET",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents/{document_id}",
        )
        return KnowledgeBaseDocument.model_validate(response.json().get("data", response.json()))

    def create(
        self,
        *,
        content: dict[str, Any],
        document_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeBaseDocument:
        """Add a document to the knowledge base.

        Args:
            content: Document content matching the knowledge base schema.
            document_id: Optional external document reference ID.
            metadata: Optional additional metadata.

        Returns:
            The created document.

        Example:
            >>> doc = client.knowledge_bases.documents("kb_123").create(
            ...     content={"title": "User Guide", "text": "..."},
            ...     metadata={"source": "manual"}
            ... )
            >>> print(f"Created: {doc.id}")
        """
        body: dict[str, Any] = {"content": content}
        if document_id is not None:
            body["documentId"] = document_id
        if metadata is not None:
            body["metadata"] = metadata

        response = self._client._request(
            "POST",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents",
            json=body,
        )
        return KnowledgeBaseDocument.model_validate(response.json().get("data", response.json()))

    def update(
        self,
        document_id: str,
        *,
        content: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeBaseDocument:
        """Update a document in the knowledge base.

        Args:
            document_id: The document ID to update.
            content: Updated document content.
            metadata: Updated metadata.

        Returns:
            The updated document.

        Example:
            >>> doc = client.knowledge_bases.documents("kb_123").update(
            ...     "doc_456",
            ...     content={"title": "Updated Guide", "text": "..."}
            ... )
        """
        body: dict[str, Any] = {}
        if content is not None:
            body["content"] = content
        if metadata is not None:
            body["metadata"] = metadata

        response = self._client._request(
            "PATCH",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents/{document_id}",
            json=body,
        )
        return KnowledgeBaseDocument.model_validate(response.json().get("data", response.json()))

    def delete(self, document_id: str) -> None:
        """Delete a document from the knowledge base.

        Args:
            document_id: The document ID to delete.

        Raises:
            NotFoundError: If the document doesn't exist.

        Example:
            >>> client.knowledge_bases.documents("kb_123").delete("doc_456")
        """
        self._client._request(
            "DELETE",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents/{document_id}",
        )


class AsyncKnowledgeBaseDocuments:
    """Asynchronous document operations for a knowledge base."""

    def __init__(self, client: BaseAsyncClient, knowledge_base_id: str) -> None:
        """Initialize the AsyncKnowledgeBaseDocuments resource.

        Args:
            client: The parent async client instance.
            knowledge_base_id: The knowledge base ID.
        """
        self._client = client
        self._knowledge_base_id = knowledge_base_id

    async def _fetch_page(
        self,
        page_num: int,
        *,
        limit: int | None = None,
        search: str | None = None,
    ) -> AsyncPage[KnowledgeBaseDocument]:
        """Fetch a specific page of documents."""
        params: dict[str, Any] = {"page": page_num}
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        response = await self._client._request(
            "GET",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents",
            params=params,
        )
        data = response.json()

        pagination = Pagination.model_validate(data.get("pagination", {}))
        items = [KnowledgeBaseDocument.model_validate(item) for item in data.get("data", [])]

        return AsyncPage(
            data=items,
            pagination=pagination,
            fetch_page=lambda p: self._fetch_page(p, limit=limit, search=search),
        )

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> AsyncPage[KnowledgeBaseDocument]:
        """List documents in the knowledge base.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page.
            search: Search term to filter documents.

        Returns:
            An AsyncPage of documents with pagination support.
        """
        return await self._fetch_page(page or 1, limit=limit, search=search)

    async def get(self, document_id: str) -> KnowledgeBaseDocument:
        """Get a specific document by ID.

        Args:
            document_id: The document ID.

        Returns:
            The document details.
        """
        response = await self._client._request(
            "GET",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents/{document_id}",
        )
        return KnowledgeBaseDocument.model_validate(response.json().get("data", response.json()))

    async def create(
        self,
        *,
        content: dict[str, Any],
        document_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeBaseDocument:
        """Add a document to the knowledge base.

        Args:
            content: Document content matching the knowledge base schema.
            document_id: Optional external document reference ID.
            metadata: Optional additional metadata.

        Returns:
            The created document.
        """
        body: dict[str, Any] = {"content": content}
        if document_id is not None:
            body["documentId"] = document_id
        if metadata is not None:
            body["metadata"] = metadata

        response = await self._client._request(
            "POST",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents",
            json=body,
        )
        return KnowledgeBaseDocument.model_validate(response.json().get("data", response.json()))

    async def update(
        self,
        document_id: str,
        *,
        content: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeBaseDocument:
        """Update a document in the knowledge base.

        Args:
            document_id: The document ID to update.
            content: Updated document content.
            metadata: Updated metadata.

        Returns:
            The updated document.
        """
        body: dict[str, Any] = {}
        if content is not None:
            body["content"] = content
        if metadata is not None:
            body["metadata"] = metadata

        response = await self._client._request(
            "PATCH",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents/{document_id}",
            json=body,
        )
        return KnowledgeBaseDocument.model_validate(response.json().get("data", response.json()))

    async def delete(self, document_id: str) -> None:
        """Delete a document from the knowledge base.

        Args:
            document_id: The document ID to delete.
        """
        await self._client._request(
            "DELETE",
            f"/api/knowledge-bases/{self._knowledge_base_id}/documents/{document_id}",
        )


class KnowledgeBases:
    """Synchronous knowledge base operations.

    Example:
        >>> client = Client(api_key="...")
        >>> # List knowledge bases
        >>> for kb in client.knowledge_bases.list().auto_paging_iter():
        ...     print(f"{kb.name}: {kb.documentCount} documents")
        >>>
        >>> # Search in a knowledge base
        >>> results = client.knowledge_bases.search("kb_123", query="authentication")
        >>> for item in results.data:
        ...     print(f"{item.document.id}: {item.similarity:.2%}")
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the KnowledgeBases resource.

        Args:
            client: The parent client instance.
        """
        self._client = client

    def _fetch_page(
        self,
        page_num: int,
        *,
        limit: int | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> Page[KnowledgeBase]:
        """Fetch a specific page of knowledge bases."""
        params: dict[str, Any] = {"page": page_num}
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if is_active is not None:
            params["isActive"] = is_active

        response = self._client._request("GET", "/api/knowledge-bases", params=params)
        data = response.json()

        pagination = Pagination.model_validate(data.get("pagination", {}))
        items = [KnowledgeBase.model_validate(item) for item in data.get("data", [])]

        return Page(
            data=items,
            pagination=pagination,
            fetch_page=lambda p: self._fetch_page(p, limit=limit, search=search, is_active=is_active),
        )

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> Page[KnowledgeBase]:
        """List knowledge bases.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page.
            search: Search term to filter by name or description.
            is_active: Filter by active status.

        Returns:
            A Page of knowledge bases with pagination support.

        Example:
            >>> for kb in client.knowledge_bases.list().auto_paging_iter():
            ...     print(f"{kb.name}: {kb.documentCount} documents")
        """
        return self._fetch_page(page or 1, limit=limit, search=search, is_active=is_active)

    def get(self, knowledge_base_id: str) -> KnowledgeBase:
        """Get a specific knowledge base by ID.

        Args:
            knowledge_base_id: The knowledge base ID.

        Returns:
            The knowledge base details.

        Raises:
            NotFoundError: If the knowledge base doesn't exist.

        Example:
            >>> kb = client.knowledge_bases.get("kb_123")
            >>> print(f"{kb.name}: {kb.description}")
        """
        response = self._client._request("GET", f"/api/knowledge-bases/{knowledge_base_id}")
        return KnowledgeBase.model_validate(response.json().get("data", response.json()))

    def create(
        self,
        *,
        name: str,
        description: str,
        schema: dict[str, Any],
        indexing_preferences: dict[str, Any] | None = None,
    ) -> KnowledgeBase:
        """Create a new knowledge base.

        Args:
            name: Unique name for the knowledge base.
            description: Description of the knowledge base.
            schema: JSON schema for documents in this knowledge base.
            indexing_preferences: Optional indexing configuration.

        Returns:
            The created knowledge base.

        Raises:
            ConflictError: If a knowledge base with that name already exists.

        Example:
            >>> kb = client.knowledge_bases.create(
            ...     name="User Documentation",
            ...     description="Product user guides and manuals",
            ...     schema={"type": "object", "properties": {"title": {"type": "string"}}}
            ... )
            >>> print(f"Created: {kb.id}")
        """
        body: dict[str, Any] = {
            "name": name,
            "description": description,
            "schema": schema,
        }
        if indexing_preferences is not None:
            body["indexingPreferences"] = indexing_preferences

        response = self._client._request("POST", "/api/knowledge-bases", json=body)
        return KnowledgeBase.model_validate(response.json().get("data", response.json()))

    def update(
        self,
        knowledge_base_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> KnowledgeBase:
        """Update a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to update.
            name: New name for the knowledge base.
            description: New description.
            is_active: Active status.

        Returns:
            The updated knowledge base.

        Example:
            >>> kb = client.knowledge_bases.update(
            ...     "kb_123",
            ...     description="Updated documentation"
            ... )
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if is_active is not None:
            body["isActive"] = is_active

        response = self._client._request(
            "PATCH",
            f"/api/knowledge-bases/{knowledge_base_id}",
            json=body,
        )
        return KnowledgeBase.model_validate(response.json().get("data", response.json()))

    def delete(self, knowledge_base_id: str) -> None:
        """Delete a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to delete.

        Raises:
            NotFoundError: If the knowledge base doesn't exist.

        Example:
            >>> client.knowledge_bases.delete("kb_123")
        """
        self._client._request("DELETE", f"/api/knowledge-bases/{knowledge_base_id}")

    def documents(self, knowledge_base_id: str) -> KnowledgeBaseDocuments:
        """Access document operations for a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID.

        Returns:
            A KnowledgeBaseDocuments instance for document operations.

        Example:
            >>> docs = client.knowledge_bases.documents("kb_123")
            >>> for doc in docs.list().auto_paging_iter():
            ...     print(doc.content)
        """
        return KnowledgeBaseDocuments(self._client, knowledge_base_id)

    def search(
        self,
        knowledge_base_id: str,
        *,
        query: str,
        limit: int | None = None,
        similarity_threshold: float | None = None,
        include_metadata: bool | None = None,
    ) -> SearchResult:
        """Perform semantic search in a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to search.
            query: Search query text.
            limit: Maximum number of results (1-50).
            similarity_threshold: Minimum similarity score (0-1).
            include_metadata: Include document metadata in results.

        Returns:
            Search results with similarity scores.

        Example:
            >>> results = client.knowledge_bases.search(
            ...     "kb_123",
            ...     query="how to configure authentication",
            ...     limit=5
            ... )
            >>> for item in results.data:
            ...     print(f"{item.similarity:.2%}: {item.document.content}")
        """
        body: dict[str, Any] = {"query": query}
        if limit is not None:
            body["limit"] = limit
        if similarity_threshold is not None:
            body["similarityThreshold"] = similarity_threshold
        if include_metadata is not None:
            body["includeMetadata"] = include_metadata

        response = self._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/search",
            json=body,
        )
        data = response.json()

        # Parse search results
        items = []
        for item_data in data.get("data", []):
            doc = KnowledgeBaseDocument.model_validate(item_data.get("document", {}))
            items.append(SearchResultItem(document=doc, similarity=item_data.get("similarity", 0)))

        return SearchResult(
            data=items,
            query=data.get("query"),
            resultsCount=data.get("resultsCount", len(items)),
        )

    def sync(
        self,
        knowledge_base_id: str,
        *,
        regenerate_embeddings: bool | None = None,
    ) -> SyncResult:
        """Trigger manual synchronization of a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to sync.
            regenerate_embeddings: Whether to regenerate all embeddings.

        Returns:
            The sync operation result.

        Example:
            >>> result = client.knowledge_bases.sync("kb_123", regenerate_embeddings=True)
            >>> print(f"Sync status: {result.status}")
        """
        body: dict[str, Any] = {}
        if regenerate_embeddings is not None:
            body["regenerateEmbeddings"] = regenerate_embeddings

        response = self._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/sync",
            json=body if body else None,
        )
        return SyncResult.model_validate(response.json().get("data", response.json()))

    @cached_property
    def with_raw_response(self) -> KnowledgeBasesWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = client.knowledge_bases.with_raw_response.list()
            >>> print(response.status_code)
            >>> page = response.parse()
        """
        return KnowledgeBasesWithRawResponse(self)


class AsyncKnowledgeBases:
    """Asynchronous knowledge base operations.

    Example:
        >>> async with AsyncClient(api_key="...") as client:
        ...     async for kb in (await client.knowledge_bases.list()).auto_paging_iter_async():
        ...         print(f"{kb.name}: {kb.documentCount} documents")
    """

    def __init__(self, client: BaseAsyncClient) -> None:
        """Initialize the AsyncKnowledgeBases resource.

        Args:
            client: The parent async client instance.
        """
        self._client = client

    async def _fetch_page(
        self,
        page_num: int,
        *,
        limit: int | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> AsyncPage[KnowledgeBase]:
        """Fetch a specific page of knowledge bases."""
        params: dict[str, Any] = {"page": page_num}
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if is_active is not None:
            params["isActive"] = is_active

        response = await self._client._request("GET", "/api/knowledge-bases", params=params)
        data = response.json()

        pagination = Pagination.model_validate(data.get("pagination", {}))
        items = [KnowledgeBase.model_validate(item) for item in data.get("data", [])]

        return AsyncPage(
            data=items,
            pagination=pagination,
            fetch_page=lambda p: self._fetch_page(p, limit=limit, search=search, is_active=is_active),
        )

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> AsyncPage[KnowledgeBase]:
        """List knowledge bases.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Number of items per page.
            search: Search term to filter by name or description.
            is_active: Filter by active status.

        Returns:
            An AsyncPage of knowledge bases with pagination support.
        """
        return await self._fetch_page(page or 1, limit=limit, search=search, is_active=is_active)

    async def get(self, knowledge_base_id: str) -> KnowledgeBase:
        """Get a specific knowledge base by ID.

        Args:
            knowledge_base_id: The knowledge base ID.

        Returns:
            The knowledge base details.
        """
        response = await self._client._request("GET", f"/api/knowledge-bases/{knowledge_base_id}")
        return KnowledgeBase.model_validate(response.json().get("data", response.json()))

    async def create(
        self,
        *,
        name: str,
        description: str,
        schema: dict[str, Any],
        indexing_preferences: dict[str, Any] | None = None,
    ) -> KnowledgeBase:
        """Create a new knowledge base.

        Args:
            name: Unique name for the knowledge base.
            description: Description of the knowledge base.
            schema: JSON schema for documents in this knowledge base.
            indexing_preferences: Optional indexing configuration.

        Returns:
            The created knowledge base.
        """
        body: dict[str, Any] = {
            "name": name,
            "description": description,
            "schema": schema,
        }
        if indexing_preferences is not None:
            body["indexingPreferences"] = indexing_preferences

        response = await self._client._request("POST", "/api/knowledge-bases", json=body)
        return KnowledgeBase.model_validate(response.json().get("data", response.json()))

    async def update(
        self,
        knowledge_base_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> KnowledgeBase:
        """Update a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to update.
            name: New name for the knowledge base.
            description: New description.
            is_active: Active status.

        Returns:
            The updated knowledge base.
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if is_active is not None:
            body["isActive"] = is_active

        response = await self._client._request(
            "PATCH",
            f"/api/knowledge-bases/{knowledge_base_id}",
            json=body,
        )
        return KnowledgeBase.model_validate(response.json().get("data", response.json()))

    async def delete(self, knowledge_base_id: str) -> None:
        """Delete a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to delete.
        """
        await self._client._request("DELETE", f"/api/knowledge-bases/{knowledge_base_id}")

    def documents(self, knowledge_base_id: str) -> AsyncKnowledgeBaseDocuments:
        """Access document operations for a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID.

        Returns:
            An AsyncKnowledgeBaseDocuments instance for document operations.
        """
        return AsyncKnowledgeBaseDocuments(self._client, knowledge_base_id)

    async def search(
        self,
        knowledge_base_id: str,
        *,
        query: str,
        limit: int | None = None,
        similarity_threshold: float | None = None,
        include_metadata: bool | None = None,
    ) -> SearchResult:
        """Perform semantic search in a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to search.
            query: Search query text.
            limit: Maximum number of results (1-50).
            similarity_threshold: Minimum similarity score (0-1).
            include_metadata: Include document metadata in results.

        Returns:
            Search results with similarity scores.
        """
        body: dict[str, Any] = {"query": query}
        if limit is not None:
            body["limit"] = limit
        if similarity_threshold is not None:
            body["similarityThreshold"] = similarity_threshold
        if include_metadata is not None:
            body["includeMetadata"] = include_metadata

        response = await self._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/search",
            json=body,
        )
        data = response.json()

        # Parse search results
        items = []
        for item_data in data.get("data", []):
            doc = KnowledgeBaseDocument.model_validate(item_data.get("document", {}))
            items.append(SearchResultItem(document=doc, similarity=item_data.get("similarity", 0)))

        return SearchResult(
            data=items,
            query=data.get("query"),
            resultsCount=data.get("resultsCount", len(items)),
        )

    async def sync(
        self,
        knowledge_base_id: str,
        *,
        regenerate_embeddings: bool | None = None,
    ) -> SyncResult:
        """Trigger manual synchronization of a knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID to sync.
            regenerate_embeddings: Whether to regenerate all embeddings.

        Returns:
            The sync operation result.
        """
        body: dict[str, Any] = {}
        if regenerate_embeddings is not None:
            body["regenerateEmbeddings"] = regenerate_embeddings

        response = await self._client._request(
            "POST",
            f"/api/knowledge-bases/{knowledge_base_id}/sync",
            json=body if body else None,
        )
        return SyncResult.model_validate(response.json().get("data", response.json()))

    @cached_property
    def with_raw_response(self) -> AsyncKnowledgeBasesWithRawResponse:
        """Access methods that return raw HTTP responses.

        Example:
            >>> response = await client.knowledge_bases.with_raw_response.list()
            >>> print(response.status_code)
            >>> page = response.parse()
        """
        return AsyncKnowledgeBasesWithRawResponse(self)


# Import here to avoid circular imports
from .._response import (  # noqa: E402
    AsyncKnowledgeBasesWithRawResponse,
    KnowledgeBasesWithRawResponse,
)
