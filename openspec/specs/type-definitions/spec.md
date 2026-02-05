# Type Definitions

## Purpose

Provides comprehensive type definitions for the DocuTray SDK enabling full type safety, IDE autocompletion, and static type checking.

## Requirements

### Requirement: Image content type literals
The SDK SHALL provide `ImageContentType` literal type for supported content types.

#### Scenario: Define supported content types
- **WHEN** user imports `ImageContentType` from `docutray.types`
- **THEN** it includes "application/pdf", "image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp", "image/tiff"

### Requirement: Rate limit type literals
The SDK SHALL provide `RateLimitType` literal type for rate limit period types.

#### Scenario: Define rate limit periods
- **WHEN** user imports `RateLimitType` from `docutray.types`
- **THEN** it includes "minute", "hour", "day"

### Requirement: Rate limit info typed dict
The SDK SHALL provide `RateLimitInfo` TypedDict for 429 response details.

#### Scenario: Access rate limit info fields
- **WHEN** user accesses `RateLimitInfo`
- **THEN** it contains error, limitType, limit, remaining, resetTime, retryAfter fields

### Requirement: Quota exceeded info typed dict
The SDK SHALL provide `QuotaExceededInfo` TypedDict for 402 response details.

#### Scenario: Access quota info fields
- **WHEN** user accesses `QuotaExceededInfo`
- **THEN** it contains error, quota, used, resetDate fields

### Requirement: Public type exports
The SDK SHALL export all public types via `docutray.types` module.

#### Scenario: Import all types
- **WHEN** user imports from `docutray.types`
- **THEN** all response models, literal types, and TypedDicts are accessible

### Requirement: Type checking compatibility
The SDK SHALL pass mypy strict mode validation.

#### Scenario: Static type checking
- **WHEN** mypy is run with strict mode on the SDK
- **THEN** no type errors are reported
