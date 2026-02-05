## Why

SDK users need practical, runnable examples to understand how to use the library. The `examples/` directory provides self-contained scripts demonstrating each SDK capability with clear warnings about API usage and billing implications.

## What Changes

- Simplify `examples/` setup: use `pip install docutray` (no project scaffold)
- Rewrite examples to follow best practices:
  - One API call per example (avoid multiple charges)
  - Each script demonstrates one specific mode of usage
  - Clear warnings that each execution consumes API credits from the associated account
- Update `README.md` with `pip install docutray` setup and billing notice
- Keep `.env.example` for API key configuration
- Keep `sample_invoice.pdf` as test document

### Example scripts:
- `basic_usage.py`: Client initialization and document type listing (no billing impact)
- `identify_document.py`: Identify document type from a file (single API call)
- `convert_document.py`: Convert document and extract data (single API call)
- `execute_steps.py`: Execute a predefined step (single API call)

## Capabilities

### New Capabilities

- `usage-examples`: Runnable example scripts demonstrating SDK features with minimal API calls and billing awareness

### Modified Capabilities

<!-- None -->

## Impact

- **Files**: `examples/` directory (not part of the published package)
- **Dependencies**: `docutray` and `python-dotenv` via pip
- **Package**: No impact on published SDK
