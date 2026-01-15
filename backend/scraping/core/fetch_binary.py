import requests
import os

def fetch_binary(url: str, out_path: str):
    """
    Descarga un recurso binario (png, jpg...) y lo guarda tal cual.
    No hace prints ruidosos, eso lo hace quien llame.
    """
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(resp.content)
