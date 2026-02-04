"""Type definitions for the DocuTray SDK."""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO, TypedDict

from typing_extensions import NotRequired, Required

# File input types
FileInput = Path | bytes | BinaryIO
"""Type alias for file inputs: Path, bytes, or file-like object."""

# Content type constants
CONTENT_TYPE_PDF = "application/pdf"
CONTENT_TYPE_JPEG = "image/jpeg"
CONTENT_TYPE_PNG = "image/png"
CONTENT_TYPE_GIF = "image/gif"
CONTENT_TYPE_BMP = "image/bmp"
CONTENT_TYPE_WEBP = "image/webp"

# Mapping of file extensions to content types
EXTENSION_TO_CONTENT_TYPE: dict[str, str] = {
    ".pdf": CONTENT_TYPE_PDF,
    ".jpg": CONTENT_TYPE_JPEG,
    ".jpeg": CONTENT_TYPE_JPEG,
    ".png": CONTENT_TYPE_PNG,
    ".gif": CONTENT_TYPE_GIF,
    ".bmp": CONTENT_TYPE_BMP,
    ".webp": CONTENT_TYPE_WEBP,
}

# Supported content types for upload
SUPPORTED_CONTENT_TYPES: frozenset[str] = frozenset([
    CONTENT_TYPE_PDF,
    CONTENT_TYPE_JPEG,
    CONTENT_TYPE_PNG,
    CONTENT_TYPE_GIF,
    CONTENT_TYPE_BMP,
    CONTENT_TYPE_WEBP,
])


class ClientOptions(TypedDict, total=False):
    """Options for configuring a DocuTray client."""

    api_key: NotRequired[str | None]
    base_url: NotRequired[str | None]
    timeout: NotRequired[float | None]


class FileUploadParams(TypedDict, total=False):
    """Parameters for file upload via multipart form data."""

    file: Required[FileInput]
    """File to upload: Path, bytes, or file-like object."""

    content_type: NotRequired[str]
    """Content type of the file. Auto-detected from Path extension if not provided."""

    filename: NotRequired[str]
    """Filename to use in the upload. Auto-detected from Path if not provided."""


class UrlUploadParams(TypedDict, total=False):
    """Parameters for URL-based file upload."""

    url: Required[str]
    """URL of the file to process."""

    content_type: NotRequired[str]
    """Content type of the file. Auto-detected by server if not provided."""


class Base64UploadParams(TypedDict, total=False):
    """Parameters for base64-encoded file upload."""

    file_base64: Required[str]
    """Base64-encoded file data. Can include data URI prefix."""

    content_type: NotRequired[str]
    """Content type of the file. Required if file_base64 doesn't include data URI."""


# =============================================================================
# Request Parameters for API Resources
# =============================================================================


class ConvertParams(TypedDict, total=False):
    """Parameters for document conversion requests."""

    document_type_code: Required[str]
    """Document type code to use for conversion."""

    document_metadata: NotRequired[dict[str, Any]]
    """Additional document metadata."""


class IdentifyParams(TypedDict, total=False):
    """Parameters for document identification requests."""

    # Currently no additional parameters beyond file input
    pass


class DocumentTypesListParams(TypedDict, total=False):
    """Parameters for listing document types."""

    page: NotRequired[int]
    """Page number (1-indexed)."""

    limit: NotRequired[int]
    """Number of items per page."""

    search: NotRequired[str]
    """Search term to filter document types."""


class StepsRunParams(TypedDict, total=False):
    """Parameters for step execution requests."""

    document_metadata: NotRequired[dict[str, Any]]
    """Additional document metadata."""
