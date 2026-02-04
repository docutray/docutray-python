"""Tests for file handling utilities."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import pytest

from docutray._files import (
    detect_content_type,
    encode_file_to_base64,
    prepare_base64_upload,
    prepare_file_upload,
    prepare_url_upload,
)
from docutray._types import CONTENT_TYPE_PDF


class TestDetectContentType:
    """Tests for detect_content_type()."""

    def test_pdf_extension(self) -> None:
        """Detect PDF content type from .pdf extension."""
        path = Path("document.pdf")
        assert detect_content_type(path) == "application/pdf"

    def test_png_extension(self) -> None:
        """Detect PNG content type from .png extension."""
        path = Path("image.png")
        assert detect_content_type(path) == "image/png"

    def test_jpg_extension(self) -> None:
        """Detect JPEG content type from .jpg extension."""
        path = Path("photo.jpg")
        assert detect_content_type(path) == "image/jpeg"

    def test_jpeg_extension(self) -> None:
        """Detect JPEG content type from .jpeg extension."""
        path = Path("photo.jpeg")
        assert detect_content_type(path) == "image/jpeg"

    def test_tiff_extension(self) -> None:
        """Detect TIFF content type from .tiff extension."""
        path = Path("scan.tiff")
        assert detect_content_type(path) == "image/tiff"

    def test_tif_extension(self) -> None:
        """Detect TIFF content type from .tif extension."""
        path = Path("scan.tif")
        assert detect_content_type(path) == "image/tiff"

    def test_webp_extension(self) -> None:
        """Detect WebP content type from .webp extension."""
        path = Path("image.webp")
        assert detect_content_type(path) == "image/webp"

    def test_unknown_extension(self) -> None:
        """Return octet-stream for unknown extension."""
        path = Path("document.xyz")
        # Falls back to mimetypes or octet-stream
        content_type = detect_content_type(path)
        assert content_type in ("application/octet-stream", None) or content_type


class TestPrepareFileUpload:
    """Tests for prepare_file_upload()."""

    def test_from_bytes(self) -> None:
        """Prepare upload from bytes."""
        data = b"fake pdf content"
        field_name, (filename, file_obj, content_type) = prepare_file_upload(data)

        assert field_name == "image"
        assert filename == "document"
        assert content_type == CONTENT_TYPE_PDF
        assert file_obj.read() == data

    def test_from_bytes_with_content_type(self) -> None:
        """Prepare upload from bytes with explicit content type."""
        data = b"fake image content"
        field_name, (filename, file_obj, content_type) = prepare_file_upload(
            data, content_type="image/png"
        )

        assert content_type == "image/png"

    def test_from_bytes_with_filename(self) -> None:
        """Prepare upload from bytes with explicit filename."""
        data = b"fake content"
        field_name, (filename, file_obj, content_type) = prepare_file_upload(
            data, filename="custom.pdf"
        )

        assert filename == "custom.pdf"

    def test_from_bytesio(self) -> None:
        """Prepare upload from BytesIO object."""
        data = b"fake content"
        file_obj = BytesIO(data)
        field_name, (filename, result_obj, content_type) = prepare_file_upload(file_obj)

        assert field_name == "image"
        assert result_obj.read() == data

    def test_from_path(self, tmp_path: Path) -> None:
        """Prepare upload from Path."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"test pdf content")

        field_name, (filename, file_obj, content_type) = prepare_file_upload(test_file)

        assert field_name == "image"
        assert filename == "test.pdf"
        assert content_type == "application/pdf"
        assert file_obj.read() == b"test pdf content"

    def test_from_path_png(self, tmp_path: Path) -> None:
        """Prepare upload from PNG file path."""
        test_file = tmp_path / "image.png"
        test_file.write_bytes(b"fake png content")

        field_name, (filename, file_obj, content_type) = prepare_file_upload(test_file)

        assert filename == "image.png"
        assert content_type == "image/png"


class TestPrepareUrlUpload:
    """Tests for prepare_url_upload()."""

    def test_url_only(self) -> None:
        """Prepare URL upload without content type."""
        result = prepare_url_upload("https://example.com/document.pdf")

        assert result == {"image_url": "https://example.com/document.pdf"}

    def test_url_with_content_type(self) -> None:
        """Prepare URL upload with explicit content type."""
        result = prepare_url_upload(
            "https://example.com/image",
            content_type="image/png",
        )

        assert result == {
            "image_url": "https://example.com/image",
            "image_content_type": "image/png",
        }


class TestPrepareBase64Upload:
    """Tests for prepare_base64_upload()."""

    def test_base64_only(self) -> None:
        """Prepare base64 upload without content type."""
        b64_data = base64.b64encode(b"test content").decode()
        result = prepare_base64_upload(b64_data)

        assert result == {"image_base64": b64_data}

    def test_base64_with_content_type(self) -> None:
        """Prepare base64 upload with explicit content type."""
        b64_data = base64.b64encode(b"test content").decode()
        result = prepare_base64_upload(b64_data, content_type="application/pdf")

        assert result == {
            "image_base64": b64_data,
            "image_content_type": "application/pdf",
        }

    def test_base64_data_uri(self) -> None:
        """Prepare base64 upload with data URI prefix."""
        b64_data = "data:image/png;base64," + base64.b64encode(b"test").decode()
        result = prepare_base64_upload(b64_data)

        # Should not add content type since it's in the data URI
        assert result == {"image_base64": b64_data}


class TestEncodeFileToBase64:
    """Tests for encode_file_to_base64()."""

    def test_encode_bytes(self) -> None:
        """Encode bytes to base64."""
        data = b"test content"
        result = encode_file_to_base64(data)

        assert result == base64.b64encode(data).decode("ascii")

    def test_encode_path(self, tmp_path: Path) -> None:
        """Encode file from path to base64."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"file content")

        result = encode_file_to_base64(test_file)

        assert result == base64.b64encode(b"file content").decode("ascii")

    def test_encode_bytesio(self) -> None:
        """Encode BytesIO to base64."""
        data = b"bytesio content"
        file_obj = BytesIO(data)

        result = encode_file_to_base64(file_obj)

        assert result == base64.b64encode(data).decode("ascii")
