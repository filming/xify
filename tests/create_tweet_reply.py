import time

from src.xify import Xify


def format_media_ids(media_ids):
    """Chunk a large list of media ids into groups of 4."""

    media_ids_chunks = []

    temp = []
    for media_id in media_ids:
        if len(temp) == 4:
            media_ids_chunks.append(temp)
            temp = []

        temp.append(media_id)

    media_ids_chunks.append(temp)

    return media_ids_chunks


def main():
    xify = Xify()
    xify.create_xas()

    message_content = "Good evening!"

    # Get media ids for locally stored media
    filepaths = [
        "./storage/media/candy.png",
        "./storage/media/charlie.png",
        "./storage/media/flower.jpg",
        "./storage/media/snoopy.jpg",
        "./storage/media/sunset.gif",
    ]
    media_ids = []

    for filepath in filepaths:
        media_id = xify.create_media_id(filepath)
        media_ids.append(media_id)

    # You can only send 4 media ids per tweet, so you'll need to format them into chunks.
    media_ids_chunks = format_media_ids(media_ids)

    previous_tweet_id = None

    for media_ids_chunk in media_ids_chunks:
        previous_tweet_id = xify.create_tweet(
            message_content, media_ids_chunk, previous_tweet_id
        )
        message_content = None

        time.sleep(2)

    print(previous_tweet_id)


if __name__ == "__main__":
    main()
