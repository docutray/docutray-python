## Context

The docutray-python SDK (v0.1.0) has complete functionality across 6 phases: core infrastructure, error handling, resources, type safety, advanced features (pagination, raw response, polling), and testing. However, the README is minimal (~50 lines) without usage examples, no CHANGELOG exists, docstrings are incomplete, and there's no API reference generation.

Current state:
- README: Basic installation and feature list only
- pyproject.toml: Missing Bug Tracker URL and docs dependencies
- Docstrings: Vary in completeness across modules
- API docs: None generated

## Goals / Non-Goals

**Goals:**
- README comprehensive enough for developers to use the SDK without reading source code
- CHANGELOG following Keep a Changelog format for version tracking
- All public APIs have Google-style docstrings with Args, Returns, Raises, Example sections
- Automated API reference generation to docs/api/ in Markdown format
- PyPI-ready metadata with all URLs and optional dependencies

**Non-Goals:**
- Hosted documentation site (future work)
- Automated doc deployment (future work)
- Internationalization of documentation
- Video tutorials or interactive examples

## Decisions

### 1. API Reference Generator: griffe over sphinx/pydoc

**Decision**: Use griffe library for API reference generation

**Alternatives considered**:
- sphinx-autodoc: Full-featured but heavyweight, requires RST, complex setup
- pydoc: Built-in but limited formatting, no Markdown output
- pdoc: Good but less active maintenance

**Rationale**: griffe is modern, AST-based, outputs clean data structures that can be transformed to Markdown. It's designed for static analysis and works well with type hints and Google-style docstrings. Lightweight with no complex dependencies.

### 2. README Structure: stripe-python pattern

**Decision**: Follow stripe-python/openai-python README structure

**Rationale**: Proven pattern for API client SDKs. Developers familiar with these popular libraries will find docutray intuitive. Structure: badges → description → installation → quick start → configuration → error handling → resources → advanced features → contributing.

### 3. Docstring Format: Google style with examples

**Decision**: Google-style docstrings with mandatory Example section for public methods

**Alternatives considered**:
- NumPy style: More verbose, better for scientific libraries
- Sphinx/RST style: Harder to read in source code

**Rationale**: Google style balances readability with completeness. griffe has excellent Google-style parsing. Examples are critical for SDK usability.

### 4. Generated Docs Location: docs/api/

**Decision**: Generate Markdown to `docs/api/` directory

**Rationale**: Keeps generated docs separate from hand-written docs. Compatible with Fumadocs (planned docs site). Can be git-ignored or committed based on preference.

### 5. Docs Dependencies: Optional group

**Decision**: Add `[project.optional-dependencies] docs = ["griffe>=1.0"]`

**Rationale**: Docs generation is not needed by SDK users, only maintainers. Keeps core dependencies minimal.

## Risks / Trade-offs

**Risk**: Docstring examples become stale as API evolves
→ **Mitigation**: Add doctest-style validation in CI (future enhancement)

**Risk**: Generated docs may have formatting issues with complex type hints
→ **Mitigation**: Test generator output thoroughly; use simple type representations where needed

**Risk**: README examples may not match actual API
→ **Mitigation**: Examples should be syntactically valid Python; run basic validation

**Trade-off**: Comprehensive docstrings increase code file size
→ Acceptable for an SDK where documentation is critical

**Trade-off**: griffe is a dev-only dependency
→ Acceptable; adds ~1MB to dev environment, zero runtime impact
