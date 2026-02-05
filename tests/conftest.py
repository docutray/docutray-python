"""Shared test fixtures for the DocuTray SDK tests."""

from __future__ import annotations

import pytest
import respx

from docutray import AsyncClient, Client


@pytest.fixture
def api_key() -> str:
    """Provide a test API key."""
    return "dt_test_key_123"


@pytest.fixture
def base_url() -> str:
    """Provide a test base URL."""
    return "https://api.test.docutray.com"


@pytest.fixture
def client(api_key: str, base_url: str) -> Client:
    """Provide a configured sync client for testing."""
    client = Client(api_key=api_key, base_url=base_url)
    yield client
    client.close()


@pytest.fixture
async def async_client(api_key: str, base_url: str) -> AsyncClient:
    """Provide a configured async client for testing."""
    client = AsyncClient(api_key=api_key, base_url=base_url)
    yield client
    await client.close()


@pytest.fixture
def mock_api(base_url: str):
    """Provide a respx mock for the API."""
    with respx.mock(base_url=base_url, assert_all_called=False) as respx_mock:
        yield respx_mock
