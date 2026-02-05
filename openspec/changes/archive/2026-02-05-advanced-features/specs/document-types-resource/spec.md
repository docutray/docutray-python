## MODIFIED Requirements

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

## ADDED Requirements

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
