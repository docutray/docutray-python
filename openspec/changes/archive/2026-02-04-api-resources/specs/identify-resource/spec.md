## ADDED Requirements

### Requirement: Synchronous document identification
The SDK SHALL provide an `identify.run()` method that sends a document to `/api/identify` and returns the identified document type with confidence score.

#### Scenario: Identify document type
- **WHEN** user calls `client.identify.run(file=Path("document.pdf"))`
- **THEN** the SDK returns `IdentificationResult` with `document_type` (code, name, confidence) and `alternatives`

#### Scenario: Identify with multiple candidates
- **WHEN** user calls `client.identify.run(file=path)` on an ambiguous document
- **THEN** the SDK returns primary match in `document_type` and other candidates in `alternatives` sorted by confidence

### Requirement: Asynchronous document identification
The SDK SHALL provide an `identify.run_async()` method that initiates identification via `/api/identify-async` and returns an identification ID.

#### Scenario: Start async identification
- **WHEN** user calls `client.identify.run_async(file=Path("document.pdf"))`
- **THEN** the SDK returns `IdentificationStatus` with `identification_id` and status `ENQUEUED`

### Requirement: Identification status polling
The SDK SHALL provide an `identify.get_status()` method to check async identification status via `/api/identify-async/status/{id}`.

#### Scenario: Check completed identification
- **WHEN** user calls `client.identify.get_status(identification_id="abc123")` after completion
- **THEN** the SDK returns `IdentificationStatus` with status `SUCCESS` and identification results

### Requirement: Async client identification methods
The SDK SHALL provide `AsyncIdentify` class with async versions accessible via `AsyncClient.identify`.

#### Scenario: Async identify with await
- **WHEN** user calls `await async_client.identify.run(file=path)`
- **THEN** the SDK performs async HTTP request and returns `IdentificationResult`
