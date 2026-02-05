## 1. PyPI Preparation

- [x] 1.1 Add Bug Tracker URL to pyproject.toml project.urls
- [x] 1.2 Add docs optional-dependencies group with griffe>=1.0

## 2. CHANGELOG

- [x] 2.1 Create CHANGELOG.md with Keep a Changelog format
- [x] 2.2 Document 0.1.0 release notes covering all phases 1-6

## 3. Docstring Audit

- [x] 3.1 Audit and enhance _client.py docstrings (Client, AsyncClient classes)
- [x] 3.2 Audit and enhance _exceptions.py docstrings (all exception classes)
- [x] 3.3 Audit and enhance resources/convert.py docstrings
- [x] 3.4 Audit and enhance resources/identify.py docstrings
- [x] 3.5 Audit and enhance resources/document_types.py docstrings
- [x] 3.6 Audit and enhance resources/steps.py docstrings
- [x] 3.7 Audit and enhance resources/knowledge_bases.py docstrings
- [x] 3.8 Audit and enhance types/*.py docstrings

## 4. README Enhancement

- [x] 4.1 Write installation section with pip and optional dependencies
- [x] 4.2 Write quick start section with sync example
- [x] 4.3 Write quick start section with async example
- [x] 4.4 Write configuration section (API key, base URL, timeout, retries)
- [x] 4.5 Write error handling section with exception hierarchy and examples
- [x] 4.6 Write convert resource examples (file and bytes)
- [x] 4.7 Write identify resource examples
- [x] 4.8 Write document_types resource examples (list, retrieve)
- [x] 4.9 Write steps resource examples (list, retrieve)
- [x] 4.10 Write knowledge_bases resource examples (CRUD and search)
- [x] 4.11 Write pagination section (iter_pages, auto_paging_iter)
- [x] 4.12 Write raw response access section (with_raw_response)
- [x] 4.13 Write async operations section with polling callbacks
- [x] 4.14 Write contributing section with dev setup and testing

## 5. API Reference Generator

- [x] 5.1 Create scripts/gen_api_ref.py using griffe
- [x] 5.2 Implement module parsing for public API extraction
- [x] 5.3 Implement Markdown generation for classes and methods
- [x] 5.4 Generate docs/api/index.md with module overview
- [x] 5.5 Generate docs/api/client.md documenting Client and AsyncClient
- [x] 5.6 Generate docs/api/exceptions.md documenting exception hierarchy
- [x] 5.7 Generate docs/api/resources/*.md for each resource module
- [x] 5.8 Generate docs/api/types/*.md for type definitions

## 6. Validation

- [x] 6.1 Run mypy to verify docstrings don't break type hints
- [x] 6.2 Run ruff to verify code style compliance
- [x] 6.3 Run API reference generator and verify output
- [x] 6.4 Verify README examples are syntactically correct
