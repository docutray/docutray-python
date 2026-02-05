## ADDED Requirements

### Requirement: Raw response access for convert
The SDK SHALL provide `with_raw_response` property on `Convert` and `AsyncConvert` resource classes.

#### Scenario: Get raw response from run
- **WHEN** user calls `client.convert.with_raw_response.run(file=path, document_type_code="invoice")`
- **THEN** SDK returns `RawResponse` with status_code, headers, and http_response

#### Scenario: Get raw response from run_async
- **WHEN** user calls `client.convert.with_raw_response.run_async(file=path, document_type_code="invoice")`
- **THEN** SDK returns `RawResponse` containing async conversion status

#### Scenario: Get raw response from get_status
- **WHEN** user calls `client.convert.with_raw_response.get_status(conversion_id="abc123")`
- **THEN** SDK returns `RawResponse` with conversion status details

#### Scenario: Parse raw response
- **WHEN** user has `RawResponse` from convert operation and calls `response.parse()`
- **THEN** SDK returns appropriate typed model (`ConversionResult` or `ConversionStatus`)

### Requirement: Async raw response for convert
The SDK SHALL provide `with_raw_response` property on `AsyncConvert` class.

#### Scenario: Async raw response from run
- **WHEN** user calls `await client.convert.with_raw_response.run(file=path, document_type_code="invoice")` on AsyncClient
- **THEN** SDK returns `RawResponse` from async HTTP request
