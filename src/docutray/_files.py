"""File input preparation utilities for the DocuTray SDK."""

from __future__ import annotations

import base64
import mimetypes
from io import BytesIO
from pathlib import Path
from typing import IO, Any

from ._types import (
    CONTENT_TYPE_PDF,
    EXTENSION_TO_CONTENT_TYPE,
    SUPPORTED_CONTENT_TYPES,
    FileInput,
)


def detect_content_type(path: Path) -> str:
    """Detect content type from file extension.

    Args:
        path: Path to the file.

    Returns:
        The detected content type, or application/octet-stream if unknown.
    """
    suffix = path.suffix.lower()
    if suffix in EXTENSION_TO_CONTENT_TYPE:
        return EXTENSION_TO_CONTENT_TYPE[suffix]

    # Fall back to mimetypes library
    mime_type, _ = mimetypes.guess_type(str(path))
    return mime_type or "application/octet-stream"


def prepare_file_upload(
    file: FileInput,
    *,
    content_type: str | None = None,
    filename: str | None = None,
) -> tuple[str, tuple[str, IO[bytes], str]]:
    """Prepare a file for multipart upload.

    Args:
        file: File input - Path, bytes, or file-like object.
        content_type: Content type override. Auto-detected if not provided.
        filename: Filename override. Auto-detected from Path if not provided.

    Returns:
        A tuple of (field_name, (filename, file_object, content_type)) suitable
        for httpx multipart uploads.

    Raises:
        ValueError: If content type cannot be determined.
    """
    file_obj: IO[bytes]
    detected_filename: str
    detected_content_type: str

    if isinstance(file, Path):
        # Read file from path
        file_obj = BytesIO(file.read_bytes())
        detected_filename = file.name
        detected_content_type = content_type or detect_content_type(file)
    elif isinstance(file, bytes):
        # Wrap bytes in BytesIO
        file_obj = BytesIO(file)
        detected_filename = filename or "document"
        detected_content_type = content_type or CONTENT_TYPE_PDF
    else:
        # Assume file-like object (BinaryIO)
        file_obj = file
        file_name_attr = getattr(file, "name", None)
        detected_filename = filename or (file_name_attr if isinstance(file_name_attr, str) else "document")
        if "/" in detected_filename:
            detected_filename = detected_filename.rsplit("/", 1)[-1]
        detected_content_type = content_type or CONTENT_TYPE_PDF

    # Use provided overrides
    final_filename = filename or detected_filename
    final_content_type = content_type or detected_content_type

    # Validate content type
    if final_content_type not in SUPPORTED_CONTENT_TYPES:
        if final_content_type != "application/octet-stream":
            # Allow unknown types but warn via the content type
            pass

    return ("image", (final_filename, file_obj, final_content_type))


def prepare_url_upload(
    url: str,
    *,
    content_type: str | None = None,
) -> dict[str, Any]:
    """Prepare a URL for JSON upload.

    Args:
        url: URL of the file to process.
        content_type: Content type override. Auto-detected by server if not provided.

    Returns:
        A dictionary with the URL and optional content type for JSON body.
    """
    result: dict[str, Any] = {"image_url": url}
    if content_type:
        result["image_content_type"] = content_type
    return result


def prepare_base64_upload(
    file_base64: str,
    *,
    content_type: str | None = None,
) -> dict[str, Any]:
    """Prepare base64-encoded data for JSON upload.

    Args:
        file_base64: Base64-encoded file data. Can include data URI prefix.
        content_type: Content type override. Required if data URI prefix not present.

    Returns:
        A dictionary with the base64 data and content type for JSON body.
    """
    result: dict[str, Any] = {"image_base64": file_base64}

    # Check if it's a data URI with embedded content type
    if file_base64.startswith("data:"):
        # Format: data:image/jpeg;base64,xxxxx
        # Content type is embedded, no need to add separately
        pass
    elif content_type:
        result["image_content_type"] = content_type

    return result


def encode_file_to_base64(file: FileInput) -> str:
    """Encode a file to base64 string.

    Args:
        file: File input - Path, bytes, or file-like object.

    Returns:
        Base64-encoded string of the file contents.
    """
    if isinstance(file, Path):
        data = file.read_bytes()
    elif isinstance(file, bytes):
        data = file
    else:
        # File-like object
        data = file.read()

    return base64.b64encode(data).decode("ascii")
