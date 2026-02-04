## ADDED Requirements

### Requirement: Client instantiation with explicit API key

The `Client` class SHALL accept an `api_key` parameter for authentication.

#### Scenario: Create client with explicit API key
- **WHEN** `Client(api_key="sk_test_123")` is called
- **THEN** the client is created successfully with the provided API key

### Requirement: Client instantiation with environment variable

The `Client` class SHALL read the `DOCUTRAY_API_KEY` environment variable when no explicit API key is provided.

#### Scenario: Create client with environment variable
- **WHEN** `DOCUTRAY_API_KEY` environment variable is set to "sk_env_456"
- **AND** `Client()` is called without an api_key parameter
- **THEN** the client is created using the environment variable value

#### Scenario: Explicit API key takes precedence
- **WHEN** `DOCUTRAY_API_KEY` environment variable is set to "sk_env_456"
- **AND** `Client(api_key="sk_explicit_789")` is called
- **THEN** the client uses "sk_explicit_789" (explicit takes precedence)

### Requirement: Client requires API key

The `Client` class SHALL raise `DocuTrayError` when no API key is available.

#### Scenario: No API key provided
- **WHEN** no `api_key` parameter is provided
- **AND** `DOCUTRAY_API_KEY` environment variable is not set
- **THEN** `DocuTrayError` is raised with message indicating missing API key

### Requirement: AsyncClient has identical API

The `AsyncClient` class SHALL provide the same constructor API as `Client`.

#### Scenario: AsyncClient instantiation mirrors Client
- **WHEN** `AsyncClient(api_key="sk_test_123")` is called
- **THEN** the async client is created with the same behavior as sync Client

### Requirement: Client context manager support

The `Client` class SHALL implement context manager protocol for resource cleanup.

#### Scenario: Sync context manager
- **WHEN** `with Client(api_key="sk_test") as client:` is used
- **THEN** the client is properly initialized on enter
- **AND** resources are cleaned up on exit

### Requirement: AsyncClient context manager support

The `AsyncClient` class SHALL implement async context manager protocol.

#### Scenario: Async context manager
- **WHEN** `async with AsyncClient(api_key="sk_test") as client:` is used
- **THEN** the client is properly initialized on enter
- **AND** resources are cleaned up on exit

### Requirement: Configurable base URL

The `Client` and `AsyncClient` SHALL accept a `base_url` parameter with a sensible default.

#### Scenario: Default base URL
- **WHEN** `Client(api_key="sk_test")` is called without base_url
- **THEN** the client uses `https://api.docutray.com` as the base URL

#### Scenario: Custom base URL
- **WHEN** `Client(api_key="sk_test", base_url="https://custom.api.com")` is called
- **THEN** the client uses the provided custom base URL

### Requirement: Configurable timeout

The `Client` and `AsyncClient` SHALL accept a `timeout` parameter with a sensible default.

#### Scenario: Default timeout
- **WHEN** `Client(api_key="sk_test")` is called without timeout
- **THEN** the client uses a default timeout of 60 seconds

#### Scenario: Custom timeout
- **WHEN** `Client(api_key="sk_test", timeout=30.0)` is called
- **THEN** the client uses 30 seconds as the timeout

### Requirement: Safe repr hides credentials

The `Client` and `AsyncClient` SHALL NOT expose the API key in their string representation.

#### Scenario: API key hidden in repr
- **WHEN** `repr(Client(api_key="sk_secret_key"))` is called
- **THEN** the output does NOT contain "sk_secret_key"
- **AND** the output indicates an API key is configured (e.g., "api_key=sk_se***")
