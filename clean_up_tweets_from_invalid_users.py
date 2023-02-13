from pathlib import Path

import pandas as pd

users_df = pd.read_excel("HRA Twitter Accounts.xlsx")

valid_screen_names = users_df[users_df.valid == 1].screen_name.to_list()

for file in Path("Tweets").iterdir():
    if file.stem not in valid_screen_names:
        print(f"Deleting {file}...")
        file.unlink()

file_screen_names = {file.stem for file in Path("Tweets").iterdir()}
assert not set(valid_screen_names).symmetric_difference(file_screen_names)
