## ADDED Requirements

### Requirement: Authorization header

The HTTP transport SHALL include an Authorization header with Bearer token.

#### Scenario: Authorization header format
- **WHEN** any HTTP request is made
- **THEN** the request includes header `Authorization: Bearer {api_key}`

### Requirement: User-Agent header

The HTTP transport SHALL include a User-Agent header identifying the SDK.

#### Scenario: User-Agent format
- **WHEN** any HTTP request is made
- **THEN** the request includes header `User-Agent: docutray-python/{version}`
- **AND** `{version}` matches the SDK version from `_version.py`

### Requirement: Content-Type header for JSON

The HTTP transport SHALL set Content-Type header for requests with JSON body.

#### Scenario: JSON Content-Type
- **WHEN** a request with JSON body is made
- **THEN** the request includes header `Content-Type: application/json`

### Requirement: Accept header

The HTTP transport SHALL include Accept header for JSON responses.

#### Scenario: Accept JSON
- **WHEN** any HTTP request is made
- **THEN** the request includes header `Accept: application/json`

### Requirement: Timeout enforcement

The HTTP transport SHALL enforce the configured timeout on all requests.

#### Scenario: Request timeout
- **WHEN** a request exceeds the configured timeout
- **THEN** the request is aborted
- **AND** an appropriate timeout exception is raised

### Requirement: Connection pooling

The HTTP transport SHALL use connection pooling for efficiency.

#### Scenario: Connection reuse
- **WHEN** multiple requests are made to the same host
- **THEN** connections are reused from the pool when available
