import logging
import os
from logging.handlers import TimedRotatingFileHandler
import zipfile
from os.path import basename

from .auth.xas import create_xas
from .tweet.tweet import create_tweet
from .tweet.media import create_media_id


class Xify:
    """A class that provides methods for interacting with the X API."""

    def __init__(self) -> None:
        self.logger = self.setup_logger()
        self.xas = None
        self.user_id = None
        self.username = None
        self.display_name = None

        self.logger.info("An instance of XIFY has been created.")

    def setup_logger(self) -> logging.Logger:
        """Create a TimedRotatingFileHandler that rotates at midnight and formats filenames dynamically."""

        # Make sure storage location for logger exists before creating logging obj
        LOG_DIR_PATH = os.path.join("storage", "logs", "xify")
        LOG_PATH = os.path.join(LOG_DIR_PATH, "current.log")
        os.makedirs(LOG_DIR_PATH, exist_ok=True)

        # Configure formatter
        formatter = logging.Formatter(
            "[ %(asctime)s ] [ %(levelname)-8s] [ %(filename)-24s ] [ %(funcName)-24s ] :: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Configure handler
        def rotator(source, dest):
            # Rotated log file is zipped and the original log file will be deleted
            zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED).write(
                source, os.path.basename(source)
            )
            os.remove(source)

        handler = TimedRotatingFileHandler(
            LOG_PATH,
            when="midnight",
            backupCount=365,
        )
        """
		default name for a log file that is being rotated (handler.namer lambda callable receives this):
		"current.log.2024-07-19"

		custom name for log file that is being rotated (lambda callable of handler.namer sets this):
		"2024-07-18.zip"
		"""
        handler.namer = lambda name: (
            os.path.join(LOG_DIR_PATH, f"{os.path.splitext(name)[1][1:]}.zip")
            if name.count(".") > 1
            else name
        )
        handler.rotator = rotator
        handler.setFormatter(formatter)

        # Configure logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger

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
