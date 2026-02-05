## Why

Implement Phase 5 of the SDK roadmap to improve developer experience with advanced features. Developers need automatic pagination to iterate through results without manual page management, raw response access for debugging HTTP details, and complete API coverage including the Knowledge Bases resource. The current polling mechanism works but lacks developer-friendly conveniences like direct `wait()` methods on status objects.

Related: GitHub issue #9

## What Changes

- Add automatic pagination with `Page[T]` class supporting `iter_pages()` and `auto_paging_iter()` methods
- Add raw HTTP response access via `.with_raw_response` property on all resources
- Enhance async job handling with `wait()` method directly on status objects
- Implement complete Knowledge Bases resource (CRUD, documents, search, sync)
- Add progress callback support for polling operations

## Capabilities

### New Capabilities
- `pagination`: Automatic pagination with `Page[T]` class supporting page-based iteration (page, limit, total pattern)
- `raw-response`: Raw HTTP response wrapper providing access to status_code, headers, and http_response
- `knowledge-bases`: Knowledge Bases resource with CRUD operations, nested documents, semantic search, and sync

### Modified Capabilities
- `async-polling`: Add `wait()` method directly on status objects with configurable poll_interval, timeout, and on_status callback
- `document-types-resource`: Update `list()` to return `Page[DocumentType]` instead of `PaginatedResponse`
- `convert-resource`: Add `with_raw_response` property
- `identify-resource`: Add `with_raw_response` property
- `steps-resource`: Add `with_raw_response` property

## Impact

- **New files**:
  - `src/docutray/_pagination.py` - Page and AsyncPage classes
  - `src/docutray/_response.py` - RawResponse wrapper
  - `src/docutray/resources/knowledge_bases.py` - KnowledgeBases resource
  - `src/docutray/types/knowledge_base.py` - Pydantic models for knowledge bases

- **Modified files**:
  - `src/docutray/_client.py` - Add knowledge_bases resource property
  - `src/docutray/_polling.py` - Enhance with callback support
  - `src/docutray/types/convert.py` - Add wait() method to ConversionStatus
  - `src/docutray/types/identify.py` - Add wait() method to IdentificationStatus
  - `src/docutray/types/step.py` - Add wait() method to StepExecutionStatus
  - `src/docutray/resources/convert.py` - Add with_raw_response property
  - `src/docutray/resources/identify.py` - Add with_raw_response property
  - `src/docutray/resources/document_types.py` - Return Page[T], add with_raw_response
  - `src/docutray/resources/steps.py` - Add with_raw_response property
  - `src/docutray/__init__.py` - Export new public classes

- **API Coverage**: Adds 12 new endpoints for Knowledge Bases
- **Backwards Compatibility**: All changes are additive; existing API remains unchanged
