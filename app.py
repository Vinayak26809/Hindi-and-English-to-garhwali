import os
import re
import difflib
from flask import Flask, render_template, request, jsonify
import pandas as pd

# Optional Google Translate support (install googletrans==4.0.0-rc1)
try:
    from googletrans import Translator
    translator_available = True
except ImportError:
    translator_available = False

app = Flask(__name__)

# Construct absolute path to dictionary.csv relative to this file
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, '../your_project.dictionary.csv')

# Read CSV safely
try:
    df = pd.read_csv(csv_path, delimiter=',', dtype=str, encoding='utf-8').fillna('')
except Exception as e:
    print(f"Error loading dictionary.csv: {e}")
    df = pd.DataFrame(columns=['hindi', 'garhwali'])  # empty fallback to avoid crash

# Build translation dictionaries
hindi_to_garhwali = dict(zip(df['hindi'], df['garhwali']))
garhwali_to_hindi = {v: k for k, v in hindi_to_garhwali.items()}

# Instantiate Translator if available
translator = Translator() if translator_available else None

def clean_text(text):
    # Remove unwanted punctuation, normalize spaces, etc.
    return re.sub(r'[,]+', ' ', text).replace('।', '.').strip()

def word_to_word_translate(text, dictionary):
    tokens = text.split()
    result = []
    for word in tokens:
        # Extract base word ignoring punctuation (allow Devanagari range plus letters)
        clean_word = re.sub(r'[^\wऀ-ॿ]+', '', word, flags=re.UNICODE)
        if clean_word in dictionary and dictionary[clean_word]:
            translated = dictionary[clean_word]
        else:
            # Fuzzy match close words for possible misspellings
            matches = difflib.get_close_matches(clean_word, dictionary.keys(), n=1, cutoff=0.75)
            translated = dictionary[matches[0]] if matches else word

        # Preserve trailing punctuation/suffixes
        suffix = word[len(clean_word):] if len(word) > len(clean_word) else ''
        result.append(translated + suffix)
    return ' '.join(result)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True)
    text = data.get('text', '')
    source = data.get('source', 'hi')

    if not text.strip():
        return jsonify({"result": ""})

    if source == "hi":
        # Hindi to Garhwali
        result = word_to_word_translate(text, hindi_to_garhwali)

    elif source == "gbm":
        # Garhwali to Hindi
        result = word_to_word_translate(text, garhwali_to_hindi)

    elif source == "en":
        # English to Garhwali via Hindi using Google Translate
        if not translator_available:
            return jsonify({"result": "Googletrans library is not installed."})
        try:
            hi_text = translator.translate(text, src='en', dest='hi').text
            result = word_to_word_translate(hi_text, hindi_to_garhwali)
        except Exception as e:
            result = f"Translation error: {e}"

    elif source == "gbm_to_en":
        # Garhwali to English via Hindi using Google Translate
        if not translator_available:
            return jsonify({"result": "Googletrans library is not installed."})
        try:
            hi_text = word_to_word_translate(text, garhwali_to_hindi)
            en_text = translator.translate(hi_text, src='hi', dest='en').text
            result = en_text
        except Exception as e:
            result = f"Translation error: {e}"

    else:
        result = "Invalid translation direction."

    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
