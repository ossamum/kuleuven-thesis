from functools import partial
from pathlib import Path
from typing import Any

import pandas as pd

users_df = pd.read_excel("HRA Twitter Accounts.xlsx")

valid_screen_names = users_df[users_df.valid == 1].screen_name.to_list()

for file in Path("Tweets").iterdir():
    if file.stem not in valid_screen_names:
        print(f"Deleting {file}...")
        file.unlink()

file_screen_names = {file.stem for file in Path("Tweets").iterdir()}
assert not set(valid_screen_names).symmetric_difference(file_screen_names)

# Merge all tweet files
tweets_df = pd.DataFrame()

for file in Path("Tweets").iterdir():
    try:
        df_tmp = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        continue
    df_tmp["author"] = file.stem
    tweets_df = pd.concat([tweets_df, df_tmp], axis=0, ignore_index=True)


# Extract certain attributes from columns
def generate_column_from_dict(new_column_name: str, old_column_name: str, row: pd.Series) -> Any:
    cell_value = getattr(row, old_column_name)
    if type(cell_value) == str:
        cell_dictionary = eval(cell_value)
        return cell_dictionary.get(new_column_name)


tweets_df["quote_count"] = tweets_df.apply(partial(generate_column_from_dict, "quote_count", "public_metrics"), axis=1)
tweets_df["retweet_count"] = tweets_df.apply(
    partial(generate_column_from_dict, "retweet_count", "public_metrics"), axis=1
)
tweets_df["like_count"] = tweets_df.apply(partial(generate_column_from_dict, "like_count", "public_metrics"), axis=1)
tweets_df["reply_count"] = tweets_df.apply(partial(generate_column_from_dict, "reply_count", "public_metrics"), axis=1)
tweets_df["impression_count"] = tweets_df.apply(
    partial(generate_column_from_dict, "impression_count", "public_metrics"), axis=1
)

tweets_df["media_keys"] = tweets_df.apply(partial(generate_column_from_dict, "media_keys", "attachments"), axis=1)
tweets_df["poll_ids"] = tweets_df.apply(partial(generate_column_from_dict, "poll_ids", "attachments"), axis=1)

tweets_df["hashtags"] = tweets_df.apply(partial(generate_column_from_dict, "hashtags", "entities"), axis=1)
tweets_df["urls"] = tweets_df.apply(partial(generate_column_from_dict, "urls", "entities"), axis=1)
tweets_df["mentions"] = tweets_df.apply(partial(generate_column_from_dict, "mentions", "entities"), axis=1)
tweets_df["cashtags"] = tweets_df.apply(partial(generate_column_from_dict, "cashtags", "entities"), axis=1)
tweets_df["annotations"] = tweets_df.apply(partial(generate_column_from_dict, "annotations", "entities"), axis=1)

tweets_df.drop(columns=["public_metrics", "attachments", "entities", "edit_controls"], inplace=True)
tweets_df["is_retweet"] = tweets_df.text.str.startswith("RT ")
tweets_df.to_csv("all_tweets.csv", lineterminator="\r\n")
