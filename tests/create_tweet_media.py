from src.xify import Xify


def main():
    xify = Xify()
    xify.create_xas()

    message_content = "Good evening!"

    # Get media ids for locally stored media
    filepaths = [
        "./storage/media/candy.png",
        "./storage/media/charlie.png",
        "./storage/media/snoopy.jpg",
        "./storage/media/sunset.gif",
    ]
    media_ids = []

    for filepath in filepaths:
        media_id = xify.create_media_id(filepath)
        media_ids.append(media_id)

    tweet_id = xify.create_tweet(message_content, media_ids)

    print(tweet_id)


if __name__ == "__main__":
    main()
