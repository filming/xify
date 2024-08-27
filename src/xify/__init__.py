import logging
import os


class Xify:
    """A class that provides methods for interacting with the X API."""

    def __init__(self) -> None:
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
