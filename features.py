import json
import pickle
import re
from datetime import datetime

import nltk
import numpy as np
import pandas as pd
import spacy
import streamlit as st
from googletrans import Translator
from nltk import word_tokenize
from nrclex import NRCLex
from spacy_langdetect import LanguageDetector
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from unidecode import unidecode

from regex_patterns import pattern_emoji, pattern_hashtag, pattern_mentions, pattern_newline, pattern_url
from utils import get_tweepy_client

# Load models / artifacts
with open("models/gsdmm_model_with_K_19", "rb") as fb:
    sttm_model = pickle.load(fb)

with open("tfidf_vectorizer_like_count.pkl", "rb") as fb:
    tfidf_vectorizer_like_count = pickle.load(fb)

with open("professions.json") as f:
    screen_name_to_profession = json.load(f)

possible_professions = ["JOURNALIST", "LAWYER", "POLITICIAN", "UNKNOWN"]

with open("genders.json") as f:
    screen_name_to_gender = json.load(f)

possible_genders = ["F", "M", "ORG", "UNKNOWN"]

nlp = spacy.load("en_core_web_sm")
spacy.language.Language.factory("language_detector", func=lambda nlp, name: LanguageDetector())
nlp.add_pipe("language_detector", last=True)

stopwords = nltk.corpus.stopwords.words("turkish")
stopwords = [unidecode(i) for i in stopwords]

possible_langs = ["en", "other", "short_text", "tr", "very_short"]

tweepy_client = get_tweepy_client()

user_fields_to_get = ["created_at", "verified", "public_metrics"]

with open("average_tweets_per_day.json") as f:
    average_tweets_per_day = json.load(f)

median_average_tweets_per_day = np.median(list(average_tweets_per_day.values()))

translator = Translator()

with open("retweet_to_tweet_ratio.json") as f:
    retweet_to_tweet_ratio_per_user = json.load(f)

median_retweet_to_tweet_ratio = np.median(list(retweet_to_tweet_ratio_per_user.values()))

with open("reply_to_tweet_ratio.json") as f:
    reply_to_tweet_ratio_per_user = json.load(f)

median_reply_to_tweet_ratio = np.median(list(reply_to_tweet_ratio_per_user.values()))


with open("tweet_count.json") as f:
    tweet_count_per_user = json.load(f)

median_tweet_count_per_user = np.median(list(tweet_count_per_user.values()))


def get_sa_model_by_name(model_name, from_tf: bool = False):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, from_tf=from_tf)
    return pipeline("sentiment-analysis", tokenizer=tokenizer, model=model)


model_zoo = {
    "tr": get_sa_model_by_name("savasy/bert-base-turkish-sentiment-cased"),
    "en": get_sa_model_by_name("cardiffnlp/twitter-roberta-base-sentiment"),
}


def create_sttm_topic_features(tweet_text, lang: str, features: dict) -> dict:
    cluster_to_meaning_mapping = {
        0: "injustice against children",
        1: "vulnerable, sick people",
        2: "politics",
        3: "Uyghurs in China",
        4: "internatial relations",
        5: "death, torture, suicide",
        6: "activism for nature",
        7: "freedom of speech",
        8: "expressing wishes",
        9: "irrelevant tweets",
        10: "lost people",
        11: "search for justice",
        12: "supreme court",
        13: "woman rights",
        14: "invitation, agenda declaration",
        15: "dismissal of governmental workers",
        16: "democracy",
        17: "inflation, financial instability",
        18: "decree-law",
        19: "other",
    }

    if lang != "tr":
        topic_index = 19
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
        tokenized_tweet_text = word_tokenize(tweet_text)
        if len(tweet_text) <= 5:
            topic_index = 19
        else:
            topic_probabilities = sttm_model.score(tokenized_tweet_text)
            topic_index = np.argmax(topic_probabilities)
            assert topic_index < sttm_model.K

    topic_features = {
        f"sttm_topic_{topic}": (0 if ind != topic_index else 1) for ind, topic in cluster_to_meaning_mapping.items()
    }
    print(f"Topic features: {topic_features}")
    return features | topic_features


