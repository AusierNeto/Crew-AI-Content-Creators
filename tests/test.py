import os, requests
from pathlib import Path
from runwayml import RunwayML

from test_utils import as_data_uri, wait_for_video


def test_eleven_tool():
    from media_crew.tools.eleven_tts import ElevenTTSTool
    mp3 = ElevenTTSTool()._run("Teste rápido!", voice_id="EXAVITQu4vr4xnSDxMaL")
    assert mp3.endswith(".mp3") and Path(mp3).exists()

def test_runwayml() -> None:
    client = RunwayML(api_key=os.environ["RUNWAY_API_KEY"])

    prompt_image_b64 = as_data_uri("assets/RPA Core.webp")

    job = client.image_to_video.create(
        model="gen4_turbo",
        prompt_image=prompt_image_b64,
        ratio="1280:720",
        prompt_text="One of these man jumps on the table and crashes out while the others look scared",
    )

    print("Job ID:", job.id)

    video_url = wait_for_video(job.id, client)
    print("Vídeo pronto em:", video_url)

    # download opcional
    video_bytes = requests.get(video_url).content
    out_path = Path("out/gen_video.mp4")
    out_path.write_bytes(video_bytes)
    print("Vídeo salvo em", out_path.resolve())


if __name__ == '__main__':
    test_runwayml()