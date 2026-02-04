"""Public type definitions for the DocuTray SDK."""

from .convert import ConversionResult, ConversionStatus, ConversionStatusType
from .document_type import (
    DocumentType,
    ValidationErrorInfo,
    ValidationResult,
    ValidationWarningInfo,
)
from .identify import (
    DocumentTypeMatch,
    IdentificationResult,
    IdentificationStatus,
    IdentificationStatusType,
)
from .shared import APIResponse, ErrorDetail, PaginatedResponse, Pagination
from .step import StepExecutionStatus, StepExecutionStatusType

__all__ = [
    # Shared
    "APIResponse",
    "ErrorDetail",
    "PaginatedResponse",
    "Pagination",
    # Convert
    "ConversionResult",
    "ConversionStatus",
    "ConversionStatusType",
    # Identify
    "DocumentTypeMatch",
    "IdentificationResult",
    "IdentificationStatus",
    "IdentificationStatusType",
    # Document Types
    "DocumentType",
    "ValidationErrorInfo",
    "ValidationResult",
    "ValidationWarningInfo",
    # Steps
    "StepExecutionStatus",
    "StepExecutionStatusType",
]
