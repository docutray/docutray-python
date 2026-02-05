"""Tests for the pagination module."""

from __future__ import annotations

import pytest

from docutray._pagination import AsyncPage, Page
from docutray.types.shared import Pagination


class TestPage:
    """Tests for the Page class."""

    def test_page_properties(self) -> None:
        """Page exposes data and pagination info."""
        pagination = Pagination(total=100, page=1, limit=10)
        page: Page[str] = Page(
            data=["a", "b", "c"],
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        assert page.data == ["a", "b", "c"]
        assert page.total == 100
        assert page.page == 1
        assert page.limit == 10

    def test_page_len(self) -> None:
        """Page length returns number of items in current page."""
        pagination = Pagination(total=100, page=1, limit=10)
        page: Page[str] = Page(
            data=["a", "b", "c"],
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        assert len(page) == 3

    def test_page_iteration(self) -> None:
        """Page is iterable over current page items only."""
        pagination = Pagination(total=100, page=1, limit=10)
        page: Page[str] = Page(
            data=["a", "b", "c"],
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        items = list(page)
        assert items == ["a", "b", "c"]

    def test_has_next_page_true(self) -> None:
        """has_next_page returns True when more pages exist."""
        pagination = Pagination(total=100, page=1, limit=10)
        page: Page[str] = Page(
            data=["a"] * 10,
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        assert page.has_next_page() is True

    def test_has_next_page_false_on_last_page(self) -> None:
        """has_next_page returns False on last page."""
        pagination = Pagination(total=25, page=3, limit=10)
        page: Page[str] = Page(
            data=["a"] * 5,
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        assert page.has_next_page() is False

    def test_has_next_page_false_on_exact_boundary(self) -> None:
        """has_next_page returns False when on exact boundary."""
        pagination = Pagination(total=20, page=2, limit=10)
        page: Page[str] = Page(
            data=["a"] * 10,
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        assert page.has_next_page() is False

    def test_has_next_page_empty_page(self) -> None:
        """has_next_page returns False for empty results."""
        pagination = Pagination(total=0, page=1, limit=10)
        page: Page[str] = Page(
            data=[],
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        assert page.has_next_page() is False

    def test_next_page_fetches_next(self) -> None:
        """next_page calls fetch_page with next page number."""
        fetch_calls: list[int] = []

        def mock_fetch(page_num: int) -> Page[str]:
            fetch_calls.append(page_num)
            return Page(
                data=["b"],
                pagination=Pagination(total=20, page=page_num, limit=10),
                fetch_page=mock_fetch,
            )

        pagination = Pagination(total=20, page=1, limit=10)
        page: Page[str] = Page(
            data=["a"],
            pagination=pagination,
            fetch_page=mock_fetch,
        )

        next_page = page.next_page()

        assert fetch_calls == [2]
        assert next_page.page == 2
        assert next_page.data == ["b"]

    def test_next_page_raises_on_last_page(self) -> None:
        """next_page raises StopIteration on last page."""
        pagination = Pagination(total=10, page=1, limit=10)
        page: Page[str] = Page(
            data=["a"] * 10,
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        with pytest.raises(StopIteration, match="No more pages"):
            page.next_page()

    def test_iter_pages_single_page(self) -> None:
        """iter_pages yields single page when total fits in one page."""
        pagination = Pagination(total=5, page=1, limit=10)
        page: Page[str] = Page(
            data=["a", "b", "c", "d", "e"],
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        pages = list(page.iter_pages())

        assert len(pages) == 1
        assert pages[0].data == ["a", "b", "c", "d", "e"]

    def test_iter_pages_multi_page(self) -> None:
        """iter_pages yields all pages sequentially."""
        def mock_fetch(page_num: int) -> Page[str]:
            if page_num == 1:
                return Page(
                    data=["a", "b"],
                    pagination=Pagination(total=5, page=1, limit=2),
                    fetch_page=mock_fetch,
                )
            elif page_num == 2:
                return Page(
                    data=["c", "d"],
                    pagination=Pagination(total=5, page=2, limit=2),
                    fetch_page=mock_fetch,
                )
            else:
                return Page(
                    data=["e"],
                    pagination=Pagination(total=5, page=3, limit=2),
                    fetch_page=mock_fetch,
                )

        page = mock_fetch(1)
        pages = list(page.iter_pages())

        assert len(pages) == 3
        assert pages[0].data == ["a", "b"]
        assert pages[1].data == ["c", "d"]
        assert pages[2].data == ["e"]

    def test_auto_paging_iter_single_page(self) -> None:
        """auto_paging_iter yields all items from single page."""
        pagination = Pagination(total=3, page=1, limit=10)
        page: Page[str] = Page(
            data=["a", "b", "c"],
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        items = list(page.auto_paging_iter())

        assert items == ["a", "b", "c"]

    def test_auto_paging_iter_multi_page(self) -> None:
        """auto_paging_iter yields all items across pages."""
        def mock_fetch(page_num: int) -> Page[str]:
            if page_num == 1:
                return Page(
                    data=["a", "b"],
                    pagination=Pagination(total=5, page=1, limit=2),
                    fetch_page=mock_fetch,
                )
            elif page_num == 2:
                return Page(
                    data=["c", "d"],
                    pagination=Pagination(total=5, page=2, limit=2),
                    fetch_page=mock_fetch,
                )
            else:
                return Page(
                    data=["e"],
                    pagination=Pagination(total=5, page=3, limit=2),
                    fetch_page=mock_fetch,
                )

        page = mock_fetch(1)
        items = list(page.auto_paging_iter())

        assert items == ["a", "b", "c", "d", "e"]

    def test_empty_page(self) -> None:
        """Empty page handles all operations gracefully."""
        pagination = Pagination(total=0, page=1, limit=10)
        page: Page[str] = Page(
            data=[],
            pagination=pagination,
            fetch_page=lambda p: page,
        )

        assert len(page) == 0
        assert list(page) == []
        assert page.has_next_page() is False
        assert list(page.iter_pages()) == [page]
        assert list(page.auto_paging_iter()) == []


class TestAsyncPage:
    """Tests for the AsyncPage class."""

    def test_async_page_properties(self) -> None:
        """AsyncPage exposes data and pagination info."""
        pagination = Pagination(total=100, page=1, limit=10)

        async def mock_fetch(p: int) -> AsyncPage[str]:
            return page

        page: AsyncPage[str] = AsyncPage(
            data=["a", "b", "c"],
            pagination=pagination,
            fetch_page=mock_fetch,
        )

        assert page.data == ["a", "b", "c"]
        assert page.total == 100
        assert page.page == 1
        assert page.limit == 10

    def test_async_page_len(self) -> None:
        """AsyncPage length returns number of items in current page."""
        pagination = Pagination(total=100, page=1, limit=10)

        async def mock_fetch(p: int) -> AsyncPage[str]:
            return page

        page: AsyncPage[str] = AsyncPage(
            data=["a", "b", "c"],
            pagination=pagination,
            fetch_page=mock_fetch,
        )

        assert len(page) == 3

    def test_async_page_sync_iteration(self) -> None:
        """AsyncPage supports sync iteration over current page."""
        pagination = Pagination(total=100, page=1, limit=10)

        async def mock_fetch(p: int) -> AsyncPage[str]:
            return page

        page: AsyncPage[str] = AsyncPage(
            data=["a", "b", "c"],
            pagination=pagination,
            fetch_page=mock_fetch,
        )

        items = list(page)
        assert items == ["a", "b", "c"]

    def test_async_page_has_next_page(self) -> None:
        """AsyncPage has_next_page works synchronously."""
        pagination = Pagination(total=100, page=1, limit=10)

        async def mock_fetch(p: int) -> AsyncPage[str]:
            return page

        page: AsyncPage[str] = AsyncPage(
            data=["a"] * 10,
            pagination=pagination,
            fetch_page=mock_fetch,
        )

        assert page.has_next_page() is True

    @pytest.mark.asyncio
    async def test_async_next_page(self) -> None:
        """AsyncPage next_page fetches next page asynchronously."""
        fetch_calls: list[int] = []

        async def mock_fetch(page_num: int) -> AsyncPage[str]:
            fetch_calls.append(page_num)
            return AsyncPage(
                data=["b"],
                pagination=Pagination(total=20, page=page_num, limit=10),
                fetch_page=mock_fetch,
            )

        pagination = Pagination(total=20, page=1, limit=10)
        page: AsyncPage[str] = AsyncPage(
            data=["a"],
            pagination=pagination,
            fetch_page=mock_fetch,
        )

        next_page = await page.next_page()

        assert fetch_calls == [2]
        assert next_page.page == 2

    @pytest.mark.asyncio
    async def test_async_iter_pages(self) -> None:
        """AsyncPage iter_pages_async yields all pages."""
        async def mock_fetch(page_num: int) -> AsyncPage[str]:
            if page_num == 1:
                return AsyncPage(
                    data=["a", "b"],
                    pagination=Pagination(total=5, page=1, limit=2),
                    fetch_page=mock_fetch,
                )
            elif page_num == 2:
                return AsyncPage(
                    data=["c", "d"],
                    pagination=Pagination(total=5, page=2, limit=2),
                    fetch_page=mock_fetch,
                )
            else:
                return AsyncPage(
                    data=["e"],
                    pagination=Pagination(total=5, page=3, limit=2),
                    fetch_page=mock_fetch,
                )

        page = await mock_fetch(1)
        pages = [p async for p in page.iter_pages_async()]

        assert len(pages) == 3
        assert pages[0].data == ["a", "b"]
        assert pages[1].data == ["c", "d"]
        assert pages[2].data == ["e"]

    @pytest.mark.asyncio
    async def test_async_auto_paging_iter(self) -> None:
        """AsyncPage auto_paging_iter_async yields all items."""
        async def mock_fetch(page_num: int) -> AsyncPage[str]:
            if page_num == 1:
                return AsyncPage(
                    data=["a", "b"],
                    pagination=Pagination(total=5, page=1, limit=2),
                    fetch_page=mock_fetch,
                )
            elif page_num == 2:
                return AsyncPage(
                    data=["c", "d"],
                    pagination=Pagination(total=5, page=2, limit=2),
                    fetch_page=mock_fetch,
                )
            else:
                return AsyncPage(
                    data=["e"],
                    pagination=Pagination(total=5, page=3, limit=2),
                    fetch_page=mock_fetch,
                )

        page = await mock_fetch(1)
        items = [item async for item in page.auto_paging_iter_async()]

        assert items == ["a", "b", "c", "d", "e"]
