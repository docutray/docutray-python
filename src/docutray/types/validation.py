"""Types for document validation results (JSON Schema + DSL rules)."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

ValidationSeverity = Literal["error", "warning"]
"""Severity of a validation issue. Warnings never make a document invalid."""

ValidationSource = Literal["schema", "rule"]
"""Layer that produced the issue: the JSON Schema or a custom (DSL) rule."""


def _field_path(value: Any) -> Any:
    """Normalize a field path to the canonical ``items[0].total`` form.

    A list of segments (``["items", 0, "total"]``) is joined, skipping
    ``null`` segments; any other non-string value is converted with ``str()``.
    """
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        path = ""
        for segment in value:
            if segment is None:
                continue
            if isinstance(segment, int) and not isinstance(segment, bool):
                path += f"[{segment}]"
            else:
                path += f".{segment}" if path else str(segment)
        return path
    return str(value)


def _to_str(value: Any) -> Any:
    """Read ``null`` as ``""`` and any other non-string value as ``str(value)``."""
    if value is None:
        return ""
    return value if isinstance(value, str) else str(value)


def _to_optional_str(value: Any) -> Any:
    """Keep ``null``; read any other non-string value as ``str(value)``."""
    if value is None or isinstance(value, str):
        return value
    return str(value)


class ValidationIssue(BaseModel):
    """A single structured validation error or warning."""

    model_config = ConfigDict(extra="allow")

    field: Annotated[str | None, BeforeValidator(_field_path)] = ""
    """Canonical path of the field (e.g. ``"items[0].total"``); empty or ``None`` for the document root."""

    code: Annotated[str, BeforeValidator(_to_str)] = ""
    """Machine-readable issue code (e.g. ``"VALIDATION_ERROR"``)."""

    message: Annotated[str, BeforeValidator(_to_str)] = ""
    """Human-readable description of the issue."""

    severity: Annotated[
        ValidationSeverity | str | None, BeforeValidator(_to_optional_str)
    ] = None
    """Issue severity. Unknown values are kept as plain strings."""

    source: Annotated[
        ValidationSource | str | None, BeforeValidator(_to_optional_str)
    ] = None
    """Validation layer that produced the issue. Unknown values are kept as plain strings."""

    rule: Annotated[str | None, BeforeValidator(_to_optional_str)] = None
    """Name of the rule that failed, when the issue comes from a rule."""

    value: Any = None
    """The value that caused the issue, when available."""

    details: Any = None
    """Additional rule-specific details (usually a dict)."""


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
