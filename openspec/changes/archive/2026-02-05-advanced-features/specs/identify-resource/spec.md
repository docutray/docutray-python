## ADDED Requirements

### Requirement: Raw response access for identify
The SDK SHALL provide `with_raw_response` property on `Identify` and `AsyncIdentify` resource classes.

#### Scenario: Get raw response from run
- **WHEN** user calls `client.identify.with_raw_response.run(file=path)`
- **THEN** SDK returns `RawResponse` with status_code, headers, and http_response

#### Scenario: Get raw response from run_async
- **WHEN** user calls `client.identify.with_raw_response.run_async(file=path)`
- **THEN** SDK returns `RawResponse` containing async identification status

#### Scenario: Get raw response from get_status
- **WHEN** user calls `client.identify.with_raw_response.get_status(identification_id="abc123")`
- **THEN** SDK returns `RawResponse` with identification status details

#### Scenario: Parse raw response
- **WHEN** user has `RawResponse` from identify operation and calls `response.parse()`
- **THEN** SDK returns appropriate typed model (`IdentificationResult` or `IdentificationStatus`)

### Requirement: Async raw response for identify
The SDK SHALL provide `with_raw_response` property on `AsyncIdentify` class.

#### Scenario: Async raw response from run
- **WHEN** user calls `await client.identify.with_raw_response.run(file=path)` on AsyncClient
- **THEN** SDK returns `RawResponse` from async HTTP request
