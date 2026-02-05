# DocuTray SDK Examples

Runnable examples demonstrating how to use the docutray Python SDK.

> **Note:** Each script makes a real API call that consumes credits from your DocuTray account. Review the code before running.

## Setup

1. Install dependencies:

```bash
pip install docutray python-dotenv
```

2. Configure your API key:

```bash
cp .env.example .env
# Edit .env and add your DOCUTRAY_API_KEY
```

3. Run an example:

```bash
python identify_document.py
```

## Examples

| File | Description | Input |
|------|-------------|-------|
| `identify_document.py` | Identify document type with confidence scores | File + URL |
| `convert_document.py` | Convert document and extract structured data | File + URL |
| `execute_steps.py` | Execute a predefined processing step | File + URL |
