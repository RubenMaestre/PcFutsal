from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re


def _clean_ws(s: str) -> str:
    if not s:
        return ""
    # colapsa espacios repetidos
    return re.sub(r"\s+", " ", s).strip()


def _safe_text(el) -> str:
    if not el:
        return ""
    return _clean_ws(el.get_text(" ", strip=True))


def _fix_mojibake(text: str) -> str:
    """
    Arregla cosas tipo 'VÃ­ctor' -> 'Víctor' si vienen mal decodificadas.
    Heurística: sólo intentamos recodificar si vemos 'Ã' o '�'.
    """
    if not text:
        return text
    if "Ã" in text or "�" in text:
        try:
            return text.encode("latin1").decode("utf-8")
        except Exception:
            return text
    return text


def _extract_equipo_info_header(soup):
    """
    Esto mira el bloque grande de arriba con el marcador:
    <div class="contenedor_equipos_info"> ... </div>
    y devuelve dicts {id_equipo, nombre} para local y visitante, más marcador.
    Lo seguimos usando para marcador.
    """
    cont = soup.find("div", class_="contenedor_equipos_info")
    if not cont:
        return (
            {"id_equipo": None, "nombre": ""},
            {"id_equipo": None, "nombre": ""},
            (None, None),
        )

    bloques_equipo = cont.find_all("div", class_="equipo")
    # normalmente [0] local, [1] visitante
    def parse_equipo_div(eq_div):
        link_nombre = eq_div.find("a", class_="enlace_nombre_equipo_info")
        nombre = _safe_text(link_nombre)
        nombre = _fix_mojibake(nombre)

        href = link_nombre.get("href", "") if link_nombre else ""
        qs = parse_qs(urlparse(href).query)
        id_equipo = None
        if "id_equipo" in qs:
            try:
                id_equipo = int(qs["id_equipo"][0])
            except (ValueError, IndexError):
                id_equipo = None

        return {
            "id_equipo": id_equipo,
            "nombre": nombre,
        }

    if len(bloques_equipo) >= 2:
        info_local = parse_equipo_div(bloques_equipo[0])
        info_visit = parse_equipo_div(bloques_equipo[-1])
    elif len(bloques_equipo) == 1:
        info_local = parse_equipo_div(bloques_equipo[0])
        info_visit = {"id_equipo": None, "nombre": ""}
    else:
        info_local = {"id_equipo": None, "nombre": ""}
        info_visit = {"id_equipo": None, "nombre": ""}

    # marcador
    marcador_div = cont.find("div", class_="resultados-cuentaatras")
    local_goles = None
    visit_goles = None
    if marcador_div:
        nums = re.findall(r"\d+", marcador_div.get_text(" ", strip=True))
        if len(nums) >= 2:
            try:
                local_goles = int(nums[0])
            except ValueError:
                pass
            try:
                visit_goles = int(nums[1])
            except ValueError:
                pass

    return info_local, info_visit, (local_goles, visit_goles)


