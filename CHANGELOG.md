# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- DSL validation rules on document types ([docutray/docutray#1111](https://github.com/docutray/docutray/issues/1111), #22):
  - `DocumentType.dslRules`, and `dsl_rules` on `client.document_types.create()` / `update()`. In `update()`, omitting `dsl_rules` keeps the saved rules and `None` or `""` clears them.
  - `client.document_types.validate(id, data, dsl_rules=...)` dry run: temporary rules replace the saved ones for that call only.
  - `DSLValidationError` (subclass of `BadRequestError`) with typed `diagnostics` (`DSLDiagnostic`: `line`, `column`, `message`) for invalid DSL.
- Structured validation results:
  - `ValidationResult.valid` and `ValidationResult.issues` (`list[ValidationIssue]`).
  - `ConversionResult.validation` and `ConversionStatus.validation`, typed as `ConversionValidation` (`ValidationOutcome | ValidationSystemFailure | dict | None`). Shapes this SDK version does not recognize stay a plain `dict` instead of failing to parse.
  - `StepExecutionStatus.validation` typed as `StepValidationSummary`. The API wire format is unchanged, but the Python attribute is now a model instead of a dict (see **Changed**).
- Webhook payload models: `ConversionWebhookPayload` (with `validation`), `IdentificationWebhookPayload`, `StepWebhookPayload` and the `WebhookEventType` literal.
- `field_locations` (`FieldLocations`) on `ConversionResult` / `ConversionStatus` for document types with bounding boxes enabled.
- Typed `DocumentType` fields `promptHints`, `identifyPromptHints`, `conversionMode`, `keepPropertyOrdering`, `boundingBoxesEnabled` and `conversionSpec`; `bounding_boxes_enabled` and `conversion_spec` arguments on `create()` / `update()` (`conversion_spec=None` clears the spec in `update()`).
- `NOT_GIVEN` / `NotGiven` sentinel for arguments where `None` has a meaning.
- API parameters and fields the SDK did not expose (#27):
  - `document_metadata` on `client.identify.run()` / `run_async()` (sync, async and raw).
  - `schema` and `indexing_preferences` on `client.knowledge_bases.update()`.
  - `force` and `sync_external_sources` on `client.knowledge_bases.sync()`.
  - `document_id` filter on `client.knowledge_bases.documents(kb_id).list()` (case-insensitive substring match, as the API applies it).
  - Typed `ConversionStatus.document_metadata`, `IdentificationStatus.document_type_code_options`, and `StepExecutionStatus.step_name`, `identification` (`StepIdentification`) and `document_metadata`. `StepWebhookPayload.identification` uses the same `StepIdentification` model.
  - `KnowledgeBaseDocument.documentId` typed as `str`: it is the ID that `documents(kb_id).get()` / `update()` / `delete()` take.
- CI workflow running ruff, mypy and pytest (Python 3.10 to 3.13) on pull requests and pushes to `main` (#25).

### Changed

- **Breaking:** `client.knowledge_bases.documents(kb_id).create()` now requires `document_id`. The API always rejected documents without it (400), so code that omitted it already failed at runtime; it now fails with `TypeError` before the request.
- `ValidationResult.is_valid()` without a `valid` flag only returns `True` when the API sent an error `count` of zero; an empty `errors` summary no longer reads as valid.
- `StepExecutionStatus.execution_id` is read from `execution_id` first, then `id` and the deprecated `conversion_id`, so it keeps working when the API drops `conversion_id`.
- `wait()` / `wait_async()` docstrings state that a failed operation is returned with `status == "ERROR"`, not raised.
- **Breaking:** `ConversionResult.validation`, `ConversionResult.field_locations`, `ConversionStatus.validation`, `ConversionStatus.field_locations` and `StepExecutionStatus.validation` used to be plain dicts (passed through by `extra="allow"`). They are now Pydantic models, so dict access such as `result.validation["valid"]` raises `TypeError`. To migrate, use attribute access (`result.validation.valid`, `result.field_locations.fields`, `status.validation.errors.count`) or call `.model_dump()` to get the previous dict. `result.validation` can be a `ValidationOutcome`, a `ValidationSystemFailure` (`status == "error"`), a `dict` (unrecognized shape) or `None`, so check its type before reading `.valid`.
- Validation models are lenient so off-spec values never break parsing of a conversion, status, document type or webhook: `ValidationIssue.field` accepts `None` and normalizes list paths (`["items", 0, "total"]` → `items[0].total`) and other non-string values to strings; `code` and `message` default to `""` and read `null` as `""`; `details` accepts any JSON value; `severity` and `source` keep unknown values as plain strings; `ValidationOutcome.errors`/`warnings` and `StepValidationSummary.errors`/`warnings` (including `count`/`messages`) default to empty; `DocumentType.conversionMode` keeps unknown modes as plain strings. One malformed issue no longer turns the whole `ValidationOutcome` into a `dict`.
- `DSLValidationError` is raised only when every entry of the 400 response's `errors` has an integer `line` and `column` and a string `message`. Any other 400 stays a plain `BadRequestError`.

### Fixed

- Docs: document types are fetched, updated and validated by internal `id`, not `codeType` (#21). The README resolves the id from the full (org-prefixed) `codeType` across all pages with `list().auto_paging_iter()`, and explains the camelCase model fields. The `type_id` docstrings say it is the internal id, examples use cuid-shaped ids, and the `search` docstring now says it matches name, `codeType` and description.
- README: knowledge base documents are fetched, updated and deleted by their `documentId` (given on create), not by `id`; the `document_id` docstrings say so.
- Docstrings quote API paths with `{id}` placeholders in backticks.
- API errors whose body is `{"error": "<message>"}` now use that message as `APIError.message` instead of the raw response text.

## [0.2.1] - 2026-05-07

### Fixed

- `client.document_types.get(id)` now correctly unwraps the `{ data }` envelope returned by `GET /api/document-types/{id}`. Previously every typed field (`id`, `name`, `codeType`, …) silently fell back to defaults because the actual fields were nested under `data`. Sync and async, including the `.with_raw_response.get()` variants. (Port of [docutray-node#20](https://github.com/docutray/docutray-node/pull/20).)

### Changed

- **Type-only breaking change:** renamed `DocumentType.schema_` to `DocumentType.jsonSchema` to match the API wire format. The previous name never received a value (the API returns `jsonSchema`), so no real consumer was reading the old attribute. Pre-1.0 patch releases are allowed to carry type-level breaking changes per project policy.

### Added

- `is_public: bool | None` keyword argument on `client.document_types.create()` and `client.document_types.update()` (sync, async, and raw response wrappers). Closes a gap from the [docutray-node#18](https://github.com/docutray/docutray-node/pull/18) port — the Node `DocumentTypeCreateParams` / `DocumentTypeUpdateParams` interfaces have always exposed `isPublic`.

## [0.2.0] - 2026-04-07

### Added

- `client.document_types.create()` method to create custom document types with JSON schemas
- `client.document_types.update()` method to update existing document types (partial update support)
- `ConversionMode` literal type for type-safe conversion mode parameter (`"json"`, `"toon"`, `"multi_prompt"`)
- `status` field on `DocumentType` model
- Sync and async support for both new methods
- Raw response wrappers (`.with_raw_response.create()` / `.with_raw_response.update()`)

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
