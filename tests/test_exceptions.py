"""Tests for exception classes."""

from __future__ import annotations

import pytest

from docutray import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    DocuTrayError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)
from docutray._exceptions import STATUS_CODE_TO_EXCEPTION, raise_for_status
import httpx


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_docutray_error_is_base(self) -> None:
        """DocuTrayError is the base for all SDK exceptions."""
        assert issubclass(APIConnectionError, DocuTrayError)
        assert issubclass(APIError, DocuTrayError)

    def test_api_connection_error_hierarchy(self) -> None:
        """APIConnectionError hierarchy is correct."""
        assert issubclass(APITimeoutError, APIConnectionError)
        assert issubclass(APITimeoutError, DocuTrayError)

    def test_api_error_hierarchy(self) -> None:
        """All HTTP error classes inherit from APIError."""
        http_errors = [
            BadRequestError,
            AuthenticationError,
            PermissionDeniedError,
            NotFoundError,
            ConflictError,
            UnprocessableEntityError,
            RateLimitError,
            InternalServerError,
        ]
        for error_class in http_errors:
            assert issubclass(error_class, APIError)
            assert issubclass(error_class, DocuTrayError)


class TestDocuTrayError:
    """Tests for base DocuTrayError."""

    def test_message_attribute(self) -> None:
        """DocuTrayError stores the message."""
        error = DocuTrayError("Test error message")
        assert error.message == "Test error message"

    def test_str_representation(self) -> None:
        """DocuTrayError string representation is the message."""
        error = DocuTrayError("Test error message")
        assert str(error) == "Test error message"


class TestAPIConnectionError:
    """Tests for APIConnectionError."""

    def test_default_should_retry(self) -> None:
        """APIConnectionError defaults to should_retry=True."""
        error = APIConnectionError("Connection failed")
        assert error.should_retry is True

    def test_custom_should_retry(self) -> None:
        """APIConnectionError respects should_retry parameter."""
        error = APIConnectionError("Connection failed", should_retry=False)
        assert error.should_retry is False


class TestAPITimeoutError:
    """Tests for APITimeoutError."""

    def test_timeout_always_retryable(self) -> None:
        """APITimeoutError is always retryable."""
        error = APITimeoutError("Request timed out")
        assert error.should_retry is True


class TestAPIError:
    """Tests for APIError base class."""

    def test_all_attributes_stored(self) -> None:
        """APIError stores all context attributes."""
        error = APIError(
            message="Test error",
            status_code=500,
            request_id="req_123",
            body={"error": "test"},
            headers={"X-Custom": "value"},
        )
        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.request_id == "req_123"
        assert error.body == {"error": "test"}
        assert error.headers == {"X-Custom": "value"}

    def test_optional_attributes_default_to_none(self) -> None:
        """APIError optional attributes default appropriately."""
        error = APIError(message="Test error", status_code=500)
        assert error.request_id is None
        assert error.body is None
        assert error.headers == {}

    def test_repr_format(self) -> None:
        """APIError repr includes key information."""
        error = APIError(
            message="Test error",
            status_code=500,
            request_id="req_123",
        )
        repr_str = repr(error)
        assert "APIError" in repr_str
        assert "Test error" in repr_str
        assert "500" in repr_str
        assert "req_123" in repr_str


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_retry_after_property(self) -> None:
        """RateLimitError extracts retry_after from headers."""
        error = RateLimitError(
            message="Rate limited",
            status_code=429,
            headers={"retry-after": "30"},
        )
        assert error.retry_after == 30.0

    def test_retry_after_case_insensitive(self) -> None:
        """RateLimitError handles Retry-After header case."""
        error = RateLimitError(
            message="Rate limited",
            status_code=429,
            headers={"Retry-After": "60"},
        )
        assert error.retry_after == 60.0

    def test_retry_after_missing(self) -> None:
        """RateLimitError returns None when header missing."""
        error = RateLimitError(
            message="Rate limited",
            status_code=429,
            headers={},
        )
        assert error.retry_after is None

    def test_retry_after_invalid(self) -> None:
        """RateLimitError handles invalid retry-after values."""
        error = RateLimitError(
            message="Rate limited",
            status_code=429,
            headers={"retry-after": "invalid"},
        )
        assert error.retry_after is None


