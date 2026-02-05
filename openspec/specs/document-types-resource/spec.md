# Document Types Resource

## Purpose

Provides access to document type definitions, schemas, and validation capabilities for the DocuTray API.

## Requirements

### Requirement: List document types
The SDK SHALL provide a `document_types.list()` method that retrieves available document types from `/api/document-types` and returns a `Page[DocumentType]` with automatic pagination support.

#### Scenario: List all document types
- **WHEN** user calls `client.document_types.list()`
- **THEN** the SDK returns a `Page[DocumentType]` with `data`, pagination info, and iteration methods

#### Scenario: List with pagination
- **WHEN** user calls `client.document_types.list(page=2, limit=10)`
- **THEN** the SDK returns the second page with 10 items as `Page[DocumentType]`

#### Scenario: Search document types
- **WHEN** user calls `client.document_types.list(search="invoice")`
- **THEN** the SDK returns `Page[DocumentType]` with document types matching the search term

#### Scenario: Iterate all document types
- **WHEN** user calls `for doc_type in client.document_types.list().auto_paging_iter()`
- **THEN** the SDK yields all document types across all pages

### Requirement: Get document type by ID
The SDK SHALL provide a `document_types.get()` method that retrieves a specific document type from `/api/document-types/{id}`.

#### Scenario: Get existing document type
- **WHEN** user calls `client.document_types.get(type_id="dt_123")`
- **THEN** the SDK returns the `DocumentType` with full details including schema

#### Scenario: Get non-existent document type
- **WHEN** user calls `client.document_types.get(type_id="invalid")`
- **THEN** the SDK raises `NotFoundError`

### Requirement: Validate JSON data against document type
The SDK SHALL provide a `document_types.validate()` method that validates JSON data against a document type's schema via `/api/document-types/{id}/validate`.

#### Scenario: Validate valid data
- **WHEN** user calls `client.document_types.validate(type_id="dt_123", data={"invoice_number": "INV-001", "total": 100})`
- **THEN** the SDK returns `ValidationResult` with zero errors

#### Scenario: Validate invalid data
- **WHEN** user calls `client.document_types.validate(type_id="dt_123", data={"total": "not-a-number"})`
- **THEN** the SDK returns `ValidationResult` with errors listing validation failures

### Requirement: Async client document types methods
The SDK SHALL provide `AsyncDocumentTypes` class with async versions accessible via `AsyncClient.document_types`.

#### Scenario: Async list document types
- **WHEN** user calls `await async_client.document_types.list()`
- **THEN** the SDK performs async HTTP request and returns list of `DocumentType`

### Requirement: Raw response access for document types
The SDK SHALL provide `with_raw_response` property on `DocumentTypes` resource.

#### Scenario: Get raw response from list
- **WHEN** user calls `client.document_types.with_raw_response.list()`
- **THEN** SDK returns `RawResponse` with HTTP details

#### Scenario: Get raw response from get
- **WHEN** user calls `client.document_types.with_raw_response.get(type_id="dt_123")`
- **THEN** SDK returns `RawResponse` with HTTP details

#### Scenario: Get raw response from validate
- **WHEN** user calls `client.document_types.with_raw_response.validate(type_id="dt_123", data={...})`
- **THEN** SDK returns `RawResponse` with HTTP details
