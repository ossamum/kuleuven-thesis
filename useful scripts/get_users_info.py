from utils import get_tweepy_client

tweepy_client = get_tweepy_client()

users_fields = [
    'name',
    'created_at',
    'description',
    'location',
    'verified',
    'public_metrics'
]


user = tweepy_client.get_user(user_fields=users_fields)
print(user)