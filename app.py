import pickle
from pathlib import Path
from typing import cast

import numpy as np
import streamlit as st

model_path = Path("xgboost_best_model_for_likes.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

with open("x_test.pkl", "rb") as f:
    x_test = pickle.load(f)


# Caching the model for faster loading
@st.cache_data
def predict_like_count() -> int:
    raw_prediction = model.predict(np.expand_dims(x_test[0], axis=0))[0]
    return round(cast(float, raw_prediction))


st.title("Predict your tweet reaction beforehand")
st.header("Enter the characteristics of your future tweet:")

tweet_text = st.text_input("Tweet Text:", value="")
account_screen_name = st.text_input("Twitter Account Screen Name:", value="")

if st.button("Predict Like and Retweet Count"):
    price = predict_like_count()
    st.success(f"The predicted like count of your tweet is {price}")
