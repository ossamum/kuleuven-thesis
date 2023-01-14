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
    "torture",
    "stop torture" "istanbul sözleşmesi",
]
# ##################################################### PARAMETERS #####################################################

api = get_tweepy_api()

for query in QUERY_LIST:
    print(f"Results for {query}...")
    response = api.search_users(q=query)
    for user in response:
        if user.statuses_count > 100:
            print(user.screen_name)
    print("\n\n")
