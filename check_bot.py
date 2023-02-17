import pandas as pd
import botometer
import yaml
import pickle
from tqdm import tqdm

with open('twitter_keys.yaml', 'r') as f:
    credentials = yaml.safe_load(f)


rapidapi_key = "a0e1c218ecmsh93ae37912ed3fb8p1b560djsn75f232661744"
twitter_app_auth = {
    'consumer_key': credentials['kul-thesis']['api_key'],
    'consumer_secret': credentials['kul-thesis']['api_key_secret'],
    # 'access_token': credentials['access_token'],
    # 'access_token_secret': credentials['access_token_secret'],
  }


bom = botometer.Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)


users = pd.read_pickle('data_users.pkl')['username'].unique()


for i in tqdm(users):
    # Check a single account by screen name
    result = bom.check_account(f'@{i}')



    with open(f'users_botometer/{i}.pkl', 'wb') as f:
        pickle.dump(result, f)