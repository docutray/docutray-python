"""DocuTray Python SDK.

A Python library for the DocuTray API, providing access to document
processing capabilities including OCR, document identification, data
extraction, and knowledge bases.

Example:
    >>> from docutray import Client
    >>> from pathlib import Path
    >>>
    >>> client = Client(api_key="your_api_key")
    >>>
    >>> # Convert a document
    >>> result = client.convert.run(
    ...     file=Path("invoice.pdf"),
    ...     document_type_code="invoice"
    ... )
    >>> print(result.data)
    >>>
    >>> # Identify document type
    >>> ident = client.identify.run(file=Path("unknown.pdf"))
    >>> print(f"Type: {ident.document_type.name}")
"""

from ._client import AsyncClient, Client
from ._exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    DocuTrayError,
    DSLValidationError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)
from ._pagination import AsyncPage, Page
from ._response import RawResponse
from ._types import NOT_GIVEN, NotGiven
from ._version import __version__
from .types import (
    ConversionMode,
    ConversionResult,
    ConversionStatus,
    ConversionValidation,
    ConversionWebhookPayload,
    DocumentType,
    DocumentTypeMatch,
    DSLDiagnostic,
    IdentificationResult,
    IdentificationStatus,
    KnowledgeBase,
    KnowledgeBaseDocument,
    Pagination,
    SearchResult,
    SearchResultItem,
    StepExecutionStatus,
    SyncResult,
    ValidationIssue,
    ValidationOutcome,
    ValidationResult,
    ValidationSystemFailure,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "Client",
    "AsyncClient",
    # Base exceptions
    "DocuTrayError",
    "APIConnectionError",
    "APITimeoutError",
    # API error hierarchy
    "APIError",
    "AuthenticationError",
    "BadRequestError",
    "DSLValidationError",
    "ConflictError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "UnprocessableEntityError",
    # Pagination
    "Page",
    "AsyncPage",
    # Raw Response
    "RawResponse",
    # Sentinel
    "NOT_GIVEN",
    "NotGiven",
    # Types - Conversion
    "ConversionResult",
    "ConversionStatus",
    # Types - Identification
    "IdentificationResult",
    "IdentificationStatus",
    "DocumentTypeMatch",
    # Types - Document Types
    "ConversionMode",
    "DocumentType",
    "ValidationResult",
    # Types - Validation
    "ConversionValidation",
    "DSLDiagnostic",
    "ValidationIssue",
    "ValidationOutcome",
    "ValidationSystemFailure",
    # Types - Webhooks
    "ConversionWebhookPayload",
    # Types - Steps
    "StepExecutionStatus",
    # Types - Knowledge Bases
    "KnowledgeBase",
    "KnowledgeBaseDocument",
    "SearchResult",
    "SearchResultItem",
    "SyncResult",
    # Types - Shared
    "Pagination",
]
