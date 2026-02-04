## Why

The SDK currently only contains a placeholder `hello()` function. To provide a functional client for developers to interact with the DocuTray API, we need professional client structure following industry patterns (stripe-python, openai-python), with both sync and async support from the start.

## What Changes

- Add 3-layer architecture: Client Layer → HTTP Layer → Exceptions Layer
- Implement `Client` (sync) and `AsyncClient` classes with identical APIs
- Add httpx-based HTTP transport with auth and header configuration
- Create base exception hierarchy for error handling
- Configure production dependencies (httpx, pydantic, typing-extensions)
- Configure development tooling (pytest, mypy, ruff)

## Capabilities

### New Capabilities

- `client`: Sync and async client classes with API key authentication, configurable base URL, timeouts, and context manager support
- `http-transport`: httpx wrapper handling auth headers, User-Agent, connection pooling
- `exceptions`: Base `DocuTrayError` class and initial exception hierarchy for API errors

### Modified Capabilities

<!-- No existing capabilities to modify -->

## Impact

- **Code**: All files in `src/docutray_python/` - new modules for client, HTTP, exceptions, types, utils
- **Dependencies**: Add httpx, pydantic, typing-extensions to pyproject.toml
- **Dev Tools**: Add pytest, mypy, ruff configuration
- **API**: New public exports `Client`, `AsyncClient`, `DocuTrayError` from package root
