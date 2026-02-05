# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-05

### Added

#### Core Infrastructure
- `Client` and `AsyncClient` classes for synchronous and asynchronous API access
- Support for API key authentication via constructor or `DOCUTRAY_API_KEY` environment variable
- Configurable base URL, timeout, and retry settings
- Context manager support for automatic resource cleanup

#### HTTP Transport
- HTTP transport layer built on httpx with automatic retry logic
- Exponential backoff with jitter for failed requests
- Configurable timeout settings (connect, read, write, pool)
- Support for multipart file uploads, JSON requests, and URL-based documents

#### Exception Handling
- Complete exception hierarchy mapping HTTP status codes to specific errors
- `DocuTrayError` base class for all SDK errors
- `APIConnectionError` and `APITimeoutError` for network issues
- `APIError` base class for HTTP errors with `status_code`, `request_id`, `body`, and `headers`
- Specific exceptions: `BadRequestError` (400), `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `ConflictError` (409), `UnprocessableEntityError` (422), `RateLimitError` (429), `InternalServerError` (5xx)
- `RateLimitError.retry_after` property for rate limit handling

#### API Resources
- **Convert**: Document conversion with `run()` for sync and `run_async()` for async operations
- **Identify**: Document type identification with confidence scores and alternatives
- **DocumentTypes**: List and retrieve document type definitions with pagination
- **Steps**: Execute predefined document processing workflows
- **KnowledgeBases**: Full CRUD operations for knowledge bases, document management, and semantic search

#### Type Safety
- Full type hints compatible with mypy strict mode
- Pydantic v2 models for all API responses
- Generic `Page[T]` and `AsyncPage[T]` classes for paginated results
- Type-safe file input handling with `FileInput` type alias

#### Advanced Features
- **Pagination**: `iter_pages()` and `auto_paging_iter()` for automatic page traversal
- **Raw Response Access**: `.with_raw_response` property on all resources for HTTP debugging
- **Async Polling**: `wait()` method on status objects with `on_status` callback support
- **Knowledge Base Search**: Semantic search with similarity scores

#### Testing & Quality
- Comprehensive test suite with pytest and pytest-asyncio
- Mock-based testing with respx for HTTP mocking
- Pre-commit hooks for code quality enforcement
- Full test coverage for all public APIs

[Unreleased]: https://github.com/docutray/docutray-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/docutray/docutray-python/releases/tag/v0.1.0
