# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

docutray-python is the official Python SDK for the DocuTray API, providing access to document processing capabilities including OCR, document identification, data extraction, and knowledge bases. The library follows patterns from stripe-python and openai-python.

### Optional Dependencies
- `pip install docutray[docs]` - Includes griffe for API reference generation

## Language Policy

All repository artifacts must be written in **English**, including:
- Pull request titles and descriptions
- Commit messages
- Code comments and docstrings
- GitHub issues
- Documentation files

This applies even when communicating with Claude Code in Spanish or any other language.

## Conventions

- Always run `git` commands directly (e.g., `git status`), never with `-C` path flag (e.g., `git -C /path status`). The working directory is always the project root.

## Development Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name

# Run tests with coverage
uv run pytest --cov=src/docutray

# Type checking
uv run mypy src

# Linting
uv run ruff check src

# Format code
uv run ruff format src

# Generate API reference docs (requires griffe)
uv run python scripts/gen_api_ref.py
```

## Architecture

The SDK follows a 3-layer architecture:

```
┌─────────────────────────────────────┐
│         Client Layer                │  ← Public interface (Client, AsyncClient)
│   (_client.py, _base_client.py)     │
├─────────────────────────────────────┤
│         HTTP Layer                  │  ← Transport with retry logic
│   (_http.py, _constants.py)         │
├─────────────────────────────────────┤
│       Exceptions Layer              │  ← Error mapping (status code → exception)
│   (_exceptions.py)                  │
└─────────────────────────────────────┘
```

### Key Components

- **`_client.py`**: Public `Client` and `AsyncClient` classes
- **`_base_client.py`**: Abstract base classes with shared initialization logic
- **`_http.py`**: HTTP transport with automatic retry, exponential backoff, and jitter
- **`_exceptions.py`**: Exception hierarchy mapping HTTP status codes to specific errors
- **`_constants.py`**: Configuration defaults including `RetryConfig` and `httpx.Timeout`
- **`_pagination.py`**: Generic `Page[T]` and `AsyncPage[T]` classes for paginated results
- **`_response.py`**: `RawResponse[T]` wrapper and `*WithRawResponse` classes for HTTP debugging
- **`_polling.py`**: Polling utilities with `on_status` callback support
- **`resources/`**: API resource classes (convert, identify, document_types, steps, knowledge_bases)
- **`types/`**: Pydantic models for API responses

### Exception Hierarchy

```
DocuTrayError (base)
├── APIConnectionError (network errors)
│   └── APITimeoutError
└── APIError (HTTP errors with status_code, request_id, body, headers)
    ├── BadRequestError (400)
    ├── AuthenticationError (401)
    ├── PermissionDeniedError (403)
    ├── NotFoundError (404)
    ├── ConflictError (409)
    ├── UnprocessableEntityError (422)
    ├── RateLimitError (429) - has retry_after property
    └── InternalServerError (5xx)
```

### Advanced Features

- **Pagination**: `Page[T]` and `AsyncPage[T]` with `iter_pages()`, `auto_paging_iter()` for automatic page traversal
- **Raw Response**: `.with_raw_response` on all resources returns `RawResponse` with `status_code`, `headers`, `parse()`
- **Polling Callbacks**: `status.wait(on_status=callback)` for progress tracking during async operations
- **Knowledge Bases**: Semantic search with `client.knowledge_bases.search(kb_id, query="...")` returning similarity scores

### API Configuration

- **Base URL**: `https://app.docutray.com` (configured in `_constants.py`)
- **Multipart uploads**: File uploads use `prepare_file_upload()` which returns an `UploadData` object with `files` and `content_type` fields
- **Field aliasing**: Pydantic models use `validation_alias=AliasChoices(...)` for API field mapping (e.g., API returns `id`, SDK exposes `identification_id`)

## Versioning and Publishing

### Version Management
- Version is defined in two files that must stay in sync:
  - `pyproject.toml`: `version = "X.Y.Z"`
  - `src/docutray/_version.py`: `__version__ = "X.Y.Z"`
- Follow [Semantic Versioning](https://semver.org/)

### Release Workflow
Publishing to PyPI is automated via `.github/workflows/publish.yml`:

```
git tag v0.1.0 → build → TestPyPI → PyPI
```

- **Trigger**: Push a `v*` tag (e.g., `v0.1.0`) or manual `workflow_dispatch`
- **Sequential flow**: TestPyPI must succeed before PyPI publishes
- **Version check**: Tag must match `pyproject.toml` version (skipped on manual trigger)
- **Authentication**: Trusted Publisher (OIDC) — no API tokens needed
- **TestPyPI**: Uses `skip-existing: true` for re-runs

### Release Steps
1. Update version in `pyproject.toml` and `src/docutray/_version.py`
2. Update `CHANGELOG.md`
3. Commit: `chore: bump version to X.Y.Z`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. Workflow publishes automatically: TestPyPI → PyPI

### Trusted Publisher Setup (one-time)
Both PyPI and TestPyPI must be configured with:
- Owner: `docutray`, Repository: `docutray-python`
- Workflow: `publish.yml`
- Environments: `pypi` and `testpypi`

## Examples

The `examples/` directory contains runnable scripts demonstrating SDK usage:
- Each script calls `main()` with a single sync API call (to avoid unnecessary charges)
- Alternative usage modes (URL, async) are provided as uncalled functions for reference
- Setup: `pip install docutray python-dotenv`, configure `.env` from `.env.example`

## Documentation

### Public Documentation
- **`README.md`**: Comprehensive SDK usage guide with examples for all features
- **`CHANGELOG.md`**: Version history following Keep a Changelog format
- **`docs/api/`**: Generated API reference (run `scripts/gen_api_ref.py` to regenerate)

### API Reference
- Main site: https://docutray.com
- API docs: https://docs.docutray.com

### Internal Documentation
The `/docs` directory contains internal design documents and research in Spanish:
- `ROADMAP.md` - Implementation phases and acceptance criteria
- `best-practices-pip-api-wrapper.md` - SDK design patterns from stripe/openai analysis
- `research-sdks-python.md` - Competitor SDK analysis

### Scripts
- **`scripts/gen_api_ref.py`**: Generates Markdown API docs from source docstrings using griffe

## OpenSpec Workflow

This project uses OpenSpec for structured change management:

- `/opsx:new` - Start a new change with artifact workflow
- `/opsx:continue` - Continue working on a change
- `/opsx:apply` - Implement tasks from a change
- `/opsx:verify` - Verify implementation before archiving

**Naming convention**: Use descriptive kebab-case names (e.g., `core-infrastructure`, `retry-logic`). Do NOT prefix with issue numbers.

Configuration: `openspec/config.yaml`
