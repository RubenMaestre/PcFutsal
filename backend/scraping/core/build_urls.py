from scraping.config_temporadas import TEMPORADAS
from urllib.parse import urlencode

def build_jugador_url(temp_key: str, jugador_id: int) -> str:
    """
    Ejemplo real:
    jugador_ficha.php?id_jugador=73361&id_temp=21
    Usamos id_temp de TEMPORADAS[temp_key]["id_temp"]
    """
    cfg = TEMPORADAS[temp_key]
    params = {
        "id_jugador": jugador_id,
        "id_temp": cfg["id_temp"],
    }
    return "https://resultadosffcv.isquad.es/jugador_ficha.php?" + urlencode(params)
