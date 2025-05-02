import base64
import mimetypes


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