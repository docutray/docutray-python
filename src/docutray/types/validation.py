"""Types for document validation results (JSON Schema + DSL rules)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

ValidationSeverity = Literal["error", "warning"]
"""Severity of a validation issue. Warnings never make a document invalid."""

ValidationSource = Literal["schema", "rule"]
"""Layer that produced the issue: the JSON Schema or a custom (DSL) rule."""


class ValidationIssue(BaseModel):
    """A single structured validation error or warning."""

    model_config = ConfigDict(extra="allow")

    field: str = ""
    """Canonical path of the field (e.g. ``"items[0].total"``); empty for the document root."""

    code: str
    """Machine-readable issue code (e.g. ``"VALIDATION_ERROR"``)."""

    message: str
    """Human-readable description of the issue."""

    severity: ValidationSeverity
    """Issue severity."""

    source: ValidationSource
    """Validation layer that produced the issue."""

    rule: str | None = None
    """Name of the rule that failed, when the issue comes from a rule."""

    value: Any = None
    """The value that caused the issue, when available."""

    details: dict[str, Any] | None = None
    """Additional rule-specific details."""


class ValidationOutcome(BaseModel):
    """Validation result attached to a successful conversion."""

    model_config = ConfigDict(extra="allow")

    valid: bool
    """Whether the data conforms (warnings do not make it invalid)."""

    errors: list[ValidationIssue]
    """Blocking issues."""

    warnings: list[ValidationIssue]
    """Non-blocking issues."""


class ValidationSystemFailure(BaseModel):
    """Validation could not be completed; no internal details are exposed."""

    model_config = ConfigDict(extra="allow")

    status: Literal["error"]
    """Always ``"error"``."""


ConversionValidation = ValidationOutcome | ValidationSystemFailure | None
"""Validation of a conversion's extracted data.

Informational only: it never changes the conversion status.

- ``ValidationOutcome`` when validation ran.
- ``ValidationSystemFailure`` when validation could not be completed.
- ``None`` when validation was skipped (no JSON Schema and no rules).
"""


class DSLDiagnostic(BaseModel):
    """A syntax diagnostic for invalid DSL rules."""

    model_config = ConfigDict(extra="allow")

    line: int
    """1-based line number."""

    column: int
    """1-based column number."""

    message: str
    """Parser diagnostic (currently in Spanish)."""
