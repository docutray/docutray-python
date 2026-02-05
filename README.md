# DocuTray Python Library

[![PyPI version](https://img.shields.io/pypi/v/docutray.svg)](https://pypi.org/project/docutray/)
[![Python versions](https://img.shields.io/pypi/pyversions/docutray.svg)](https://pypi.org/project/docutray/)
[![License](https://img.shields.io/pypi/l/docutray.svg)](https://github.com/docutray/docutray-python/blob/main/LICENSE)

The official Python library for the [DocuTray API](https://docutray.com), providing access to document processing capabilities including OCR, document identification, data extraction, and knowledge bases.

## Documentation

Full API documentation is available at [docs.docutray.com](https://docs.docutray.com).

## Installation

```bash
pip install docutray
```

For API reference generation tools (maintainers only):

```bash
pip install docutray[docs]
```

### Requirements

- Python 3.10+

## Quick Start

### Synchronous Usage

```python
from pathlib import Path
from docutray import Client

client = Client(api_key="your-api-key")

# Convert a document
result = client.convert.run(
    file=Path("invoice.pdf"),
    document_type_code="invoice"
)
print(result.data)

client.close()
```

### Asynchronous Usage

```python
import asyncio
from pathlib import Path
from docutray import AsyncClient

async def main():
    async with AsyncClient(api_key="your-api-key") as client:
        result = await client.convert.run(
            file=Path("invoice.pdf"),
            document_type_code="invoice"
        )
        print(result.data)

asyncio.run(main())
```

## Configuration

### API Key

Set your API key via constructor argument or environment variable:

```python
# Via constructor
client = Client(api_key="your-api-key")

# Via environment variable
# export DOCUTRAY_API_KEY="your-api-key"
client = Client()  # Reads from DOCUTRAY_API_KEY
```

### Base URL

Override the default API endpoint:

```python
client = Client(
    api_key="your-api-key",
    base_url="https://custom-api.example.com"
)
```

### Timeout

Configure request timeouts (in seconds):

```python
import httpx

# Simple timeout (applies to all operations)
client = Client(api_key="your-api-key", timeout=30.0)

# Granular timeout control
client = Client(
    api_key="your-api-key",
    timeout=httpx.Timeout(
        connect=5.0,
        read=60.0,
        write=60.0,
        pool=10.0
    )
)
```

### Retries

Configure automatic retry behavior:

```python
# Default: 2 retries with exponential backoff
client = Client(api_key="your-api-key")

# Custom retry count
client = Client(api_key="your-api-key", max_retries=5)

# Disable retries
client = Client(api_key="your-api-key", max_retries=0)
```

## Error Handling

The SDK provides a comprehensive exception hierarchy:

```
DocuTrayError (base)
├── APIConnectionError (network errors)
│   └── APITimeoutError (request timeout)
└── APIError (HTTP errors)
    ├── BadRequestError (400)
    ├── AuthenticationError (401)
    ├── PermissionDeniedError (403)
    ├── NotFoundError (404)
    ├── ConflictError (409)
    ├── UnprocessableEntityError (422)
    ├── RateLimitError (429)
    └── InternalServerError (5xx)
```

### Catching Errors

```python
from pathlib import Path
from docutray import Client
from docutray import (
    DocuTrayError,
    APIConnectionError,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
)

client = Client(api_key="your-api-key")

try:
    result = client.convert.run(
        file=Path("document.pdf"),
        document_type_code="invoice"
    )
except AuthenticationError as e:
    print(f"Invalid API key: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NotFoundError as e:
    print(f"Resource not found: {e.message}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
    print(f"Request ID: {e.request_id}")
except APIConnectionError as e:
    print(f"Connection failed: {e.message}")
except DocuTrayError as e:
    print(f"SDK error: {e.message}")
```

### Rate Limit Handling

```python
import time
from pathlib import Path
from docutray import Client, RateLimitError

client = Client(api_key="your-api-key")

try:
    result = client.convert.run(file=Path("document.pdf"), document_type_code="invoice")
except RateLimitError as e:
    if e.retry_after:
        print(f"Rate limited. Waiting {e.retry_after} seconds...")
        time.sleep(e.retry_after)
        # Retry the request
```

## Resources

### Convert

Convert documents to structured data using OCR and AI extraction.

```python
from pathlib import Path

# Synchronous conversion (waits for result)
result = client.convert.run(
    file=Path("invoice.pdf"),
    document_type_code="invoice"
)
print(result.data)

# From bytes
with open("invoice.pdf", "rb") as f:
    result = client.convert.run(
        file=f.read(),
        document_type_code="invoice"
    )

# From URL
result = client.convert.run(
    url="https://example.com/invoice.pdf",
    document_type_code="invoice"
)

# Asynchronous conversion (returns immediately)
status = client.convert.run_async(
    file=Path("large_document.pdf"),
    document_type_code="invoice"
)
print(f"Conversion ID: {status.conversion_id}")

# Poll for completion
final_status = status.wait()
if final_status.is_success():
    print(final_status.data)
```

### Identify

Automatically identify document types.

```python
result = client.identify.run(file=Path("unknown_document.pdf"))

print(f"Identified as: {result.document_type.name}")
print(f"Confidence: {result.document_type.confidence:.2%}")

# View alternatives
for alt in result.alternatives:
    print(f"  Alternative: {alt.name} ({alt.confidence:.2%})")
```

### Document Types

List and retrieve document type definitions.

```python
# List all document types
page = client.document_types.list()
for doc_type in page.data:
    print(f"{doc_type.code}: {doc_type.name}")

# Search document types
page = client.document_types.list(search="invoice")

# Get a specific document type
doc_type = client.document_types.get("dt_invoice")
print(f"Schema: {doc_type.schema_}")

# Validate data against a document type schema
validation = client.document_types.validate(
    "dt_invoice",
    {"invoice_number": "INV-001", "total": 100.00}
)
if validation.is_valid():
    print("Data is valid!")
else:
    for error in validation.errors.messages:
        print(f"Validation error: {error}")
```

### Steps

Execute predefined document processing workflows.

```python
# Start async step execution
status = client.steps.run_async(
    step_id="step_invoice_extraction",
    file=Path("invoice.pdf")
)

# Wait for completion with progress callback
def on_progress(s):
    print(f"Status: {s.status}")

final = status.wait(on_status=on_progress)
print(final.data)
```

### Knowledge Bases

Manage document collections with semantic search capabilities.

```python
# List knowledge bases
for kb in client.knowledge_bases.list().auto_paging_iter():
    print(f"{kb.name}: {kb.document_count} documents")

# Create a knowledge base
kb = client.knowledge_bases.create(
    name="Product Documentation",
    description="Technical documentation for products",
    schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"},
            "category": {"type": "string"}
        }
    }
)

# Add documents
doc = client.knowledge_bases.documents(kb.id).create(
    content={
        "title": "Getting Started",
        "content": "Welcome to our product...",
        "category": "guides"
    },
    metadata={"source": "manual"}
)

# Semantic search
results = client.knowledge_bases.search(
    kb.id,
    query="how to configure authentication",
    limit=5
)
for item in results.data:
    print(f"{item.similarity:.2%}: {item.document.content['title']}")

# Update a document
client.knowledge_bases.documents(kb.id).update(
    doc.id,
    content={"title": "Updated Title", "content": "..."}
)

# Delete a document
client.knowledge_bases.documents(kb.id).delete(doc.id)

# Delete knowledge base
client.knowledge_bases.delete(kb.id)
```

## Pagination

Resources that return lists support pagination:

```python
# Get the first page
page = client.document_types.list(limit=10)
print(f"Page {page.page} of {page.total_pages}")

# Iterate through all pages manually
for page in client.document_types.list().iter_pages():
    for doc_type in page.data:
        print(doc_type.name)

# Auto-iterate through all items
for doc_type in client.document_types.list().auto_paging_iter():
    print(doc_type.name)

# Async pagination (inside an async function)
# async for doc_type in (await client.document_types.list()).auto_paging_iter_async():
#     print(doc_type.name)
```

## Raw Response Access

Access raw HTTP response data for debugging:

```python
from pathlib import Path
from docutray import Client

client = Client(api_key="your-api-key")

response = client.convert.with_raw_response.run(
    file=Path("invoice.pdf"),
    document_type_code="invoice"
)

print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Request ID: {response.headers.get('x-request-id')}")

# Parse the response body
result = response.parse()
print(result.data)
```

## Async Operations

For long-running operations, use async methods with polling:

```python
from pathlib import Path
from docutray import Client

client = Client(api_key="your-api-key")

# Start async conversion
status = client.convert.run_async(
    file=Path("large_document.pdf"),
    document_type_code="invoice"
)

# Poll with progress callback
def on_status(s):
    print(f"Status: {s.status}, Progress: {s.progress or 'N/A'}")

final = status.wait(
    on_status=on_status,
    poll_interval=2.0,  # seconds between polls
    timeout=300.0       # maximum wait time
)

if final.is_success():
    print("Conversion complete!")
    print(final.data)
elif final.is_failed():
    print(f"Conversion failed: {final.error}")
```

## Type Safety

The SDK uses Pydantic models for all responses, providing full type safety:

```python
from pathlib import Path
from docutray import Client
from docutray.types import ConversionResult, DocumentType

client = Client(api_key="your-api-key")

# Type hints work with your IDE
result: ConversionResult = client.convert.run(
    file=Path("invoice.pdf"),
    document_type_code="invoice"
)

# Access typed attributes
print(result.conversion_id)  # str
print(result.data)           # dict[str, Any]
print(result.status)         # str
```

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/docutray/docutray-python.git
cd docutray-python

# Install dependencies with uv
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/docutray

# Type checking
uv run mypy src

# Linting
uv run ruff check src

# Format code
uv run ruff format src
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_client.py

# Specific test
uv run pytest tests/test_client.py::test_client_initialization
```

## Support

- [Documentation](https://docs.docutray.com)
- [API Reference](https://docs.docutray.com/api)
- [Issue Tracker](https://github.com/docutray/docutray-python/issues)

## License

MIT