def create_tfidf_features(text: str, features: dict) -> dict:
    sparse_tfidf_features = tfidf_vectorizer_like_count.transform([text])

    tfidf_features = (
        pd.DataFrame.sparse.from_spmatrix(
            sparse_tfidf_features, columns=tfidf_vectorizer_like_count.get_feature_names_out()
        )
        .iloc[0]
        .to_dict()
    )
    return features | tfidf_features


def create_profession_features(screen_name: str, features: dict) -> dict:
    profession = screen_name_to_profession.get(screen_name, "UNKNOWN")
    profession_features = {f"profession_of_author_{p}": (0 if p != profession else 1) for p in possible_professions}
    print(f"profession features: {profession_features}")

    return features | profession_features


def create_gender_features(screen_name: str, features: dict) -> dict:
    gender = screen_name_to_gender.get(screen_name, "UNKNOWN")
    gender_features = {f"gender_of_author_{g}": (0 if g != gender else 1) for g in possible_genders}

    print(f"gender features: {gender_features}")

    return features | gender_features


def contains_only_mentions(text: str) -> bool:
    mentions_regex = r"@\w+"
    mentions = re.findall(mentions_regex, text)
    return text.strip() == " ".join(mentions)


def contains_only_cashtags(text: str) -> bool:
    cashtags_regex = r"\$\w+"
    cashtags = re.findall(cashtags_regex, text)
    return text.strip() == " ".join(cashtags)


def contains_only_hashtags(text: str) -> bool:
    hashtags_regex = r"#[A-Za-z0-9_]+"
    hashtags = re.findall(hashtags_regex, text)
    return text.strip() == " ".join(hashtags)


def includes_media_link(tweet: str) -> bool:
    media_link_prefix = "https://t.co/"
    return media_link_prefix in tweet


def has_short_text(text: str) -> bool:
    return len(text) < 5


@st.cache_data
def create_lang_features_and_lang(tweet_text: str, features: dict) -> tuple[dict, str]:
    clean_text = tweet_text
    clean_text = re.sub(pattern_url, "", clean_text)
    clean_text = re.sub(pattern_hashtag, "", clean_text)
    clean_text = re.sub(pattern_newline, "", clean_text)
    clean_text = re.sub(pattern_mentions, "", clean_text)
    clean_text = re.sub(pattern_emoji, "", clean_text)
    clean_text = clean_text.strip()
    word_count = len(clean_text.split())

    if word_count == 0:
        lang = "very_short"

    elif any(
        [
            contains_only_mentions(tweet_text),
            contains_only_cashtags(tweet_text),
            contains_only_hashtags(tweet_text),
            # includes_media_link(tweet_text),
            has_short_text(tweet_text),
        ]
    ):
        lang = "short_text"

    else:
        raw_lang = nlp(tweet_text)._.language["language"]
        print(f"Detected raw lang: {raw_lang}")
        lang = "other" if raw_lang not in ["tr", "en"] else raw_lang
    lang_features = {f"new_lang_{l}": (0 if l != lang else 1) for l in possible_langs} | {"word_count": word_count}
    print(f"lang_features: {lang_features}")

    return features | lang_features, lang


def create_user_features(screen_name: str, features: dict) -> dict:
    user = tweepy_client.get_user(username=screen_name, user_fields=user_fields_to_get).data
    today = datetime.now()
    age_of_account_in_days_author_when_tweeted = (today - user.created_at.replace(tzinfo=None)).days
    average_tweets_of_author_per_day = average_tweets_per_day.get(screen_name, median_average_tweets_per_day)
    retweet_to_tweet_ratio = retweet_to_tweet_ratio_per_user.get(screen_name, median_retweet_to_tweet_ratio)
    reply_to_tweet_ratio = reply_to_tweet_ratio_per_user.get(screen_name, median_reply_to_tweet_ratio)
    tweet_count_author = tweet_count_per_user.get(screen_name, median_tweet_count_per_user)
    following_count_author = user.public_metrics["following_count"]
    followers_count_author = user.public_metrics["followers_count"]
    verified_author = user.verified

    user_features = {
        "age_of_account_in_days_author_when_tweeted": age_of_account_in_days_author_when_tweeted,
        "average_tweets_of_author_per_day": average_tweets_of_author_per_day,
        "retweet_to_tweet_ratio": retweet_to_tweet_ratio,
        "reply_to_tweet_ratio": reply_to_tweet_ratio,
        "tweet_count_author": tweet_count_author,
        "following_count_author": following_count_author,
        "followers_count_author": followers_count_author,
        "verified_author": int(verified_author),
    }
    print(f"user_features: {user_features}")

    return features | user_features


