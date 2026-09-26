from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp.intents import intents
from nlp.preprocessing import preprocess_text


# -------------------------
# PREPARE INTENT DOCUMENTS
# -------------------------

intent_names = list(intents.keys())

intent_documents = []

for intent in intent_names:

    processed_examples = [
        preprocess_text(example)
        for example in intents[intent]
    ]

    intent_document = " ".join(
        " ".join(example)
        for example in processed_examples
    )

    intent_documents.append(
        intent_document
    )


# -------------------------
# TF-IDF
# -------------------------

vectorizer = TfidfVectorizer()

tfidf_matrix = vectorizer.fit_transform(
    intent_documents
)


# -------------------------
# INTENT PREDICTION
# -------------------------

def predict_intent(
    user_text,
    threshold=0.20
):

    processed_text = " ".join(
        preprocess_text(user_text)
    )

    user_vector = vectorizer.transform(
        [processed_text]
    )

    similarities = cosine_similarity(
        user_vector,
        tfidf_matrix
    )[0]

    best_match_index = similarities.argmax()

    best_score = similarities[
        best_match_index
    ]

    predicted_intent = intent_names[
        best_match_index
    ]

    if best_score < threshold:
        return "fallback", best_score

    return predicted_intent, best_score