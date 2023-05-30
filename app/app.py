import json
import logging
import pickle
from pathlib import Path
from typing import cast

import pandas as pd
import streamlit as st
from features import (
    create_content_features,
    create_emotion_features,
    create_gender_features,
    create_lang_features_and_lang,
    create_profession_features,
    create_sentiment_features,
    create_sttm_topic_features,
    create_tfidf_features,
    create_time_features,
    create_user_features,
)

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


model_path = Path("decision_tree_model_for_like_count.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

with open("../x_test.pkl", "rb") as f:
    x_test = pickle.load(f)

with open("ordered_feature_names.json") as f:
    ordered_feature_names = json.load(f)

# Caching the model for faster loading
@st.cache_data
def predict_like_count(tweet_text: str, screen_name: str) -> int:
    logger.debug(f"Predicting for screen_name={screen_name}, tweet_text={tweet_text}")
    features = {}
    features, lang = create_lang_features_and_lang(tweet_text, features)
    logger.debug(f"Detected lang: {lang}")

    features = create_sttm_topic_features(tweet_text, lang, features)
    logger.debug("Topic features are calculated")

    features = create_tfidf_features(tweet_text, features)
    logger.debug("TFIDF features are calculated")

    features = create_profession_features(screen_name, features)
    logger.debug("Profession features are calculated")

    features = create_gender_features(screen_name, features)
    logger.debug("Gender features are calculated")

    features = create_user_features(screen_name, features)
    logger.debug("User features are calculated")

    features = create_emotion_features(tweet_text, lang, features)
    logger.debug("Emotion features are calculated")

    features = create_content_features(tweet_text, features)
    logger.debug("Content features are calculated")

    features = create_time_features(features)
    logger.debug("Time features are calculated")

    features = create_sentiment_features(tweet_text, lang, features)
    logger.debug("Sentiment features are calculated")

    features = features | {
        "n_photos": n_photos,
        "n_videos": n_videos,
        "n_animated_gif": n_animated_gif,
        "posted_during_an_important_event": int(posted_during_an_important_event),
        "political_context_annotation": int(political_context_annotation),
        "n_trend_topics": n_trend_topics,
        "n_media_keys": 0,  # All zero during training.
    }
    logger.debug("App user inputs features are calculated")

    for k, v in features.items():
        # if np.isnan(v):
        print(k, v)

    raw_prediction = model.predict(pd.DataFrame([features], columns=ordered_feature_names))[0]
    return round(cast(float, raw_prediction))


@st.cache_data
def predict_retweet_count() -> int:
    pass


st.title("Predict your tweet reaction beforehand")
st.header("Enter the characteristics of your future tweet:")

tweet_text = st.text_input("Tweet Text:", value="")
screen_name = st.text_input("Twitter Account Screen Name:", value="")
n_photos = st.number_input("Number of photos in your tweet:", min_value=0)
n_videos = st.number_input("Number of videos in your tweet:", min_value=0)
n_animated_gif = st.number_input("Number of animated gifs in your tweet:", min_value=0)
posted_during_an_important_event = st.checkbox("Do you post your tweet during an important event:", value=False)  # TODO
political_context_annotation = st.checkbox("Do you post a tweet with a political context:", value=False)  # TODO
n_trend_topics = st.number_input("Number of trend topics in your tweet:", min_value=0)


if st.button("Predict Like and Retweet Count"):
    like_count = predict_like_count(tweet_text, screen_name)
    logger.debug(like_count)
    retweet_count = predict_retweet_count()
    st.success(f"The predicted like count of your tweet is {like_count}")
