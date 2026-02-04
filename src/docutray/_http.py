"""HTTP transport layer for the DocuTray SDK."""

from __future__ import annotations

import asyncio
import logging
import os
import random
import time
from typing import Any

import httpx

from ._constants import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    ENV_VAR_LOG,
    RetryConfig,
)
from ._exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    RateLimitError,
    raise_for_status,
)
from ._version import __version__

# Configure logger
logger = logging.getLogger("docutray")


def _is_logging_enabled() -> bool:
    """Check if logging is enabled via environment variable.

    Returns:
        True if DOCUTRAY_LOG is set to a truthy value.
    """
    log_value = os.environ.get(ENV_VAR_LOG, "").lower()
    return log_value in ("1", "true", "yes", "on", "debug")


def build_headers(api_key: str) -> dict[str, str]:
    """Build the default headers for API requests.

    Args:
        api_key: The API key for authentication.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": f"docutray-python/{__version__}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def calculate_delay(
    attempt: int,
    config: RetryConfig,
    retry_after: float | None = None,
) -> float:
    """Calculate the delay before the next retry attempt.

    Uses exponential backoff with jitter.

    Args:
        attempt: The current attempt number (0-indexed).
        config: The retry configuration.
        retry_after: Optional Retry-After header value in seconds.

    Returns:
        The delay in seconds before the next retry.
    """
    # Calculate exponential backoff
    delay = min(
        config.initial_delay * (config.exponential_base**attempt),
        config.max_delay,
    )

    # Add jitter (random factor between jitter_min and jitter_max of delay)
    jitter_factor = random.uniform(config.jitter_min, config.jitter_max)
    delay += delay * jitter_factor

    # Respect Retry-After header if present
    if retry_after is not None:
        delay = max(delay, retry_after)

    return delay


def should_retry(
    attempt: int,
    config: RetryConfig,
    exception: Exception | None = None,
    status_code: int | None = None,
) -> bool:
    """Determine whether a request should be retried.

    Args:
        attempt: The current attempt number (0-indexed).
        config: The retry configuration.
        exception: The exception that occurred, if any.
        status_code: The HTTP status code, if any.

    Returns:
        True if the request should be retried.
    """
    # Don't retry if we've exhausted retries
    if attempt >= config.max_retries:
        return False

    # Retry connection errors (they have should_retry attribute)
    if isinstance(exception, APIConnectionError):
        return exception.should_retry

    # Retry specific status codes
    if status_code is not None and status_code in config.retryable_status_codes:
        return True

    return False


def _get_retry_after(response: httpx.Response) -> float | None:
    """Extract Retry-After header value from response.

    Args:
        response: The HTTP response.

    Returns:
        The Retry-After value in seconds, or None if not present.
    """
    retry_after = response.headers.get("retry-after") or response.headers.get("Retry-After")
    if retry_after is None:
        return None
    try:
        return float(retry_after)
    except (ValueError, TypeError):
        return None


class SyncHTTPClient:
    """Synchronous HTTP client wrapper around httpx with retry support."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: httpx.Timeout | float | None = None,
        retry_config: RetryConfig | None = None,
    ) -> None:
        """Initialize the sync HTTP client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for API requests.
            timeout: Request timeout configuration.
            retry_config: Configuration for retry behavior.
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._retry_config = retry_config if retry_config is not None else DEFAULT_RETRY_CONFIG
        self._client: httpx.Client | None = None

    def _ensure_client(self) -> httpx.Client:
        """Ensure the httpx client is initialized.

        Returns:
            The httpx client instance.
        """
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._base_url,
                headers=build_headers(self._api_key),
                timeout=self._timeout,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an HTTP request with automatic retry.

        Args:
            method: The HTTP method.
            path: The request path.
            **kwargs: Additional arguments to pass to httpx.

        Returns:
            The HTTP response.

        Raises:
            APITimeoutError: If the request times out after all retries.
            APIConnectionError: If a connection error occurs after all retries.
            APIError: If the API returns an error response after all retries.
        """
        client = self._ensure_client()
        last_exception: Exception | None = None
        logging_enabled = _is_logging_enabled()

        for attempt in range(self._retry_config.max_retries + 1):
            try:
                response = client.request(method, path, **kwargs)

                # Check for HTTP errors
                if not response.is_success:
                    status_code = response.status_code

                    # Check if we should retry
                    if should_retry(attempt, self._retry_config, status_code=status_code):
                        retry_after = _get_retry_after(response)
                        delay = calculate_delay(attempt, self._retry_config, retry_after)

                        if logging_enabled:
                            logger.warning(
                                "Request failed with status %d, retrying in %.2fs (attempt %d/%d)",
                                status_code,
                                delay,
                                attempt + 1,
                                self._retry_config.max_retries + 1,
                            )

                        time.sleep(delay)
                        continue

                    # Not retryable, raise immediately
                    raise_for_status(response)

                return response

            except httpx.TimeoutException as e:
                last_exception = APITimeoutError(str(e))

                if should_retry(attempt, self._retry_config, exception=last_exception):
                    delay = calculate_delay(attempt, self._retry_config)

                    if logging_enabled:
                        logger.warning(
                            "Request timed out, retrying in %.2fs (attempt %d/%d)",
                            delay,
                            attempt + 1,
                            self._retry_config.max_retries + 1,
                        )

                    time.sleep(delay)
                    continue

                raise last_exception from e

            except httpx.RequestError as e:
                last_exception = APIConnectionError(str(e))

                if should_retry(attempt, self._retry_config, exception=last_exception):
                    delay = calculate_delay(attempt, self._retry_config)

                    if logging_enabled:
                        logger.warning(
                            "Connection error: %s, retrying in %.2fs (attempt %d/%d)",
                            str(e),
                            delay,
                            attempt + 1,
                            self._retry_config.max_retries + 1,
                        )

                    time.sleep(delay)
                    continue

                raise last_exception from e

            except (APIError, RateLimitError):
                # Re-raise API errors (they were already processed)
                raise

        # Should not reach here, but just in case
        if last_exception is not None:
            raise last_exception

        raise APIConnectionError("Request failed after all retries")


