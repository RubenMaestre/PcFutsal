from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs


def _safe_text(el):
    if not el:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())


def _get_equipo_metadata(soup):
    """
    Extrae los metadatos del equipo desde la página de plantilla de FFCV.
    Esta función parsea la estructura HTML específica de FFCV para obtener:
    - id_equipo (del parámetro en la URL activa del tab)
    - nombre_equipo (h1.titulo_card_club)
    - pabellon (span.nombre_estadio dentro del <a class='datos_clubs_info'> con icono-estadio)
    - telefono (fa-phone)
    - email (fa-envelope)
    - escudo_url (div.bloque_club_logo img[src=...])
    """

    # El id_equipo se extrae de la URL de las pestañas del menú de clubes.
    # FFCV usa pestañas con URLs que contienen el parámetro id_equipo.
    id_equipo = None
    pestañas = soup.select("div.menu_clubs a.tab_menu_club[href*='equipo_plantilla.php']")
    if pestañas:
        href = pestañas[0].get("href", "")
        qs = parse_qs(urlparse(href).query)
        if "id_equipo" in qs:
            try:
                id_equipo = int(qs["id_equipo"][0])
            except (ValueError, IndexError):
                # Si el parámetro no es un número válido, dejamos id_equipo como None
                id_equipo = None

    # escudo
    escudo_img = soup.select_one(".bloque_club_logo img")
    escudo_url = escudo_img.get("src").strip() if escudo_img and escudo_img.has_attr("src") else ""

    # nombre equipo
    nombre_equipo_el = soup.select_one(".card_info_club h1.titulo_card_club")
    nombre_equipo = _safe_text(nombre_equipo_el)

    # pabellón: es el primer .datos_clubs_info con icono-estadio.png
    pabellon = ""
    for datos_div in soup.select(".card_info_club .datos_clubs_info"):
        icon = datos_div.find("img", src=re.compile("icono-estadio"))
        if icon:
            pabellon_span = datos_div.select_one(".nombre_estadio")
            pabellon = _safe_text(pabellon_span)
            break

    # Teléfono: se busca el icono fa-phone y se extrae el número.
    # Usamos regex para limpiar cualquier texto que no sea numérico al inicio,
    # ya que el icono puede estar pegado al número en el HTML.
    telefono = ""
    for datos_div in soup.select(".card_info_club .datos_clubs_info"):
        phone_i = datos_div.find("i", class_=re.compile("fa-phone"))
        if phone_i:
            telefono = datos_div.get_text(" ", strip=True)
            # Eliminamos cualquier carácter no numérico al inicio (incluyendo el icono si está pegado).
            telefono = re.sub(r"^[^0-9+]*", "", telefono)
            break

    # Email: se busca el icono fa-envelope en los bloques de datos del club.
    # También se buscan divs con estilo inline que puedan contener el email.
    email = ""
    for datos_div in soup.select(".card_info_club .datos_clubs_info, .card_info_club div[style*='color:white']"):
        mail_i = datos_div.find("i", class_=re.compile("fa-envelope"))
        if mail_i:
            email_span = datos_div.find("span")
            email = _safe_text(email_span)
            break

    return {
        "id_equipo": id_equipo,
        "nombre_equipo": nombre_equipo,
        "pabellon": pabellon,
        "telefono": telefono,
        "email": email,
        "escudo_url": escudo_url,
    }


def _get_jugadores(soup):
    """
    En la sección:
    <div class="row listado_jugadores"> ... <a href="jugador_ficha.php?id_jugador=XXXXX" class="card_jugador"> ...
        <h4>APELLIDOS, NOMBRE</h4>
    Guardamos id_jugador y nombre.
    """
    jugadores = []

    for card in soup.select("a.card_jugador[href*='jugador_ficha.php']"):
        href = card.get("href", "")
        qs = parse_qs(urlparse(href).query)
        jugador_id = None
        if "id_jugador" in qs:
            try:
                jugador_id = int(qs["id_jugador"][0])
            except (ValueError, IndexError):
                jugador_id = None

        nombre_el = card.select_one("h4")
        nombre = _safe_text(nombre_el)

        # También podríamos sacar la foto base64 si quieres más adelante.
        jugadores.append({
            "jugador_id": jugador_id,
            "nombre": nombre,
        })

    return jugadores


def _get_tecnicos(soup):
    """
    Técnicos tienen <a class='card_tecnico'> en la segunda sección de listado_jugadores
    Dentro:
      <h4>APELLIDOS, NOMBRE</h4>
      <dt>Cargo</dt><dd><span>Técnico</span></dd>
    """
    tecnicos = []
    for card in soup.select("a.card_tecnico"):
        nombre_el = card.select_one("h4")
        nombre = _safe_text(nombre_el)

        cargo_el = card.select_one("dd span")
        cargo = _safe_text(cargo_el)

        tecnicos.append({
            "nombre": nombre,
            "cargo": cargo,
        })
    return tecnicos


def parse_equipo_plantilla(html_text):
    """
    Devuelve:
    {
      "equipo": {
         "id_equipo": ...,
         "nombre_equipo": ...,
         "pabellon": ...,
         "telefono": ...,
         "email": ...,
         "escudo_url": ...
      },
      "jugadores": [
         { "jugador_id":..., "nombre":... },
         ...
      ],
      "tecnicos": [
         { "nombre":..., "cargo":... },
         ...
      ]
    }
    """
    soup = BeautifulSoup(html_text, "html.parser")

    equipo_info = _get_equipo_metadata(soup)
    jugadores = _get_jugadores(soup)
    tecnicos = _get_tecnicos(soup)

    return {
        "equipo": equipo_info,
        "jugadores": jugadores,
        "tecnicos": tecnicos,
    }
