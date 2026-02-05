# Knowledge Bases

## Purpose

Provides access to Knowledge Bases API for managing document collections with semantic search capabilities.

## Requirements

### Requirement: List knowledge bases
The SDK SHALL provide a `knowledge_bases.list()` method that retrieves all knowledge bases from `/api/knowledge-bases` with pagination.

#### Scenario: List all knowledge bases
- **WHEN** user calls `client.knowledge_bases.list()`
- **THEN** SDK returns `Page[KnowledgeBase]` with pagination support

#### Scenario: Filter by active status
- **WHEN** user calls `client.knowledge_bases.list(is_active=True)`
- **THEN** SDK returns only active knowledge bases

#### Scenario: Search knowledge bases
- **WHEN** user calls `client.knowledge_bases.list(search="manual")`
- **THEN** SDK returns knowledge bases matching the search term

### Requirement: Get knowledge base by ID
The SDK SHALL provide a `knowledge_bases.get()` method that retrieves a specific knowledge base from `/api/knowledge-bases/{id}`.

#### Scenario: Get existing knowledge base
- **WHEN** user calls `client.knowledge_bases.get(kb_id="kb_123")`
- **THEN** SDK returns `KnowledgeBase` with full details including schema and document count

#### Scenario: Get non-existent knowledge base
- **WHEN** user calls `client.knowledge_bases.get(kb_id="invalid")`
- **THEN** SDK raises `NotFoundError`

### Requirement: Create knowledge base
The SDK SHALL provide a `knowledge_bases.create()` method that creates a new knowledge base via POST `/api/knowledge-bases`.

#### Scenario: Create knowledge base
- **WHEN** user calls `client.knowledge_bases.create(name="User Manual", description="System docs", schema={...})`
- **THEN** SDK returns newly created `KnowledgeBase` with assigned ID

### Requirement: Update knowledge base
The SDK SHALL provide a `knowledge_bases.update()` method that updates a knowledge base via PUT `/api/knowledge-bases/{id}`.

#### Scenario: Update knowledge base name
- **WHEN** user calls `client.knowledge_bases.update(kb_id="kb_123", name="New Name")`
- **THEN** SDK returns updated `KnowledgeBase`

### Requirement: Delete knowledge base
The SDK SHALL provide a `knowledge_bases.delete()` method that deletes a knowledge base via DELETE `/api/knowledge-bases/{id}`.

#### Scenario: Delete knowledge base
- **WHEN** user calls `client.knowledge_bases.delete(kb_id="kb_123")`
- **THEN** SDK returns None and knowledge base is soft-deleted

### Requirement: List documents in knowledge base
The SDK SHALL provide a `knowledge_bases.documents(kb_id).list()` method that retrieves documents from `/api/knowledge-bases/{id}/documents`.

#### Scenario: List documents
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").list()`
- **THEN** SDK returns `Page[KnowledgeBaseDocument]` with pagination

#### Scenario: Search documents
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").list(search="installation")`
- **THEN** SDK returns documents matching search term

### Requirement: Get document from knowledge base
The SDK SHALL provide a `knowledge_bases.documents(kb_id).get()` method that retrieves a specific document from `/api/knowledge-bases/{id}/documents/{documentId}`.

#### Scenario: Get document
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").get("doc_456")`
- **THEN** SDK returns `KnowledgeBaseDocument` with content and metadata

### Requirement: Create document in knowledge base
The SDK SHALL provide a `knowledge_bases.documents(kb_id).create()` method that adds a document via POST `/api/knowledge-bases/{id}/documents`.

#### Scenario: Create document
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").create(document_id="doc-001", content={...})`
- **THEN** SDK returns newly created `KnowledgeBaseDocument`

#### Scenario: Create document with embedding
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").create(document_id="doc-001", content={...}, generate_embedding=True)`
- **THEN** SDK creates document and generates embedding automatically

### Requirement: Update document in knowledge base
The SDK SHALL provide a `knowledge_bases.documents(kb_id).update()` method that updates a document via PUT `/api/knowledge-bases/{id}/documents/{documentId}`.

#### Scenario: Update document content
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").update("doc_456", content={...})`
- **THEN** SDK returns updated `KnowledgeBaseDocument`

#### Scenario: Regenerate embedding
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").update("doc_456", content={...}, regenerate_embedding=True)`
- **THEN** SDK updates content and regenerates embedding

### Requirement: Delete document from knowledge base
The SDK SHALL provide a `knowledge_bases.documents(kb_id).delete()` method that removes a document via DELETE `/api/knowledge-bases/{id}/documents/{documentId}`.

#### Scenario: Delete document
- **WHEN** user calls `client.knowledge_bases.documents("kb_123").delete("doc_456")`
- **THEN** SDK returns None and document is deleted

### Requirement: Semantic search in knowledge base
The SDK SHALL provide a `knowledge_bases.search()` method that performs semantic search via `/api/knowledge-bases/{id}/search`.

#### Scenario: Basic search
- **WHEN** user calls `client.knowledge_bases.search(kb_id="kb_123", query="How to configure?")`
- **THEN** SDK returns `SearchResult` with matching documents and similarity scores

#### Scenario: Search with threshold
- **WHEN** user calls `client.knowledge_bases.search(kb_id="kb_123", query="...", similarity_threshold=0.8)`
- **THEN** SDK returns only documents with similarity >= 0.8

#### Scenario: Search with limit
- **WHEN** user calls `client.knowledge_bases.search(kb_id="kb_123", query="...", limit=5)`
- **THEN** SDK returns at most 5 matching documents

### Requirement: Sync knowledge base
The SDK SHALL provide a `knowledge_bases.sync()` method that triggers synchronization via POST `/api/knowledge-bases/{id}/sync`.

#### Scenario: Sync knowledge base
- **WHEN** user calls `client.knowledge_bases.sync(kb_id="kb_123")`
- **THEN** SDK returns `SyncResult` with sync status and statistics

#### Scenario: Force regenerate embeddings
- **WHEN** user calls `client.knowledge_bases.sync(kb_id="kb_123", regenerate_embeddings=True)`
- **THEN** SDK regenerates all embeddings during sync

### Requirement: Async knowledge bases resource
The SDK SHALL provide `AsyncKnowledgeBases` class with async versions of all methods accessible via `AsyncClient.knowledge_bases`.

#### Scenario: Async list knowledge bases
- **WHEN** user calls `await client.knowledge_bases.list()` on AsyncClient
- **THEN** SDK performs async HTTP request and returns `Page[KnowledgeBase]`

#### Scenario: Async search
- **WHEN** user calls `await client.knowledge_bases.search(kb_id="kb_123", query="...")`
- **THEN** SDK performs async HTTP request and returns `SearchResult`
