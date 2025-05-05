import time
import base64
import mimetypes

from runwayml import RunwayML


def as_data_uri(image_path: str) -> str:
    """
    Converte um arquivo de imagem local para data-URI (base64) compatível
    com o parâmetro `prompt_image` do Runway.
    """
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:          # garante um MIME válido
        mime_type = "image/png"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")

    return f"data:{mime_type};base64,{encoded}"

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
