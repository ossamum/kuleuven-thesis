import time
from datetime import datetime, timezone

import pandas as pd
import tweepy

from utils import get_tweepy_api

# ##################################################### PARAMETERS #####################################################
QUERY_LIST = [
    "insan hakları aktivisti",
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
CSV_PATH = "archive/users_found_with_keywords.csv"
# ##################################################### PARAMETERS #####################################################

api = get_tweepy_api()


def is_user_valid(api: tweepy.API, user: tweepy.User, retry_count: int = 0) -> bool:
    if user.statuses_count > 100:
        try:
            last_tweet = api.user_timeline(user_id=user.id)[0]
            if last_tweet.created_at >= datetime(2022, 1, 1, tzinfo=timezone.utc):
                return True
        except tweepy.errors.Unauthorized:
            print(f"Received Unauthorized Error for user with screen name: {user.screen_name}")
        except IndexError:
            print(f"The user with screen name {user.screen_name} seems not to have any tweet")
        except tweepy.errors.TweepyException as e:
            if retry_count > 10:
                raise e
            retry_count += 1
            print(f"Received TweepyException Error, retrying one more time: retry count {retry_count}. \n\n Error: {e}")
            time.sleep(1)
            return is_user_valid(api, user, retry_count)
    return False


queried_user_ids = set()
for query in QUERY_LIST:
    print(f"Starting querying {query}...\n\n")
    n_last_page_user_found = 0
    for page in range(50):
        print(f"\nRetrieving results for {query} with page {page}\n")
        response = api.search_users(q=query, page=page, count=20)

        users_df = pd.DataFrame()
        new_user_found = False
        for user in response:
            if user.id not in queried_user_ids and is_user_valid(api, user):
                print(f"Found user with screen name: {user.screen_name}")
                queried_user_ids.add(user.id)
                user_dict = {
                    "id": user.id,
                    "full name": user.name,
                    "screen_name": user.screen_name,
                    "method_to_find": "keyword search",
                    "location": user.location,
                }

                users_df = pd.concat([users_df, pd.DataFrame([user_dict])], ignore_index=True)

                n_last_page_user_found = 0
                new_user_found = True
        users_df.to_csv(CSV_PATH, mode="a", header=False)
        if not new_user_found:
            n_last_page_user_found += 1
        if n_last_page_user_found > 5:  # Break the pagination loop to continue the next query, if no new user found
            # after 5-page results
            break
    print("\n\n")


# I know this is VERY INEFFICIENT. I use the below code to convert csv into excel. Append mode in excel isn't
# straightforward based on this (https://stackoverflow.com/a/64824686/11758585)
users_df = pd.read_csv(
    CSV_PATH, index_col=0, header=None, names=["user_id", "full_name", "screen_name", "method_to_find", "location"]
)
users_df.reset_index(inplace=True, drop=True)
users_df.to_excel("users_found_with_keywords.xlsx")

print(f"Total number of found users: {len(users_df)}")
