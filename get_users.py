from datetime import datetime, timezone

import tweepy

from utils import get_tweepy_api

# ##################################################### PARAMETERS #####################################################
QUERY_LIST = [
    "insan hakları",
    "khk",
    "LGBT",
    "işkence",
    "iskence",
    "askeri öğrenci",
    "hapishane",
    "hukuksuzluk",
    "torture Turkey",
    "stop torture Turkey",
    "istanbul sözleşmesi",
]
# ##################################################### PARAMETERS #####################################################

api = get_tweepy_api()


def is_user_valid(api: tweepy.API, user: tweepy.User) -> bool:
    if user.statuses_count > 100:
        try:
            last_tweet = api.user_timeline(user_id=user.id)[0]
            if last_tweet.created_at >= datetime(2022, 1, 1, tzinfo=timezone.utc):
                return True
        except tweepy.errors.Unauthorized:
            print(f"Received Unauthorized Error for user with screen name: {user.screen_name}")
    return False


queried_user_ids = set()
for query in QUERY_LIST:
    print(f"Starting querying {query}...\n\n")
    for page in range(100):
        print(f"\nRetrieving results for {query} with page {page}\n")
        response = api.search_users(q=query, page=page)

        new_user_found = False
        for user in response:
            if user.id not in queried_user_ids and is_user_valid(api, user):
                print(f"Found user with screen name: {user.screen_name}")
                queried_user_ids.add(user.id)
                new_user_found = True
        if not new_user_found:  # Break the pagination loop to continue the next query
            break
    print("\n\n")
