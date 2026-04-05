from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import os
import traceback

app = Flask(__name__)
CORS(app)

ELEVEN_VOICE_ID = "XB0fDUnXU5powFXDhCwa"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
        eleven_key = data.get("eleven_key", "")
        print(f"TTS - text: {len(text)} chars, key: {eleven_key[:8] if eleven_key else 'EMPTY'}")
        if not text or not eleven_key:
            return jsonify({"error": "missing params"}), 400
        res = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}",
            headers={"Content-Type": "application/json", "xi-api-key": eleven_key},
            json={"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.42, "similarity_boost": 0.85, "style": 0.3, "use_speaker_boost": True}},
            timeout=20
        )
        print(f"ElevenLabs status: {res.status_code}")
        if not res.ok:
            print(f"ElevenLabs error: {res.text}")
            return jsonify({"error": res.text, "status": res.status_code}), 500
        return Response(res.content, mimetype="audio/mpeg")
    except Exception as e:
        print(f"TTS error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        system = data.get("system", "")
        anthropic_key = data.get("anthropic_key", "")
        print(f"Chat - {len(messages)} messages, key: {anthropic_key[:12] if anthropic_key else 'EMPTY'}")
        if not messages or not anthropic_key:
            return jsonify({"error": "missing params"}), 400
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json", "x-api-key": anthropic_key, "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 250, "system": system, "messages": messages},
            timeout=20
        )
        print(f"Anthropic status: {res.status_code}")
        if not res.ok:
            print(f"Anthropic error: {res.text}")
            return jsonify({"error": res.text, "status": res.status_code}), 500
        return jsonify(res.json())
    except Exception as e:
        print(f"Chat error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
