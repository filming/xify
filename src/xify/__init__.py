import logging
import os

from .auth.xas import create_xas
from .tweet.tweet import create_tweet
from .tweet.media import create_media_id


class Xify:
    """A class that provides methods for interacting with the X API."""

    def __init__(self) -> None:
        # Setup obj attributes
        self.logger = None
        self.xas = None
        self.user_id = None
        self.username = None
        self.display_name = None

        # Make sure storage location exists before creating logging obj
        LOG_DIR_PATH = os.path.join("storage", "logs")
        LOG_PATH = os.path.join(LOG_DIR_PATH, "xify.log")
        os.makedirs(LOG_DIR_PATH, exist_ok=True)

        # Setup a logger for this xify object
        logger = logging.getLogger(__name__)  # Get a logger with the class name
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler = logging.FileHandler(LOG_PATH, "w")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        self.logger = logger
        self.logger.info("Xify initialized successfully!")

    def create_xas(self):
        self.logger.info("Attempting to authorize XIFY instance with API keys.")

        self.xas, self.user_id, self.username, self.display_name = create_xas()

    def create_media_id(self, filepath):
        self.logger.info(
            "Attempting to create media id for file stored at: %s", filepath
        )
        media_id = create_media_id(self.xas, filepath)

        return media_id

    def create_tweet(self, message_content=None, media_ids=None, reply_id=None):
        self.logger.info(
            "Attempting to send tweet. (messageContent: %s, mediaIds: %s, replyIds: %s)",
            message_content,
            media_ids,
            reply_id,
        )

        tweet_id = create_tweet(self.xas, message_content, media_ids, reply_id)

        return tweet_id