class TestStatusCodeMapping:
    """Tests for STATUS_CODE_TO_EXCEPTION mapping."""

    def test_400_maps_to_bad_request(self) -> None:
        """400 maps to BadRequestError."""
        assert STATUS_CODE_TO_EXCEPTION[400] is BadRequestError

    def test_401_maps_to_authentication(self) -> None:
        """401 maps to AuthenticationError."""
        assert STATUS_CODE_TO_EXCEPTION[401] is AuthenticationError

    def test_403_maps_to_permission_denied(self) -> None:
        """403 maps to PermissionDeniedError."""
        assert STATUS_CODE_TO_EXCEPTION[403] is PermissionDeniedError

    def test_404_maps_to_not_found(self) -> None:
        """404 maps to NotFoundError."""
        assert STATUS_CODE_TO_EXCEPTION[404] is NotFoundError

    def test_409_maps_to_conflict(self) -> None:
        """409 maps to ConflictError."""
        assert STATUS_CODE_TO_EXCEPTION[409] is ConflictError

    def test_422_maps_to_unprocessable_entity(self) -> None:
        """422 maps to UnprocessableEntityError."""
        assert STATUS_CODE_TO_EXCEPTION[422] is UnprocessableEntityError

    def test_429_maps_to_rate_limit(self) -> None:
        """429 maps to RateLimitError."""
        assert STATUS_CODE_TO_EXCEPTION[429] is RateLimitError


class TestRaiseForStatus:
    """Tests for raise_for_status function."""

    def test_success_does_not_raise(self) -> None:
        """Successful responses don't raise exceptions."""
        response = httpx.Response(200, json={"data": "test"})
        raise_for_status(response)  # Should not raise

    def test_400_raises_bad_request(self) -> None:
        """400 response raises BadRequestError."""
        response = httpx.Response(
            400,
            json={"error": {"message": "Invalid input"}},
            headers={"X-Request-ID": "req_123"},
        )
        with pytest.raises(BadRequestError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 400
        assert exc_info.value.request_id == "req_123"
        assert "Invalid input" in exc_info.value.message

    def test_401_raises_authentication(self) -> None:
        """401 response raises AuthenticationError."""
        response = httpx.Response(
            401,
            json={"message": "Invalid API key"},
        )
        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 401

    def test_403_raises_permission_denied(self) -> None:
        """403 response raises PermissionDeniedError."""
        response = httpx.Response(403, json={"detail": "Forbidden"})
        with pytest.raises(PermissionDeniedError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 403

    def test_404_raises_not_found(self) -> None:
        """404 response raises NotFoundError."""
        response = httpx.Response(404, text="Not Found")
        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 404

    def test_429_raises_rate_limit(self) -> None:
        """429 response raises RateLimitError with retry_after."""
        response = httpx.Response(
            429,
            json={"error": {"message": "Too many requests"}},
            headers={"Retry-After": "60"},
        )
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60.0

    def test_500_raises_internal_server(self) -> None:
        """500 response raises InternalServerError."""
        response = httpx.Response(500, text="Internal Server Error")
        with pytest.raises(InternalServerError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 500

    def test_502_raises_internal_server(self) -> None:
        """502 response raises InternalServerError."""
        response = httpx.Response(502, text="Bad Gateway")
        with pytest.raises(InternalServerError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 502

    def test_unknown_4xx_raises_api_error(self) -> None:
        """Unknown 4xx response raises APIError."""
        response = httpx.Response(418, text="I'm a teapot")
        with pytest.raises(APIError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.status_code == 418
        assert type(exc_info.value) is APIError  # Not a subclass

    def test_extracts_request_id_case_insensitive(self) -> None:
        """Request ID is extracted case-insensitively."""
        response = httpx.Response(
            400,
            json={},
            headers={"x-request-id": "req_lower"},
        )
        with pytest.raises(BadRequestError) as exc_info:
            raise_for_status(response)
        assert exc_info.value.request_id == "req_lower"

    def test_handles_non_json_response(self) -> None:
        """Non-JSON responses are handled gracefully."""
        response = httpx.Response(
            500,
            content=b"Plain text error",
            headers={"Content-Type": "text/plain"},
        )
        with pytest.raises(InternalServerError) as exc_info:
            raise_for_status(response)
        assert "Plain text error" in exc_info.value.message
