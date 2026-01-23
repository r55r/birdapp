from __future__ import annotations

from typing import Any

import requests

from .config import get_credential, load_config, save_config

BASE_URL = "https://api.twitterapi.io"
DEFAULT_TIMEOUT = 30


def require_credential(key: str) -> str:
    value = get_credential(key)
    if not value:
        raise ValueError(f"Missing required credential: {key}. Run `birdapp auth config`.")
    return value


def require_login_cookie() -> str:
    value = get_credential("TWITTERAPI_IO_LOGIN_COOKIE")
    if not value:
        raise ValueError("Missing login cookie. Run `birdapp auth login` first.")
    return value


def require_proxy() -> str:
    value = get_credential("TWITTERAPI_IO_PROXY")
    if not value:
        raise ValueError("Missing proxy. Run `birdapp auth config` first.")
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


def login_user(store_cookie: bool = True) -> dict[str, Any]:
    payload = {
        "user_name": require_credential("TWITTERAPI_IO_USERNAME"),
        "email": require_credential("TWITTERAPI_IO_EMAIL"),
        "password": require_credential("TWITTERAPI_IO_PASSWORD"),
        "proxy": require_proxy(),
    }
    totp_secret = get_credential("TWITTERAPI_IO_TOTP_SECRET")
    if totp_secret:
        payload["totp_secret"] = totp_secret

    response = request("POST", "/twitter/user_login_v2", json_body=payload)
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError(f"Login failed: {response.text}") from None
    if not response.ok or data.get("status") != "success":
        message = data.get("msg") or response.text
        raise RuntimeError(f"Login failed: {message}")

    login_cookie = data.get("login_cookies") or data.get("login_cookie")
    if not login_cookie:
        raise RuntimeError("Login response missing login_cookie")
    if store_cookie:
        _store_login_cookie(login_cookie)
    return data


def _store_login_cookie(login_cookie: str) -> None:
    config = load_config()
    config["TWITTERAPI_IO_LOGIN_COOKIE"] = login_cookie
    save_config(config)
