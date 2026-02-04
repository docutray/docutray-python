"""Type definitions for the DocuTray SDK."""

from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired


class ClientOptions(TypedDict, total=False):
    """Options for configuring a DocuTray client."""

    api_key: NotRequired[str | None]
    base_url: NotRequired[str | None]
    timeout: NotRequired[float | None]
