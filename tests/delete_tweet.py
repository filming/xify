from src.xify import Xify


def main():
    xify = Xify()
    xify.create_xas()

    tweet_id = ""
    xify.delete_tweet(tweet_id)


if __name__ == "__main__":
    main()