def _extract_info_partido(soup):
    """
    Saca pabellón, árbitros, fecha, hora.

    Nuevo enfoque:
    - El bloque .estadio_barra tiene varios hijos en orden:
        <a> [icono_campo + <p class="nombre_campo">Pabellón ... |</p> ] </a>
        <img class="icono_campo" src="images/arbitros.png">
        <p class="nombre_campo">Árbitro1 | Árbitro2 | ... | dd-mm-YYYY | HH:MM</p>

    - También hay <input id="fecha"> y <input id="hora"> que suelen ser fiables.
    """
    # 1. fecha/hora base desde los inputs ocultos
    fecha_input = soup.find("input", {"id": "fecha"})
    hora_input = soup.find("input", {"id": "hora"})
    fecha_txt = fecha_input.get("value", "").strip() if fecha_input else ""
    hora_txt = hora_input.get("value", "").strip() if hora_input else ""

    pabellon = ""
    arbitros = []

    barra = soup.find("div", class_="estadio_barra")
    if barra:
        # vamos a recorrer los hijos directos en orden para entender la estructura real
        hijos = list(barra.children)

        # helper regex para detectar fecha y hora
        def es_fecha(s):
            return bool(re.match(r"\d{2}-\d{2}-\d{4}$", s.strip()))

        def es_hora(s):
            return bool(re.match(r"\d{1,2}:\d{2}$", s.strip()))

        # 1) intentar sacar el pabellón
        # normalmente está en el primer <p class="nombre_campo"> dentro del <a>
        primer_p = barra.find("a")
        if primer_p:
            p_pab = primer_p.find("p", class_="nombre_campo")
            if p_pab:
                raw_pab = p_pab.get_text(" ", strip=True)
                # suele venir con una barra final "|", se la quitamos
                raw_pab = raw_pab.rstrip("|").strip()
                pabellon = _fix_mojibake(raw_pab)

        # 2) buscar el <img ... arbitros.png> y coger el <p class="nombre_campo"> justo después
        img_arbitros = None
        for h in hijos:
            if getattr(h, "name", None) == "img":
                src = h.get("src", "")
                if "arbitros" in src:
                    img_arbitros = h
                    break

        if img_arbitros:
            # El siguiente hermano con tag <p class="nombre_campo"> debería tener árbitros | árbitros | ... | fecha | hora
            p_detalles = img_arbitros.find_next_sibling("p", class_="nombre_campo")
            if p_detalles:
                trozos = [t.strip() for t in p_detalles.get_text("|", strip=True).split("|")]
                trozos = [t for t in trozos if t]  # fuera vacíos

                # recorremos en orden: todo lo que NO sea fecha ni hora lo consideramos árbitro, hasta que aparezca fecha/hora
                for pieza in trozos:
                    if es_fecha(pieza):
                        if not fecha_txt:
                            fecha_txt = pieza
                        continue
                    if es_hora(pieza):
                        if not hora_txt:
                            hora_txt = pieza
                        continue
                    # si no es fecha ni hora, es árbitro
                    arbitros.append(_fix_mojibake(pieza))

    return {
        "fecha": fecha_txt,
        "hora": hora_txt,
        "pabellon": pabellon,
        "arbitros": arbitros,
    }



def _clean_player_info_block(info_div, dorsal_num, etiqueta_txt):
    """
    info_div = <div style="font-size..."> ... spans ... </div> dentro del <a class="lista_plantilla_jugadores">
    Queremos sacar el nombre limpio del jugador SIN:
    - minutos "12'"
    - iconos <img>
    - etiqueta 'Pt', 'Ps', 'C'
    - dorsal
    """
    # quitamos spans basura antes de leer texto
    # minutos:
    for sp in info_div.find_all("span", class_="minutos"):
        sp.decompose()
    # etiqueta tipo Pt/Ps/C:
    for sp in info_div.find_all("span", class_="span_etiqueta_alin"):
        sp.decompose()
    # iconos baloncito/tarjeta
    for img in info_div.find_all("img"):
        img.decompose()

    texto_bruto = _safe_text(info_div)

    # quita dorsal suelto
    if dorsal_num is not None:
        # palabra exacta igual al dorsal
        texto_bruto = re.sub(rf"\b{dorsal_num}\b", "", texto_bruto).strip()

    # quita etiqueta suelta (Pt, Ps, C)
    if etiqueta_txt:
        # tal cual
        texto_bruto = re.sub(rf"\b{re.escape(etiqueta_txt)}\b", "", texto_bruto).strip()

    # quita minutos tipo "12'"
    texto_bruto = re.sub(r"\b\d{1,2}'\b", "", texto_bruto).strip()

    # normaliza espacios
    texto_bruto = _clean_ws(texto_bruto)

    # arreglamos mojibake si hay
    texto_bruto = _fix_mojibake(texto_bruto)

    return texto_bruto


def _parse_players_from_ul(ul_tag):
    """
    Devuelve lista de jugadores de un <ul> Titulares o Suplentes.

    Cada li.listaJugador:
      - id_jugador en el href del <a.lista_plantilla_jugadores>
      - dorsal en <span style='color:#ffa500'>..</span>
      - etiqueta (Pt, Ps, C...) en <span class='span_etiqueta_alin'>..</span>
      - nombre limpio usando _clean_player_info_block
    """
    jugadores = []
    if not ul_tag:
        return jugadores

    for li in ul_tag.find_all("li", class_="listaJugador", recursive=False):
        a = li.find("a", class_="lista_plantilla_jugadores")
        if not a:
            continue

        # id_jugador
        jugador_id = None
        href = a.get("href", "")
        qs = parse_qs(urlparse(href).query)
        if "id_jugador" in qs:
            try:
                jugador_id = int(qs["id_jugador"][0])
            except (ValueError, IndexError):
                jugador_id = None

        # dorsal: span con estilo naranja (#ffa500)
        dorsal_span = None
        for sp in a.find_all("span"):
            style = sp.get("style", "")
            if "#ffa500" in style:
                dorsal_span = sp
        dorsal = None
        if dorsal_span:
            m = re.search(r"\d+", dorsal_span.get_text(strip=True))
            if m:
                try:
                    dorsal = int(m.group(0))
                except ValueError:
                    dorsal = None

        # etiqueta (Pt, Ps, C...)
        etiqueta_span = a.find("span", class_="span_etiqueta_alin")
        etiqueta = etiqueta_span.get_text(strip=True) if etiqueta_span else ""
        etiqueta = _clean_ws(etiqueta)

        # nombre jugador:
        info_div = a.find("div")
        nombre_jugador = ""
        if info_div:
            nombre_jugador = _clean_player_info_block(info_div, dorsal, etiqueta)

        jugadores.append({
            "jugador_id": jugador_id,
            "nombre": nombre_jugador,
            "dorsal": dorsal,
            "etiqueta": etiqueta,
        })

    return jugadores


