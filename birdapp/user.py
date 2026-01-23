from __future__ import annotations

import logging
from typing import Any

from .twitterapi_io import request

logger = logging.getLogger(__name__)


def _handle_api_error(payload: dict[str, Any], response_reason: str) -> str:
    return payload.get("msg") or payload.get("message") or response_reason


def _normalize_usernames(usernames: list[str]) -> list[str]:
    return [u.lstrip("@") for u in usernames]


def get_user_by_id(user_id: str) -> tuple[bool, dict[str, Any] | str]:
    """Get user details by user ID."""
    return get_users_by_ids([user_id])


def get_users_by_ids(user_ids: list[str]) -> tuple[bool, dict[str, Any] | str]:
    """Get multiple users by their IDs."""
    if len(user_ids) > 100:
        return False, "1リクエストあたり最大100ユーザーIDまでです"

    params = {"userIds": ",".join(user_ids)}
    try:
        response = request("GET", "/twitter/user/batch_info_by_ids", params=params)
        payload = response.json()
        if not response.ok:
            message = _handle_api_error(payload, response.reason)
            logger.error("Failed to retrieve users by id: %s", message)
            return False, message
        return True, {"users": payload.get("users", [])}
    except Exception as e:
        logger.error("Error retrieving users by id: %s", str(e))
        return False, str(e)


def get_user_by_username(username: str) -> tuple[bool, dict[str, Any] | str]:
    """Get user details by username."""
    username = username.lstrip("@")
    try:
        response = request("GET", "/twitter/user/search", params={"query": username})
        payload = response.json()
        if not response.ok:
            message = _handle_api_error(payload, response.reason)
            logger.error("Failed to retrieve user by username: %s", message)
            return False, message

        users = payload.get("users", [])
        match = next(
            (user for user in users if (user.get("screen_name") or user.get("userName") or "").lower() == username.lower()),
            None,
        )
        if match:
            return True, {"users": [match]}
        return False, f"ユーザー @{username} が見つかりません"
    except Exception as e:
        logger.error("Error retrieving user by username: %s", str(e))
        return False, str(e)


def get_users_by_usernames(usernames: list[str]) -> tuple[bool, dict[str, Any] | str]:
    """Get multiple users by their usernames."""
    usernames = _normalize_usernames(usernames)
    users: list[dict[str, Any]] = []
    missing: list[str] = []

    for username in usernames:
        success, result = get_user_by_username(username)
        if success:
            users.extend(result.get("users", []))
            continue
        if isinstance(result, str) and "が見つかりません" in result:
            missing.append(username)
            continue
        return False, result

    if missing:
        missing_labels = ", ".join(f"@{name}" for name in missing)
        return False, f"ユーザーが見つかりません: {missing_labels}"

    return True, {"users": users}
