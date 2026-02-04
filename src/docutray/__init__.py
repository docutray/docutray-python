"""DocuTray Python SDK.

A Python library for the DocuTray API, providing access to document
processing capabilities including OCR, document identification, data
extraction, and knowledge bases.
"""

from ._client import AsyncClient, Client
from ._exceptions import (
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
from ._version import __version__

__all__ = [
    # Version
    "__version__",
    # Clients
    "Client",
    "AsyncClient",
    # Base exceptions
    "DocuTrayError",
    "APIConnectionError",
    "APITimeoutError",
    # API error hierarchy
    "APIError",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "UnprocessableEntityError",
]
