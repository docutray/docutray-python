# Proposal: Type Safety Enhancements

## Summary

Implement comprehensive type safety features for the DocuTray Python SDK following Phase 4 of the roadmap. This enhances developer experience through IDE autocompletion, static type checking validation, and fully typed API responses.

## Related Issue

GitHub Issue #7: feat: Phase 4 - Type Safety

## Motivation

Strong typing provides:
- Better IDE autocompletion and IntelliSense
- Catch errors at development time vs runtime
- Self-documenting code through type annotations
- Consistency with industry-leading SDKs (stripe-python, openai-python)

## Current State

Previous phases established:
- `py.typed` marker (PEP 561)
- mypy strict mode passing
- Basic Pydantic response models
- Core TypedDicts for request parameters

## Proposed Changes

1. **Add Literal types for all status enums and string constants**
   - `ImageContentType` for supported MIME types
   - `RateLimitType` for rate limit period types

2. **Complete response models with API spec fields**
   - Add `status_url` to `ConversionStatus` and `IdentificationStatus`
   - Add rate limit detail properties to `RateLimitError`

3. **Add TypedDicts for rate limit and quota information**
   - `RateLimitInfo` for 429 response details
   - `QuotaExceededInfo` for 402 response details

4. **Export all public types via `types/__init__.py`**
   - Response models (Pydantic)
   - Literal types (status enums)
   - TypedDicts (request parameters)
   - Type aliases (FileInput)

## Scope

### In Scope
- New Literal types for string constants
- TypedDicts for API response details
- Enhanced exception properties
- Comprehensive type exports

### Out of Scope
- `@overload` signatures (evaluated but unnecessary - current sync/async pattern is cleaner)
- Changes to existing method signatures
- New API resources

## Success Criteria

- mypy strict mode continues to pass with no errors
- All public types exported and documented
- IDE autocompletion works for all types
- Existing tests continue to pass
