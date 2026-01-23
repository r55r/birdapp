import logging
import requests

from .config import get_credential
from .media import upload_media
from .twitterapi_io import request, require_login_cookie, require_proxy
from .utils import extract_tweet_id

logger = logging.getLogger(__name__)

def create_tweet_payload(
    text: str,
    media_path: str | None = None,
    reply_to: str | None = None,
) -> dict:
    login_cookie = require_login_cookie()
    proxy = require_proxy()
    payload = {
        "login_cookies": login_cookie,
        "tweet_text": text,
        "proxy": proxy,
    }

    if reply_to:
        payload["reply_to_tweet_id"] = extract_tweet_id(reply_to)

    if media_path:
        media_ids = upload_media(path=media_path)
        if not media_ids:
            raise RuntimeError("Media upload failed; aborting tweet.")
        payload["media_ids"] = media_ids

    return payload

def construct_tweet_link(tweet_id: str) -> str:
    """Construct the tweet link from the username and tweet ID."""
    username = get_credential("TWITTERAPI_IO_USERNAME")
    if not username:
        return f"https://x.com/i/status/{tweet_id}"
    return f"https://x.com/{username}/status/{tweet_id}"


def handle_tweet_response(response: requests.Response) -> tuple[bool, str]:
    """
    Handle the response from posting a tweet.
    Returns (success, message) tuple where:
    - success: Boolean indicating if the tweet was posted successfully
    - message: A user-friendly message describing the result
    """
    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if response.ok and payload.get("status") == "success":
        tweet_id = payload.get("tweet_id", "")
        tweet_link = construct_tweet_link(tweet_id=tweet_id)
        logger.info("Successfully posted tweet: %s", tweet_link)
        return True, f"Tweet posted successfully! View it at: {tweet_link}"

    if response.status_code == 429:
        error_msg = "Rate limit exceeded. Please wait a few minutes and try again."
    else:
        detail = payload.get("msg") or payload.get("message") or response.reason
        error_msg = f"Error ({response.status_code}): {detail}"
        logger.error("API error %d: %s", response.status_code, detail)
    
    logger.error("Failed to post tweet: %s", error_msg)
    return False, f"Failed to post tweet: {error_msg}"

def submit_tweet(
    text: str,
    media_path: str | None = None,
    reply_to: str | None = None,
) -> requests.Response:
    """
    Post a tweet with optional media and reply using TwitterAPI.io.
    Returns the raw response object.
    """
    tweet_payload = create_tweet_payload(text=text, media_path=media_path, reply_to=reply_to)
    redacted_payload = dict(tweet_payload)
    if "login_cookies" in redacted_payload:
        redacted_payload["login_cookies"] = "REDACTED"
    if "proxy" in redacted_payload:
        redacted_payload["proxy"] = "REDACTED"
    logger.info("Posting tweet with payload: %s", redacted_payload)

    return request("POST", "/twitter/create_tweet_v2", json_body=tweet_payload)

def post_tweet(text: str, media_path: str | None = None, reply_to: str | None = None) -> tuple[bool, str]:
    """
    Post a tweet with optional media and reply using TwitterAPI.io.
    Returns (success, message) tuple.
    """
    try:
        response = submit_tweet(text=text, media_path=media_path, reply_to=reply_to)
        return handle_tweet_response(response)
    except Exception as e:
        logger.error("Error posting tweet: %s", str(e))
        return False, f"Error posting tweet: {str(e)}"

def get_tweets_by_ids(tweet_ids: list[str]) -> tuple[bool, str | dict]:
    """
    Retrieve tweets by their IDs using TwitterAPI.io.
    Returns (success, result) tuple where result is either error message or tweet data.
    """
    if not tweet_ids:
        return False, "No tweet IDs provided"
    
    if len(tweet_ids) > 100:
        return False, "Too many tweet IDs provided (maximum 100)"
    
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
        return False, f"Error retrieving tweets: {str(e)}"
