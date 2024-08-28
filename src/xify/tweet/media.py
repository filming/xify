import logging
import json
import os

logger = logging.getLogger(__name__)


def get_media_mime(filepath):
    """Get the MIME type of a file."""

    filepath_parts = filepath.split(".")

    if filepath_parts[-1] == "png":
        return "tweet_image", "image/png"

    elif filepath_parts[-1] == "jpeg":
        return "tweet_image", "image/jpeg"

    elif filepath_parts[-1] == "gif":
        return "tweet_gif", "image/gif"

    else:
        return "tweet_video", "video/mp4"


def upload_init(xas, filepath):
    """Create a request to initiate a file upload session."""

    logger.info("Upload INIT request has started.")

    params = {
        "command": "INIT",
        "total_bytes": os.path.getsize(filepath),
        "media_type": get_media_mime(filepath),
    }

    r = xas.post("https://upload.twitter.com/1.1/media/upload.json", params=params)

    if 200 <= r.status_code <= 299:
        resp = json.loads(r.text)

        media_id = resp["media_id_string"]

        logger.info(
            "Upload INIT request has finished successfully. (mediaId: %s)", media_id
        )

        return media_id

    else:
        logger.critical("Upload INIT failed. Reason: %s | %s", r.status_code, r.text)


def create_media_id(xas, filepath):
    """Handle the flow of obtaining a media id."""

    media_id = upload_init(xas, filepath)

    return media_id
