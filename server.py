from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import os
import traceback

app = Flask(__name__)
CORS(app)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
        eleven_key = data.get("eleven_key", "")
        voice_id = data.get("voice_id", "XB0fDUnXU5powFXDhCwa")

        if not text or not eleven_key:
            return jsonify({"error": "missing params"}), 400

        print(f"TTS - {len(text)} chars, voice: {voice_id[:8]}")

        res = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream",
            headers={
                "Content-Type": "application/json",
                "xi-api-key": eleven_key
            },
            json={
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.75,
                    "style": 0.1,
                    "use_speaker_boost": True
                }
            },
            stream=True,
            timeout=20
        )

        print(f"ElevenLabs status: {res.status_code}")

        if not res.ok:
            body = res.text
            print(f"ElevenLabs error: {body}")
            return jsonify({"error": body}), 500

        def generate():
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            mimetype="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Transfer-Encoding": "chunked",
                "X-Accel-Buffering": "no"
            }
        )

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

        if not messages or not anthropic_key:
            return jsonify({"error": "missing params"}), 400

        print(f"Chat - {len(messages)} messages")

        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 180,
                "system": system,
                "messages": messages
            },
            timeout=15
        )

        print(f"Anthropic status: {res.status_code}")

        if not res.ok:
            print(f"Anthropic error: {res.text}")
            return jsonify({"error": res.text}), 500

        return jsonify(res.json())

    except Exception as e:
        print(f"Chat error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
