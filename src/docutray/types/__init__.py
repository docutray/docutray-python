"""Public type definitions for the DocuTray SDK.

This module exports all public types used by the SDK, including:
- Response models (Pydantic BaseModel classes)
- Request parameter types (TypedDicts)
- Literal types for status enums and constants
- Type aliases for file inputs

Example:
    >>> from docutray.types import (
    ...     ConversionResult,
    ...     ConversionStatus,
    ...     ConversionStatusType,
    ...     DocumentType,
    ... )
"""

# Conversion types
# Re-export internal types for public access
from .._types import (
    # Request parameter types
    Base64UploadParams,
    ClientOptions,
    ConvertParams,
    DocumentTypesListParams,
    # File types
    FileInput,
    FileUploadParams,
    IdentifyParams,
    ImageContentType,
    # Rate limit types
    QuotaExceededInfo,
    RateLimitInfo,
    RateLimitType,
    StepsRunParams,
    UrlUploadParams,
)
from .convert import ConversionResult, ConversionStatus, ConversionStatusType

# Document type types
from .document_type import (
    DocumentType,
    ValidationErrorInfo,
    ValidationResult,
    ValidationWarningInfo,
)

# Identification types
from .identify import (
    DocumentTypeMatch,
    IdentificationResult,
    IdentificationStatus,
    IdentificationStatusType,
)

# Shared types
from .shared import APIResponse, ErrorDetail, PaginatedResponse, Pagination

# Step types
from .step import StepExecutionStatus, StepExecutionStatusType

__all__ = [
    # ==========================================================================
    # Response Models (Pydantic)
    # ==========================================================================
    # Shared
    "APIResponse",
    "ErrorDetail",
    "PaginatedResponse",
    "Pagination",
    # Convert
    "ConversionResult",
    "ConversionStatus",
    # Identify
    "DocumentTypeMatch",
    "IdentificationResult",
    "IdentificationStatus",
    # Document Types
    "DocumentType",
    "ValidationErrorInfo",
    "ValidationResult",
    "ValidationWarningInfo",
    # Steps
    "StepExecutionStatus",
    # ==========================================================================
    # Literal Types (Status Enums)
    # ==========================================================================
    "ConversionStatusType",
    "IdentificationStatusType",
    "StepExecutionStatusType",
    "ImageContentType",
    "RateLimitType",
    # ==========================================================================
    # TypedDicts (Request Parameters)
    # ==========================================================================
    "ClientOptions",
    "FileUploadParams",
    "UrlUploadParams",
    "Base64UploadParams",
    "ConvertParams",
    "IdentifyParams",
    "DocumentTypesListParams",
    "StepsRunParams",
    "RateLimitInfo",
    "QuotaExceededInfo",
    # ==========================================================================
    # Type Aliases
    # ==========================================================================
    "FileInput",
]
