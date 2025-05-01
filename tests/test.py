import os, requests, json, time

from pathlib import Path


def test_eleven_tool():
    from media_crew.tools.eleven_tts import ElevenTTSTool
    mp3 = ElevenTTSTool()._run("Teste rápido!", voice_id="EXAVITQu4vr4xnSDxMaL")
    assert mp3.endswith(".mp3") and Path(mp3).exists()

API_BASE    = "https://api.dev.runwayml.com/v1"
API_VERSION = "2024-11-06"
MODEL       = "gen4_turbo"
PROMPT      = "A cute dog and cat playing chess, cinematic, 9:16"
DURATION    = 4
OUT_DIR     = Path("out/video")

def test_runway_tool():
    key = os.getenv("RUNWAY_API_KEY")
    if not key:
        raise SystemExit("❌  RUNWAY_API_KEY não definido")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Runway-Version": API_VERSION,
    }
    payload = {
        "model": MODEL,
        "input": {
            "prompt": PROMPT,
            "duration": DURATION
        }
    }

    print("🚀 Criando geração…")
    r = requests.post(f"{API_BASE}/image_to_video",
                      json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    task_id = r.json()["id"]
    print("🆔 Task:", task_id)

    # poll
    while True:
        info = requests.get(f"{API_BASE}/tasks/{task_id}",
                            headers=headers, timeout=30).json()
        status = info["status"]
        print("⏳", status)
        if status == "SUCCEEDED":
            video_url = info["output"][0]["url"]
            break
        if status in ("FAILED", "CANCELED"):
            raise RuntimeError(info.get("error", "Runway task failed"))
        time.sleep(5)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mp4 = OUT_DIR / f"runway_{task_id[-6:]}.mp4"
    mp4.write_bytes(requests.get(video_url, timeout=120).content)
    print("✅ Salvo em", mp4.resolve())


if __name__ == '__main__':
    test_runway_tool()