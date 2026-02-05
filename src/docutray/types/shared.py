"""Shared types used across multiple resources."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Pagination(BaseModel):
    """Pagination information for list responses."""

    model_config = ConfigDict(extra="allow")

    total: int
    """Total number of items matching the query."""

    page: int
    """Current page number (1-indexed)."""

    limit: int
    """Number of items per page."""


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    model_config = ConfigDict(extra="allow")

    data: list[T]
    """List of items in the current page."""

    pagination: Pagination
    """Pagination metadata."""


class APIResponse(BaseModel):
    """Base class for API responses with common fields."""

    model_config = ConfigDict(extra="allow")


class ErrorDetail(BaseModel):
    """Error detail information."""

    model_config = ConfigDict(extra="allow")

    message: str
    """Error message."""

    errors: list[str] | None = None
    """List of specific validation errors."""
