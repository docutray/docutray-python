# DocuTray SDK Examples

This directory contains examples demonstrating how to use the docutray Python SDK.

## Setup

1. Install dependencies (uses the development version of docutray):

```bash
uv sync
```

2. Configure your API key:

```bash
cp .env.example .env
# Edit .env and add your DOCUTRAY_API_KEY
```

3. Run an example:

```bash
uv run python basic_usage.py
```

## Development Mode

The examples environment installs `docutray` in editable mode from the parent directory. Any changes to `src/docutray/` are immediately available without reinstalling.

## Examples

| File | Description |
|------|-------------|
| `basic_usage.py` | Basic client initialization and document types listing |
| `identify_document.py` | Identify document type with confidence scores |
| `convert_document.py` | Convert document and extract structured data |
