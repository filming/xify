from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth1

import logging
import os
import json

load_dotenv()


logger = logging.getLogger(__name__)


def create_xas():
    """Create an X authorized session object."""

    # Make sure ENV variables exist
    CONSUMER_API_KEY_TOKEN = os.getenv("CONSUMER_API_KEY_TOKEN")
    if CONSUMER_API_KEY_TOKEN is None:
        logger.critical("'CONSUMER_API_KEY_TOKEN' could not be found!")

    CONSUMER_API_KEY_SECRET = os.getenv("CONSUMER_API_KEY_SECRET")
    if CONSUMER_API_KEY_SECRET == None:
        logger.critical("'CONSUMER_API_KEY_SECRET' could not be found!")

    AUTH_ACCESS_TOKEN = os.getenv("AUTH_ACCESS_TOKEN")
    if AUTH_ACCESS_TOKEN is None:
        logger.critical("'AUTH_ACCESS_TOKEN' could not be found!")

    AUTH_ACCESS_SECRET = os.getenv("AUTH_ACCESS_SECRET")
    if AUTH_ACCESS_SECRET == None:
        logger.critical("'AUTH_ACCESS_SECRET' could not be found!")

    # Create and validate authenticated requests obj
    s = requests.Session()
    s.headers.update(
        {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
    )
    s.auth = OAuth1(
        CONSUMER_API_KEY_TOKEN,
        CONSUMER_API_KEY_SECRET,
        AUTH_ACCESS_TOKEN,
        AUTH_ACCESS_SECRET,
    )

    r = s.get("https://api.twitter.com/2/users/me", timeout=2)

    if r.status_code == 200:
        resp = json.loads(r.text)

        user_id = resp["data"]["id"]
        username = resp["data"]["username"]
        display_name = resp["data"]["name"]

        logger.info(
            "Successfully authenticated! (username: %s, userId: %s, displayName: %s)",
            username,
            user_id,
            display_name,
        )

        return s, user_id, username, display_name

    else:
        logger.critical(
            "Failed to authenticate. Reason: %s | %s", r.status_code, r.text
        )
