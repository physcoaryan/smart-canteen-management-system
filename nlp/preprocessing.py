import re

import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


# -------------------------
# NLTK RESOURCES
# -------------------------

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")


# -------------------------
# NLP TOOLS
# -------------------------

stop_words = set(
    stopwords.words("english")
)

lemmatizer = WordNetLemmatizer()


# -------------------------
# PREPROCESSING FUNCTION
# -------------------------

def preprocess_text(text):

    # Lowercase
    text = text.lower()

    # Remove special characters and numbers
    text = re.sub(
        r"[^a-zA-Z\s]",
        "",
        text
    )

    # Tokenization
    tokens = word_tokenize(text)

    # Remove stopwords
    tokens = [
        word
        for word in tokens
        if word not in stop_words
    ]

    # Lemmatization
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
    ]

    return tokens