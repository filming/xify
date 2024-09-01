import requests

import logging
import json
import os
import math
import time
from typing import Tuple, Union


logger = logging.getLogger(__name__)

MAX_BYTES_PER_SEG = 5000000


def upload_status(xas: requests.Session, media_id: str) -> None:
    """Periodically poll for updates of a media processing operation."""

    logger.info("Upload STATUS has started.")

    params = {"command": "STATUS", "media_id": media_id}

    is_finialized = False

    while not is_finialized:
        r = xas.get("https://upload.twitter.com/1.1/media/upload.json", params=params)

        if 200 <= r.status_code <= 299:
            resp = json.loads(r.text)

            if resp["processing_info"]["state"] == "in_progress":
                check_after_secs = resp["processing_info"]["check_after_secs"] + 1

                logger.info(
                    "The media processing operation associated with media ID: %s is still in progress. Checking again in %s second(s).",
                    media_id,
                    check_after_secs,
                )

                time.sleep(check_after_secs)

            elif resp["processing_info"]["state"] == "succeeded":
                logger.info(
                    "The media processing operation associated with media ID: %s has finalized.",
                    media_id,
                )

                is_finialized = True

            elif resp["processing_info"]["state"] == "failed":
                logger.critical(
                    "Failed to find status on operation with media ID: %s. Reason: %s | %s",
                    media_id,
                    r.status_code,
                    r.text,
                )

                break

        else:
            logger.critical(
                "Failed to find status on operation with media ID: %s. Reason: %s | %s",
                media_id,
                r.status_code,
                r.text,
            )

            break


def upload_finalize(xas: requests.Session, media_id: str) -> None:
    """Finalize the flow of uploading media to X."""

    logger.info("Upload FINALIZE has started.")

    params = {"command": "FINALIZE", "media_id": media_id}

    r = xas.post("https://upload.twitter.com/1.1/media/upload.json", params=params)

    if 200 <= r.status_code <= 299:
        resp = json.loads(r.text)

        if "processing_info" in resp:

            if resp["processing_info"]["state"] == "pending":
                check_after_secs = resp["processing_info"]["check_after_secs"] + 1

                logger.info(
                    "The media processing operation with media ID: %s is not finalized yet. Checking again in %s second(s).",
                    media_id,
                    check_after_secs,
                )

                time.sleep(check_after_secs)

                upload_status(xas, media_id)

            elif resp["processing_info"]["state"] == "succeeded":
                logger.info(
                    "The media processing operation associated with media ID: %s has finalized.",
                    media_id,
                )

        else:
            logger.info(
                "The media processing operation associated with media ID: %s has finalized.",
                media_id,
            )

    else:
        logger.critical(
            "The media processing operation associated with media ID: %s could not be finalized. Reason: %s | %s",
            media_id,
            r.status_code,
            r.text,
        )


def upload_append(xas: requests.Session, filepath: str, media_id: str) -> None:
    """Upload a chunk of the media file.

    The APPEND command is used to upload a chunk (consecutive byte range) of the media file.
    For example, a 3 MB file could be split into 3 chunks of size 1 MB, and uploaded using 3 APPEND command requests.
    """

    logger.info("Upload APPEND request has started.")

    params = {
        "command": "APPEND",
        "media_id": media_id,
        "segment_index": -1,  # Setting this to -1 so we can increment at the start of the while loop instead of at the end
    }

    with open(filepath, "rb") as f:
        file_content = f.read()

    remaining_bytes = len(file_content)
    total_segments = math.ceil(remaining_bytes / MAX_BYTES_PER_SEG)

    logger.info(
        "The file located at %s has been broken into %s segment(s).",
        filepath,
        total_segments,
    )

    while remaining_bytes > 0:
        params["segment_index"] += 1

        logger.info(
            "Attempting to append segment #%s to the media ID: %s.",
            params["segment_index"] + 1,
            media_id,
        )

        # Get current chunk
        if remaining_bytes >= MAX_BYTES_PER_SEG:
            current_chunk = file_content[:MAX_BYTES_PER_SEG]
            file_content = file_content[MAX_BYTES_PER_SEG:]
            remaining_bytes -= MAX_BYTES_PER_SEG
        else:
            current_chunk = file_content
            remaining_bytes = 0

        # Send current chunk to twitter
        files = {"media": current_chunk}

        try:
            r = xas.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                params=params,
                files=files,
            )

            if 200 <= r.status_code <= 299:
                logger.info(
                    "Successfully appended segment #%s to the media ID: %s.",
                    params["segment_index"] + 1,
                    media_id,
                )

            else:
                logger.critical(
                    "Failed to append segment #%s to the media ID: %s. Reason: %s | %s",
                    params["segment_index"] + 1,
                    media_id,
                    r.status_code,
                    r.text,
                )

        except Exception as e:
            logger.critical(
                "Failed to append segment #%s to the media ID: %s. Reason: %s",
                params["segment_index"] + 1,
                media_id,
                e,
            )

        time.sleep(2)


def get_media_attributes(filepath: str) -> Tuple[str, str]:
    """Get the MIME type and category of a file."""

    filepath_parts = filepath.split(".")

    if filepath_parts[-1] == "png":
        return "tweet_image", "image/png"

    elif filepath_parts[-1] in ("jpeg", "jpg"):
        return "tweet_image", "image/jpeg"

    elif filepath_parts[-1] == "gif":
        return "tweet_gif", "image/gif"

    else:
        return "tweet_video", "video/mp4"


def upload_init(xas: requests.Session, filepath: str) -> Union[str, None]:
    """Create a request to initiate a file upload session."""

    logger.info("Upload INIT request has started.")

    media_attributes = get_media_attributes(filepath)

    params = {
        "command": "INIT",
        "total_bytes": os.path.getsize(filepath),
        "media_type": media_attributes[1],
        "media_category": media_attributes[0],
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


def create_media_id(xas: requests.Session, filepath: str) -> str:
    """Handle the flow of obtaining a media id."""

    media_id = upload_init(xas, filepath)
    upload_append(xas, filepath, media_id)
    upload_finalize(xas, media_id)

    return media_id
