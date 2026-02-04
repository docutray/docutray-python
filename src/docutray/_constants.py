"""Constants for the DocuTray SDK."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

# API Configuration
DEFAULT_BASE_URL = "https://api.docutray.com"
ENV_VAR_API_KEY = "DOCUTRAY_API_KEY"
ENV_VAR_LOG = "DOCUTRAY_LOG"

# Timeout Configuration (in seconds)
# Using httpx.Timeout for granular control
DEFAULT_TIMEOUT = httpx.Timeout(
    connect=5.0,   # Time to establish connection
    read=60.0,     # Time to read response
    write=60.0,    # Time to send request
    pool=10.0,     # Time waiting for connection from pool
)

# For backward compatibility
DEFAULT_TIMEOUT_SECONDS = 60.0

# Retry Configuration
DEFAULT_MAX_RETRIES = 2
INITIAL_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 8.0  # seconds
EXPONENTIAL_BASE = 2.0
JITTER_MIN = 0.25  # 25% of delay
JITTER_MAX = 0.5   # 50% of delay

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries in seconds.
        exponential_base: Base for exponential backoff calculation.
        jitter_min: Minimum jitter as fraction of delay (0.0-1.0).
        jitter_max: Maximum jitter as fraction of delay (0.0-1.0).
        retryable_status_codes: HTTP status codes that should trigger a retry.
    """

    max_retries: int = DEFAULT_MAX_RETRIES
    initial_delay: float = INITIAL_RETRY_DELAY
    max_delay: float = MAX_RETRY_DELAY
    exponential_base: float = EXPONENTIAL_BASE
    jitter_min: float = JITTER_MIN
    jitter_max: float = JITTER_MAX
    retryable_status_codes: frozenset[int] = RETRYABLE_STATUS_CODES

    def with_max_retries(self, max_retries: int) -> RetryConfig:
        """Create a new config with a different max_retries value.

        Args:
            max_retries: The new maximum number of retries.

        Returns:
            A new RetryConfig with the updated value.
        """
        return RetryConfig(
            max_retries=max_retries,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter_min=self.jitter_min,
            jitter_max=self.jitter_max,
            retryable_status_codes=self.retryable_status_codes,
        )


# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig()

# Async Polling Configuration
DEFAULT_POLL_INTERVAL = 2.0  # seconds between status checks
DEFAULT_POLL_TIMEOUT = 300.0  # 5 minutes total timeout
