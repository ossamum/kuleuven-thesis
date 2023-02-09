import numpy as np
import pandas as pd

from utils import get_tweepy_api, get_tweepy_client, is_user_valid

# TODO what is favorites count?

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
    "insan haklari savunucusu",
    "LGBT Dayanisma",
    "lezbiyen",
    "gay",
    "escinsel",
    "lezbiyen hakları",
    "gay hakları",
    "eşcinsel hakları",
    "kadinsavunmasi",
    "esitlik",
    "LGBTI Turkiye",
    "Kadin haklari",
    "hak savunucusudur",
    "hak savunucusu",
]

CSV_PATH = "archive/users_found_with_keywords.csv"
# ##################################################### PARAMETERS #####################################################

api = get_tweepy_api()
tweepy_client = get_tweepy_client()

users_df = pd.read_excel("HRA Twitter Accounts.xlsx")

users_df = users_df[
    ~users_df.method_to_find.str.startswith("keyword search", na=False)
]  # remove all keyword search results
# from previous runs
users_df.reset_index(drop=True, inplace=True)


# Update well-known and web-search results
users_fields = [
    "name",
    "created_at",
    "description",
    "location",
    "public_metrics",
    "verified",
]

if "location2" in users_df.columns:
    users_df.drop(columns="location2", inplace=True)


for i in range(int(np.ceil(users_df.shape[0] / 100))):
    usernames = users_df.iloc[i * 100 : (i + 1) * 100].screen_name.to_list()  # noqa
    users = tweepy_client.get_users(usernames=usernames, user_fields=users_fields)
    for j, user in enumerate(users.data):
        ind = (i * 100) + j
        if users_df.loc[ind, "valid"]:
            users_df.loc[ind, "location"] = user.location
            users_df.loc[ind, "created_at"] = user.created_at
            users_df.loc[ind, "description"] = user.description
            users_df.loc[ind, "verified"] = user.verified
            users_df.loc[ind, "following_count"] = user.public_metrics["following_count"]
            users_df.loc[ind, "followers_count"] = user.public_metrics["followers_count"]
            users_df.loc[ind, "tweet_count"] = user.public_metrics["tweet_count"]
            users_df.loc[ind, "id"] = user.id

users_df.to_csv(CSV_PATH, header=True)

queried_user_ids = set()
for keyword in QUERY_LIST:
    print(f"Starting querying {keyword}...\n\n")
    n_last_page_user_found = 0
    for page in range(50):
        print(f"\nRetrieving results for {keyword} with page {page}\n")
        response = api.search_users(q=keyword, page=page, count=20)

        users_df = pd.DataFrame(columns=users_df.columns)
        new_user_found = False
        for user in response:
            if user.id not in queried_user_ids and is_user_valid(api, user):
                print(f"Found user with screen name: {user.screen_name}")
                queried_user_ids.add(user.id)
                user_dict = {
                    "id": user.id,
                    "name": user.name,
                    "full_name": user.name,
                    "screen_name": user.screen_name,
                    "method_to_find": f"keyword search - {keyword}",
                    "location": user.location,
                    "created_at": user.created_at,
                    "description": user.description,
                    "verified": user.verified,
                    "following_count": user.friends_count,
                    "followers_count": user.followers_count,
                    "tweet_count": user.statuses_count,
                    "comment": "validity inferred automatically",
                    "valid": 1,
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
users_df = pd.read_csv(CSV_PATH, index_col=0, header=None)
users_df.reset_index(inplace=True, drop=True)
users_df.to_excel("users_found_with_keywords.xlsx")

print(f"Total number of found users: {len(users_df)}")
