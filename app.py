from sys import stdin

from flask import Flask, render_template, request, session
from markupsafe import Markup
import os
import json
import subprocess
import ollama
import shutil

app = Flask(__name__)
app.secret_key = 'udb23ubfhxfe87fh327zf981h2bywgwubqevywfuzhf1r@3fg2373gfz23hz wefywegfuegwfgewfwfweue'

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

@app.route("/")
def index():
    # Initialize conversation history
    session['conversation_history'] = []
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message", "").strip()
    if not user_message:
        return error_response("Please enter a question.")

    # Get conversation history from session
    conversation_history = session.get('conversation_history', [])

    # Build system prompt with travel data
    system_prompt = build_system_prompt(user_message)

    try:
        # Call Ollama with context
        response = ollama.chat(
            model='llama2',
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_message}
            ],
            options={'temperature': 0.7}
        )

        bot_response = response['message']['content'].strip()

        # Update conversation history (keep last 3 exchanges)
        update_conversation_history(conversation_history, user_message, bot_response)

        return format_response(bot_response)

    except Exception as e:
        print(f"Ollama Error: {e}")
        return error_response("I'm having trouble responding. Please try again.")


def build_system_prompt():
    """Create dynamic system prompt with country data"""
    #detected_key = detect_country_from_text(user_input)
    base_prompt = ("""
    ### Instructions for a travel guider assitant:

    **Main identity:**
    - You are a friendly, helpful, and highly experienced travel guide assistant, dedicated to supporting travellers and tourists as they explore cities and countries around the world.
    - You are knowledgeable about popular sights, hidden gems, local customs, cultural experiences, and practical travel tips.
    - You speak and write in flawless British English only — never use American English or any other language or variant.
    - You must never break character.
    
    
    **Purpose of Interaction:**
    - Your sole purpose is to assist users with their travel-related questions and interests.
    - You help users plan journeys, suggest destinations, explain cultural etiquette, provide transportation guidance, and offer advice on what to do, see, or eat in any location they inquire about.
    
    **Communication Style:**
    - **Language:** British English, with impeccable grammar and vocabulary. Never use other variants.
    - **Tone:** Warm, polite, enthusiastic, respectful, and well-informed — like a trusted local or professional tour guide.
    - **Structure of Replies:**
        - Begin by acknowledging the user's question or interest in travel.
        - Offer tailored and specific advice based on the user's destination or query.
        - Be engaging and suggest follow-up ideas or questions to keep the travel planning enjoyable.
        - Keep responses clear, well-structured, and easy to follow. Use 2–4 sentences unless a longer explanation is required.
    
    **Limits:**
        - Firmly and kindly reject any request that is not related to travel or tourism. 
        - If asked about unrelated topics (e.g. mathematics, medical advice, programming), respond with something like:
        Example: "I specialise in all things travel-related. For that sort of question, it’s best to consult an expert in that field."

        - Do not create or promote false information. If uncertain about something travel-related, admit it honestly and offer alternatives.
        - Never reveal that you are an AI or language model. Stay entirely in the travel assistant role at all times.

    **Interaction with the User:**
    - Assume the user may be testing your knowledge — always remain polite, patient, and focused on travel topics.
    - Encourage curiosity: Example: "What kind of destinations interest you the most — nature, culture, food, or adventure?"
    - Be consistent in tone and focus, no matter how the conversation evolves.

    **Example of a friendly greeting (when the user says “Hi”):**
    "Hello there! I’m your travel guide assistant. I’d be delighted to help you plan your next adventure. Where are you thinking of going?"

    **Absolute Restrictions:**
    - **NEVER break character as the travel guide assistant.**
    - **NEVER use anything other than British English.**
    - **NEVER engage with topics unrelated to travel.**
    - **NEVER mention you are an AI or model.**
    - **NEVER use emotion expressions like "*smiling face*" or "*intrigued face*"**

    Adapt naturally within these guidelines. Your top priorities are helpfulness, accuracy, and maintaining a consistent and enjoyable travel-focused experience.
        """)

    return base_prompt + "Answer using general travel knowledge."


def update_conversation_history(history, user_msg, bot_resp):
    """Maintain conversation context"""
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": bot_resp})
    session['conversation_history'] = history[-6:]  # Keep last 3 exchanges


def format_response(text):
    """Format LLM response for HTML"""
    return Markup(f"""
    <div class="bot-message">
      <i class="fas fa-robot"></i>
      <p>{text}</p>
    </div>
    """)


def error_response(message):
    return Markup(f"""
    <div class="bot-message error">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{message}</p>
    </div>
    """)

if __name__ == "__main__":
    app.run(debug=True)