def _parse_tecnicos_from_ul(ul_tag):
    """
    Devuelve lista de técnicos del bloque 'Técnicos':
    [
      { "nombre": "...", "rol": "Entrenador" },
      ...
    ]
    """
    tecnicos = []
    if not ul_tag:
        return tecnicos

    for li in ul_tag.find_all("li", recursive=False):
        a = li.find("a", class_="lista_plantilla_jugadores")
        if not a:
            continue
        info_div = a.find("div")
        if not info_div:
            continue

        # clonar texto para rol
        # el rol suele ir en <span style='font-size: 10px; color: orange;'>Entrenador</span>
        rol_span = info_div.find("span")
        rol = ""
        if rol_span:
            rol = _safe_text(rol_span)
            rol_span.decompose()

        nombre = _safe_text(info_div)
        nombre = _fix_mojibake(nombre)
        rol = _fix_mojibake(rol)

        tecnicos.append({
            "nombre": nombre,
            "rol": rol,
        })

    return tecnicos


def _find_section_ul(block_div, titulo_text):
    """
    Busca el <p> cuyo texto contenga 'Titulares', 'Suplentes' o 'Técnicos',
    y devuelve el <ul> inmediatamente siguiente.
    """
    p = None
    for cand in block_div.find_all("p"):
        if titulo_text.lower() in cand.get_text(strip=True).lower():
            p = cand
            break
    if not p:
        return None
    return p.find_next_sibling("ul")


def _parse_lineup_block(block_div, lado):
    """
    block_div es cada una de las columnas de alineación:
    <div class="col-lg-4 col-md-6" ...>   (local)
    ...
    <div class="col-lg-4 col-md-6" ...>   (visitante)

    Devuelve:
    {
      "id_equipo": ...,
      "nombre": ...,
      "titulares": [...],
      "suplentes": [...],
      "tecnicos": [...],
      "lado": "local"|"visitante"
    }
    """

    # nombre del equipo en este bloque:
    # normalmente hay un span plano (sin id/class) al principio con el nombre.
    nombre_equipo = ""
    for sp in block_div.find_all("span", recursive=False):
        if sp.get("id") or sp.get("class"):
            continue
        txt = _safe_text(sp)
        if txt:
            nombre_equipo = txt
            break
    nombre_equipo = _fix_mojibake(nombre_equipo)

    # id_equipo está en el span.boton_equipacion -> id="boton_297544"
    boton_span = block_div.find("span", class_="boton_equipacion")
    id_equipo = None
    if boton_span and boton_span.has_attr("id"):
        m = re.search(r"_(\d+)$", boton_span["id"])
        if m:
            try:
                id_equipo = int(m.group(1))
            except ValueError:
                id_equipo = None

    # Titulares / Suplentes / Técnicos
    ul_tit = _find_section_ul(block_div, "Titulares")
    ul_sup = _find_section_ul(block_div, "Suplentes")
    ul_tec = _find_section_ul(block_div, "Técnicos")

    titulares = _parse_players_from_ul(ul_tit)
    suplentes = _parse_players_from_ul(ul_sup)
    tecnicos = _parse_tecnicos_from_ul(ul_tec)

    return {
        "id_equipo": id_equipo,
        "nombre": nombre_equipo,
        "titulares": titulares,
        "suplentes": suplentes,
        "tecnicos": tecnicos,
        "lado": lado,
    }


