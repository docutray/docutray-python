## ADDED Requirements

### Requirement: Synchronous document conversion
The SDK SHALL provide a `convert.run()` method that sends a document to the `/api/convert` endpoint and returns the extracted data synchronously.

#### Scenario: Convert document from file path
- **WHEN** user calls `client.convert.run(file=Path("invoice.pdf"), document_type_code="invoice")`
- **THEN** the SDK sends the file to `/api/convert` and returns a `ConversionResult` with extracted data

#### Scenario: Convert document from bytes
- **WHEN** user calls `client.convert.run(file=document_bytes, document_type_code="invoice")`
- **THEN** the SDK sends the bytes as multipart form data and returns extracted data

#### Scenario: Convert document from URL
- **WHEN** user calls `client.convert.run(url="https://example.com/doc.pdf", document_type_code="invoice")`
- **THEN** the SDK sends the URL to the API for server-side download

### Requirement: Asynchronous document conversion
The SDK SHALL provide a `convert.run_async()` method that initiates conversion via `/api/convert-async` and returns a conversion ID for polling.

#### Scenario: Start async conversion
- **WHEN** user calls `client.convert.run_async(file=Path("large.pdf"), document_type_code="invoice")`
- **THEN** the SDK returns a `ConversionStatus` with `conversion_id` and status `ENQUEUED`

### Requirement: Conversion status polling
The SDK SHALL provide a `convert.get_status()` method to check the status of an async conversion via `/api/convert-async/status/{id}`.

#### Scenario: Check pending conversion
- **WHEN** user calls `client.convert.get_status(conversion_id="abc123")` while processing
- **THEN** the SDK returns `ConversionStatus` with status `PROCESSING`

#### Scenario: Check completed conversion
- **WHEN** user calls `client.convert.get_status(conversion_id="abc123")` after completion
- **THEN** the SDK returns `ConversionStatus` with status `SUCCESS` and extracted `data`

#### Scenario: Check failed conversion
- **WHEN** user calls `client.convert.get_status(conversion_id="abc123")` after failure
- **THEN** the SDK returns `ConversionStatus` with status `ERROR` and error message

### Requirement: Async client conversion methods
The SDK SHALL provide `AsyncConvert` class with async versions of all convert methods accessible via `AsyncClient.convert`.

#### Scenario: Async convert with await
- **WHEN** user calls `await async_client.convert.run(file=path, document_type_code="invoice")`
- **THEN** the SDK performs async HTTP request and returns `ConversionResult`

### Requirement: Document metadata support
The SDK SHALL allow passing optional `document_metadata` dict to conversion methods.

#### Scenario: Convert with metadata
- **WHEN** user calls `client.convert.run(file=path, document_type_code="invoice", document_metadata={"customer_id": "123"})`
- **THEN** the SDK includes metadata in the API request
