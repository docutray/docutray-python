"""Tests for retry logic."""

from __future__ import annotations

import random
from unittest import mock

import httpx
import pytest
import respx

from docutray import (
    APIConnectionError,
    APITimeoutError,
    AsyncClient,
    BadRequestError,
    Client,
    InternalServerError,
)
from docutray._constants import (
    DEFAULT_RETRY_CONFIG,
    RETRYABLE_STATUS_CODES,
    RetryConfig,
)
from docutray._http import calculate_delay, should_retry


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_config_values(self) -> None:
        """Default RetryConfig has expected values."""
        config = DEFAULT_RETRY_CONFIG
        assert config.max_retries == 2
        assert config.initial_delay == 0.5
        assert config.max_delay == 8.0
        assert config.exponential_base == 2.0
        assert config.jitter_min == 0.25
        assert config.jitter_max == 0.5
        assert config.retryable_status_codes == frozenset({429, 500, 502, 503, 504})

    def test_with_max_retries_creates_new_config(self) -> None:
        """with_max_retries creates a new config with updated value."""
        original = DEFAULT_RETRY_CONFIG
        modified = original.with_max_retries(5)

        assert modified.max_retries == 5
        assert modified.initial_delay == original.initial_delay
        assert modified.max_delay == original.max_delay
        assert original.max_retries == 2  # Original unchanged

    def test_config_is_frozen(self) -> None:
        """RetryConfig is immutable."""
        config = RetryConfig()
        with pytest.raises(AttributeError):
            config.max_retries = 10  # type: ignore


class TestRetryableStatusCodes:
    """Tests for retryable status codes."""

    def test_429_is_retryable(self) -> None:
        """429 (Rate Limit) is retryable."""
        assert 429 in RETRYABLE_STATUS_CODES

    def test_500_is_retryable(self) -> None:
        """500 (Internal Server Error) is retryable."""
        assert 500 in RETRYABLE_STATUS_CODES

    def test_502_is_retryable(self) -> None:
        """502 (Bad Gateway) is retryable."""
        assert 502 in RETRYABLE_STATUS_CODES

    def test_503_is_retryable(self) -> None:
        """503 (Service Unavailable) is retryable."""
        assert 503 in RETRYABLE_STATUS_CODES

    def test_504_is_retryable(self) -> None:
        """504 (Gateway Timeout) is retryable."""
        assert 504 in RETRYABLE_STATUS_CODES

    def test_400_is_not_retryable(self) -> None:
        """400 (Bad Request) is not retryable."""
        assert 400 not in RETRYABLE_STATUS_CODES

    def test_401_is_not_retryable(self) -> None:
        """401 (Unauthorized) is not retryable."""
        assert 401 not in RETRYABLE_STATUS_CODES

    def test_404_is_not_retryable(self) -> None:
        """404 (Not Found) is not retryable."""
        assert 404 not in RETRYABLE_STATUS_CODES


