import math
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
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
        wait_on_rate_limit=True,
    )

    print("TWEEPY client is successfully created...")
    return tweepy_client


def get_tweepy_api() -> tweepy.API:
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
    auth.set_access_token(TWITTER_API_ACCESS_TOKEN, TWITTER_API_ACCESS_TOKEN_SECRET)

    tweepy_api = tweepy.API(auth=auth, wait_on_rate_limit=True, retry_count=5)

    print("TWEEPY api is successfully created...")
    return tweepy_api


def get_all_user_tweets(tweepy_client: tweepy.Client, query: str, years: int = 1, days_range: int = 10) -> pd.DataFrame:
    """Get all tweets from a given user
    Example of query: from: mehdizana_ -is:retweet
    """

    # select time range
    end_time = datetime.today()
    start_time = end_time - timedelta(days=days_range)

    num_iter = math.ceil(years * 365 / days_range)

    all_tweets = []
    for _ in range(num_iter):
        tweets = tweepy_client.search_all_tweets(
            query=query,
            tweet_fields=[
                "attachments",
                "author_id",
                "context_annotations",
                "conversation_id",
                "created_at",
                "edit_controls",
                "entities",
                "geo",
                "id",
                "in_reply_to_user_id",
                "lang",
                "public_metrics",
                "possibly_sensitive",
                "referenced_tweets",
                "reply_settings",
                "source",
                "text",
                "withheld",
            ],
            start_time=start_time,
            end_time=end_time,
            max_results=100,
        )

        # include only valid tweets
        if tweets.meta["result_count"] > 0:
            all_tweets += tweets.data

            # alert when there is more than 100 tweets in the considered time range
            if tweets.meta["result_count"] > 100:
                print(f"There are more tweets between {start_time} and {end_time}")

        end_time -= timedelta(days=days_range)
        start_time -= timedelta(days=days_range)

        sleep(1)

    return pd.DataFrame(all_tweets)
