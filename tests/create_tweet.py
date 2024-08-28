from src.xify import Xify


def main():
    xify = Xify()
    xify.create_xas()

    message_content = "Hello World!"
    tweet_id = xify.create_tweet(message_content)

    print(tweet_id)


if __name__ == "__main__":
    main()
