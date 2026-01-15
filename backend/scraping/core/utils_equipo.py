from typing import Dict, Set, List

def collect_equipo_ids_from_jornada(jornada_data: Dict) -> Set[int]:
    """
    Recoge los id_equipo únicos a partir de los partidos detallados parseados.
    
    IMPORTANTE: La jornada general (total_partidos) no tiene el id_equipo, sólo nombres.
    El id_equipo solo está disponible en los JSON de partidos_detalle, por lo que
    esta función debe recibir datos ya parseados de partidos detallados.
    
    Este helper no accede a disco: asume que le pasas ya los dicts de partidos_detalle
    en memoria, lo que mejora el rendimiento al evitar I/O repetido.
    """
    ids: Set[int] = set()

    # jornada_data aquí será lista de dicts partido_detalle (uno por partido)
    for partido in jornada_data:
        equipos = partido.get("equipos", {})
        # Recorremos ambos equipos (local y visitante) para obtener todos los IDs.
        for lado in ("local", "visitante"):
            eq = equipos.get(lado, {})
            eid = eq.get("id_equipo")
            # Solo añadimos IDs válidos (enteros) para evitar errores.
            if isinstance(eid, int):
                ids.add(eid)

    return ids
