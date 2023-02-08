"""
This script add FALSE value to the valid column based on:
- If the user doesn't tweet in Turkish in his/her last 100 tweets
- If the user doesn't have at least 1000 followers
"""
import time
from typing import Optional, cast

import pandas as pd
import requests
import tweepy
from tqdm import tqdm

from utils import get_tweepy_client

tweepy_client = get_tweepy_client()
users_df = pd.read_excel("HRA Twitter Accounts.xlsx")


def get_user_tweets(retry_count: int = 0) -> Optional[tweepy.client.Response]:
    try:
        user = tweepy_client.get_user(username=row.screen_name)
        result = tweepy_client.get_users_tweets(id=user.data.id, tweet_fields=["lang"], max_results=100)
        return cast(tweepy.client.Response, result)
    except tweepy.errors.BadRequest:
        print(f"Received BadRequest Error, for {row.screen_name}")
        return None
    except (tweepy.errors.TweepyException, requests.exceptions.ConnectionError) as e:
        if retry_count > 10:
            return None
        retry_count += 1
        print(f"Received TweepyException Error, retrying one more time: retry count {retry_count}. \n\n Error: {e}")
        time.sleep(1)
        return get_user_tweets(retry_count)


for i, row in tqdm(users_df.iterrows(), total=users_df.shape[0]):
    if row.valid in [0, 1]:  # Previously inferred either manually or automatically
        print(f"Skipping user with screen name {row.screen_name}, his/her validity is {row.valid}")
        continue

    users_df.loc[i, "comment"] = "validity inferred automatically"
    if row.followers_count < 1000:
        users_df.loc[i, "valid"] = 0
        continue

    user_tweets = get_user_tweets()
    if user_tweets is None or user_tweets.data is None or all(t["lang"] != "tr" for t in user_tweets.data):
        users_df.loc[i, "valid"] = 0
    else:
        users_df.loc[i, "valid"] = 1

users_df.to_excel("Eliminated HRA Twitter Accounts.xlsx")
