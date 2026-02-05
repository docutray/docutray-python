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
