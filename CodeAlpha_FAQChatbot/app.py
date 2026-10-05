"""
CodeAlpha - Task 2: Chatbot for FAQs
--------------------------------------
A Flask web app that answers user questions by matching them against a
collection of FAQs using NLP preprocessing (NLTK) + TF-IDF cosine similarity.

Run:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import json
import re
import os
from flask import Flask, render_template, request, jsonify

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# One-time NLTK downloads (safe to run every time; they no-op if already present)
# ---------------------------------------------------------------------------
NLTK_PACKAGES = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]
for pkg in NLTK_PACKAGES:
    try:
        nltk.data.find(f"tokenizers/{pkg}") if "punkt" in pkg else nltk.data.find(
            f"corpora/{pkg}"
        )
    except LookupError:
        nltk.download(pkg, quiet=True)

app = Flask(__name__)

LEMMATIZER = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words("english"))

# Similarity threshold below which we tell the user we don't understand
CONFIDENCE_THRESHOLD = 0.30

# ---------------------------------------------------------------------------
# Load FAQ data
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "faqs.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    FAQS = json.load(f)

FAQ_QUESTIONS = [item["question"] for item in FAQS]
FAQ_ANSWERS = [item["answer"] for item in FAQS]


def preprocess(text: str) -> str:
    """Clean, tokenize, remove stopwords, and lemmatize input text."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = word_tokenize(text)
    tokens = [
        LEMMATIZER.lemmatize(tok) for tok in tokens if tok not in STOP_WORDS and tok.strip()
    ]
    return " ".join(tokens)


# Pre-process all FAQ questions once at startup and fit a TF-IDF vectorizer
PROCESSED_FAQS = [preprocess(q) for q in FAQ_QUESTIONS]
VECTORIZER = TfidfVectorizer()
FAQ_VECTORS = VECTORIZER.fit_transform(PROCESSED_FAQS)


def get_best_match(user_question: str):
    """Return (answer, matched_question, score) for the closest FAQ match."""
    processed = preprocess(user_question)
    if not processed.strip():
        return None, None, 0.0

    user_vec = VECTORIZER.transform([processed])
    similarities = cosine_similarity(user_vec, FAQ_VECTORS).flatten()

    best_idx = int(similarities.argmax())
    best_score = float(similarities[best_idx])

    if best_score < CONFIDENCE_THRESHOLD:
        return None, None, best_score

    return FAQ_ANSWERS[best_idx], FAQ_QUESTIONS[best_idx], best_score


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"answer": "Please type a question so I can help you!", "matched": None, "score": 0})

    answer, matched_question, score = get_best_match(user_message)

    if answer is None:
        answer = (
            "I'm sorry, I couldn't find a good match for that question. "
            "Could you try rephrasing it, or ask something about the CodeAlpha internship "
            "(tasks, certificates, submission, LinkedIn post, etc.)?"
        )

    return jsonify(
        {
            "answer": answer,
            "matched": matched_question,
            "score": round(score, 3),
        }
    )


@app.route("/api/faqs", methods=["GET"])
def list_faqs():
    """Optional endpoint to let the UI show all available FAQs."""
    return jsonify(FAQS)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
