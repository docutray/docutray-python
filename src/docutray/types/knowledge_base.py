"""Types for knowledge base operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBase(BaseModel):
    """A knowledge base for semantic document search."""

    model_config = ConfigDict(extra="allow")

    id: str
    """Unique knowledge base ID."""

    name: str
    """Name of the knowledge base."""

    description: str | None = None
    """Description of the knowledge base."""

    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    """JSON schema for documents in this knowledge base."""

    isActive: bool = True
    """Whether the knowledge base is active."""

    createdAt: datetime | None = None
    """Timestamp when the knowledge base was created."""

    updatedAt: datetime | None = None
    """Timestamp when the knowledge base was last updated."""

    documentCount: int | None = None
    """Number of documents in the knowledge base."""


class KnowledgeBaseDocument(BaseModel):
    """A document stored in a knowledge base."""

    model_config = ConfigDict(extra="allow")

    id: str
    """Unique document ID within the knowledge base."""

    documentId: str | None = None
    """External document reference ID."""

    content: dict[str, Any]
    """Document content matching the knowledge base schema."""

    metadata: dict[str, Any] | None = None
    """Additional metadata for the document."""

    createdAt: datetime | None = None
    """Timestamp when the document was added."""

    updatedAt: datetime | None = None
    """Timestamp when the document was last updated."""


class SearchResultItem(BaseModel):
    """A single search result with similarity score."""

    model_config = ConfigDict(extra="allow")

    document: KnowledgeBaseDocument
    """The matched document."""

    similarity: float
    """Similarity score (0-1), higher is more similar."""


class SearchResult(BaseModel):
    """Result of a semantic search operation."""

    model_config = ConfigDict(extra="allow")

    data: list[SearchResultItem]
    """List of matching documents with similarity scores."""

    query: str | None = None
    """The processed search query."""

    resultsCount: int
    """Total number of results returned."""


class SyncResult(BaseModel):
    """Result of a knowledge base synchronization operation."""

    model_config = ConfigDict(extra="allow")

    syncId: str | None = None
    """Unique sync operation ID."""

    status: str
    """Sync status (e.g., 'started', 'completed', 'failed')."""

    documentsProcessed: int | None = None
    """Number of documents processed during sync."""

    errors: list[str] | None = None
    """Any errors encountered during sync."""

    startedAt: datetime | None = None
    """Timestamp when sync started."""

    completedAt: datetime | None = None
    """Timestamp when sync completed."""
