"""Exception classes for the DocuTray SDK."""

from __future__ import annotations


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


class AuthenticationError(DocuTrayError):
    """Raised when authentication fails or API key is missing."""


class APIConnectionError(DocuTrayError):
    """Raised when the SDK cannot connect to the API server."""


class APITimeoutError(APIConnectionError):
    """Raised when a request times out."""