class TestCalculateDelay:
    """Tests for calculate_delay function."""

    def test_first_attempt_uses_initial_delay(self) -> None:
        """First attempt (0) uses initial delay plus jitter."""
        config = RetryConfig(initial_delay=0.5, jitter_min=0.0, jitter_max=0.0)
        delay = calculate_delay(0, config)
        assert delay == 0.5

    def test_exponential_backoff(self) -> None:
        """Delay increases exponentially."""
        config = RetryConfig(
            initial_delay=0.5,
            exponential_base=2.0,
            jitter_min=0.0,
            jitter_max=0.0,
        )
        assert calculate_delay(0, config) == 0.5
        assert calculate_delay(1, config) == 1.0
        assert calculate_delay(2, config) == 2.0
        assert calculate_delay(3, config) == 4.0

    def test_max_delay_cap(self) -> None:
        """Delay is capped at max_delay."""
        config = RetryConfig(
            initial_delay=0.5,
            exponential_base=2.0,
            max_delay=2.0,
            jitter_min=0.0,
            jitter_max=0.0,
        )
        # Would be 4.0 without cap
        assert calculate_delay(3, config) == 2.0

    def test_jitter_adds_randomness(self) -> None:
        """Jitter adds random factor to delay."""
        config = RetryConfig(
            initial_delay=1.0,
            jitter_min=0.25,
            jitter_max=0.5,
        )
        # With jitter, delay should be between 1.25 and 1.5
        with mock.patch.object(random, "uniform", return_value=0.25):
            delay = calculate_delay(0, config)
            assert delay == 1.25

        with mock.patch.object(random, "uniform", return_value=0.5):
            delay = calculate_delay(0, config)
            assert delay == 1.5

    def test_retry_after_takes_precedence(self) -> None:
        """Retry-After header value takes precedence when larger."""
        config = RetryConfig(initial_delay=0.5, jitter_min=0.0, jitter_max=0.0)
        delay = calculate_delay(0, config, retry_after=10.0)
        assert delay == 10.0

    def test_retry_after_ignored_when_smaller(self) -> None:
        """Retry-After is ignored when smaller than calculated delay."""
        config = RetryConfig(initial_delay=5.0, jitter_min=0.0, jitter_max=0.0)
        delay = calculate_delay(0, config, retry_after=1.0)
        assert delay == 5.0


class TestShouldRetry:
    """Tests for should_retry function."""

    def test_exhausted_retries(self) -> None:
        """Returns False when max retries exhausted."""
        config = RetryConfig(max_retries=2)
        assert should_retry(2, config, status_code=500) is False
        assert should_retry(3, config, status_code=500) is False

    def test_retryable_status_code(self) -> None:
        """Returns True for retryable status codes."""
        config = RetryConfig(max_retries=2)
        assert should_retry(0, config, status_code=429) is True
        assert should_retry(0, config, status_code=500) is True
        assert should_retry(0, config, status_code=503) is True

    def test_non_retryable_status_code(self) -> None:
        """Returns False for non-retryable status codes."""
        config = RetryConfig(max_retries=2)
        assert should_retry(0, config, status_code=400) is False
        assert should_retry(0, config, status_code=401) is False
        assert should_retry(0, config, status_code=404) is False

    def test_connection_error_respects_should_retry(self) -> None:
        """Connection errors respect their should_retry attribute."""
        config = RetryConfig(max_retries=2)

        retryable_error = APIConnectionError("Network error", should_retry=True)
        assert should_retry(0, config, exception=retryable_error) is True

        non_retryable_error = APIConnectionError("Fatal error", should_retry=False)
        assert should_retry(0, config, exception=non_retryable_error) is False

    def test_timeout_error_is_retryable(self) -> None:
        """Timeout errors are retryable."""
        config = RetryConfig(max_retries=2)
        error = APITimeoutError("Request timed out")
        assert should_retry(0, config, exception=error) is True


class TestClientMaxRetries:
    """Tests for max_retries client configuration."""

    def test_default_max_retries(self) -> None:
        """Client defaults to 2 max retries."""
        client = Client(api_key="sk_test")
        assert client._max_retries == 2
        client.close()

    def test_custom_max_retries(self) -> None:
        """Client accepts custom max_retries."""
        client = Client(api_key="sk_test", max_retries=5)
        assert client._max_retries == 5
        client.close()

    def test_zero_retries(self) -> None:
        """Client can be configured with zero retries."""
        client = Client(api_key="sk_test", max_retries=0)
        assert client._max_retries == 0
        client.close()

    def test_negative_max_retries_raises_error(self) -> None:
        """Client raises ValueError for negative max_retries."""
        with pytest.raises(ValueError, match="max_retries must be >= 0"):
            Client(api_key="sk_test", max_retries=-1)

    def test_async_client_negative_max_retries_raises_error(self) -> None:
        """AsyncClient raises ValueError for negative max_retries."""
        with pytest.raises(ValueError, match="max_retries must be >= 0"):
            AsyncClient(api_key="sk_test", max_retries=-1)


