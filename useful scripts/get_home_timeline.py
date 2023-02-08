from utils import get_tweepy_client

tweepy_client = get_tweepy_client()

public_tweets = tweepy_client.get_users_tweets(max_results=5)
print(public_tweets)

print()
