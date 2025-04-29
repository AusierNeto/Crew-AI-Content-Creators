"""
quick_tts_test.py  –  Testa a API do ElevenLabs com requests

Uso:
  $ export ELEVEN_API_KEY="sk-···"          # Linux/macOS
  # setx ELEVEN_API_KEY "sk-···"            # Windows (PowerShell)
  $ python quick_tts_test.py
"""
import os
import uuid
from pathlib import Path

import requests

# Configuráveis ──────────────────────────────────────────────────────────
VOICE_ID   = "EXAVITQu4vr4xnSDxMaL"          # Bella (pode trocar)
TEXT       = "Olá! Este é um teste da API de texto para fala da ElevenLabs."
MODEL_ID   = "eleven_multilingual_v2"        # modelo default
OUTPUT_DIR = Path("out")                     # pasta destino
# -----------------------------------------------------------------------

def main() -> None:
    api_key = os.getenv("ELEVEN_API_KEY")
    if not api_key:
        raise SystemExit("❌  Defina ELEVEN_API_KEY no ambiente antes de rodar o script.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "xi-api-key": api_key,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }
    payload = {
        "text": TEXT,
        "model_id": MODEL_ID,
        "output_format": "mp3_44100",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
        "optimize_streaming_latency": 0,
    }

    print("🔊 Gerando áudio…")
    with requests.post(url, json=payload, headers=headers, stream=True, timeout=90) as r:
        r.raise_for_status()

        OUTPUT_DIR.mkdir(exist_ok=True)
        mp3_path = OUTPUT_DIR / f"voice_{uuid.uuid4()}.mp3"
        with open(mp3_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"✅  Arquivo salvo em {mp3_path.resolve()}")

if __name__ == "__main__":
    main()
