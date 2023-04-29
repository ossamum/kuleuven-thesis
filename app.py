import logging
import pickle
import re
from pathlib import Path
from typing import cast

import nltk
import numpy as np
import spacy
import streamlit as st
from nltk.tokenize import word_tokenize
from spacy_langdetect import LanguageDetector
from unidecode import unidecode

# create logger
logger = logging.getLogger("simple_example")
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


model_path = Path("xgboost_best_model_for_likes.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

with open("x_test.pkl", "rb") as f:
    x_test = pickle.load(f)

with open("models/gsdmm_model_with_K_19", "rb") as fb:
    sttm_model = pickle.load(fb)


def get_lang_detector(nlp, name):
    return LanguageDetector()


nlp = spacy.load("en_core_web_sm")
spacy.language.Language.factory("language_detector", func=get_lang_detector)
nlp.add_pipe("language_detector", last=True)


stopwords = nltk.corpus.stopwords.words("turkish")
stopwords = [unidecode(i) for i in stopwords]


@st.cache_data
def get_lang_from_text(tweet_text: str):
    lang = nlp(tweet_text)._.language
    return lang["language"]


def get_sttm_topic(tweet_text, lang: str) -> str:
    cluster_to_meaning_mapping = {
        18: "decree-law",
        11: "search for justice",
        15: "dismissal of governmental workers",
        9: "irrelevant tweets",
        0: "injustice against children",
        8: "expressing wishes",
        2: "politics",
        13: "woman rights",
        14: "invitation, agenda declaration",
        5: "death, torture, suicide",
        16: "democracy",
        17: "inflation, financial instability",
        12: "supreme court",
        7: "freedom of speech",
        1: "vulnerable, sick people",
        4: "internatial relations",
        3: "Uyghurs in China",
        10: "lost people",
        6: "activism for nature",
    }
    if lang != "tr":
        return lang
    else:
        # preprocessing
        tweet_text = tweet_text
        tweet_text = tweet_text.lower()
        tweet_text = re.sub("\n", " ", tweet_text)
        tweet_text = re.sub("#(\w+)[^\w]", " ", tweet_text)  # remove hashtag
        tweet_text = re.sub("@([A-Za-z0-9_]+)", " ", tweet_text)  # remove mentions
        tweet_text = re.sub("https://t.co/[A-Za-z0-9]+", " ", tweet_text)  # remove link
        tweet_text = re.sub("\b\w*khk\w*\b", " ", tweet_text)  # normalise khk words
        tweet_text = tweet_text.replace("[^\w\s]", "")
        tweet_text = unidecode(tweet_text)  # remove accents
        tweet_text = " ".join([word for word in tweet_text.split() if word not in (stopwords)])
        if len(tweet_text) <= 5:
            return "too_short_tweet"
        tokenized_tweet_text = word_tokenize(tweet_text)

        topic_probabilities = sttm_model.score(tokenized_tweet_text)
        topic_index = np.argmax(topic_probabilities)
        assert topic_index != sttm_model.K

        return cluster_to_meaning_mapping[topic_index]


# Caching the model for faster loading
@st.cache_data
def predict_like_count(tweet_text: str) -> int:
    lang = get_lang_from_text(tweet_text)
    sttm_topic = get_sttm_topic(tweet_text, lang)
    logger.debug(f"Detected lang: {lang}, detected topic: {sttm_topic}")
    raw_prediction = model.predict(np.expand_dims(x_test[0], axis=0))[0]
    return round(cast(float, raw_prediction))


@st.cache_data
def predict_retweet_count() -> int:
    pass


st.title("Predict your tweet reaction beforehand")
st.header("Enter the characteristics of your future tweet:")

tweet_text = st.text_input("Tweet Text:", value="")
account_screen_name = st.text_input("Twitter Account Screen Name:", value="")

if st.button("Predict Like and Retweet Count"):
    like_count = predict_like_count(tweet_text)
    logger.debug(like_count)
    retweet_count = predict_retweet_count()
    st.success(f"The predicted like count of your tweet is {like_count}")