class TestRetryBehavior:
    """Integration tests for retry behavior."""

    @respx.mock
    def test_retries_on_500(self) -> None:
        """Client retries on 500 errors."""
        # First two calls fail, third succeeds
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.Response(500, text="Server Error"),
                httpx.Response(500, text="Server Error"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        client = Client(api_key="sk_test", max_retries=2)
        response = client._http.request("GET", "/test")

        assert response.status_code == 200
        assert route.call_count == 3
        client.close()

    @respx.mock
    def test_retries_on_429(self) -> None:
        """Client retries on 429 with Retry-After."""
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "0.01"}),
                httpx.Response(200, json={"success": True}),
            ]
        )

        client = Client(api_key="sk_test", max_retries=2)
        response = client._http.request("GET", "/test")

        assert response.status_code == 200
        assert route.call_count == 2
        client.close()

    @respx.mock
    def test_no_retry_on_400(self) -> None:
        """Client does not retry on 400 errors."""
        route = respx.get("https://app.docutray.com/test").mock(
            return_value=httpx.Response(400, json={"error": "Bad request"})
        )

        client = Client(api_key="sk_test", max_retries=2)
        with pytest.raises(BadRequestError):
            client._http.request("GET", "/test")

        assert route.call_count == 1
        client.close()

    @respx.mock
    def test_raises_after_max_retries(self) -> None:
        """Client raises after exhausting retries."""
        respx.get("https://app.docutray.com/test").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        client = Client(api_key="sk_test", max_retries=2)
        with pytest.raises(InternalServerError):
            client._http.request("GET", "/test")

        client.close()

    @respx.mock
    def test_zero_retries_no_retry(self) -> None:
        """Client with max_retries=0 doesn't retry."""
        route = respx.get("https://app.docutray.com/test").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        client = Client(api_key="sk_test", max_retries=0)
        with pytest.raises(InternalServerError):
            client._http.request("GET", "/test")

        assert route.call_count == 1
        client.close()


