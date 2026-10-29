"""Types for document type operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .validation import ValidationIssue

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
    """Unique document type code.

    Codes of an organization's own types carry its slug as a prefix (``acme_invoice``).
    """

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
    """JSON Schema for the document type (returned by ``GET /api/document-types/{id}``)."""

    promptHints: str | None = None
    """Hints for the OCR extraction prompt."""

    identifyPromptHints: str | None = None
    """Hints for the document identification prompt."""

    conversionMode: ConversionMode | str | None = None
    """Conversion mode used by the OCR pipeline. Unknown modes are kept as plain strings."""

    keepPropertyOrdering: bool | None = None
    """Whether property ordering in the schema is preserved."""

    boundingBoxesEnabled: bool | None = None
    """Whether extraction also returns per-field locations (``field_locations``)."""

    conversionSpec: dict[str, Any] | None = None
    """Spec that maps extracted JSON to CSV/Excel columns on tray export."""

    dslRules: str | None = None
    """Saved DSL validation rules, or ``None`` when no rules are configured."""


class ValidationErrorInfo(BaseModel):
    """Validation error information."""

    model_config = ConfigDict(extra="allow")

    count: int = 0
    """Total number of errors found."""

    messages: list[str] = Field(default_factory=list)
    """List of descriptive error messages."""


class ValidationWarningInfo(BaseModel):
    """Validation warning information."""

    model_config = ConfigDict(extra="allow")

    count: int = 0
    """Total number of warnings found."""

    messages: list[str] = Field(default_factory=list)
    """List of descriptive warning messages."""


class ValidationResult(BaseModel):
    """Result of validating JSON data against a document type.

    Validation runs the document type's JSON Schema and its DSL rules.
    ``valid`` and ``issues`` carry the structured result; ``errors`` and
    ``warnings`` keep the summarized ``count``/``messages`` format.
    """

    model_config = ConfigDict(extra="allow")

    valid: bool | None = None
    """Whether the data conforms (warnings do not make it invalid).

    ``None`` only for API versions that predate structured validation.
    """

    issues: list[ValidationIssue] = []
    """Structured errors followed by warnings."""

    errors: ValidationErrorInfo
    """Validation errors summary."""

    warnings: ValidationWarningInfo
    """Validation warnings summary."""

    def is_valid(self) -> bool:
        """Check if validation passed with no errors.

        Uses ``valid`` when the API sends it. Otherwise the data is valid only
        when the API reported an error ``count`` of zero; a summary without a
        ``count`` is not treated as valid.
        """
        if self.valid is not None:
            return self.valid
        return "count" in self.errors.model_fields_set and self.errors.count == 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return self.warnings.count > 0
