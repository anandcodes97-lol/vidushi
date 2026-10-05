"""
chatbot.py
----------
The "brain" of the FAQ chatbot.

Pipeline:
  1. Preprocess text with NLTK (tokenize -> remove stopwords -> lemmatize).
     If NLTK's small language data files aren't available (e.g. first run
     with no internet, or a blocked download), it automatically falls back
     to scikit-learn's built-in stopword list so the bot still works.
  2. Turn every FAQ question into a TF-IDF vector.
  3. Compare a new user message to every FAQ using cosine similarity and
     return the best match (or a friendly fallback if nothing scores high
     enough).
"""

import json
import random
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# 1) Text preprocessing (NLTK, with a safe offline fallback)
# ---------------------------------------------------------------------------
NLTK_READY = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize

    def _ensure_nltk_data():
        """Best-effort download of the small NLTK corpora we need.

        Tries both old and new resource names since they differ across
        NLTK versions, and never lets a failed download crash the app.
        """
        for package in ("punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"):
            try:
                nltk.download(package, quiet=True)
            except Exception:
                pass

    _ensure_nltk_data()
    _STOPWORDS = set(stopwords.words("english"))
    _lemmatizer = WordNetLemmatizer()
    _lemmatizer.lemmatize("test")     # forces wordnet to actually load
    word_tokenize("test sentence")    # forces punkt to actually load
    _tokenize = word_tokenize
    NLTK_READY = True

except Exception:
    # No internet on first run, download blocked, or nltk isn't installed.
    # Fall back to scikit-learn's bundled stopword list (already on disk,
    # no download needed) plus a plain regex tokenizer.
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

    _STOPWORDS = set(ENGLISH_STOP_WORDS)
    _lemmatizer = None
    _tokenize = lambda text: re.findall(r"[a-zA-Z']+", text)

# A handful of short words that generic stopword lists throw away but that
# actually carry intent in a question ("how", "where", "can" ...).
_KEEP_WORDS = {"how", "what", "when", "where", "why", "who", "which", "can", "do", "does"}
_STOPWORDS = _STOPWORDS - _KEEP_WORDS