class AsyncHTTPClient:
    """Asynchronous HTTP client wrapper around httpx with retry support."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: httpx.Timeout | float | None = None,
        retry_config: RetryConfig | None = None,
    ) -> None:
        """Initialize the async HTTP client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for API requests.
            timeout: Request timeout configuration.
            retry_config: Configuration for retry behavior.
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._retry_config = retry_config if retry_config is not None else DEFAULT_RETRY_CONFIG
        self._client: httpx.AsyncClient | None = None

    def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the httpx async client is initialized.

        Returns:
            The httpx async client instance.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=build_headers(self._api_key),
                timeout=self._timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async HTTP request with automatic retry.

        Args:
            method: The HTTP method.
            path: The request path.
            **kwargs: Additional arguments to pass to httpx.

        Returns:
            The HTTP response.

        Raises:
            APITimeoutError: If the request times out after all retries.
            APIConnectionError: If a connection error occurs after all retries.
            APIError: If the API returns an error response after all retries.
        """
        client = self._ensure_client()
        last_exception: Exception | None = None
        logging_enabled = _is_logging_enabled()

        for attempt in range(self._retry_config.max_retries + 1):
            try:
                response = await client.request(method, path, **kwargs)

                # Check for HTTP errors
                if not response.is_success:
                    status_code = response.status_code

                    # Check if we should retry
                    if should_retry(attempt, self._retry_config, status_code=status_code):
                        retry_after = _get_retry_after(response)
                        delay = calculate_delay(attempt, self._retry_config, retry_after)

                        if logging_enabled:
                            logger.warning(
                                "Request failed with status %d, retrying in %.2fs (attempt %d/%d)",
                                status_code,
                                delay,
                                attempt + 1,
                                self._retry_config.max_retries + 1,
                            )

                        await asyncio.sleep(delay)
                        continue

                    # Not retryable, raise immediately
                    raise_for_status(response)

                return response

            except httpx.TimeoutException as e:
                last_exception = APITimeoutError(str(e))

                if should_retry(attempt, self._retry_config, exception=last_exception):
                    delay = calculate_delay(attempt, self._retry_config)

                    if logging_enabled:
                        logger.warning(
                            "Request timed out, retrying in %.2fs (attempt %d/%d)",
                            delay,
                            attempt + 1,
                            self._retry_config.max_retries + 1,
                        )

                    await asyncio.sleep(delay)
                    continue

                raise last_exception from e

            except httpx.RequestError as e:
                last_exception = APIConnectionError(str(e))

                if should_retry(attempt, self._retry_config, exception=last_exception):
                    delay = calculate_delay(attempt, self._retry_config)

                    if logging_enabled:
                        logger.warning(
                            "Connection error: %s, retrying in %.2fs (attempt %d/%d)",
                            str(e),
                            delay,
                            attempt + 1,
                            self._retry_config.max_retries + 1,
                        )

                    await asyncio.sleep(delay)
                    continue

                raise last_exception from e

            except (APIError, RateLimitError):
                # Re-raise API errors (they were already processed)
                raise

        # Should not reach here, but just in case
        if last_exception is not None:
            raise last_exception

        raise APIConnectionError("Request failed after all retries")
