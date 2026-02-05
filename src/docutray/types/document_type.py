"""Types for document type operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


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

    createdAt: datetime | None = None
    """Creation timestamp."""

    updatedAt: datetime | None = None
    """Last update timestamp."""

    schema_: dict[str, Any] | None = None
    """JSON schema for the document type (when retrieved by ID)."""


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
