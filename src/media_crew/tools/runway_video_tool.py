# tools/runway_video.py
from __future__ import annotations
import os, time, uuid, requests
from pathlib import Path
from typing import Final

from crewai.tools import BaseTool


class RunwayVideoTool(BaseTool):
    """Gera vídeos 9:16 via Runway Gen-4 Turbo."""
    name: str = "runway_video"
    description: str = "Cria MP4 vertical usando a API dev.runwayml.com."

    _BASE:   Final[str] = "https://api.dev.runwayml.com/v1"
    _VERSION: Final[str] = "2024-11-06"
    _MODEL:  Final[str] = "gen4_turbo"
    _OUTDIR: Final[Path] = Path("out/video")

    def _run(self, prompt: str, duration: int = 4) -> str:
        key = os.getenv("RUNWAY_API_KEY")
        if not key:
            raise EnvironmentError("Defina RUNWAY_API_KEY")

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Runway-Version": self._VERSION,
        }
        payload = {
            "model": self._MODEL,
            "promptText": prompt,
            "duration": duration,          # inteiro 1-10 s
            # opcional: "promptImage": "https://...",
        }

        # 1. cria a geração
        res = requests.post(f"{self._BASE}/image_to_video",
                            json=payload, headers=headers, timeout=60)
        res.raise_for_status()
        task_id = res.json()["id"]

        # 2. polla até concluir
        while True:
            task = requests.get(f"{self._BASE}/tasks/{task_id}",
                                headers=headers, timeout=30).json()
            if task["status"] == "SUCCEEDED":
                url = task["output"][0]["url"]
                break
            if task["status"] in ("FAILED", "CANCELED"):
                raise RuntimeError(f"Runway falhou: {task.get('error')}")
            time.sleep(5)

        # 3. baixa o MP4 (opcional)
        self._OUTDIR.mkdir(parents=True, exist_ok=True)
        mp4 = self._OUTDIR / f"runway_{uuid.uuid4()}.mp4"
        mp4.write_bytes(requests.get(url, timeout=120).content)
        return str(mp4.resolve())
