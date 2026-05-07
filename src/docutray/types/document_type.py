"""Types for document type operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

ConversionMode = Literal["json", "toon", "multi_prompt"]
"""Conversion mode for document type processing."""


class DocumentType(BaseModel):
    """A document type definition."""

    model_config = ConfigDict(extra="allow")

    id: str
    """Unique document type ID."""

    name: str
    """Document type name."""

    codeType: str
    """Unique document type code."""

    description: str | None = None
    """Document type description."""

    isPublic: bool = False
    """Indicates if the document type is public."""

    isDraft: bool = False
    """Indicates if the document type is a draft."""

    status: str | None = None
    """Document type status."""

    createdAt: datetime | None = None
    """Creation timestamp."""

    updatedAt: datetime | None = None
    """Last update timestamp."""

    jsonSchema: dict[str, Any] | None = None
    """JSON Schema for the document type (returned by GET /api/document-types/{id})."""


class ValidationErrorInfo(BaseModel):
    """Validation error information."""

    model_config = ConfigDict(extra="allow")

    count: int
    """Total number of errors found."""

    messages: list[str]
    """List of descriptive error messages."""


class ValidationWarningInfo(BaseModel):
    """Validation warning information."""

    model_config = ConfigDict(extra="allow")

    count: int
    """Total number of warnings found."""

    messages: list[str]
    """List of descriptive warning messages."""


class ValidationResult(BaseModel):
    """Result of JSON validation against a document type schema."""

    model_config = ConfigDict(extra="allow")

    errors: ValidationErrorInfo
    """Validation errors."""

    warnings: ValidationWarningInfo
    """Validation warnings."""

    def is_valid(self) -> bool:
        """Check if validation passed with no errors."""
        return self.errors.count == 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return self.warnings.count > 0
