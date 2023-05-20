import re

pattern_url = r"https://\S*"
pattern_hashtag = r"\s?#[\w\d]+\b"
pattern_newline = r"\n"
pattern_mentions = r"@\w+\s?"
pattern_emoji = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F910-\U0001F917"  # emojis with modifier
    "\U0001F918-\U0001F91F"  # emojis with fingers
    "\U0001F920-\U0001F927"  # emojis with pictographs
    "\U0001F928-\U0001F92F"  # emojis with characters
    "\U0001F930-\U0001F93F"  # emojis with animals
    "\U0001F940-\U0001F94F"  # emojis with food
    "\U0001F950-\U0001F95F"  # emojis with plants
    "\U0001F960-\U0001F97F"  # emojis with objects
    "\U0001F980-\U0001F9DF"  # emojis with faces
    "\U0001F9E0-\U0001F9FF"  # emojis with people
    "]+",
    flags=re.UNICODE,
)
