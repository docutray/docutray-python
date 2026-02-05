"""Tests for the raw response module."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx

from docutray._response import RawResponse


class TestRawResponse:
    """Tests for the RawResponse class."""

    def test_status_code(self) -> None:
        """RawResponse exposes status_code from underlying response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        raw = RawResponse(mock_response, lambda r: None)

        assert raw.status_code == 200

    def test_headers(self) -> None:
        """RawResponse exposes headers from underlying response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.headers = httpx.Headers({"x-request-id": "req_123", "content-type": "application/json"})

        raw = RawResponse(mock_response, lambda r: None)

        assert raw.headers["x-request-id"] == "req_123"
        assert raw.headers["content-type"] == "application/json"

    def test_http_response(self) -> None:
        """RawResponse provides access to underlying httpx.Response."""
        mock_response = MagicMock(spec=httpx.Response)

        raw = RawResponse(mock_response, lambda r: None)

        assert raw.http_response is mock_response

    def test_content(self) -> None:
        """RawResponse exposes raw bytes content."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.content = b'{"data": "test"}'

        raw = RawResponse(mock_response, lambda r: None)

        assert raw.content == b'{"data": "test"}'

    def test_text(self) -> None:
        """RawResponse exposes text content."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.text = '{"data": "test"}'

        raw = RawResponse(mock_response, lambda r: None)

        assert raw.text == '{"data": "test"}'

    def test_json(self) -> None:
        """RawResponse can parse JSON from response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"data": "test"}

        raw = RawResponse(mock_response, lambda r: None)

        assert raw.json() == {"data": "test"}

    def test_parse_calls_parse_func(self) -> None:
        """RawResponse.parse() calls the provided parse function."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "123", "name": "Test"}

        # Simple parse function that returns a dict
        def parse_func(r: httpx.Response) -> dict:
            return {"parsed": r.json()["name"]}

        raw = RawResponse(mock_response, parse_func)
        result = raw.parse()

        assert result == {"parsed": "Test"}

    def test_parse_returns_typed_result(self) -> None:
        """RawResponse.parse() returns properly typed result."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"value": 42}

        raw: RawResponse[int] = RawResponse(
            mock_response,
            lambda r: r.json()["value"],
        )
        result = raw.parse()

        assert result == 42
        assert isinstance(result, int)

    def test_multiple_parse_calls(self) -> None:
        """RawResponse.parse() can be called multiple times."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"count": 0}

        call_count = 0

        def parse_func(r: httpx.Response) -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        raw = RawResponse(mock_response, parse_func)

        # Each call to parse() invokes parse_func
        result1 = raw.parse()
        result2 = raw.parse()

        assert result1 == 1
        assert result2 == 2
