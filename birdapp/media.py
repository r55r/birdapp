import logging

from .twitterapi_io import request, require_login_cookie, require_proxy

logger = logging.getLogger("uvicorn.error")

def upload_media(path: str | None) -> list[str]:
    """Upload media via TwitterAPI.io and return uploaded media IDs."""
    if not path:
        return []

    login_cookie = require_login_cookie()
    proxy = require_proxy()

    try:
        with open(path, "rb") as file:
            files = {"file": file}
            data = {
                "proxy": proxy,
                "login_cookies": login_cookie,
            }
            logger.info("Uploading media via TwitterAPI.io")
            response = request(
                "POST",
                "/twitter/upload_media_v2",
                files=files,
                data=data,
            )
            payload = response.json()
            if response.ok and payload.get("status") == "success":
                media_id = payload.get("media_id")
                if media_id:
                    return [media_id]
            message = payload.get("msg") or response.text
            logger.error("Media upload failed: %s", message)
    except Exception as e:
        logger.error("Error uploading media: %s", e)

    return []
