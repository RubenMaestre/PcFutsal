import os
import json
from typing import Set, Dict, Any, List


def collect_jugadores_from_equipos(clean_equipos_dir: str) -> List[int]:
    """
    Lee todos los JSON de data_clean/equipos/
    y devuelve todos los jugador_id únicos que aparezcan en ["jugadores"].

    clean_equipos_dir: carpeta tipo "data_clean/equipos"
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
            print(f"[utils_jugadores] No pude leer {fpath}: {e}")
            continue

        jugadores = data.get("jugadores", [])
        for j in jugadores:
            j_id = j.get("jugador_id")
            if isinstance(j_id, int):
                ids.add(j_id)

    return sorted(ids)
