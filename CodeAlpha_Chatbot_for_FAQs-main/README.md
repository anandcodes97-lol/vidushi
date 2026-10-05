# Wren — FAQ Chatbot

A web-based FAQ chatbot built for **CodeAlpha's AI Internship — Task 2 (Chatbot for FAQs)**.

Type a question in plain English and Wren matches it against a bank of FAQs using NLP
preprocessing (NLTK) and TF-IDF + cosine similarity (scikit-learn), then replies with the
best-matching answer — or a friendly fallback with suggestions if it isn't confident.

## Features

- **30 FAQs across 6 categories** (Orders, Shipping, Returns & Refunds, Payments, Account, General)
  for a fictional store, "Nimbus Supply Co." — easy to swap for your own topic.
- **NLP preprocessing pipeline**: lowercasing, tokenizing, stopword removal, and lemmatization
  via NLTK, with a safe automatic fallback if NLTK's data can't be downloaded.
- **TF-IDF + cosine similarity matching**, plus a small rule-based intent layer for greetings,
  thanks, and goodbyes.
- **Three-tier confidence system**: confident answers, hedged "best guess" answers, and a
  clean fallback with clickable suggestions when nothing matches well.
- **Polished, custom chat UI** — no generic chatbot template: a boarding-pass-style card with
  a perforated header edge, light/dark mode, animated typing indicator, and quick-reply chips
  that adapt to the conversation.
- Fully responsive (mobile-friendly) and keyboard/screen-reader accessible.

## Tech stack

| Layer      | Tools |
|------------|-------|
| Backend    | Python, Flask |
| NLP        | NLTK (tokenizing, stopwords, lemmatization) |
| Matching   | scikit-learn (TF-IDF vectorizer + cosine similarity) |
| Frontend   | Vanilla HTML / CSS / JavaScript (no build step, no frameworks) |

## How the matching works

1. Every FAQ's question **and** a handful of alternate phrasings ("keywords") are cleaned with
   NLTK — lowercased, tokenized, stripped of stopwords/punctuation, and lemmatized.
2. That cleaned text is turned into TF-IDF vectors (`chatbot.py`, using word + 2-word phrase
   features).
3. When you send a message, it goes through the same cleaning step, gets vectorized, and is
   compared against every FAQ with cosine similarity.
4. The best score decides what you see:
   - **≥ 0.35** → answered directly, tagged with the category and match %.
   - **0.16 – 0.35** → answered but clearly flagged as a guess, plus two alternative questions.
   - **< 0.16** → "I'm not sure" fallback with three suggested questions instead of a guess.

## Folder structure

```
faq_chatbot/
├── app.py              # Flask routes ( / , /get_response , /categories )
├── chatbot.py          # NLP preprocessing + TF-IDF matching engine (FAQChatbot class)
├── faq_data.json        # The FAQ bank — edit this to change the topic
├── requirements.txt
├── templates/
│   └── index.html      # Chat UI markup
└── static/
    ├── style.css        # All styling (light + dark theme)
    └── script.js        # Chat behaviour, calls the Flask API
```

## 1. Prerequisites

- Python 3.9 or newer
- pip
- An internet connection the **first** time you run it (so NLTK can download its small
  language-data files — a few MB, one-time only)

## 2. Setup

Open a terminal in the `faq_chatbot` folder and run:

```bash
# (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Run it

```bash
python app.py
```

You should see output ending in:

```
 * Running on http://127.0.0.1:5000
```

Open **http://127.0.0.1:5000** in your browser. That's it — start chatting.

> The first run downloads NLTK's `punkt`, `stopwords`, and `wordnet` data automatically.
> If your machine has no internet access at that moment, the bot automatically falls back
> to scikit-learn's built-in stopword list so it still works — you'll just see
> `NLTK preprocessing active: False` if you run `python chatbot.py` directly.

## Customizing the FAQs

Open `faq_data.json` and edit/add entries in this shape:

```json
{
  "id": 31,
  "category": "Orders",
  "question": "Do you offer same-day delivery?",
  "answer": "Same-day delivery is available in select cities for orders placed before 2 PM.",
  "keywords": ["same day delivery", "fast delivery", "delivery today"]
}
```

- `category` groups questions for the quick-reply chips (shown via `/categories`).
- `keywords` are extra phrasings that should also point to this answer — add as many
  real-world ways of asking the question as you can think of; it's the biggest lever for
  better matching.
- Restart `python app.py` after editing so the TF-IDF index rebuilds.

## Tuning match sensitivity

In `chatbot.py`, inside the `FAQChatbot` class:

```python
HIGH_CONFIDENCE = 0.35   # confident enough to answer directly
LOW_CONFIDENCE = 0.16    # too low even to hedge -> show suggestions only
```

Raise these if the bot feels too eager to guess; lower them if it falls back to "I'm not
sure" too often.

## Testing the matching logic on its own

```bash
python chatbot.py
```

This runs a small built-in smoke test (a handful of sample questions) without starting the
web server — useful for quickly checking matches after editing `faq_data.json`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` (or `nltk`/`sklearn`) | Run `pip install -r requirements.txt` again, and make sure your virtual environment is activated. |
| `Address already in use` | Another program is using port 5000. Either stop it, or run `app.run(debug=True, port=5001)` in `app.py` and open that port instead. |
| NLTK download seems stuck or fails | Check your internet connection. The app will still run using the offline fallback cleaner; matching quality is only slightly reduced. |
| Page loads but looks unstyled | Make sure `static/style.css` and `static/script.js` are still inside the `static/` folder — Flask serves them from there automatically. |

## Submitting for CodeAlpha

Per the internship instructions: create a GitHub repo named `CodeAlpha_FAQChatbot` (or
similar), push this whole folder to it, then record your LinkedIn video demo showing the
UI in action and briefly explaining the NLTK → TF-IDF → cosine similarity pipeline before
linking the repo. A `.gitignore` is included so your `venv/` and cache files don't get
committed.
