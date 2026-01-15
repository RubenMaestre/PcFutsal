from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List, Optional


def _safe_text(el) -> str:
    if not el:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())


def _parse_player_header(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extrae:
      - nombre mostrado grande (id="playerName")
      - competición actual (id="playerCompet")
      - dorsal grande (id="playerNumber") si viene
      - escudo equipo actual (dentro de .icono_equipo_ficha_jugador img) <-- podría ser útil luego
    También intenta sacar la foto principal del jugador (img grande en .img_jugador_ficha)
    """
    header = {}

    name_el = soup.select_one("#playerName")
    header["nombre_header"] = _safe_text(name_el)

    compet_el = soup.select_one("#playerCompet")
    header["competicion_header"] = _safe_text(compet_el)

    dorsal_el = soup.select_one("#playerNumber")
    # ojo: a veces viene vacío, a veces un número enorme tipo "10"
    dorsal_txt = _safe_text(dorsal_el)
    header["dorsal_header"] = dorsal_txt if dorsal_txt else None

    # escudo del equipo actual (icono a la derecha del jugador)
    escudo_equipo_el = soup.select_one(".icono_equipo_ficha_jugador img")
    header["escudo_equipo_url"] = escudo_equipo_el["src"].strip() if escudo_equipo_el and escudo_equipo_el.has_attr("src") else None

    # foto del jugador
    foto_el = soup.select_one(".img_jugador_ficha img")
    foto_src = None
    if foto_el and foto_el.has_attr("src"):
        foto_src = foto_el["src"].strip()

    header["foto_src"] = foto_src  # puede ser data:image/...base64 o http...
    return header


def _parse_info_jugador_general(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Bloque:
        <h3>Información Jugador</h3>
        luego una .tabla_info_jugador_general con 3 columnas:
          - Nombre y Apellidos -> .info_general
          - Edad -> .info_general
          - Equipo Actual -> .info_general
    """
    out = {
        "nombre_completo": "",
        "edad": None,
        "equipo_actual": "",
    }

    # vamos a pillar la sección cuyo <h3> contenga "Información Jugador"
    info_section = None
    for sec in soup.select("div.info_jugador_general section"):
        h3 = sec.find("h3")
        if h3 and "información jugador" in h3.get_text(strip=True).lower():
            info_section = sec
            break

    if not info_section:
        return out

    # dentro hay .tabla_info_jugador_general con columnas .col-md-4
    cols = info_section.select(".tabla_info_jugador_general > div.col-md-4")
    # esperamos 3 columnas, pero vamos a leer por etiqueta .label_general
    for col in cols:
        label = _safe_text(col.select_one(".label_general")).lower()
        value = _safe_text(col.select_one(".info_general"))

        if "nombre" in label:
            out["nombre_completo"] = value
        elif "edad" in label:
            # intentar convertir a int
            try:
                out["edad"] = int(value)
            except ValueError:
                out["edad"] = None
        elif "equipo actual" in label:
            out["equipo_actual"] = value

    return out


def _parse_estadisticas_sidebar(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Bloque lateral izquierdo:
        <h3>Estadísticas</h3>
        Secuencia de parejas:
            <div class="label_ficha">Convocados</div>
            <div class="enlace_sidebar info">2</div>
        ... etc ...
        Luego amarillas/rojas con class="label_ficha tarjetas_plantilla"
    Vamos a leer en orden e ir emparejando.
    """
    stats = {
        "convocados": None,
        "titular": None,
        "suplente": None,
        "jugados": None,
        "total_goles": None,
        "media_goles": None,
        "amarillas": None,
        "rojas": None,
    }

    # ubicamos el <h3>Estadísticas</h3> dentro de la sidebar
    est_section = None
    for sec in soup.select(".sidebar_ficha_jugador section"):
        h3 = sec.find("h3")
        if h3 and "estadísticas" in h3.get_text(strip=True).lower():
            est_section = sec
            break

    if not est_section:
        return stats

    # Dentro de est_section hay repetición label_ficha / enlace_sidebar.info
    # Vamos a leer todos los hijos directos en orden y emparejar.
    # Truco: iteramos todos los elementos que sean div.label_ficha(...) y cogemos
    # el siguiente sibling .enlace_sidebar.info como valor.

    # OJO: BeautifulSoup.next_siblings incluye textos "\n". Vamos a ir manual:
    labels = est_section.find_all("div", class_=lambda c: c and "label_ficha" in c)

    for label_div in labels:
        label_txt = _safe_text(label_div).lower()
        # buscar el siguiente div.enlace_sidebar.info hermano
        value_div = None
        sib = label_div.next_sibling
        while sib and not (getattr(sib, "name", None) == "div" and "enlace_sidebar" in sib.get("class", []) and "info" in sib.get("class", [])):
            sib = sib.next_sibling
        if sib:
            value_div = sib

        value_txt = _safe_text(value_div) if value_div else ""

        # ahora mapeamos
        if "convocados" in label_txt:
            stats["convocados"] = _to_number(value_txt)
        elif "titular" in label_txt:
            stats["titular"] = _to_number(value_txt)
        elif "suplente" in label_txt:
            stats["suplente"] = _to_number(value_txt)
        elif "jugados" in label_txt:
            stats["jugados"] = _to_number(value_txt)
        elif "total goles" in label_txt:
            stats["total_goles"] = _to_number(value_txt)
        elif "media goles" in label_txt:
            # puede ser decimal
            stats["media_goles"] = _to_float(value_txt)
        elif "amarillas" in label_txt:
            stats["amarillas"] = _to_number(value_txt)
        elif "rojas" in label_txt:
            stats["rojas"] = _to_number(value_txt)

    return stats


def _to_number(txt: str) -> Optional[int]:
    txt = txt.strip()
    if not txt:
        return None
    m = re.search(r"\d+", txt)
    if not m:
        return None
    try:
        return int(m.group(0))
    except ValueError:
        return None


def _to_float(txt: str) -> Optional[float]:
    txt = txt.strip().replace(",", ".")
    if not txt:
        return None
    try:
        return float(txt)
    except ValueError:
        return None


def _parse_historico(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Bloque "Histórico Equipos":
    Dentro del mismo <section> de Información Jugador hay otro <h3>Histórico Equipos</h3>
    y luego <div class="row tabla_info_jugador_general" ...> que contiene muchos
    <div class="row" style="height:25%; ...">, cada uno con:
        div.col-md-10 > [div temporada strong] [div competicion] [div equipo]
    """
    historico: List[Dict[str, str]] = []

    # localizamos el <h3>Histórico Equipos</h3>
    hist_container = None
    for h3 in soup.select("div.info_jugador_general h3"):
        if "histórico equipos" in h3.get_text(strip=True).lower():
            # el contenedor es el siguiente div.tabla_info_jugador_general
            parent_section = h3.find_parent("section")
            if not parent_section:
                continue
            hist_container = parent_section.find("div", class_="tabla_info_jugador_general", attrs={"style": re.compile("overflow-y")})
            if hist_container:
                break

    if not hist_container:
        return historico

    # Cada entrada histórica es un <div class="row" ...> hijo directo dentro de hist_container
    # Seleccionamos sólo los hijos directos con class row (no recursivo)
    for row in hist_container.find_all("div", class_="row", recursive=False):
        block = row.find("div", class_=re.compile(r"\bcol-md-10\b"))
        if not block:
            continue

        # dentro de block hay 3 divs (temporada / competicion / equipo)
        inner_divs = block.find_all("div", recursive=False)
        if len(inner_divs) < 3:
            continue

        temporada_txt = _safe_text(inner_divs[0])
        # temporada_txt puede contener <strong>2016-2017</strong>
        # _safe_text ya lo limpia

        competicion_txt = _safe_text(inner_divs[1])
        equipo_txt = _safe_text(inner_divs[2])

        historico.append({
            "temporada": temporada_txt,
            "competicion": competicion_txt,
            "equipo": equipo_txt,
        })

    return historico


def parse_jugador_ficha(html_text: str, jugador_id: int, id_temp: int) -> Dict[str, Any]:
    """
    Parser principal de ficha de jugador.

    Devuelve dict:
    {
      "jugador_id": ...,
      "id_temp": ...,
      "datos_generales": {
        "nombre_completo": ...,
        "edad": ...,
        "equipo_actual": ...,
      },
      "estadisticas": {
        "convocados": ...,
        "titular": ...,
        "suplente": ...,
        "jugados": ...,
        "total_goles": ...,
        "media_goles": ...,
        "amarillas": ...,
        "rojas": ...,
      },
      "historico": [
        {"temporada": "...", "competicion": "...", "equipo": "..."},
        ...
      ],
      "header": {
        "nombre_header": ...,
        "competicion_header": ...,
        "dorsal_header": ...,
        "escudo_equipo_url": ...,
      },
      "foto": {
        "source": <str>,   # lo que venga en el src del <img> del jugador
        "is_base64": <bool>
      }
    }
    """
    soup = BeautifulSoup(html_text, "lxml")

    header_info = _parse_player_header(soup)
    general_info = _parse_info_jugador_general(soup)
    stats_info = _parse_estadisticas_sidebar(soup)
    historico_info = _parse_historico(soup)

    foto_src = header_info.get("foto_src")
    is_base64 = False
    if foto_src and foto_src.startswith("data:image"):
        is_base64 = True

    data = {
        "jugador_id": jugador_id,
        "id_temp": id_temp,
        "datos_generales": general_info,
        "estadisticas": stats_info,
        "historico": historico_info,
        "header": {
            "nombre_header": header_info.get("nombre_header"),
            "competicion_header": header_info.get("competicion_header"),
            "dorsal_header": header_info.get("dorsal_header"),
            "escudo_equipo_url": header_info.get("escudo_equipo_url"),
        },
        "foto": {
            "source": foto_src,
            "is_base64": is_base64,
        },
    }

    return data
