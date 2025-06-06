from sys import stdin

from flask import Flask, render_template, request
from markupsafe import Markup
import os
import json
import subprocess
import ollama
import shutil

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 1) At startup, build a list of “available” country keys and their friendly names
# ──────────────────────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(app.root_path, "data")

# Look for files like “france.json”, “united_kingdom.json”, etc.
# We'll map each “file key” → a normalized name to match in user text.
# e.g. "united_kingdom" → "united kingdom"
COUNTRY_FILE_KEYS = []
for fname in os.listdir(DATA_DIR):
    if not fname.endswith(".json"):
        continue
    base = fname[:-5]  # strip “.json”
    COUNTRY_FILE_KEYS.append(base)

COUNTRY_LOOKUP = {}
for key in COUNTRY_FILE_KEYS:
    friendly = key.replace("_", " ").lower()
    COUNTRY_LOOKUP[friendly] = key

def load_country_data(file_key: str) -> dict:
    path = os.path.join(DATA_DIR, f"{file_key}.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_country_from_text(text: str) -> str | None:
    """
    Attempt to find any “friendly” country name in the input text.
    Returns the matching file_key (e.g. "portugal") or None if no match.
    """
    text_lower = text.lower()
    for friendly_name, file_key in COUNTRY_LOOKUP.items():
        # if “portugal” (friendly_name) appears as a substring in text
        if friendly_name in text_lower:
            return file_key
    return None

def call_ollama(system_prompt: str, user_prompt: str) -> str:
    model_name = "llama2"  # your Ollama model
    combined = f"""// System:{system_prompt} -- User: {user_prompt}"""
    try:
        proc = subprocess.run(
            ["ollama", "run", model_name],
            input=combined.encode("utf-8"),  # send the prompt on stdin
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600
        )
        if proc.returncode != 0:
            error_msg = proc.stderr.decode().strip()
            print(f"Ollama error: {error_msg}")  # For debugging
            return "Sorry, I'm having trouble generating a response."

        return proc.stdout.decode().strip()
    except Exception as e:  # Capture the exception instance
        print(f"Exception occurred: {e}")
        return "Sorry, I couldn’t reach the language model. Please try again later."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message", "").strip()
    if not user_message:
        return Markup("""
        <div class="bot-message">
          <i class="fas fa-robot"></i>
          <p>Please enter a question.</p>
        </div>
        """)

    # Step 1: try to detect a country name in the user's text
    detected_key = detect_country_from_text(user_message)

    # Step 2: load that JSON (if we found a key), otherwise None
    if detected_key:
        country_data = load_country_data(detected_key)
        system_prompt = (
            f"You are a travel‐guide chatbot. Here is a list of points of interest for {detected_key.replace('_',' ')}:\n"
            f"{json.dumps(country_data, ensure_ascii=False, indent=2)}\n\n"
            "Use this data in your answer, alongside your general travel knowledge."
        )
    else:
        # No country detected: proceed with a generic prompt
        system_prompt = (
            "You are a travel‐guide chatbot. I do not have any country‐specific data. "
            "Answer questions about travel and destinations using your general knowledge."
        )

    # Step 3: call the LLM
    bot_response = call_ollama(system_prompt, user_message)

    # Step 4: wrap the LLM’s text in an HTML fragment
    html_fragment = Markup(f"""
        <div class="bot-message">
          <i class="fas fa-robot"></i>
          <p>{bot_response}</p>
        </div>
        """)
    return html_fragment

if __name__ == "__main__":
    app.run(debug=True)
