"""
app.py
------
Flask server for the FAQ chatbot.

Routes:
  GET  /                -> the chat UI
  POST /get_response    -> { "message": "..." }  ->  chatbot's JSON reply
  GET  /categories      -> FAQ questions grouped by category (for quick-reply chips)
"""

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from chatbot import FAQChatbot

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
bot = FAQChatbot(data_path=str(BASE_DIR / "faq_data.json"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message", "")
    result = bot.get_response(user_message)
    return jsonify(result)


@app.route("/categories")
def categories():
    return jsonify(bot.get_categories())


if __name__ == "__main__":
    # debug=True gives auto-reload while you edit; turn it off in production.
    app.run(debug=True, port=5000)
