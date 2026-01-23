from __future__ import annotations

import logging
from typing import Any

from .twitterapi_io import request

logger = logging.getLogger(__name__)

ALLOWED_REPLIES_V2_QUERY_TYPES = {"Relevance", "Latest", "Likes"}
ALLOWED_SEARCH_QUERY_TYPES = {"Latest", "Top"}


def _handle_api_error(payload: dict[str, Any], response_reason: str) -> str:
    return payload.get("msg") or payload.get("message") or response_reason


def _build_params(**kwargs: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        params[key] = value
    return params


def _call_tweet_endpoint(path: str, params: dict[str, Any]) -> tuple[bool, str | dict[str, Any]]:
    try:
        response = request("GET", path, params=params)
        try:
            payload = response.json()
        except ValueError:
            message = response.text.strip() or response.reason
            logger.error("Invalid JSON response for %s: %s", path, message)
            return False, f"無効なJSONレスポンス: {message}"

        if response.ok:
            status = payload.get("status")
            if status in (None, "success"):
                return True, payload

        message = _handle_api_error(payload, response.reason)
        logger.error("Failed request for %s: %s", path, message)
        return False, message
    except Exception as exc:
        logger.error("Error requesting %s: %s", path, str(exc))
        return False, f"{path} へのリクエストエラー: {exc}"


def get_tweets_by_ids(tweet_ids: list[str]) -> tuple[bool, str | dict[str, Any]]:
    """Retrieve tweets by their IDs using TwitterAPI.io."""
    normalized_ids = [tweet_id.strip() for tweet_id in tweet_ids if tweet_id and tweet_id.strip()]
    if not normalized_ids:
        return False, "ツイートIDが指定されていません"

    if len(normalized_ids) > 100:
        return False, "ツイートIDが多すぎます（最大100件）"

    params = {"tweet_ids": ",".join(normalized_ids)}
    success, payload = _call_tweet_endpoint("/twitter/tweets", params)
    if success:
        logger.info("Successfully retrieved tweets")
    return success, payload


def get_tweet_replies(
    tweet_id: str,
    *,
    since_time: int | None = None,
    until_time: int | None = None,
    cursor: str | None = None,
) -> tuple[bool, str | dict[str, Any]]:
    """Retrieve replies for a tweet."""
    tweet_id = str(tweet_id).strip()
    if not tweet_id:
        return False, "ツイートIDが指定されていません"

    params = _build_params(
        tweetId=tweet_id,
        sinceTime=since_time,
        untilTime=until_time,
        cursor=cursor,
    )
    return _call_tweet_endpoint("/twitter/tweet/replies", params)


def get_tweet_replies_v2(
    tweet_id: str,
    *,
    cursor: str | None = None,
    query_type: str | None = None,
) -> tuple[bool, str | dict[str, Any]]:
    """Retrieve replies for a tweet (V2)."""
    tweet_id = str(tweet_id).strip()
    if not tweet_id:
        return False, "ツイートIDが指定されていません"

    if query_type and query_type not in ALLOWED_REPLIES_V2_QUERY_TYPES:
        return False, "queryType は Relevance / Latest / Likes のいずれかで指定してください"

    params = _build_params(tweetId=tweet_id, cursor=cursor, queryType=query_type)
    return _call_tweet_endpoint("/twitter/tweet/replies/v2", params)


def get_tweet_quotes(
    tweet_id: str,
    *,
    since_time: int | None = None,
    until_time: int | None = None,
    include_replies: bool | None = None,
    cursor: str | None = None,
) -> tuple[bool, str | dict[str, Any]]:
    """Retrieve quote tweets for a tweet."""
    tweet_id = str(tweet_id).strip()
    if not tweet_id:
        return False, "ツイートIDが指定されていません"

    params = _build_params(
        tweetId=tweet_id,
        sinceTime=since_time,
        untilTime=until_time,
        includeReplies=include_replies,
        cursor=cursor,
    )
    return _call_tweet_endpoint("/twitter/tweet/quotes", params)


def get_tweet_retweeters(
    tweet_id: str,
    *,
    cursor: str | None = None,
) -> tuple[bool, str | dict[str, Any]]:
    """Retrieve retweeters for a tweet."""
    tweet_id = str(tweet_id).strip()
    if not tweet_id:
        return False, "ツイートIDが指定されていません"

    params = _build_params(tweetId=tweet_id, cursor=cursor)
    return _call_tweet_endpoint("/twitter/tweet/retweeters", params)


def get_tweet_thread_context(
    tweet_id: str,
    *,
    cursor: str | None = None,
) -> tuple[bool, str | dict[str, Any]]:
    """Retrieve thread context for a tweet."""
    tweet_id = str(tweet_id).strip()
    if not tweet_id:
        return False, "ツイートIDが指定されていません"

    params = _build_params(tweetId=tweet_id, cursor=cursor)
    return _call_tweet_endpoint("/twitter/tweet/thread_context", params)


def get_tweet_article(tweet_id: str) -> tuple[bool, str | dict[str, Any]]:
    """Retrieve article content for a tweet."""
    tweet_id = str(tweet_id).strip()
    if not tweet_id:
        return False, "ツイートIDが指定されていません"

    params = _build_params(tweet_id=tweet_id)
    return _call_tweet_endpoint("/twitter/article", params)


def search_tweets_advanced(
    query: str,
    *,
    query_type: str | None = None,
    cursor: str | None = None,
) -> tuple[bool, str | dict[str, Any]]:
    """Perform advanced search for tweets."""
    query = str(query).strip()
    if not query:
        return False, "検索クエリが指定されていません"

    if query_type and query_type not in ALLOWED_SEARCH_QUERY_TYPES:
        return False, "queryType は Latest / Top のいずれかで指定してください"

    params = _build_params(query=query, queryType=query_type, cursor=cursor)
    return _call_tweet_endpoint("/twitter/tweet/advanced_search", params)
