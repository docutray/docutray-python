"""Tests for Client and AsyncClient instantiation and configuration."""

from __future__ import annotations

import os
from unittest import mock

import pytest

from docutray import AsyncClient, AuthenticationError, Client


class TestClientInstantiation:
    """Tests for Client instantiation."""

    def test_client_with_explicit_api_key(self) -> None:
        """Client can be created with explicit API key."""
        client = Client(api_key="sk_test_123")
        assert client._api_key == "sk_test_123"
        client.close()

    def test_client_with_env_var(self) -> None:
        """Client reads API key from environment variable."""
        with mock.patch.dict(os.environ, {"DOCUTRAY_API_KEY": "sk_env_456"}):
            client = Client()
            assert client._api_key == "sk_env_456"
            client.close()

    def test_explicit_api_key_takes_precedence(self) -> None:
        """Explicit API key takes precedence over environment variable."""
        with mock.patch.dict(os.environ, {"DOCUTRAY_API_KEY": "sk_env_456"}):
            client = Client(api_key="sk_explicit_789")
            assert client._api_key == "sk_explicit_789"
            client.close()

    def test_client_raises_without_api_key(self) -> None:
        """Client raises AuthenticationError when no API key is available."""
        with mock.patch.dict(os.environ, {}, clear=True):
            # Remove the env var if it exists
            os.environ.pop("DOCUTRAY_API_KEY", None)
            with pytest.raises(AuthenticationError) as exc_info:
                Client()
            assert "No API key provided" in str(exc_info.value)


class TestAsyncClientInstantiation:
    """Tests for AsyncClient instantiation."""

    def test_async_client_with_explicit_api_key(self) -> None:
        """AsyncClient can be created with explicit API key."""
        client = AsyncClient(api_key="sk_test_123")
        assert client._api_key == "sk_test_123"

    def test_async_client_with_env_var(self) -> None:
        """AsyncClient reads API key from environment variable."""
        with mock.patch.dict(os.environ, {"DOCUTRAY_API_KEY": "sk_env_456"}):
            client = AsyncClient()
            assert client._api_key == "sk_env_456"

    def test_async_client_raises_without_api_key(self) -> None:
        """AsyncClient raises AuthenticationError when no API key is available."""
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DOCUTRAY_API_KEY", None)
            with pytest.raises(AuthenticationError):
                AsyncClient()


class TestClientConfiguration:
    """Tests for client configuration options."""

    def test_default_base_url(self) -> None:
        """Client uses default base URL when not specified."""
        client = Client(api_key="sk_test")
        assert client._base_url == "https://api.docutray.com"
        client.close()

    def test_custom_base_url(self) -> None:
        """Client uses custom base URL when specified."""
        client = Client(api_key="sk_test", base_url="https://custom.api.com")
        assert client._base_url == "https://custom.api.com"
        client.close()

    def test_default_timeout(self) -> None:
        """Client uses default granular timeout when not specified."""
        import httpx

        client = Client(api_key="sk_test")
        assert isinstance(client._timeout, httpx.Timeout)
        assert client._timeout.connect == 5.0
        assert client._timeout.read == 60.0
        assert client._timeout.write == 60.0
        assert client._timeout.pool == 10.0
        client.close()

    def test_custom_timeout(self) -> None:
        """Client uses custom timeout when specified."""
        client = Client(api_key="sk_test", timeout=30.0)
        assert client._timeout == 30.0
        client.close()


class TestContextManagers:
    """Tests for context manager functionality."""

    def test_sync_context_manager(self) -> None:
        """Client works as a sync context manager."""
        with Client(api_key="sk_test_123") as client:
            assert client._api_key == "sk_test_123"
        # Client should be closed after exiting context
        assert client._http_client is None

    async def test_async_context_manager(self) -> None:
        """AsyncClient works as an async context manager."""
        async with AsyncClient(api_key="sk_test_123") as client:
            assert client._api_key == "sk_test_123"
        # Client should be closed after exiting context
        assert client._http_client is None


class TestSafeRepr:
    """Tests for credential masking in repr."""

    def test_api_key_hidden_in_repr(self) -> None:
        """API key is masked in repr output."""
        client = Client(api_key="sk_secret_key_12345")
        repr_str = repr(client)
        assert "sk_secret_key_12345" not in repr_str
        assert "sk_se" in repr_str  # First 5 chars visible
        assert "***" in repr_str
        client.close()

    def test_async_client_api_key_hidden_in_repr(self) -> None:
        """API key is masked in AsyncClient repr output."""
        client = AsyncClient(api_key="sk_secret_key_12345")
        repr_str = repr(client)
        assert "sk_secret_key_12345" not in repr_str
        assert "sk_se" in repr_str
        assert "***" in repr_str

    def test_repr_shows_base_url(self) -> None:
        """repr includes the base URL."""
        client = Client(api_key="sk_test", base_url="https://custom.api.com")
        repr_str = repr(client)
        assert "https://custom.api.com" in repr_str
        client.close()