class TestRetryLogging:
    """Tests for retry logging."""

    @respx.mock
    def test_logging_disabled_by_default(self) -> None:
        """Retry logging is disabled by default."""
        import logging

        respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.Response(500, text="Server Error"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        # Set up log capture
        logger = logging.getLogger("docutray")
        with mock.patch.object(logger, "warning") as mock_warning:
            client = Client(api_key="sk_test", max_retries=1)
            client._http.request("GET", "/test")
            mock_warning.assert_not_called()
            client.close()

    @respx.mock
    def test_logging_enabled_via_env_var(self) -> None:
        """Retry logging can be enabled via environment variable."""
        import logging
        import os

        respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.Response(500, text="Server Error"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        # Set up log capture
        logger = logging.getLogger("docutray")
        with mock.patch.dict(os.environ, {"DOCUTRAY_LOG": "1"}):
            with mock.patch.object(logger, "warning") as mock_warning:
                client = Client(api_key="sk_test", max_retries=1)
                client._http.request("GET", "/test")
                mock_warning.assert_called()
                client.close()


class TestTimeoutRetryBehavior:
    """Integration tests for timeout retry behavior."""

    @respx.mock
    def test_retries_on_timeout(self) -> None:
        """Client retries on timeout errors."""
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.TimeoutException("Connection timed out"),
                httpx.TimeoutException("Connection timed out"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        client = Client(api_key="sk_test", max_retries=2)
        response = client._http.request("GET", "/test")

        assert response.status_code == 200
        assert route.call_count == 3
        client.close()

    @respx.mock
    def test_raises_timeout_after_max_retries(self) -> None:
        """Client raises APITimeoutError after exhausting retries."""
        respx.get("https://app.docutray.com/test").mock(
            side_effect=httpx.TimeoutException("Connection timed out")
        )

        client = Client(api_key="sk_test", max_retries=2)
        with pytest.raises(APITimeoutError):
            client._http.request("GET", "/test")

        client.close()

    @respx.mock
    def test_retries_on_connection_error(self) -> None:
        """Client retries on connection errors."""
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.ConnectError("Connection refused"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        client = Client(api_key="sk_test", max_retries=2)
        response = client._http.request("GET", "/test")

        assert response.status_code == 200
        assert route.call_count == 3
        client.close()

    @respx.mock
    def test_raises_connection_error_after_max_retries(self) -> None:
        """Client raises APIConnectionError after exhausting retries."""
        respx.get("https://app.docutray.com/test").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        client = Client(api_key="sk_test", max_retries=2)
        with pytest.raises(APIConnectionError):
            client._http.request("GET", "/test")

        client.close()


class TestAsyncTimeoutRetryBehavior:
    """Integration tests for async timeout retry behavior."""

    @respx.mock
    async def test_async_retries_on_timeout(self) -> None:
        """AsyncClient retries on timeout errors."""
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.TimeoutException("Connection timed out"),
                httpx.TimeoutException("Connection timed out"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            response = await client._http.request("GET", "/test")

            assert response.status_code == 200
            assert route.call_count == 3

    @respx.mock
    async def test_async_raises_timeout_after_max_retries(self) -> None:
        """AsyncClient raises APITimeoutError after exhausting retries."""
        respx.get("https://app.docutray.com/test").mock(
            side_effect=httpx.TimeoutException("Connection timed out")
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            with pytest.raises(APITimeoutError):
                await client._http.request("GET", "/test")

    @respx.mock
    async def test_async_retries_on_connection_error(self) -> None:
        """AsyncClient retries on connection errors."""
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.ConnectError("Connection refused"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            response = await client._http.request("GET", "/test")

            assert response.status_code == 200
            assert route.call_count == 3

    @respx.mock
    async def test_async_raises_connection_error_after_max_retries(self) -> None:
        """AsyncClient raises APIConnectionError after exhausting retries."""
        respx.get("https://app.docutray.com/test").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            with pytest.raises(APIConnectionError):
                await client._http.request("GET", "/test")


class TestAsyncRetryBehavior:
    """Integration tests for async retry behavior."""

    @respx.mock
    async def test_async_retries_on_500(self) -> None:
        """AsyncClient retries on 500 errors."""
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.Response(500, text="Server Error"),
                httpx.Response(500, text="Server Error"),
                httpx.Response(200, json={"success": True}),
            ]
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            response = await client._http.request("GET", "/test")

            assert response.status_code == 200
            assert route.call_count == 3

    @respx.mock
    async def test_async_retries_on_429(self) -> None:
        """AsyncClient retries on 429 with Retry-After."""
        route = respx.get("https://app.docutray.com/test").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "0.01"}),
                httpx.Response(200, json={"success": True}),
            ]
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            response = await client._http.request("GET", "/test")

            assert response.status_code == 200
            assert route.call_count == 2

    @respx.mock
    async def test_async_no_retry_on_400(self) -> None:
        """AsyncClient does not retry on 400 errors."""
        route = respx.get("https://app.docutray.com/test").mock(
            return_value=httpx.Response(400, json={"error": "Bad request"})
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            with pytest.raises(BadRequestError):
                await client._http.request("GET", "/test")

            assert route.call_count == 1

    @respx.mock
    async def test_async_raises_after_max_retries(self) -> None:
        """AsyncClient raises after exhausting retries."""
        respx.get("https://app.docutray.com/test").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        async with AsyncClient(api_key="sk_test", max_retries=2) as client:
            with pytest.raises(InternalServerError):
                await client._http.request("GET", "/test")

    @respx.mock
    async def test_async_zero_retries_no_retry(self) -> None:
        """AsyncClient with max_retries=0 doesn't retry."""
        route = respx.get("https://app.docutray.com/test").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        async with AsyncClient(api_key="sk_test", max_retries=0) as client:
            with pytest.raises(InternalServerError):
                await client._http.request("GET", "/test")

            assert route.call_count == 1
