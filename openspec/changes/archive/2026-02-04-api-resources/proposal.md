## Why

The SDK has completed core infrastructure (Phase 1) and robustness features (Phase 2), but lacks the API resource layer that enables developers to interact with DocuTray API endpoints. Without this, the SDK cannot be used for its primary purpose: document processing via OCR, identification, and extraction.

This phase is critical to deliver a functional SDK following the Stainless-like pattern (stripe-python, openai-python) with intuitive `client.resource.method()` syntax.

## What Changes

- Add typed resource classes for all DocuTray API endpoints
- Implement both sync and async versions of each resource
- Add Pydantic models for all API responses
- Add TypedDict definitions for request parameters
- Support multiple file input formats (Path, bytes, BinaryIO, URL, base64)
- Add polling helpers for async operations with configurable timeout
- Integrate resources into Client and AsyncClient via cached_property

## Capabilities

### New Capabilities

- `convert-resource`: Document conversion (OCR/extraction) with sync, async, and status polling
- `identify-resource`: Document type identification with confidence scores
- `document-types-resource`: Document type catalog listing, retrieval, and JSON validation
- `steps-resource`: Step-based document processing execution
- `file-handling`: Unified file input handling for multipart, base64, and URL uploads
- `async-polling`: Polling helpers with configurable interval and timeout for async operations

### Modified Capabilities

(none - this is new functionality)

## Impact

**Code Changes:**
- `src/docutray/_client.py`: Add resource properties to Client and AsyncClient
- `src/docutray/_base_client.py`: Add `_request()` method for resources
- `src/docutray/resources/`: New resource modules (convert.py, identify.py, document_types.py, steps.py)
- `src/docutray/types/`: New Pydantic response models
- `src/docutray/_types.py`: TypedDict definitions for request params
- `src/docutray/__init__.py`: Export new public types

**API Surface:**
- New public classes: Convert, AsyncConvert, Identify, AsyncIdentify, DocumentTypes, AsyncDocumentTypes, Steps, AsyncSteps
- New public types: ConversionResult, ConversionStatus, IdentificationResult, DocumentType, ValidationResult, StepExecutionStatus

**Dependencies:**
- No new dependencies (uses existing httpx, pydantic)
