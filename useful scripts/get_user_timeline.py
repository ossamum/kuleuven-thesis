from utils import get_tweepy_client

# #############################################   PARAMETERS   #########################################################
USERNAME = "gergerliogluof"  # https://twitter.com/gergerliogluof
NUM_TWEETS = 5
# #############################################   PARAMETERS   #########################################################
expansions = [
    "attachments.poll_ids",
    "attachments.media_keys",
    "author_id",
    "edit_history_tweet_ids",
    "entities.mentions.username",
    "geo.place_id",
    "in_reply_to_user_id",
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
]
tweet_fields = [
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
]

tweepy_client = get_tweepy_client()
user = tweepy_client.get_user(username=USERNAME)
user_tweets = tweepy_client.get_users_tweets(
    id=user.data.id, expansions=expansions, tweet_fields=tweet_fields, max_results=NUM_TWEETS
)
print(user_tweets)
print()
