"""Types for document validation results (JSON Schema + DSL rules)."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ValidationSeverity = Literal["error", "warning"]
"""Severity of a validation issue. Warnings never make a document invalid."""

ValidationSource = Literal["schema", "rule"]
"""Layer that produced the issue: the JSON Schema or a custom (DSL) rule."""


class ValidationIssue(BaseModel):
    """A single structured validation error or warning."""

    model_config = ConfigDict(extra="allow")

    field: str | None = ""
    """Canonical path of the field (e.g. ``"items[0].total"``); empty or ``None`` for the document root."""

    code: str = ""
    """Machine-readable issue code (e.g. ``"VALIDATION_ERROR"``)."""

    message: str = ""
    """Human-readable description of the issue."""

    severity: ValidationSeverity | str | None = None
    """Issue severity. Unknown values are kept as plain strings."""

    source: ValidationSource | str | None = None
    """Validation layer that produced the issue. Unknown values are kept as plain strings."""

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

    errors: list[ValidationIssue] = Field(default_factory=list)
    """Blocking issues."""

    warnings: list[ValidationIssue] = Field(default_factory=list)
    """Non-blocking issues."""


class ValidationSystemFailure(BaseModel):
    """Validation could not be completed; no internal details are exposed."""

    model_config = ConfigDict(extra="allow")

    status: Literal["error"]
    """Always ``"error"``."""


ConversionValidation = Annotated[
    ValidationOutcome | ValidationSystemFailure | dict[str, Any] | None,
    Field(union_mode="left_to_right"),
]
"""Validation of a conversion's extracted data.

Informational only: it never changes the conversion status.

- ``ValidationOutcome`` when validation ran.
- ``ValidationSystemFailure`` when validation could not be completed.
- ``None`` when validation was skipped (no JSON Schema and no rules).
- A plain ``dict`` for any shape this SDK version does not recognize, so new
  API variants never break parsing of the conversion itself.
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
