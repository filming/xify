import logging
import json

logger = logging.getLogger(__name__)


def create_tweet(xas, message_content, media_ids, reply_ids):
    """Create a tweet with possiblities of adding media and replying to other tweets."""

    # message_content is required if media_ids is not present.
    if (not message_content) and (not media_ids):
        logger.critical(
            "Message content or media IDs must be present when sending a tweet."
        )

    else:
        payload = {}

        if message_content:
            payload["text"] = message_content

        if media_ids:
            payload["media"] = {"media_ids": media_ids}

        # Send tweet
        headers = {"content-type": "application/json"}
        r = xas.post(
            "https://api.x.com/2/tweets", data=json.dumps(payload), headers=headers
        )

        if 200 <= r.status_code <= 299:
            resp = json.loads(r.text)

            tweet_id = resp["data"]["id"]

            logger.info("Tweet was successfully sent. (tweetId: %s)", tweet_id)

            return tweet_id

        else:
            logger.critical(
                "Failed to send tweet. Reason: %s | %s", r.status_code, r.text
            )
