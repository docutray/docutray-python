## ADDED Requirements

### Requirement: RawResponse wrapper class
The SDK SHALL provide a `RawResponse` class that wraps HTTP responses and provides access to status code, headers, and the underlying httpx.Response.

#### Scenario: Access status code
- **WHEN** user has a `RawResponse` object
- **THEN** user can access `response.status_code` as an integer

#### Scenario: Access response headers
- **WHEN** user has a `RawResponse` object
- **THEN** user can access `response.headers` as httpx.Headers

#### Scenario: Access underlying HTTP response
- **WHEN** user has a `RawResponse` object
- **THEN** user can access `response.http_response` as the raw httpx.Response

### Requirement: Parse raw response to typed model
The SDK SHALL provide a `parse()` method on `RawResponse` that returns the typed response model.

#### Scenario: Parse to typed result
- **WHEN** user calls `response.parse()` on a RawResponse from convert operation
- **THEN** SDK returns `ConversionResult` model parsed from response body

### Requirement: with_raw_response property on resources
The SDK SHALL provide a `with_raw_response` property on all resource classes that returns a wrapper exposing the same methods but returning `RawResponse`.

#### Scenario: Get raw response from convert
- **WHEN** user calls `client.convert.with_raw_response.run(file=path, document_type_code="invoice")`
- **THEN** SDK returns `RawResponse` instead of `ConversionResult`

#### Scenario: Get raw response from identify
- **WHEN** user calls `client.identify.with_raw_response.run(file=path)`
- **THEN** SDK returns `RawResponse` containing identification response

#### Scenario: Get raw response from document_types.list
- **WHEN** user calls `client.document_types.with_raw_response.list()`
- **THEN** SDK returns `RawResponse` with paginated list data

### Requirement: Async raw response support
The SDK SHALL provide `with_raw_response` property on async resource classes returning `AsyncRawResponse`.

#### Scenario: Async raw response
- **WHEN** user calls `await client.convert.with_raw_response.run(file=path, document_type_code="invoice")` on AsyncClient
- **THEN** SDK returns `RawResponse` from async HTTP request

### Requirement: Raw response for debugging headers
The SDK SHALL preserve request-id and other debugging headers accessible via `RawResponse`.

#### Scenario: Access request ID header
- **WHEN** user has a `RawResponse` from any API call
- **THEN** user can access `response.headers.get("x-request-id")` for debugging
