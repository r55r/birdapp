from __future__ import annotations

from typing import Any

import requests

from .config import get_credential

BASE_URL = "https://api.twitterapi.io"
DEFAULT_TIMEOUT = 30


def require_credential(key: str) -> str:
    value = get_credential(key)
    if not value:
        raise ValueError(f"必須の認証情報がありません: {key}。`birdapp auth config` を実行してください。")
    return value


def _build_headers(content_type: str | None = None) -> dict[str, str]:
    headers = {"X-API-Key": require_credential("TWITTERAPI_IO_API_KEY")}
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> requests.Response:
    url = f"{BASE_URL}{path}"
    content_type = "application/json" if json_body is not None and not files else None
    headers = _build_headers(content_type=content_type)
    return requests.request(
        method,
        url,
        params=params,
        json=json_body,
        files=files,
        data=data,
        headers=headers,
        timeout=timeout,
    )

