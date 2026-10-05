# CodeAlpha_FAQChatbot

**Task 2 — Chatbot for FAQs** (CodeAlpha AI Internship)

A web-based FAQ chatbot that matches a user's question against a knowledge base
of FAQs using NLP preprocessing (NLTK) and TF‑IDF + cosine similarity, served
through a Flask backend with a custom chat UI.

## Features
- Text cleaning, tokenization, stopword removal, and lemmatization (NLTK)
- TF‑IDF vectorization + cosine similarity for best-match FAQ retrieval
- Confidence threshold — if no FAQ is similar enough, the bot admits it doesn't know
- Clean chat UI: message bubbles, typing indicator, timestamps, live "match %" badge
- Sidebar with quick-suggestion prompts and a "View all FAQs" browser modal
- Fully responsive (works on mobile)
- Easy to re-skin: just edit `faqs.json` to use your own topic/product FAQs

## Project structure
```
CodeAlpha_FAQChatbot/
├── app.py                  # Flask backend + NLP matching logic
├── faqs.json                # FAQ knowledge base (question/answer pairs)
├── requirements.txt
├── templates/
│   └── index.html           # Chat UI markup
└── static/
    ├── css/style.css         # Chat UI styling
    └── js/script.js          # Chat UI interactivity (fetch calls, DOM updates)
```

## How the matching works
1. Every FAQ question is preprocessed: lowercased, punctuation stripped,
   tokenized, stopwords removed, and lemmatized.
2. All FAQ questions are turned into TF‑IDF vectors once at startup.
3. When a user asks something, the same preprocessing is applied to their
   message, it's vectorized with the same TF‑IDF vocabulary, and cosine
   similarity is computed against every FAQ vector.
4. The highest-scoring FAQ's answer is returned. If the best score is below
   `CONFIDENCE_THRESHOLD` (0.30 by default, in `app.py`), the bot replies
   that it couldn't find a good match instead of guessing.

## Setup & Execution

### 1. Install Python
Make sure you have **Python 3.9+** installed.

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```
The first run will automatically download the small NLTK data packages it
needs (punkt, stopwords, wordnet) — this requires an internet connection
just for that first run.

### 5. Open the chatbot
Go to **http://127.0.0.1:5000** in your browser and start chatting.

## Customizing the FAQs
Open `faqs.json` and edit/add entries in this format:
```json
{
  "question": "Your question here?",
  "answer": "The answer to show the user."
}
```
No code changes are needed — the app rebuilds its TF‑IDF vectors from
`faqs.json` automatically every time it starts.

## Tuning match sensitivity
In `app.py`, adjust:
```python
CONFIDENCE_THRESHOLD = 0.30
```
- Lower it (e.g. 0.15) to make the bot answer more often, at the risk of
  wrong matches.
- Raise it (e.g. 0.45) to make the bot more conservative / accurate but more
  likely to say "I don't understand."

## Submitting for CodeAlpha
1. Push this folder to a GitHub repo named `CodeAlpha_FAQChatbot`.
2. Record a short video demo of the chatbot answering a few questions.
3. Post the video + repo link on LinkedIn, tagging **@CodeAlpha**.
4. Submit through the CodeAlpha submission form shared in your WhatsApp group.
