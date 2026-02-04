## 1. Project Configuration

- [x] 1.1 Add production dependencies to pyproject.toml (httpx, pydantic, typing-extensions)
- [x] 1.2 Add development dependencies to pyproject.toml (pytest, pytest-asyncio, mypy, ruff)
- [x] 1.3 Configure ruff in pyproject.toml (linting rules, line length)
- [x] 1.4 Configure mypy in pyproject.toml (strict mode)
- [x] 1.5 Configure pytest in pyproject.toml (asyncio mode)
- [x] 1.6 Run uv sync to install all dependencies

## 2. Core Modules

- [x] 2.1 Create _version.py with __version__ = "0.1.0"
- [x] 2.2 Create _constants.py with DEFAULT_TIMEOUT, DEFAULT_BASE_URL, ENV_VAR_API_KEY
- [x] 2.3 Create _types.py with ClientOptions TypedDict

## 3. Exceptions Layer

- [x] 3.1 Create _exceptions.py with base DocuTrayError class
- [x] 3.2 Add AuthenticationError subclass
- [x] 3.3 Add APIConnectionError subclass
- [x] 3.4 Add APITimeoutError subclass (inherits from APIConnectionError)

## 4. Utilities

- [x] 4.1 Create _utils.py with get_api_key_from_env() function
- [x] 4.2 Add mask_api_key() function for safe repr

## 5. HTTP Layer

- [x] 5.1 Create _http.py with SyncHTTPClient class wrapping httpx.Client
- [x] 5.2 Add AsyncHTTPClient class wrapping httpx.AsyncClient
- [x] 5.3 Implement header building (Authorization, User-Agent, Content-Type, Accept)
- [x] 5.4 Implement timeout configuration

## 6. Client Layer

- [x] 6.1 Create _base_client.py with BaseClient abstract class
- [x] 6.2 Add BaseAsyncClient abstract class
- [x] 6.3 Implement config handling (api_key resolution, base_url, timeout)
- [x] 6.4 Implement safe __repr__ that hides credentials
- [x] 6.5 Create _client.py with Client class implementing context manager
- [x] 6.6 Add AsyncClient class implementing async context manager

## 7. Package Exports

- [x] 7.1 Update __init__.py with public exports (Client, AsyncClient, DocuTrayError, exceptions)
- [x] 7.2 Create resources/__init__.py placeholder
- [x] 7.3 Create types/__init__.py placeholder

## 8. Tests

- [x] 8.1 Create tests/ directory structure
- [x] 8.2 Write tests for Client instantiation (explicit key, env var, missing key)
- [x] 8.3 Write tests for AsyncClient instantiation
- [x] 8.4 Write tests for context managers (sync and async)
- [x] 8.5 Write tests for configuration (base_url, timeout)
- [x] 8.6 Write tests for safe repr (credential masking)

## 9. Validation

- [x] 9.1 Run mypy and fix any type errors
- [x] 9.2 Run ruff and fix any linting issues
- [x] 9.3 Run pytest and ensure all tests pass
