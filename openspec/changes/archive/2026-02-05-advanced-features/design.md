## Context

The DocuTray Python SDK (Phases 1-4) provides core functionality for document processing: conversion, identification, document types, and steps. Phase 5 focuses on improving developer experience with automatic pagination, raw response access, enhanced polling, and complete API coverage for Knowledge Bases.

The SDK follows the 3-layer architecture (Client → HTTP → Exceptions) established in Phase 1, and uses Pydantic v2 for models. All features need both sync and async variants.

## Goals / Non-Goals

**Goals:**
- Implement automatic pagination with `Page[T]` class following stripe-python patterns
- Add `.with_raw_response` property for HTTP debugging access
- Add `wait()` method directly on status objects for better DX
- Implement complete Knowledge Bases resource (12 API endpoints)
- Maintain backwards compatibility with existing API

**Non-Goals:**
- Streaming responses (DocuTray API doesn't support streaming)
- Cursor-based pagination (API uses page-based pagination)
- Bulk upload with SSE progress (complex SSE handling deferred to future)
- Breaking changes to existing resource methods

## Decisions

### 1. Pagination Architecture

**Decision**: Create `Page[T]` and `AsyncPage[T]` classes in `_pagination.py` that wrap paginated responses and provide iteration methods.

**Rationale**: Following stripe-python pattern where `Page` holds data + pagination info + fetch function. This allows:
- `page.data` for direct access to items
- `page.iter_pages()` for page-by-page iteration
- `page.auto_paging_iter()` for transparent item iteration across pages

**Alternatives considered**:
- Generator functions: Less discoverable, harder to type
- Cursor-based pagination: API doesn't support it

### 2. Raw Response Pattern

**Decision**: Use `ResourceWithRawResponse` wrapper classes that mirror the resource API but return `RawResponse` objects.

**Rationale**: Following openai-python pattern where:
```python
response = client.convert.with_raw_response.run(...)
# response.status_code, response.headers, response.http_response
result = response.parse()  # Get typed result
```

This is cleaner than adding `raw=True` parameter to every method.

**Alternatives considered**:
- `raw=True` parameter: Would require modifying every method signature
- Separate client mode: Too heavy-handed for occasional debugging

### 3. Enhanced Polling with wait() on Status Objects

**Decision**: Add `wait()` method directly on status model classes (`ConversionStatus`, `IdentificationStatus`, `StepExecutionStatus`) that uses stored resource reference for polling.

**Rationale**: More intuitive API:
```python
status = client.convert.run_async(...)
result = status.wait(timeout=60, on_status=lambda s: print(s.status))
```

The status object stores `_resource` reference (set via `object.__setattr__` since Pydantic models are frozen).

**Alternatives considered**:
- Keep `wait_for_completion()` as standalone function: Less discoverable
- Add to resource class only: `client.convert.wait(status)` is less intuitive

### 4. Knowledge Bases Resource Structure

**Decision**: Implement as `KnowledgeBases` resource with nested `documents` sub-resource accessed via `knowledge_bases.documents`.

**Rationale**: Mirrors API structure:
```python
client.knowledge_bases.list()  # List KBs
client.knowledge_bases.documents.list(kb_id)  # List docs in KB
client.knowledge_bases.search(kb_id, query="...")  # Search
```

**Alternatives considered**:
- Flat methods with kb_id prefix: `list_documents(kb_id)` - less organized
- Separate `KnowledgeBaseDocuments` top-level resource: Doesn't reflect API hierarchy

### 5. Type System for New Models

**Decision**: Use Pydantic v2 models with `ConfigDict(extra="allow")` for forward compatibility.

**Rationale**: Consistent with existing types (`ConversionStatus`, `DocumentType`, etc.). Extra fields allowed to handle API additions without breaking.

## Risks / Trade-offs

**[Risk] Page class holds resource reference for fetching** → Mitigation: Use weak reference or document that Page is tied to client lifecycle

**[Risk] wait() on frozen Pydantic models requires workaround** → Mitigation: Use `object.__setattr__` which is already established pattern in the codebase

**[Risk] Knowledge Bases is large feature** → Mitigation: Implement incrementally (CRUD first, then documents, then search/sync)

**[Trade-off] with_raw_response creates many wrapper classes** → Acceptable for cleaner API; wrappers are lightweight

**[Trade-off] Page iteration exhausts generator** → Document that `auto_paging_iter()` can only be iterated once
