from __future__ import annotations
import os, uuid, requests, re
from pathlib import Path
from typing import Final, Literal
from crewai.tools import BaseTool

class ElevenTTSTool(BaseTool):
    name: str = "eleven_tts"
    description: str = "Gera narração via ElevenLabs TTS (stream)."

    _BASE: Final[str] = "https://api.elevenlabs.io/v1"
    _MODEL: Final[str] = "eleven_multilingual_v2"
    _OUT:   Final[Path] = Path("out")
    _FMT:   Final[str] = "mp3_44100"
    _LAT:   Final[Literal[0, 1, 2]] = 0

    # --- util --------------------------------------------------
    def _resolve_voice(self, voice_or_name: str, key: str) -> str:
        # se parece um slug/nome, busca
        if re.fullmatch(r"[A-Za-z\- ]{3,}", voice_or_name):
            url = f"{self._BASE}/voices/search?query={voice_or_name}"
            r = requests.get(url, headers={"xi-api-key": key}, timeout=30).json()
            if not r["voices"]:
                raise ValueError(f"Voz '{voice_or_name}' não encontrada")
            return r["voices"][0]["voice_id"]
        return voice_or_name  # já é ID

    # --- run ---------------------------------------------------
    def _run(self, text: str, voice_id: str = "pNInz6obpgDQGcFmaJgB") -> str:
        api_key = os.getenv("ELEVEN_API_KEY") or os.getenv("ELEVEN_LABS_API_KEY")
        if not api_key:
            raise EnvironmentError("Defina ELEVEN_API_KEY")

        vid = self._resolve_voice(voice_id, api_key)

        url = f"{self._BASE}/text-to-speech/{vid}/stream"
        headers = {"xi-api-key": api_key, "Accept": "audio/mpeg"}
        payload = {
            "text": text,
            "model_id": self._MODEL,
            "output_format": self._FMT,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
            "optimize_streaming_latency": self._LAT,
        }

        with requests.post(url, json=payload, headers=headers, stream=True, timeout=90) as r:
            r.raise_for_status()
            self._OUT.mkdir(exist_ok=True)
            out_file = self._OUT / f"voice_{uuid.uuid4()}.mp3"
            with open(out_file, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

        return str(out_file.resolve())
