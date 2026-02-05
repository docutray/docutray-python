# Design: Type Safety Enhancements

## Architecture

The type safety enhancements follow the existing SDK architecture, adding types at appropriate layers:

```
┌─────────────────────────────────────┐
│         types/ Module               │  ← Public type exports
│   (Pydantic models, TypedDicts)     │
├─────────────────────────────────────┤
│         _types.py                   │  ← Internal type definitions
│   (Literals, TypedDicts, aliases)   │
├─────────────────────────────────────┤
│       _exceptions.py                │  ← Enhanced exception types
│   (RateLimitError properties)       │
└─────────────────────────────────────┘
```

## Type Definitions

### Literal Types

```python
# _types.py
ImageContentType = Literal[
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/tiff",
]

RateLimitType = Literal["minute", "hour", "day"]
```

### TypedDicts for API Response Details

```python
# _types.py
class RateLimitInfo(TypedDict, total=False):
    error: str
    limitType: NotRequired[RateLimitType]
    limit: NotRequired[int]
    remaining: NotRequired[int]
    resetTime: NotRequired[int]
    retryAfter: NotRequired[int]

class QuotaExceededInfo(TypedDict, total=False):
    error: str
    quota: NotRequired[int]
    used: NotRequired[int]
    resetDate: NotRequired[str]
```

### Response Model Enhancements

```python
# types/convert.py
class ConversionStatus(BaseModel):
    status_url: str | None = None  # NEW
    # ... existing fields

# types/identify.py
class IdentificationStatus(BaseModel):
    status_url: str | None = None  # NEW
    # ... existing fields
```

### Exception Enhancements

```python
# _exceptions.py
class RateLimitError(APIError):
    @property
    def limit_type(self) -> str | None: ...

    @property
    def limit(self) -> int | None: ...

    @property
    def remaining(self) -> int | None: ...

    @property
    def reset_time(self) -> int | None: ...
```

## Type Exports Structure

```python
# types/__init__.py
__all__ = [
    # Response Models (Pydantic)
    "ConversionResult", "ConversionStatus",
    "IdentificationResult", "IdentificationStatus",
    "DocumentType", "ValidationResult",
    "StepExecutionStatus",
    "Pagination", "PaginatedResponse",

    # Literal Types (Status Enums)
    "ConversionStatusType",
    "IdentificationStatusType",
    "StepExecutionStatusType",
    "ImageContentType",
    "RateLimitType",

    # TypedDicts (Request Parameters)
    "ConvertParams", "IdentifyParams",
    "RateLimitInfo", "QuotaExceededInfo",

    # Type Aliases
    "FileInput",
]
```

## Design Decisions

### Why No @overload Signatures

The issue mentioned `@overload` for polymorphic methods, but after evaluation:
- Current design uses separate methods (`run` vs `run_async`)
- This pattern follows stripe-python and openai-python conventions
- `@overload` would be needed for methods with `stream=True` returning iterators
- Our API doesn't have streaming, so separate methods are cleaner

### Forward Compatibility

All Pydantic models maintain `extra="allow"` to handle future API fields gracefully:

```python
class ConversionStatus(BaseModel):
    model_config = ConfigDict(extra="allow")
```

### Property-based Exception Details

Rate limit details are exposed as computed properties rather than stored attributes:
- Parses from response body on access
- Handles missing fields gracefully
- No storage duplication
