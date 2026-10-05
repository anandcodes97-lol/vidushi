# 🌍 CodeAlpha_LanguageTranslator

A language translation web app built with **Flask** and **Google Translate**, made for the CodeAlpha Artificial Intelligence Internship — **Task 1: Language Translation Tool**.

## ✨ Features
- Translate between 130+ languages
- Auto-detect the source language
- Translates live as you type (600ms after you stop), plus a manual **Translate** button
- Searchable "From" / "To" language pickers
- Swap source ⇄ target in one click
- Copy translated text to the clipboard
- Listen to input/output text with text-to-speech
- Light / dark mode (remembers your choice)
- Responsive layout for desktop and mobile

## 🛠 Tech Stack
- **Backend:** Python + Flask
- **Translation engine:** [deep-translator](https://pypi.org/project/deep-translator/) (Google Translate backend — free, no API key needed)
- **Frontend:** plain HTML, CSS, and JavaScript — no frontend framework or build step

## 📦 Setup & Installation

**Prerequisites:** Python 3.8+ and an internet connection (needed for translation requests).

1. **Get the files** — unzip the project, or clone it after you've pushed it to GitHub.

2. **(Recommended) create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Open it** — go to **http://127.0.0.1:5000** in your browser.

## 🧭 How to use it
1. Pick a "From" language, or leave it on **Detect Language**.
2. Pick a "To" language.
3. Type or paste text on the left — the translation appears on the right automatically.
4. Use 🔊 to hear it spoken, the clipboard icon to copy, and ⇄ to swap languages.

## 🩹 Troubleshooting
| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt` again — make sure your virtual environment is activated first |
| Port 5000 already in use | Stop whatever else is using it, or run `flask run --port 5001` instead |
| "Couldn't reach the translator" | Check your internet connection — translation requests need it |
| `pip install` fails | Try `pip install -r requirements.txt --break-system-packages` (needed on some Linux setups) |

## 📁 Project Structure
```
CodeAlpha_LanguageTranslator/
├── app.py                 # Flask routes + translation logic
├── requirements.txt
├── templates/
│   └── index.html         # Page structure
├── static/
│   ├── style.css          # Design system + layout
│   └── script.js          # Dropdowns, translate calls, swap/copy/speak, theme
└── README.md
```

## 🔁 Swapping the translation engine
`app.py` funnels every translation call through one function, `translate_text()`. `deep-translator` also supports MyMemory, and the official Google Cloud Translation / Microsoft Translator APIs if you'd rather use a paid, officially supported service — swap the class used inside that one function and everything else keeps working.

## 📝 Submission checklist (from your CodeAlpha instructions)
- [ ] Push this project to GitHub as **CodeAlpha_LanguageTranslator**
- [ ] Record a short video walking through the code + a live demo
- [ ] Post the video on LinkedIn, tagging **@CodeAlpha**, with your GitHub link
- [ ] Submit through the form shared in your WhatsApp group
