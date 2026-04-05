from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

ELEVEN_VOICE_ID = "XB0fDUnXU5powFXDhCwa"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/tts", methods=["POST"])
def tts():
    data = request.json
    text = data.get("text", "")
    eleven_key = data.get("eleven_key", "")
    if not text or not eleven_key:
        return jsonify({"error": "missing params"}), 400
    res = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}",
        headers={"Content-Type": "application/json", "xi-api-key": eleven_key},
        json={"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.42, "similarity_boost": 0.85, "style": 0.3, "use_speaker_boost": True}},
        timeout=15
    )
    if not res.ok:
        return jsonify({"error": "eleven error"}), 500
    return Response(res.content, mimetype="audio/mpeg")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    system = data.get("system", "")
    anthropic_key = data.get("anthropic_key", "")
    if not messages or not anthropic_key:
        return jsonify({"error": "missing params"}), 400
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"Content-Type": "application/json", "x-api-key": anthropic_key, "anthropic-version": "2023-06-01"},
        json={"model": "claude-sonnet-4-20250514", "max_tokens": 250, "system": system, "messages": messages},
        timeout=15
    )
    if not res.ok:
        return jsonify({"error": "claude error"}), 500
    return jsonify(res.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
