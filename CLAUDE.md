# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

docutray-python is the official Python library for the DocuTray API, providing access to document processing capabilities including OCR, document identification, data extraction, knowledge bases, and workflows.

## Development Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name

# Type checking
uv run mypy src

# Linting
uv run ruff check src

# Format code
uv run ruff format src
```

## Architecture

This is an API wrapper library following patterns similar to stripe-python. The package is published as `docutray` on PyPI.

- **Source code**: `src/docutray/`
- **Package is typed**: includes `py.typed` marker
- **Build system**: uv with uv_build backend
- **Python support**: 3.10+

## API Reference

- Main site: https://docutray.com
- API docs: https://docs.docutray.com

## Internal Documentation

The `/docs` directory contains internal design documents, research, and implementation roadmaps. These documents are in Spanish and serve as reference for architectural decisions and best practices. Consult them when planning new features or understanding design rationale.

## OpenSpec Workflow

This project uses OpenSpec for structured change management. Use the following commands:

- `/opsx:new` - Start a new change with artifact workflow
- `/opsx:continue` - Continue working on a change
- `/opsx:apply` - Implement tasks from a change
- `/opsx:verify` - Verify implementation before archiving

**Naming convention**: Use descriptive kebab-case names for changes (e.g., `core-infrastructure`, `retry-logic`). Do NOT prefix with issue numbers like `issue-1-` or `issue-X-`.

Configuration is in `openspec/config.yaml`.
