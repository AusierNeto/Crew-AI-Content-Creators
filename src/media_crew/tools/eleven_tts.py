from __future__ import annotations
import os, uuid, requests
from pathlib import Path
from typing import Final, Literal

from crewai.tools import BaseTool   # pip install crewai[tools]

class ElevenTTSTool(BaseTool):
    """Gera narração via ElevenLabs e devolve o caminho do MP3."""
    name: str = "eleven_tts"
    description: str = "Converte texto em voz realista (stream endpoint)."

    _BASE: Final[str] = "https://api.elevenlabs.io/v1"
    _MODEL: Final[str] = "eleven_multilingual_v2"
    _FMT:   Final[str] = "mp3_44100"
    _DIR:   Final[Path] = Path("out")
    _LAT:   Final[Literal[0, 1, 2]] = 0

    def _run(self, text: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL") -> str:
        key = os.getenv("ELEVEN_API_KEY") or os.getenv("ELEVEN_LABS_API_KEY")
        if not key:
            raise EnvironmentError("Defina ELEVEN_API_KEY")

        url = f"{self._BASE}/text-to-speech/{voice_id}/stream"
        headers = {"xi-api-key": key, "Accept": "audio/mpeg"}
        payload = {
            "text": text,
            "model_id": self._MODEL,
            "output_format": self._FMT,
            "voice_settings": {"stability": .45, "similarity_boost": .8},
            "optimize_streaming_latency": self._LAT,
        }

        with requests.post(url, json=payload, headers=headers, stream=True, timeout=90) as r:
            r.raise_for_status()
            self._DIR.mkdir(exist_ok=True)
            out = self._DIR / f"voice_{uuid.uuid4()}.mp3"
            with open(out, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

        return str(out.resolve())
