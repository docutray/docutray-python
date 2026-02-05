# Tasks: Type Safety Enhancements

## Implementation Checklist

- [x] Add `ImageContentType` Literal for supported MIME types
- [x] Add `RateLimitType` Literal for rate limit periods
- [x] Add `RateLimitInfo` TypedDict for 429 response details
- [x] Add `QuotaExceededInfo` TypedDict for 402 response details
- [x] Add `status_url` field to `ConversionStatus`
- [x] Add `status_url` field to `IdentificationStatus`
- [x] Add `limit_type` property to `RateLimitError`
- [x] Add `limit` property to `RateLimitError`
- [x] Add `remaining` property to `RateLimitError`
- [x] Add `reset_time` property to `RateLimitError`
- [x] Export all types in `types/__init__.py`
- [x] Add `__all__` exports in `_types.py`
- [x] Verify mypy strict mode passes
- [x] Verify all tests pass
- [x] Verify ruff linting passes

## Files Modified

| File | Changes |
|------|---------|
| `_types.py` | Added Literal types, TypedDicts, `__all__` exports |
| `types/__init__.py` | Comprehensive type exports with documentation |
| `types/convert.py` | Added `status_url` field |
| `types/identify.py` | Added `status_url` field |
| `_exceptions.py` | Enhanced `RateLimitError` with computed properties |

## Validation Results

```
✅ mypy strict: 22 source files, no errors
✅ ruff check: All checks passed
✅ pytest: 149 tests passed
```
