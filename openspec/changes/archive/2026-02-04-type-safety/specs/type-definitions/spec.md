# Spec: Type Definitions

## Overview

Comprehensive type definitions for the DocuTray SDK providing full type safety for IDE autocompletion and static type checking.

## Files

- `src/docutray/_types.py` - Internal type definitions
- `src/docutray/types/__init__.py` - Public type exports

## Literal Types

### ImageContentType

Supported image and document content types:

```python
ImageContentType = Literal[
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/tiff",
]
```

### RateLimitType

Rate limit period types from API responses:

```python
RateLimitType = Literal["minute", "hour", "day"]
```

## TypedDicts

### RateLimitInfo

Details from 429 rate limit responses:

| Field | Type | Description |
|-------|------|-------------|
| `error` | `str` | Error message |
| `limitType` | `RateLimitType` | Period type (minute/hour/day) |
| `limit` | `int` | Maximum limit for period |
| `remaining` | `int` | Remaining requests |
| `resetTime` | `int` | Unix timestamp when limit resets |
| `retryAfter` | `int` | Seconds until retry allowed |

### QuotaExceededInfo

Details from 402 quota exceeded responses:

| Field | Type | Description |
|-------|------|-------------|
| `error` | `str` | Error message |
| `quota` | `int` | Monthly quota limit |
| `used` | `int` | Conversions used this month |
| `resetDate` | `str` | ISO 8601 date when quota resets |

## Public Exports

All types exported via `docutray.types`:

```python
from docutray.types import (
    # Response models
    ConversionResult, ConversionStatus,
    DocumentType, ValidationResult,
    # Literal types
    ConversionStatusType, ImageContentType,
    # TypedDicts
    ConvertParams, RateLimitInfo,
    # Type aliases
    FileInput,
)
```

## Validation

- mypy strict mode must pass
- All types must have docstrings
- All optional fields must have explicit `None` defaults
