## 1. Pagination

- [x] 1.1 Create `_pagination.py` with `Page[T]` class containing data, pagination info, and fetch_page callable
- [x] 1.2 Implement `has_next_page()` method checking if current page * limit < total
- [x] 1.3 Implement `next_page()` method that fetches and returns next Page
- [x] 1.4 Implement `iter_pages()` generator yielding pages sequentially
- [x] 1.5 Implement `auto_paging_iter()` generator yielding items across all pages
- [x] 1.6 Create `AsyncPage[T]` class with async versions: `iter_pages_async()`, `auto_paging_iter_async()`
- [x] 1.7 Update `DocumentTypes.list()` to return `Page[DocumentType]` instead of `DocumentTypesListResponse`
- [x] 1.8 Update `AsyncDocumentTypes.list()` to return `AsyncPage[DocumentType]`
- [x] 1.9 Add tests for pagination: empty page, single page, multi-page iteration

## 2. Raw Response

- [x] 2.1 Create `_response.py` with `RawResponse` class wrapping httpx.Response
- [x] 2.2 Implement `status_code`, `headers`, `http_response` properties
- [x] 2.3 Implement generic `parse()` method returning typed model
- [x] 2.4 Create `ConvertWithRawResponse` wrapper class for `Convert` resource
- [x] 2.5 Create `IdentifyWithRawResponse` wrapper class for `Identify` resource
- [x] 2.6 Create `DocumentTypesWithRawResponse` wrapper class for `DocumentTypes` resource
- [x] 2.7 Create `StepsWithRawResponse` wrapper class for `Steps` resource
- [x] 2.8 Add `with_raw_response` cached_property to all sync resource classes
- [x] 2.9 Create async raw response wrappers: `AsyncConvertWithRawResponse`, etc.
- [x] 2.10 Add `with_raw_response` cached_property to all async resource classes
- [x] 2.11 Add tests for raw response access: status_code, headers, parse()

## 3. Enhanced Polling

- [x] 3.1 Add `on_status` callback parameter to `wait_for_completion()` in `_polling.py`
- [x] 3.2 Add `on_status` callback parameter to `wait_for_completion_async()` in `_polling.py`
- [x] 3.3 Add `wait()` method to `ConversionStatus` model using stored `_resource` reference
- [x] 3.4 Add `wait()` method to `IdentificationStatus` model
- [x] 3.5 Add `wait()` method to `StepExecutionStatus` model
- [x] 3.6 Add async `wait()` method to all status models for async client usage
- [x] 3.7 Add tests for wait() on status objects with callback verification

## 4. Knowledge Bases Types

- [x] 4.1 Create `types/knowledge_base.py` with `KnowledgeBase` Pydantic model
- [x] 4.2 Add `KnowledgeBaseDocument` model with id, documentId, content, metadata, timestamps
- [x] 4.3 Add `SearchResult` model with documents list and similarity scores
- [x] 4.4 Add `SearchResultItem` model with document and similarity score
- [x] 4.5 Add `SyncResult` model with syncId, status, documentsProcessed, errors
- [x] 4.6 Export new types in `types/__init__.py`

## 5. Knowledge Bases Resource

- [x] 5.1 Create `resources/knowledge_bases.py` with `KnowledgeBases` class
- [x] 5.2 Implement `list()` method returning `Page[KnowledgeBase]`
- [x] 5.3 Implement `get()` method returning `KnowledgeBase`
- [x] 5.4 Implement `create()` method for creating knowledge bases
- [x] 5.5 Implement `update()` method for updating knowledge bases
- [x] 5.6 Implement `delete()` method for deleting knowledge bases
- [x] 5.7 Create nested `KnowledgeBaseDocuments` class for document operations
- [x] 5.8 Implement `documents.list()` returning `Page[KnowledgeBaseDocument]`
- [x] 5.9 Implement `documents.get()` returning `KnowledgeBaseDocument`
- [x] 5.10 Implement `documents.create()` for adding documents
- [x] 5.11 Implement `documents.update()` for updating documents
- [x] 5.12 Implement `documents.delete()` for removing documents
- [x] 5.13 Implement `search()` method returning `SearchResult`
- [x] 5.14 Implement `sync()` method returning `SyncResult`
- [x] 5.15 Create `AsyncKnowledgeBases` with async versions of all methods
- [x] 5.16 Create `AsyncKnowledgeBaseDocuments` for async document operations
- [x] 5.17 Add `knowledge_bases` cached_property to `Client` in `_client.py`
- [x] 5.18 Add `knowledge_bases` cached_property to `AsyncClient` in `_client.py`
- [x] 5.19 Add `with_raw_response` support to KnowledgeBases resource
- [x] 5.20 Export `KnowledgeBases` and types in `__init__.py`

## 6. Testing

- [x] 6.1 Create `tests/test_pagination.py` with Page class unit tests
- [x] 6.2 Create `tests/test_response.py` with RawResponse unit tests
- [x] 6.3 Create `tests/test_resources/test_knowledge_bases.py` with mocked API tests
- [x] 6.4 Add integration tests for knowledge_bases CRUD operations
- [x] 6.5 Add tests for knowledge_bases.documents operations
- [x] 6.6 Add tests for knowledge_bases.search and sync operations
- [x] 6.7 Run mypy and fix any type errors
- [x] 6.8 Run ruff check and fix any linting issues
- [x] 6.9 Verify all tests pass with `uv run pytest`
