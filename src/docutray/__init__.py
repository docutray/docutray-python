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
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)
from ._version import __version__
from .types import (
    ConversionResult,
    ConversionStatus,
    DocumentType,
    DocumentTypeMatch,
    IdentificationResult,
    IdentificationStatus,
    Pagination,
    StepExecutionStatus,
    ValidationResult,
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
    "ConflictError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "UnprocessableEntityError",
    # Types - Conversion
    "ConversionResult",
    "ConversionStatus",
    # Types - Identification
    "IdentificationResult",
    "IdentificationStatus",
    "DocumentTypeMatch",
    # Types - Document Types
    "DocumentType",
    "ValidationResult",
    # Types - Steps
    "StepExecutionStatus",
    # Types - Shared
    "Pagination",
]
