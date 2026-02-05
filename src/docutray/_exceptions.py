"""Exception classes for the DocuTray SDK."""

from __future__ import annotations

from typing import Any

import httpx


class DocuTrayError(Exception):
    """Base exception for all DocuTray SDK errors."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: The error message.
        """
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class APIConnectionError(DocuTrayError):
    """Raised when the SDK cannot connect to the API server.

    This includes network errors, DNS resolution failures, and other
    connection-level problems.
    """

    def __init__(self, message: str, *, should_retry: bool = True) -> None:
        """Initialize the connection error.

        Args:
            message: The error message.
            should_retry: Whether this error should be retried.
        """
        super().__init__(message)
        self.should_retry = should_retry


class APITimeoutError(APIConnectionError):
    """Raised when a request times out."""

    def __init__(self, message: str) -> None:
        """Initialize the timeout error.

        Args:
            message: The error message.
        """
        super().__init__(message, should_retry=True)


class APIError(DocuTrayError):
    """Base class for errors returned by the API.

    All HTTP error responses from the API are converted to subclasses
    of this exception. Contains rich context for debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        request_id: str | None = None,
        body: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the API error.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code from the response.
            request_id: Request ID from X-Request-ID header for debugging.
            body: Parsed JSON response body (can be any JSON type).
            headers: Response headers.
        """
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.body = body
        self.headers = headers or {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"request_id={self.request_id!r})"
        )


class BadRequestError(APIError):
    """Raised when the API returns a 400 Bad Request error.

    This typically indicates invalid parameters or malformed request data.
    """


class AuthenticationError(APIError):
    """Raised when authentication fails (401 Unauthorized).

    This indicates an invalid, expired, or missing API key.
    """


class PermissionDeniedError(APIError):
    """Raised when access is forbidden (403 Forbidden).

    This indicates the API key doesn't have permission for the requested operation.
    """


class NotFoundError(APIError):
    """Raised when a resource is not found (404 Not Found)."""


class ConflictError(APIError):
    """Raised when there's a conflict with the current state (409 Conflict).

    This typically occurs when trying to create a resource that already exists
    or when there's a version conflict.
    """


class UnprocessableEntityError(APIError):
    """Raised when the request is well-formed but contains semantic errors (422).

    This indicates validation errors in the request payload.
    """


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429 Too Many Requests).

    Check the `retry_after` property for the recommended wait time.
    Additional rate limit details are available in `limit_type`, `limit`,
    `remaining`, and `reset_time` properties when provided by the API.
    """

    @property
    def retry_after(self) -> float | None:
        """Get the recommended wait time in seconds from Retry-After header.

        Returns:
            The number of seconds to wait before retrying, or None if not specified.
        """
        if not self.headers:
            return None

        # Case-insensitive header lookup
        retry_after_value: str | None = None
        for key, value in self.headers.items():
            if key.lower() == "retry-after":
                retry_after_value = value
                break

        if retry_after_value is None:
            # Also check body for retryAfter field
            if isinstance(self.body, dict):
                body_retry = self.body.get("retryAfter")
                if body_retry is not None:
                    try:
                        return float(body_retry)
                    except (ValueError, TypeError):
                        pass
            return None

        try:
            return float(retry_after_value)
        except (ValueError, TypeError):
            return None

    @property
    def limit_type(self) -> str | None:
        """Get the type of rate limit exceeded (minute, hour, day).

        Returns:
            The limit type as a string, or None if not specified or not a string.
        """
        if isinstance(self.body, dict):
            limit_type_val = self.body.get("limitType")
            if isinstance(limit_type_val, str):
                return limit_type_val
        return None

    @property
    def limit(self) -> int | None:
        """Get the maximum limit for this period.

        Returns:
            The limit value, or None if not specified.
        """
        if isinstance(self.body, dict):
            limit_val = self.body.get("limit")
            if isinstance(limit_val, int):
                return limit_val
        return None

    @property
    def remaining(self) -> int | None:
        """Get the number of remaining requests.

        Returns:
            The remaining requests, or None if not specified.
        """
        if isinstance(self.body, dict):
            remaining_val = self.body.get("remaining")
            if isinstance(remaining_val, int):
                return remaining_val
        return None

    @property
    def reset_time(self) -> int | None:
        """Get the timestamp when the rate limit resets.

        Returns:
            Unix timestamp when limit resets, or None if not specified.
        """
        if isinstance(self.body, dict):
            reset_val = self.body.get("resetTime")
            if isinstance(reset_val, int):
                return reset_val
        return None


class InternalServerError(APIError):
    """Raised when the API returns a 5xx server error.

    These errors are typically transient and can be retried.
    """


def make_authentication_error(message: str) -> AuthenticationError:
    """Create an AuthenticationError for use during client initialization.

    This factory function creates an AuthenticationError without requiring
    HTTP response context, for cases like missing API keys.

    Args:
        message: The error message.

    Returns:
        An AuthenticationError with minimal context.
    """
    return AuthenticationError(
        message=message,
        status_code=401,
        request_id=None,
        body=None,
        headers=None,
    )


# Mapping of HTTP status codes to exception classes
STATUS_CODE_TO_EXCEPTION: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


def raise_for_status(response: httpx.Response) -> None:
    """Raise an appropriate exception for HTTP error responses.

    Args:
        response: The HTTP response to check.

    Raises:
        APIError: An appropriate subclass based on the status code.
    """
    if response.is_success:
        return

    status_code = response.status_code
    request_id = response.headers.get("X-Request-ID") or response.headers.get(
        "x-request-id"
    )
    headers = dict(response.headers)

    # Try to parse JSON body for error message
    body: Any | None = None
    message: str = response.text or f"HTTP {status_code}"

    try:
        body = response.json()
    except (ValueError, TypeError):
        # JSON parsing failed, use text response
        pass
    else:
        # JSON parsed successfully, try to extract message if it's a dict
        if isinstance(body, dict):
            extracted_message = (
                (
                    body.get("error", {}).get("message")
                    if isinstance(body.get("error"), dict)
                    else None
                )
                or body.get("message")
                or body.get("detail")
            )
            if extracted_message:
                message = str(extracted_message)

    # Get the appropriate exception class
    exc_class = STATUS_CODE_TO_EXCEPTION.get(status_code)
    if exc_class is None:
        exc_class = InternalServerError if status_code >= 500 else APIError

    raise exc_class(
        message=message,
        status_code=status_code,
        request_id=request_id,
        body=body,
        headers=headers,
    )
