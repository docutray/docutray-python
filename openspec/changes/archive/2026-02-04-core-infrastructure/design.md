## Context

The DocuTray Python SDK needs a solid foundation before adding API resources. Currently, only a placeholder `hello()` function exists. This design establishes the 3-layer architecture that will support all future SDK functionality.

**Current state**: Empty SDK with no client, no HTTP handling, no error handling.

**Constraints**:
- Must support Python 3.10+
- Must work with both sync and async code
- Must follow patterns from stripe-python and openai-python
- Must pass mypy strict mode

## Goals / Non-Goals

**Goals:**
- Establish 3-layer architecture (Client → HTTP → Exceptions)
- Provide both sync (`Client`) and async (`AsyncClient`) interfaces
- Support API key authentication via constructor or environment variable
- Configure httpx for HTTP transport with proper headers
- Create extensible exception hierarchy

**Non-Goals:**
- API resources (documents, workflows, etc.) - Phase 3
- Retry logic and rate limiting - Phase 2
- Response parsing and Pydantic models - Phase 4
- Pagination handling - Future phase

## Decisions

### 1. Use httpx for HTTP transport

**Decision**: Use httpx as the HTTP client library.

**Alternatives considered**:
- `requests` + `aiohttp`: Two libraries to maintain, different APIs
- `urllib3`: Lower level, no async support

**Rationale**: httpx provides both sync and async with identical API, excellent typing, and is used by openai-python.

### 2. Private module naming convention

**Decision**: Prefix internal modules with underscore (`_client.py`, `_http.py`).

**Rationale**: Follows stripe-python and openai-python patterns. Makes public vs internal clear. Allows re-exporting only public symbols from `__init__.py`.

### 3. Abstract base class for client

**Decision**: Use `_base_client.py` with `BaseClient` and `BaseAsyncClient` abstract classes.

**Rationale**: Centralizes shared logic (config handling, header building). Concrete clients focus on sync/async transport specifics.

### 4. Single version source of truth

**Decision**: Store version in `_version.py` as `__version__` string.

**Rationale**: Can be imported without side effects. Used in User-Agent header and package metadata.

### 5. Environment variable precedence

**Decision**: Explicit `api_key` parameter takes precedence over `DOCUTRAY_API_KEY` environment variable.

**Rationale**: Allows easy testing and multi-tenant scenarios while supporting zero-config for simple cases.

## Risks / Trade-offs

**[Risk] httpx version constraints** → Pin to `>=0.23.0,<1` to avoid breaking changes while allowing minor updates.

**[Risk] API key exposure in logs** → Implement `__repr__` that hides credentials. Never log API key.

**[Trade-off] Abstract base class complexity** → Adds indirection but significantly reduces duplication between sync/async clients.

**[Trade-off] No retry logic in Phase 1** → Simpler initial implementation, but users may hit transient failures. Addressed in Phase 2.
