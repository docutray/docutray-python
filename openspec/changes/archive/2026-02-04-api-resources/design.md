## Context

The DocuTray Python SDK has completed Phase 1 (core infrastructure) and Phase 2 (error handling & retry). The SDK follows the 3-layer architecture pattern from stripe-python and openai-python:

```
┌─────────────────────────────────────┐
│         Client Layer                │  ← Public interface (Client, AsyncClient)
├─────────────────────────────────────┤
│         HTTP Layer                  │  ← Transport with retry logic
├─────────────────────────────────────┤
│       Exceptions Layer              │  ← Error mapping
└─────────────────────────────────────┘
```

Current state:
- `Client` and `AsyncClient` exist but expose no resources
- `SyncHTTPClient` and `AsyncHTTPClient` handle transport with retry
- Exception hierarchy maps HTTP status codes to typed errors
- No Pydantic models or TypedDict definitions exist yet

Constraints:
- Python 3.10+ required
- Must use httpx for HTTP (already in place)
- Must use Pydantic v2 for response models
- mypy strict mode compliance required

## Goals / Non-Goals

**Goals:**
- Implement all 4 API resources (convert, identify, document_types, steps)
- Provide both sync and async versions of all methods
- Support multiple file input formats transparently
- Add polling helpers for async operations
- Full type coverage for IDE autocompletion

**Non-Goals:**
- Knowledge Bases resource (deferred to Phase 4)
- Streaming responses (not supported by current API)
- Pagination auto-iteration (deferred to Phase 5)
- Webhook handling

## Decisions

### 1. Resource Access Pattern: Lazy-loaded cached_property

**Decision:** Resources accessed via `client.resource` using `@cached_property`.

**Rationale:** Follows stripe-python and openai-python patterns. Resources are only instantiated when first accessed, reducing memory for clients that don't use all resources.

**Alternatives considered:**
- Eager initialization in `__init__`: Wastes memory, slower startup
- Factory methods `client.get_convert()`: Less intuitive API

```python
class Client:
    @cached_property
    def convert(self) -> Convert:
        return Convert(self)
```

### 2. File Input Handling: Union type with internal normalization

**Decision:** Accept `Union[Path, bytes, BinaryIO]` for `file` param, `str` for `url`, `str` for `file_base64`. Internal `_prepare_file_upload()` normalizes to API format.

**Rationale:** Maximum flexibility for users. Detection of content type from Path extension. Clear separation between local files and URLs.

**Alternatives considered:**
- Single `input` param with type detection: Ambiguous for string paths vs URLs
- Separate methods per input type: API bloat, poor DX

### 3. Response Models: Pydantic with extra="allow"

**Decision:** All response models use `model_config = ConfigDict(extra="allow")` for forward compatibility.

**Rationale:** API may add fields in future. SDK should not break when unknown fields appear.

```python
class ConversionResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    data: dict[str, Any]
```

### 4. Async Polling: Method on status objects

**Decision:** `wait()` method on status objects (`ConversionStatus.wait()`).

**Rationale:** Fluent API, keeps polling logic close to status. Allows chaining: `client.convert.run_async(...).wait()`.

**Alternatives considered:**
- Separate `client.wait(status)`: Less discoverable
- Callback-based: More complex, less Pythonic

### 5. Request Parameters: TypedDict over Pydantic

**Decision:** Use `TypedDict` for request parameters in `_types.py`.

**Rationale:** TypedDict provides type hints without runtime validation overhead. Request validation happens server-side.

```python
class ConvertParams(TypedDict, total=False):
    document_type_code: Required[str]
    document_metadata: dict[str, Any]
```

### 6. Module Organization: One file per resource

**Decision:** Each resource in own file: `resources/convert.py`, `resources/identify.py`, etc.

**Rationale:** Clear organization, manageable file sizes, easy to navigate.

### 7. HTTP Request Method: Add to base client

**Decision:** Add `_request()` and `_request_async()` methods to base clients that resources call.

**Rationale:** Resources shouldn't access HTTP client directly. Base client can handle common concerns (headers, error handling).

```python
class BaseClient:
    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        return self._client.request(method, path, **kwargs)
```

## Risks / Trade-offs

### Risk: API response format changes
**Mitigation:** Use `extra="allow"` in Pydantic models. Add integration tests against staging API.

### Risk: Polling timeout edge cases
**Mitigation:** Clear timeout error with conversion_id for manual recovery. Document timeout behavior.

### Risk: Large file uploads
**Mitigation:** Use streaming upload via httpx. Document 100MB limit from API.

### Trade-off: No request validation
**Impact:** Invalid requests only caught by API, not locally.
**Acceptance:** Matches stripe-python pattern. Server validation is authoritative.

### Trade-off: Sync/Async code duplication
**Impact:** Each resource has two classes (Convert, AsyncConvert).
**Acceptance:** Explicit is better than implicit. Clear which methods are async.
