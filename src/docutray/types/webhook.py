"""Types for webhook event payloads sent by DocuTray.

These models parse the JSON body of webhook deliveries. The event type is in
the ``X-Docutray-Event`` header.

Example:
    >>> from docutray.types import ConversionWebhookPayload
    >>> payload = ConversionWebhookPayload.model_validate_json(request_body)
    >>> if payload.status == "SUCCESS" and payload.validation:
    ...     print(payload.validation)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from .identify import DocumentTypeMatch
from .step import StepIdentification, StepValidationSummary
from .validation import ConversionValidation

WebhookEventType = Literal[
    "CONVERSION_STARTED",
    "CONVERSION_COMPLETED",
    "CONVERSION_FAILED",
    "IDENTIFICATION_STARTED",
    "IDENTIFICATION_COMPLETED",
    "IDENTIFICATION_FAILED",
    "STEP_STARTED",
    "STEP_COMPLETED",
    "STEP_FAILED",
]
"""Webhook event types (value of the ``X-Docutray-Event`` header)."""


class ConversionWebhookPayload(BaseModel):
    """Payload of ``CONVERSION_*`` webhook events."""

    model_config = ConfigDict(extra="allow")

    conversion_id: str
    """Unique conversion ID."""

    status: str
    """``PROCESSING``, ``SUCCESS`` or ``ERROR``."""

    request_timestamp: datetime | None = None
    """Timestamp when the conversion started."""

    response_timestamp: datetime | None = None
    """Timestamp when the conversion finished."""

    document_type_code: str | None = None
    """Document type code used."""

    original_filename: str | None = None
    """Original filename of the processed file."""

    document_metadata: dict[str, Any] | None = None
    """Custom metadata sent with the conversion."""

    data: dict[str, Any] | None = None
    """Extracted data (``CONVERSION_COMPLETED`` only)."""

    validation: ConversionValidation = None
    """Validation of ``data`` (``CONVERSION_COMPLETED`` only). Informational only."""

    error: str | None = None
    """Error message (``CONVERSION_FAILED`` only)."""


class IdentificationWebhookPayload(BaseModel):
    """Payload of ``IDENTIFICATION_*`` webhook events."""

    model_config = ConfigDict(extra="allow")

    identification_id: str
    """Unique identification ID."""

    status: str
    """``PROCESSING``, ``SUCCESS`` or ``ERROR``."""

    request_timestamp: datetime | None = None
    response_timestamp: datetime | None = None

    original_filename: str | None = None
    document_metadata: dict[str, Any] | None = None

    document_type: DocumentTypeMatch | None = None
    """Identified document type (``IDENTIFICATION_COMPLETED`` only)."""

    document_type_code_options: list[str] | None = None
    """Document type codes the identification chose from."""

    alternatives: list[DocumentTypeMatch] | None = None
    """Other candidate document types."""

    error: str | None = None
    """Error message (``IDENTIFICATION_FAILED`` only)."""


class StepWebhookPayload(BaseModel):
    """Payload of ``STEP_*`` webhook events."""

    model_config = ConfigDict(extra="allow")

    step_execution_id: str
    """Unique step execution ID."""

    step_id: str
    step_name: str | None = None

    status: str
    """``started``, ``completed`` or ``failed``."""

    request_timestamp: datetime | None = None
    response_timestamp: datetime | None = None

    document_metadata: dict[str, Any] | None = None

    data: dict[str, Any] | None = None
    """Extracted data (``STEP_COMPLETED`` only)."""

    identification: StepIdentification | None = None
    """Identification result (``STEP_COMPLETED`` only)."""

    validation: StepValidationSummary | None = None
    """Validation summary (``STEP_COMPLETED`` only). Informational only."""

    error: str | None = None
    """Error message (``STEP_FAILED`` only)."""
