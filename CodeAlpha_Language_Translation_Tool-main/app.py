from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

MAX_CHARACTERS = 4900

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Bengali": "bn",
    "Turkish": "tr",
    "Dutch": "nl",
    "Polish": "pl",
    "Vietnamese": "vi",
    "Thai": "th",
    "Swedish": "sv",
    "Greek": "el",
    "Urdu": "ur",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa"
}


def translate_text(text, source, target):

    url = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"{source}|{target}"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if data.get("responseStatus") != 200:
        raise Exception(
            data.get("responseDetails", "Translation failed")
        )

    translated = data["responseData"]["translatedText"]

    if not translated:
        raise Exception("Empty translation received")

    return translated


@app.route("/")
def home():

    return render_template(
        "index.html",
        languages=LANGUAGES
    )


@app.route("/translate", methods=["POST"])
def translate():

    data = request.get_json(silent=True) or {}

    text = (data.get("text") or "").strip()
    source = (data.get("source") or "auto").strip()
    target = (data.get("target") or "en").strip()

    if not text:
        return jsonify({
            "error": "Enter some text to translate."
        }), 400

    if len(text) > MAX_CHARACTERS:
        return jsonify({
            "error": f"Please keep the text under {MAX_CHARACTERS} characters."
        }), 400

    try:

        print("\n-----------------------------")
        print("Translation request")
        print("Text:", text)
        print("Source:", source)
        print("Target:", target)

        # MyMemory needs an actual source language.
        # For auto detection, use English as fallback.
        if source == "auto":
            source = "en"

        translated = translate_text(
            text,
            source,
            target
        )

        print("Translation:", translated)
        print("-----------------------------\n")

        return jsonify({
            "translated_text": translated
        })

    except requests.exceptions.Timeout:

        print("ERROR: Translation request timed out.")

        return jsonify({
            "error": "Translation service timed out. Please try again."
        }), 502

    except requests.exceptions.RequestException as error:

        print("ERROR: Network request failed:")
        print(error)

        return jsonify({
            "error": "Unable to connect to the translation service."
        }), 502

    except Exception as error:

        print("ERROR:", error)

        return jsonify({
            "error": "Translation failed. Please try again."
        }), 502


if __name__ == "__main__":

    print("\n===================================")
    print("   LANGUAGE TRANSLATOR")
    print("===================================")
    print("Server: http://127.0.0.1:5000")
    print("===================================\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )