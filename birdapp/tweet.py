from __future__ import annotations

import logging

from .twitterapi_io import request

logger = logging.getLogger(__name__)


def get_tweets_by_ids(tweet_ids: list[str]) -> tuple[bool, str | dict]:
    """Retrieve tweets by their IDs using TwitterAPI.io."""
    if not tweet_ids:
        return False, "ツイートIDが指定されていません"

    if len(tweet_ids) > 100:
        return False, "ツイートIDが多すぎます（最大100件）"
    
    try:
        ids_param = ",".join(tweet_ids)
        response = request(
            "GET",
            "/twitter/tweets",
            params={"tweet_ids": ids_param},
        )
        payload = response.json()
        if response.ok and payload.get("status") == "success":
            logger.info("Successfully retrieved tweets")
            return True, payload

        message = payload.get("message") or payload.get("msg") or response.reason
        logger.error("Failed to retrieve tweets: %s", message)
        return False, message
    except Exception as e:
        logger.error("Error retrieving tweets: %s", str(e))
        return False, f"ツイート取得エラー: {str(e)}"
