import os, requests, time
from pathlib import Path
from runwayml import RunwayML

from media_crew.utils import as_data_uri


def test_eleven_tool():
    from media_crew.tools.eleven_tts import ElevenTTSTool
    mp3 = ElevenTTSTool()._run("Teste rápido!", voice_id="EXAVITQu4vr4xnSDxMaL")
    assert mp3.endswith(".mp3") and Path(mp3).exists()

def wait_for_video(task_id: str, client: RunwayML, poll=5, timeout=300):
    """
    Bloqueia até a tarefa terminar ou estourar o timeout.
    Retorna o URL do vídeo.
    """
    start = time.time()
    while True:
        task = client.tasks.retrieve(id=task_id)     # <-- consulta
        status = task.status.upper()                 # PENDING | RUNNING | SUCCEEDED | FAILED | CANCELED
        print(f"[{round(time.time()-start):>3}s] status: {status}")

        if status == "SUCCEEDED":
            return task.output[0]                    # lista de URLs
        if status in ("FAILED", "CANCELED"):
            raise RuntimeError(f"Tarefa terminou com status {status}: {task.error}")

        if time.time() - start > timeout:
            raise TimeoutError("Tempo de espera excedido.")
        time.sleep(poll)

def test_runwayml() -> None:
    client = RunwayML(api_key=os.environ["RUNWAY_API_KEY"])

    prompt_image_b64 = as_data_uri("assets/RPA Core.webp")

    job = client.image_to_video.create(
        model="gen4_turbo",
        prompt_image=prompt_image_b64,
        ratio="1280:720",
        prompt_text="Make it with wind blowing and smooth waves",
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
    video_url = wait_for_video(task_id="1b8cd7cc-d919-4f63-aa1f-f955a9b4b392", client=RunwayML(api_key=os.environ["RUNWAY_API_KEY"]))

    video_bytes = requests.get(video_url).content
    out_path = Path("gen_video.mp4")
    out_path.write_bytes(video_bytes)
    print("Vídeo salvo em", out_path.resolve())