def _parse_timeline_events(soup):
    """
    Devuelve lista de eventos (goles, tarjetas...) de la timeLineContainer:
    [
      {
        "minuto": 16,
        "tipo": "Gol",
        "jugador_id": 27442892,
        "jugador_nombre": "GARCÍA CAMPILLO, ALBERTO",
        "equipo": "local" | "visitante"
      },
      ...
    ]
    """
    out = []
    timeline = soup.find("div", class_="timeLineContainer")
    if not timeline:
        return out

    for ev_div in timeline.select(".eventosTimeLine > div"):
        clases = ev_div.get("class", [])
        if "eventosLocalTimeLine" in clases:
            equipo = "local"
        elif "eventosVisitanteTimeLine" in clases:
            equipo = "visitante"
        else:
            continue  # saltar 'eventosFijosTimeLine' etc

        header = ev_div.find("header", class_="eventoInfoCabecera")
        if not header:
            continue

        # minuto tipo "16'"
        minuto_el = header.find("time", class_="eventoInfoMinuto")
        minuto_raw = _safe_text(minuto_el)  # "16'"
        minuto_num = None
        if minuto_raw:
            m = re.search(r"(\d+)", minuto_raw)
            if m:
                try:
                    minuto_num = int(m.group(1))
                except ValueError:
                    minuto_num = None

        # tipo = header sin el minuto
        header_text = _safe_text(header)
        tipo = header_text.replace(minuto_raw, "").strip() if minuto_raw else header_text
        tipo = _clean_ws(tipo)

        # jugador
        jugador_a = ev_div.find("a", class_="eventoInfoJugadorNombre")
        jugador_nombre = _fix_mojibake(_safe_text(jugador_a))
        jugador_id = None
        if jugador_a:
            href = jugador_a.get("href", "")
            qs = parse_qs(urlparse(href).query)
            if "id_jugador" in qs:
                try:
                    jugador_id = int(qs["id_jugador"][0])
                except (ValueError, IndexError):
                    jugador_id = None

        out.append({
            "minuto": minuto_num,
            "tipo": tipo,
            "jugador_id": jugador_id,
            "jugador_nombre": jugador_nombre,
            "equipo": equipo,
        })

    return out


def parse_partido_detalle(html_text: str):
    """
    Parser principal de un partido individual (partido.php).
    Devuelve un dict con:
    {
      "info_partido": {...},
      "marcador": {...},
      "equipos": {
         "local": {...},
         "visitante": {...}
      },
      "eventos": [...]
    }
    """
    soup = BeautifulSoup(html_text, "lxml")

    # info general partido (fecha, hora, pabellón, árbitros)
    info_partido = _extract_info_partido(soup)

    # datos cabecera (equipos + marcador arriba)
    info_local_hdr, info_visit_hdr, (g_local, g_visit) = _extract_equipo_info_header(soup)

    # columnas de alineación en la parte baja
    alineacion_cols = soup.select(
        "div.contenido-partido div.container div.row > div.col-lg-4.col-md-6"
    )
    # por tu HTML:
    #   [0] -> local
    #   [1] -> visitante
    equipo_local_data = _parse_lineup_block(alineacion_cols[0], "local") if len(alineacion_cols) > 0 else {}
    equipo_visitante_data = _parse_lineup_block(alineacion_cols[-1], "visitante") if len(alineacion_cols) > 0 else {}

    # si en la alineación no ha salido nombre/id (o por seguridad),
    # usa los de la cabecera
    if info_local_hdr.get("id_equipo") and not equipo_local_data.get("id_equipo"):
        equipo_local_data["id_equipo"] = info_local_hdr["id_equipo"]
    if info_local_hdr.get("nombre") and not equipo_local_data.get("nombre"):
        equipo_local_data["nombre"] = info_local_hdr["nombre"]

    if info_visit_hdr.get("id_equipo") and not equipo_visitante_data.get("id_equipo"):
        equipo_visitante_data["id_equipo"] = info_visit_hdr["id_equipo"]
    if info_visit_hdr.get("nombre") and not equipo_visitante_data.get("nombre"):
        equipo_visitante_data["nombre"] = info_visit_hdr["nombre"]

    marcador = {
        "local": g_local,
        "visitante": g_visit,
    }

    eventos = _parse_timeline_events(soup)

    data = {
        "info_partido": info_partido,
        "marcador": marcador,
        "equipos": {
            "local": equipo_local_data,
            "visitante": equipo_visitante_data,
        },
        "eventos": eventos,
    }
    return data
