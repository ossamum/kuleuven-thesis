import tweepy

from config import (
    TWITTER_API_ACCESS_TOKEN,
    TWITTER_API_ACCESS_TOKEN_SECRET,
    TWITTER_API_KEY,
    TWITTER_API_KEY_SECRET,
    TWITTER_BEARER_TOKEN,
)


def get_tweepy_client() -> tweepy.Client:
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
    auth.set_access_token(TWITTER_API_ACCESS_TOKEN, TWITTER_API_ACCESS_TOKEN_SECRET)

    tweepy_client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_KEY_SECRET,
        access_token=TWITTER_API_ACCESS_TOKEN,
        access_token_secret=TWITTER_API_ACCESS_TOKEN_SECRET,
    )

    print("TWEEPY API client is successfully created...")
    return tweepy_client
