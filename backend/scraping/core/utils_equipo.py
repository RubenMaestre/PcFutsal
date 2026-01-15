from typing import Dict, Set, List

def collect_equipo_ids_from_jornada(jornada_data: Dict) -> Set[int]:
    """
    Recoge los id_equipo a partir de los partidos detallados que ya hemos parseado.
    OJO: la jornada general (total_partidos) no tiene el id_equipo, sólo nombres.
    El id_equipo lo tenemos en los JSON de partidos_detalle.

    Este helper no mira disco: asume que le pasas ya los dicts de partidos_detalle.
    """
    ids: Set[int] = set()

    # jornada_data aquí será lista de dicts partido_detalle (uno por partido)
    for partido in jornada_data:
        equipos = partido.get("equipos", {})
        for lado in ("local", "visitante"):
            eq = equipos.get(lado, {})
            eid = eq.get("id_equipo")
            if isinstance(eid, int):
                ids.add(eid)

    return ids
