import os
import time
import requests

BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://resultadosffcv.isquad.es/",
}

def fetch_url(url: str, save_path: str, sleep_after: float = 1.0) -> str:
    """
    Descarga una URL y guarda el HTML en disco.
    Devuelve la ruta final en disco.
    Ahora también imprime info debug.
    """
    print(f"[fetch_url] GET {url}")
    resp = requests.get(url, headers=BASE_HEADERS, timeout=10)
    print(f"[fetch_url] status_code={resp.status_code}")
    print(f"[fetch_url] content_length={len(resp.text)} chars")

    resp.raise_for_status()

    # nos aseguramos de que existe la carpeta destino
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(resp.text)

    time.sleep(sleep_after)

    return save_path
