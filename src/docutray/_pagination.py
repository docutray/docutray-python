"""Pagination utilities for list operations."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from typing import TYPE_CHECKING, Generic, TypeVar

from .types.shared import Pagination

if TYPE_CHECKING:
    from collections.abc import Awaitable

T = TypeVar("T")


class Page(Generic[T]):
    """A page of results from a paginated API endpoint.

    Provides convenient methods for iterating through paginated results.

    Example:
        >>> # Access current page data
        >>> page = client.document_types.list()
        >>> for item in page.data:
        ...     print(item.name)
        >>>
        >>> # Iterate through all pages
        >>> for page in client.document_types.list().iter_pages():
        ...     print(f"Page {page.page}: {len(page.data)} items")
        >>>
        >>> # Iterate through all items across pages
        >>> for item in client.document_types.list().auto_paging_iter():
        ...     print(item.name)
    """

    def __init__(
        self,
        data: list[T],
        pagination: Pagination,
        fetch_page: Callable[[int], Page[T]],
    ) -> None:
        """Initialize a Page.

        Args:
            data: The items in this page.
            pagination: Pagination metadata (total, page, limit).
            fetch_page: Function to fetch a specific page number.
        """
        self._data = data
        self._pagination = pagination
        self._fetch_page = fetch_page

    @property
    def data(self) -> list[T]:
        """The items in this page."""
        return self._data

    @property
    def total(self) -> int:
        """Total number of items across all pages."""
        return self._pagination.total

    @property
    def page(self) -> int:
        """Current page number (1-indexed)."""
        return self._pagination.page

    @property
    def limit(self) -> int:
        """Number of items per page."""
        return self._pagination.limit

    def has_next_page(self) -> bool:
        """Check if there are more pages available.

        Returns:
            True if there are more pages, False otherwise.
        """
        return self._pagination.page * self._pagination.limit < self._pagination.total

    def next_page(self) -> Page[T]:
        """Fetch the next page of results.

        Returns:
            The next page of results.

        Raises:
            StopIteration: If there are no more pages.
        """
        if not self.has_next_page():
            raise StopIteration("No more pages")
        return self._fetch_page(self._pagination.page + 1)

    def iter_pages(self) -> Iterator[Page[T]]:
        """Iterate through all pages starting from this page.

        Yields:
            Each page of results.

        Example:
            >>> for page in result.iter_pages():
            ...     print(f"Page {page.page}: {len(page.data)} items")
        """
        page = self
        while True:
            yield page
            if not page.has_next_page():
                break
            page = page.next_page()

    def auto_paging_iter(self) -> Iterator[T]:
        """Iterate through all items across all pages.

        Automatically fetches subsequent pages as needed.

        Yields:
            Each item from all pages.

        Example:
            >>> for item in result.auto_paging_iter():
            ...     print(item.name)
        """
        for page in self.iter_pages():
            yield from page.data

    def __iter__(self) -> Iterator[T]:
        """Iterate over items in this page only.

        For iterating across all pages, use iter_pages() or auto_paging_iter().
        """
        return iter(self._data)

    def __len__(self) -> int:
        """Return the number of items in this page."""
        return len(self._data)


class AsyncPage(Generic[T]):
    """An async page of results from a paginated API endpoint.

    Provides async methods for iterating through paginated results.

    Example:
        >>> # Access current page data
        >>> page = await client.document_types.list()
        >>> for item in page.data:
        ...     print(item.name)
        >>>
        >>> # Iterate through all pages
        >>> async for page in (await client.document_types.list()).iter_pages_async():
        ...     print(f"Page {page.page}: {len(page.data)} items")
        >>>
        >>> # Iterate through all items across pages
        >>> async for item in (await client.document_types.list()).auto_paging_iter_async():
        ...     print(item.name)
    """

    def __init__(
        self,
        data: list[T],
        pagination: Pagination,
        fetch_page: Callable[[int], Awaitable[AsyncPage[T]]],
    ) -> None:
        """Initialize an AsyncPage.

        Args:
            data: The items in this page.
            pagination: Pagination metadata (total, page, limit).
            fetch_page: Async function to fetch a specific page number.
        """
        self._data = data
        self._pagination = pagination
        self._fetch_page = fetch_page

    @property
    def data(self) -> list[T]:
        """The items in this page."""
        return self._data

    @property
    def total(self) -> int:
        """Total number of items across all pages."""
        return self._pagination.total

    @property
    def page(self) -> int:
        """Current page number (1-indexed)."""
        return self._pagination.page

    @property
    def limit(self) -> int:
        """Number of items per page."""
        return self._pagination.limit

    def has_next_page(self) -> bool:
        """Check if there are more pages available.

        Returns:
            True if there are more pages, False otherwise.
        """
        return self._pagination.page * self._pagination.limit < self._pagination.total

    async def next_page(self) -> AsyncPage[T]:
        """Fetch the next page of results.

        Returns:
            The next page of results.

        Raises:
            StopIteration: If there are no more pages.
        """
        if not self.has_next_page():
            raise StopIteration("No more pages")
        return await self._fetch_page(self._pagination.page + 1)

    async def iter_pages_async(self) -> AsyncIterator[AsyncPage[T]]:
        """Iterate through all pages starting from this page.

        Yields:
            Each page of results.

        Example:
            >>> async for page in result.iter_pages_async():
            ...     print(f"Page {page.page}: {len(page.data)} items")
        """
        page = self
        while True:
            yield page
            if not page.has_next_page():
                break
            page = await page.next_page()

    async def auto_paging_iter_async(self) -> AsyncIterator[T]:
        """Iterate through all items across all pages.

        Automatically fetches subsequent pages as needed.

        Yields:
            Each item from all pages.

        Example:
            >>> async for item in result.auto_paging_iter_async():
            ...     print(item.name)
        """
        async for page in self.iter_pages_async():
            for item in page.data:
                yield item

    def __iter__(self) -> Iterator[T]:
        """Iterate over items in this page only.

        For iterating across all pages, use iter_pages_async() or auto_paging_iter_async().
        """
        return iter(self._data)

    def __len__(self) -> int:
        """Return the number of items in this page."""
        return len(self._data)
