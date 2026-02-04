"""DocuTray Python SDK.

A Python library for the DocuTray API, providing access to document
processing capabilities including OCR, document identification, data
extraction, knowledge bases, and workflows.
"""

from ._client import AsyncClient, Client
from ._exceptions import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    DocuTrayError,
)
from ._version import __version__

__all__ = [
    "__version__",
    "Client",
    "AsyncClient",
    "DocuTrayError",
    "AuthenticationError",
    "APIConnectionError",
    "APITimeoutError",
]
