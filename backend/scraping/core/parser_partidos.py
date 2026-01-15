from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import re


def _extraer_jornada_actual(soup: BeautifulSoup) -> Optional[int]:
    """
    Lee el bloque del selector de jornada y saca el texto "Jornada X".
    Está en el botón naranja (Filtro por Jornada).
    """
    # buscamos el dropdown de jornadas
    boton_jornada = soup.select_one(
        "div.dropdown-jornadas button.boton_selector div"
    )
    if not boton_jornada:
        return None

    txt = boton_jornada.get_text(strip=True)  # "Jornada 1"
    m = re.search(r"Jornada\s+(\d+)", txt, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _extraer_partidos_y_fechas(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Recorre las filas del <table class='table sobrestante'>.
    Cada bloque de fecha viene en un <tr class='sinsombra'> con .fecha.
    Cada partido viene en el siguiente <tr> normal.
    Vamos guardando la 'fecha_texto' actual para asignarla a los partidos que sigan.
    """
    partidos: List[Dict[str, Any]] = []

    tbody = soup.select_one("table.sobrestante tbody")
    if not tbody:
        return partidos

    current_fecha_texto: Optional[str] = None

    # recorrer hijos <tr> en orden
    for tr in tbody.find_all("tr", recursive=False):
        # caso 1: fila de fecha
        if "sinsombra" in tr.get("class", []):
            fecha_div = tr.select_one("div.fecha")
            if fecha_div:
                current_fecha_texto = fecha_div.get_text(strip=True)
            continue

        # caso 2: fila de partido normal
        celdas = tr.find_all("td", recursive=False)
        if len(celdas) < 6:
            # fila rara (modal, etc)
            continue

        # --- equipo local ---
        # primera celda tiene <a> con nombre local
        a_local = celdas[0].select_one("a.nombre_equipos_tabla")
        local_nombre = a_local.get_text(strip=True) if a_local else None

        # --- marcador ---
        marcador_td = celdas[2]
        spans_marcador = marcador_td.select("span.marcador")
        goles_local = None
        goles_visitante = None
        if len(spans_marcador) >= 2:
            # primer span = local, segundo = visitante
            goles_local = spans_marcador[0].get_text(strip=True)
            goles_visitante = spans_marcador[1].get_text(strip=True)

        # --- equipo visitante ---
        a_visitante = celdas[4].select_one("a.nombre_equipos_tabla")
        visitante_nombre = a_visitante.get_text(strip=True) if a_visitante else None

        # --- pabellón ---
        pabellon_div = celdas[5].select_one("div")
        pabellon_txt = pabellon_div.get_text(strip=True) if pabellon_div else None

        # --- id_partido ---
        # podemos sacar el primer <a href='partido.php?...id_partido=XXXXX...'>
        enlace_partido = tr.select_one("a[href*='partido.php']")
        id_partido = None
        if enlace_partido and enlace_partido.has_attr("href"):
            href = enlace_partido["href"]
            m_id = re.search(r"id_partido=(\d+)", href)
            if m_id:
                id_partido = int(m_id.group(1))

        # si no lo encontramos por href, plan B: mirar el onclick del botón Historial
        if not id_partido:
            btn_hist = tr.select_one("[onclick*='modalHistorial']")
            if btn_hist and btn_hist.has_attr("onclick"):
                oc = btn_hist["onclick"]
                m2 = re.search(r"modalHistorial\((\d+)", oc)
                if m2:
                    id_partido = int(m2.group(1))

        partidos.append({
            "fecha_texto": current_fecha_texto,  # ej "jueves, 11 De septiembre"
            "local_nombre": local_nombre,
            "visitante_nombre": visitante_nombre,
            "goles_local": goles_local,
            "goles_visitante": goles_visitante,
            "pabellon": pabellon_txt,
            "id_partido": id_partido,
        })

    return partidos


def parse_jornada_partidos(html_text: str) -> Dict[str, Any]:
    """
    Dado el HTML de una jornada (lista de partidos),
    devuelve una estructura limpia con:
      - jornada_num
      - partidos: [ { ... }, ... ]
    """
    soup = BeautifulSoup(html_text, "lxml")

    jornada_num = _extraer_jornada_actual(soup)
    partidos = _extraer_partidos_y_fechas(soup)

    data = {
        "jornada": jornada_num,
        "partidos": partidos,
    }
    return data