def create_emotion_features(tweet: str, lang: str, features: dict) -> dict:
    emotions = [
        "fear",
        "anger",
        "anticip",
        "trust",
        "surprise",
        "positive",
        "negative",
        "sadness",
        "disgust",
        "joy",
        "anticipation",
    ]
    if lang not in ["en", "tr"]:
        emotion_features = {e: 0 for e in emotions}
    else:
        if lang == "tr":
            print(f"Translating turkish tweet: {tweet}")
            tweet = translator.translate(tweet, dest="en", src="tr").text
        emotion_features = NRCLex(tweet).affect_frequencies

    print(f"emotion_features: {emotion_features}")

    return features | emotion_features


def count_hashtags(text: str) -> int:
    hashtags_regex = r"#[A-Za-z0-9_]+"
    hashtags = re.findall(hashtags_regex, text)
    return len(hashtags)


def count_mentions(text: str) -> int:
    mentions_regex = r"@\w+"
    mentions = re.findall(mentions_regex, text)
    return len(mentions)


def count_urls(text: str) -> int:
    urls_regex = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    urls = re.findall(urls_regex, text)
    return len(urls)


def create_content_features(text: str, features: dict) -> dict:
    n_hashtags = count_hashtags(text)
    n_mentions = count_mentions(text)
    n_urls = count_urls(text)
    text_length = len(text)

    content_features = {
        "n_hashtags": n_hashtags,
        "n_mentions": n_mentions,
        "n_urls": n_urls,
        "text_length": text_length,
    }
    print(f"content_features: {content_features}")

    return features | content_features


def create_time_features(features: dict) -> dict:
    max_value = 86.400  # seconds in a day  # TODO fix the bug
    now = datetime.now()
    seconds_in_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds
    time_features = {
        "created_at_time_of_day_in_seconds_sin": np.sin(seconds_in_day * (2.0 * np.pi / max_value)),
        "created_at_time_of_day_in_seconds_cos": np.cos(seconds_in_day * (2.0 * np.pi / max_value)),
    }

    print(f"time_features: {time_features}")

    return features | time_features


def preprocess_tweet_text_for_english(text):
    new_text = []
    for t in text.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        new_text.append(t)
    return " ".join(new_text)


def create_sentiment_features(tweet: str, lang: str, features: dict) -> dict:
    if lang == "tr":
        sentiment_result = model_zoo["tr"](tweet)[0]
        assert sentiment_result["label"].lower() in ["positive", "negative"], (tweet, lang)
        sentiment_score = (
            -sentiment_result["score"] if sentiment_result["label"].lower() == "NEGATIVE" else sentiment_result["score"]
        )
    elif lang == "en":
        tweet = preprocess_tweet_text_for_english(tweet)
        sentiment_result = model_zoo["en"](tweet)[0]
        assert sentiment_result["label"] in ["LABEL_0", "LABEL_1", "LABEL_2"], (tweet, lang)
        if sentiment_result["label"] == "LABEL_1":
            sentiment_score = 0
        else:
            sentiment_score = (
                -sentiment_result["score"] if sentiment_result["label"] == "LABEL_0" else sentiment_result["score"]
            )
    else:
        sentiment_score = 0

    print(f"sentiment_score: {sentiment_score}")

    return features | {"sentiment": sentiment_score}
