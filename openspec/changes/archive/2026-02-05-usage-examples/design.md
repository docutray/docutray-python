## Context

The `examples/` directory already contains scripts but they make multiple API calls per file (sync, URL, async variants in each script) and use a uv project scaffold. This change simplifies them: one call per script, pip-based install, and clear billing warnings.

Existing files to rewrite:
- `identify_document.py` (currently 3 API calls → 1)
- `convert_document.py` (currently 3 API calls → 1)
- `execute_steps.py` (currently 3 API calls → 1)
- `README.md` (currently references uv sync → pip install)
- `.env.example` (keep as-is)
- `sample_invoice.pdf` (keep as-is)

Already removed:
- `basic_usage.py` (only listed types, no real SDK usage)
- `pyproject.toml`, `uv.lock`, `.venv/` (project scaffold)

## Goals / Non-Goals

**Goals:**
- Each script demonstrates one SDK capability with one API call
- Clear billing awareness in docstrings and README
- Simple setup: `pip install docutray python-dotenv`
- Consistent script structure across all examples

**Non-Goals:**
- Async examples (keep sync-only for simplicity)
- Error handling patterns (keep examples minimal)
- Integration testing via examples

## Decisions

### 1. One API call per script

**Decision**: Each script makes exactly one API call using the sync interface.

**Rationale**: Users pay per API call. Running examples should not surprise users with unexpected charges. Each script demonstrates one concept clearly.

### 2. Consistent script structure

**Decision**: Every script follows this pattern:

```python
"""Description of what this example does.

NOTE: Running this script makes an API call that consumes credits
from your DocuTray account.

Usage:
    python <script_name>.py
"""

import ...
from dotenv import load_dotenv
import docutray

load_dotenv()

api_key = os.getenv("DOCUTRAY_API_KEY")
if not api_key:
    print("Error: DOCUTRAY_API_KEY not set. Copy .env.example to .env and add your key.")
    exit(1)

client = docutray.Client(api_key=api_key)

# Single API call
result = client.<resource>.<method>(...)

# Display results
print(...)
```

### 3. Input mode per example

**Decision**:
- `identify_document.py`: file input (`sample_invoice.pdf`)
- `convert_document.py`: file input (`sample_invoice.pdf`)
- `execute_steps.py`: URL input (public sample URL)

**Rationale**: This covers both input modes across the examples without duplicating calls.

### 4. pip install instead of project scaffold

**Decision**: Remove `pyproject.toml`, `uv.lock`, `.venv`. README documents `pip install docutray python-dotenv`.

**Rationale**: Lower barrier to entry. Users don't need to understand uv to run examples.
