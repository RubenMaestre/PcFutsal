import os
import json
from typing import Set, Dict, Any, List


def collect_jugadores_from_equipos(clean_equipos_dir: str) -> List[int]:
    """
    Recopila todos los IDs únicos de jugadores desde los JSON de equipos parseados.
    Esta función es útil para determinar qué jugadores necesitan ser scrapeados
    después de haber parseado las plantillas de los equipos.
    
    clean_equipos_dir: carpeta tipo "data_clean/equipos" con los JSON parseados
    """
    ids: Set[int] = set()

    for fname in os.listdir(clean_equipos_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(clean_equipos_dir, fname)

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            # Si un archivo está corrupto o no se puede leer, lo saltamos
            # para no interrumpir el proceso completo.
            print(f"[utils_jugadores] No pude leer {fpath}: {e}")
            continue

        jugadores = data.get("jugadores", [])
        for j in jugadores:
            j_id = j.get("jugador_id")
            # Solo añadimos IDs válidos (enteros) para evitar errores en el scraping posterior.
            if isinstance(j_id, int):
                ids.add(j_id)

    return sorted(ids)  # Devolvemos ordenados para facilitar el debugging
