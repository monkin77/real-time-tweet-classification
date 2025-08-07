# preprocessor.py

import re

def clean_text(text: str) -> str:
    # Example: remove URLs, mentions, hashtags, lowercase, etc.
    text = re.sub(r"http\S+", "", text)        # Remove URLs
    text = re.sub(r"@\w+", "", text)           # Remove mentions
    text = re.sub(r"#\w+", "", text)           # Remove hashtags
    text = text.lower().strip()
    return text

def preprocess(text: str) -> str:
    return clean_text(text)