def preprocess(text: str) -> str:
    """Lowercase -> tokenize -> drop stopwords/punctuation -> lemmatize."""
    text = text.lower()
    tokens = _tokenize(text)
    tokens = [t for t in tokens if t.isalpha() and len(t) > 1]
    tokens = [t for t in tokens if t not in _STOPWORDS]
    if _lemmatizer is not None:
        tokens = [_lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# 2) Small-talk layer, handled before FAQ matching so greetings feel natural
# ---------------------------------------------------------------------------
_INTENTS = {
    "greeting": {
        "triggers": {"hi", "hello", "hey", "yo", "hii", "hiya", "greeting", "sup"},
        "responses": [
            "Hey there! 👋 What can I help you with?",
            "Hi! Ask me anything about your order, shipping, returns, or your account.",
            "Hello! What would you like to know?",
        ],
    },
    "thanks": {
        "triggers": {"thank", "thanks", "thankyou", "appreciate", "awesome", "great", "perfect"},
        "responses": [
            "You're welcome! Anything else I can help with?",
            "Glad that helped 😊 Anything else on your mind?",
        ],
    },
    "goodbye": {
        "triggers": {"bye", "goodbye", "byebye", "seeya", "cya", "exit", "quit"},
        "responses": [
            "Goodbye! Have a great day. 👋",
            "See you soon! Come back anytime you have a question.",
        ],
    },
}


def _match_intent(cleaned_text: str):
    tokens = set(cleaned_text.split())
    for intent in _INTENTS.values():
        if tokens & intent["triggers"]:
            return random.choice(intent["responses"])
    return None


# ---------------------------------------------------------------------------
# 3) The chatbot itself: TF-IDF + cosine similarity over the FAQ bank
# ---------------------------------------------------------------------------
class FAQChatbot:
    HIGH_CONFIDENCE = 0.35   # confident enough to answer directly
    LOW_CONFIDENCE = 0.16    # too low even to hedge -> show suggestions only

    def __init__(self, data_path: str = "faq_data.json"):
        with open(data_path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        self.questions = [item["question"] for item in self.faqs]

        # Each FAQ is matched not just on its literal question but also on
        # a handful of common paraphrases/synonyms/abbreviations stored in
        # "keywords" (e.g. "cod" / "pay cash on arrival" for the cash-on-
        # delivery FAQ). This is what lets the bot handle real-world
        # phrasing instead of only exact-ish wording.
        search_text = [
            item["question"] + " " + " ".join(item.get("keywords", []))
            for item in self.faqs
        ]
        clean_search_text = [preprocess(t) for t in search_text]

        # ngram_range=(1,2) lets phrase-level matches ("track order") score
        # higher than scattered single-word overlaps.
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.faq_matrix = self.vectorizer.fit_transform(clean_search_text)

    def get_categories(self):
        categories = {}
        for item in self.faqs:
            categories.setdefault(item.get("category", "General"), []).append(item["question"])
        return categories

    def get_response(self, user_message: str) -> dict:
        user_message = (user_message or "").strip()
        if not user_message:
            return {
                "answer": "Please type a question and I'll do my best to help!",
                "confidence": 0.0,
                "matched_question": None,
                "category": None,
                "tier": None,
                "suggestions": [],
            }

        cleaned = preprocess(user_message)

        # Small talk short-circuits FAQ matching entirely.
        canned = _match_intent(cleaned)
        if canned:
            return {
                "answer": canned, "confidence": 1.0, "matched_question": None,
                "category": None, "tier": "smalltalk", "suggestions": [],
            }

        if not cleaned:
            top = random.sample(self.questions, k=min(3, len(self.questions)))
            return {
                "answer": "I didn't quite catch that. Could you try one of these instead?",
                "confidence": 0.0, "matched_question": None, "category": None,
                "tier": "none", "suggestions": top,
            }

        query_vec = self.vectorizer.transform([cleaned])
        similarities = cosine_similarity(query_vec, self.faq_matrix).flatten()
        best_idx = int(similarities.argmax())
        best_score = float(similarities[best_idx])
        ranked = similarities.argsort()[::-1]

        # "tier" tells the frontend how to present the answer without it
        # needing to know our confidence cutoffs itself:
        #   high  -> confident direct answer, shown with a solid match tag
        #   guess -> answer shown, but flagged + backed by alternatives
        #   none  -> no answer we trust; suggestions only
        if best_score >= self.HIGH_CONFIDENCE:
            match = self.faqs[best_idx]
            return {
                "answer": match["answer"],
                "confidence": round(best_score, 2),
                "matched_question": match["question"],
                "category": match.get("category"),
                "tier": "high",
                "suggestions": [],
            }

        if best_score >= self.LOW_CONFIDENCE:
            match = self.faqs[best_idx]
            alt_idx = [i for i in ranked if i != best_idx][:2]
            return {
                "answer": f"I'm not fully sure, but this might help: {match['answer']}",
                "confidence": round(best_score, 2),
                "matched_question": match["question"],
                "category": match.get("category"),
                "tier": "guess",
                "suggestions": [self.faqs[i]["question"] for i in alt_idx],
            }

        top_idx = ranked[:3]
        return {
            "answer": "I'm not fully sure I understood that. Could you rephrase, or try one of these?",
            "confidence": round(best_score, 2),
            "matched_question": None,
            "category": None,
            "tier": "none",
            "suggestions": [self.faqs[i]["question"] for i in top_idx],
        }


if __name__ == "__main__":
    # Quick manual smoke test: python chatbot.py
    bot = FAQChatbot("faq_data.json")
    print("NLTK preprocessing active:", NLTK_READY)
    for q in [
        "hi there",
        "how do i track my order",
        "can i get my money back",
        "is cod available",
        "what languages do you support",
    ]:
        result = bot.get_response(q)
        print(f"\nQ: {q}\n-> {json.dumps(result, indent=2)}")
