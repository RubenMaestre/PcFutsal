from django.core.management.base import BaseCommand
from django.db import transaction

import os
import json
from urllib.parse import urlencode

from scraping.core.config_temporadas import TEMPORADAS
from scraping.core.fetcher import fetch_url
from scraping.core.parser_partidos import parse_jornada_partidos
from scraping.core.parser_partido_detalle import parse_partido_detalle
from scraping.core.temporadas_utils import get_or_create_temporada

from nucleo.models import Temporada, Grupo, Competicion
from clubes.models import Club
from partidos.models import Partido, EventoPartido, AlineacionPartidoJugador
from jugadores.models import Jugador, JugadorEnClubTemporada
from arbitros.models import Arbitro, ArbitrajePartido
from staff.models import StaffClub, StaffEnPartido


# ======================================
# HELPERS DE NOMBRE DE COMPETICIÓN (BD)
# ======================================

# Mapeo de claves de competición usadas en FFCV a nombres normalizados en nuestra BD.
# Esto permite mantener consistencia en los nombres aunque FFCV use abreviaciones diferentes.
COMPETICION_NAME_MAP = {
    "TERCERA": "Tercera División",
    "PREFERENTE": "Preferente",
    "PRIMERA": "Primera Regional",
    "SEGUNDA": "Segunda Regional",
}


def _competicion_nombre_for_bd(competicion_key: str) -> str:
    # Normaliza el nombre de la competición para almacenarlo en BD.
    # Si la clave no está en el mapa, usa "Tercera División" como fallback.
    return COMPETICION_NAME_MAP.get(competicion_key.upper(), "Tercera División")


# ======================================
# COMANDO
# ======================================

class Command(BaseCommand):
    help = "Descarga una jornada, parsea actas y mete TODO en BD (partidos, eventos, clubs, jugadores, staff, árbitros...)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--temporada",
            type=str,
            default="2025-2026",
            help="Clave de temporada (por defecto: 2025-2026)",
        )
        parser.add_argument(
            "--jornada",
            type=int,
            default=1,
            help="Número de jornada (por defecto: 1)",
        )
        parser.add_argument(
            "--competicion",
            type=str,
            default="TERCERA",
            help="Competición: TERCERA | PREFERENTE | PRIMERA | SEGUNDA (por defecto: TERCERA)",
        )
        parser.add_argument(
            "--grupo",
            type=str,
            default="XV",
            help="Grupo (p.ej: XIV, XV, G1, G2, G3, G4). Por defecto XV.",
        )
        # Overrides opcionales (para testear si aún no tenemos IDs en config)
        parser.add_argument("--id_competicion", type=int, default=None)
        parser.add_argument("--id_torneo", type=int, default=None)
        parser.add_argument("--id_modalidad", type=int, default=None)  # rara vez cambia, pero por si acaso

    # ------------------------
    # HELPERS DE URL SCRAPING
    # ------------------------

    def _build_url_jornada(self, cfg_sel, jornada_num: int) -> str:
        # Construye la URL para obtener el listado de partidos de una jornada.
        # FFCV requiere múltiples parámetros (torneo, temporada, modalidad, competición)
        # para identificar correctamente la jornada en su sistema.
        params = {
            "id_torneo": cfg_sel["id_torneo"],
            "jornada": jornada_num,
            "id_temp": cfg_sel["id_temp"],
            "id_modalidad": cfg_sel["id_modalidad"],
            "id_competicion": cfg_sel["id_competicion"],
        }
        return "https://resultadosffcv.isquad.es/total_partidos.php?" + urlencode(params)

    def _build_url_partido(self, cfg_sel, jornada_num: int, id_partido: int) -> str:
        # Construye la URL para obtener el detalle completo de un partido (acta).
        # Requiere el id_partido específico además de los parámetros de temporada/competición.
        params = {
            "id_temp": cfg_sel["id_temp"],
            "id_modalidad": cfg_sel["id_modalidad"],
            "id_competicion": cfg_sel["id_competicion"],
            "id_partido": id_partido,
            "id_torneo": cfg_sel["id_torneo"],
            "jornada": jornada_num,
        }
        return "https://resultadosffcv.isquad.es/partido.php?" + urlencode(params)

    # ---------------------------------
    # HELPERS PARA CREAR OBJETOS BASE
    # ---------------------------------

    def _get_or_create_competicion(self, competicion_key: str) -> Competicion:
        """
        Asegura que existe la Competicion en BD (nombre dinámico según competición).
        """
        nombre_comp = _competicion_nombre_for_bd(competicion_key)
        comp, _ = Competicion.objects.get_or_create(
            nombre=nombre_comp,
            defaults={"ambito": "", "categoria": ""},
        )
        return comp

    def _get_or_create_grupo(
        self,
        temporada_obj: Temporada,
        competicion_obj: Competicion,
        grupo_nombre: str,
        provincia: str | None,
    ) -> Grupo:
        """
        Creamos (o reutilizamos) el Grupo concreto dentro de esa competición y temporada.
        """
        grupo, created = Grupo.objects.get_or_create(
            temporada=temporada_obj,
            competicion=competicion_obj,
            nombre=grupo_nombre,
            defaults={"provincia": provincia or ""},
        )
        if (not created) and provincia and not grupo.provincia:
            grupo.provincia = provincia
            grupo.save(update_fields=["provincia"])
        return grupo

    # -------------------------
    # CLUB
    # -------------------------

    def _get_or_create_club_from_equipo_data(self, equipo_dict: dict):
        """
        Reutiliza o crea un Club desde los datos scrapeados del equipo.
        
        Estrategia de búsqueda en orden de prioridad:
        1. Por identificador_federacion (más fiable, evita duplicados)
        2. Por nombre_oficial (fallback si no hay ID)
        
        Si el club ya existe pero le faltan campos, los rellena para mantener
        la BD actualizada con la información más reciente del scraping.
        """
        club_id_fed = equipo_dict.get("id_equipo")
        nombre_equipo = (equipo_dict.get("nombre") or "").strip() or "DESCONOCIDO"

        # 1) Buscar por identificador_federacion (más fiable)
        club_obj = None
        if club_id_fed:
            club_obj = Club.objects.filter(
                identificador_federacion=str(club_id_fed)
            ).first()

        # 2) Fallback por nombre_oficial si no se encontró por ID
        if club_obj is None:
            club_obj, created = Club.objects.get_or_create(
                nombre_oficial=nombre_equipo,
                defaults={
                    "nombre_corto": nombre_equipo[:100],
                    "identificador_federacion": str(club_id_fed) if club_id_fed else None,
                    "activo": True,
                },
            )
        else:
            created = False

        # 3) Rellenar campos faltantes si el club ya existía
        # Esto asegura que los datos se actualicen con información más reciente del scraping.
        dirty_fields = []
        if not club_obj.nombre_corto:
            club_obj.nombre_corto = nombre_equipo[:100]
            dirty_fields.append("nombre_corto")

        if club_id_fed and not club_obj.identificador_federacion:
            club_obj.identificador_federacion = str(club_id_fed)
            dirty_fields.append("identificador_federacion")

        if dirty_fields:
            club_obj.save(update_fields=dirty_fields)

        return club_obj

    # -------------------------
    # FECHA / INTENSIDAD
    # -------------------------

    def _parse_fecha_hora(self, info_partido):
        """
        info_partido['fecha'] = "11-09-2025"
        info_partido['hora']  = "20:30"
        """
        from datetime import datetime
        fecha_txt = info_partido.get("fecha", "")
        hora_txt = info_partido.get("hora", "")

        if not fecha_txt:
            return None

        try:
            if hora_txt:
                dt_naive = datetime.strptime(f"{fecha_txt} {hora_txt}", "%d-%m-%Y %H:%M")
            else:
                dt_naive = datetime.strptime(fecha_txt, "%d-%m-%Y")
        except ValueError:
            return None

        return dt_naive  # naive por ahora

    def _calcular_indice_intensidad(self, partido_data):
        """
        Calcula un índice de intensidad del partido (0-100) basado en el número de eventos.
        
        Un partido con muchos eventos (goles, tarjetas, etc.) se considera más "intenso"
        y puede ser más interesante para destacar en la interfaz.
        La escala es lineal hasta 50 eventos (máximo 100).
        """
        eventos = partido_data.get("eventos", [])
        total_ev = len(eventos)
        if total_ev == 0:
            return 0
        if total_ev >= 50:
            return 100  # Cap a 100 para partidos muy intensos
        return int((total_ev / 50) * 100)

    # -------------------------
    # JUGADORES / ESTADÍSTICAS
    # -------------------------

    def _upsert_jugador(self, jugador_nombre: str, jugador_id: int | None):
        """
        Crea o actualiza un jugador desde los datos scrapeados.
        
        Prioridad de búsqueda:
        1. Por identificador_federacion (más fiable)
        2. Por nombre (fallback)
        
        Si el jugador existe pero le falta el nombre, lo actualiza.
        Si le falta el identificador_federacion, lo añade para futuras búsquedas más rápidas.
        """
        clean_name = (jugador_nombre or "").strip() or "DESCONOCIDO"

        # Buscar primero por ID de federación (más fiable)
        if jugador_id is not None:
            j = Jugador.objects.filter(identificador_federacion=str(jugador_id)).first()
            if j:
                # Actualizar nombre si falta
                if not j.nombre:
                    j.nombre = clean_name
                    j.save(update_fields=["nombre"])
                return j

        # Si no se encontró por ID, buscar/crear por nombre
        j, _ = Jugador.objects.get_or_create(
            nombre=clean_name,
            defaults={
                "identificador_federacion": str(jugador_id) if jugador_id is not None else None,
                "activo": True,
            },
        )
        # Si el jugador ya existía pero le faltaba el ID, añadirlo
        if not j.identificador_federacion and jugador_id is not None:
            j.identificador_federacion = str(jugador_id)
            j.save(update_fields=["identificador_federacion"])
        return j

    def _upsert_stats_jugador_en_club_temporada(
        self,
        jugador_obj: Jugador,
        club_obj: Club,
        temporada_obj: Temporada,
        stats_fuente: dict,
    ):
        rec, created = JugadorEnClubTemporada.objects.get_or_create(
            jugador=jugador_obj,
            club=club_obj,
            temporada=temporada_obj,
            defaults={
                "dorsal": stats_fuente.get("dorsal", "") or "",
                "partidos_jugados": 0,
                "goles": 0,
                "tarjetas_amarillas": 0,
                "tarjetas_rojas": 0,
                "convocados": 0,
                "titular": 0,
                "suplente": 0,
            },
        )

        if stats_fuente.get("dorsal") and not rec.dorsal:
            rec.dorsal = str(stats_fuente["dorsal"])

        if stats_fuente.get("jugó_este_partido", False):
            rec.partidos_jugados += 1

        if stats_fuente.get("fue_titular"):
            rec.titular += 1
        else:
            if stats_fuente.get("jugó_este_partido", False):
                rec.suplente += 1

        rec.goles += stats_fuente.get("goles_en_este_partido", 0)
        rec.tarjetas_amarillas += stats_fuente.get("amarillas_en_este_partido", 0)
        rec.tarjetas_rojas += stats_fuente.get("rojas_en_este_partido", 0)
        rec.save()

    def _registrar_alineacion_equipo(
        self,
        partido_obj: Partido,
        lado_label: str,
        alineacion_data: dict,
        club_obj: Club,
        temporada_obj: Temporada,
    ):
        for es_titular, bloque in (
            (True, alineacion_data.get("titulares", [])),
            (False, alineacion_data.get("suplentes", [])),
        ):
            for jinfo in bloque:
                j_obj = self._upsert_jugador(
                    jugador_nombre=jinfo.get("nombre"),
                    jugador_id=jinfo.get("jugador_id"),
                )

                AlineacionPartidoJugador.objects.get_or_create(
                    partido=partido_obj,
                    club=club_obj,
                    jugador=j_obj,
                    dorsal=str(jinfo.get("dorsal") or "")[:10],
                    titular=es_titular,
                    etiqueta=jinfo.get("etiqueta") or "",
                )

                stats_fuente = {
                    "dorsal": jinfo.get("dorsal"),
                    "jugó_este_partido": True,
                    "fue_titular": es_titular,
                    "goles_en_este_partido": 0,
                    "amarillas_en_este_partido": 0,
                    "rojas_en_este_partido": 0,
                }
                self._upsert_stats_jugador_en_club_temporada(
                    jugador_obj=j_obj,
                    club_obj=club_obj,
                    temporada_obj=temporada_obj,
                    stats_fuente=stats_fuente,
                )

        for tinfo in alineacion_data.get("tecnicos", []):
            nombre_staff = (tinfo.get("nombre") or "").strip()
            rol_staff = (tinfo.get("rol") or "").strip()
            if not nombre_staff:
                continue

            staff_obj, _ = StaffClub.objects.get_or_create(
                club=club_obj,
                temporada=temporada_obj,
                nombre=nombre_staff,
                defaults={"rol": rol_staff or "Cuerpo técnico", "activo": True},
            )

            StaffEnPartido.objects.get_or_create(
                partido=partido_obj,
                club=club_obj,
                staff=staff_obj,
                nombre=nombre_staff,
                rol=rol_staff or "Cuerpo técnico",
            )

    def _registrar_eventos(
        self,
        partido_obj: Partido,
        partido_data: dict,
        club_local_obj: Club,
        club_visitante_obj: Club,
        temporada_obj: Temporada,
    ):
        eventos_list = partido_data.get("eventos", [])

        for ev in eventos_list:
            minuto = ev.get("minuto")
            tipo_raw = (ev.get("tipo") or "").lower()

            if "gol" in tipo_raw and "pp" in tipo_raw:
                tipo_evento = "gol_pp"
            elif "gol" in tipo_raw:
                tipo_evento = "gol"
            elif "doble" in tipo_raw and "amarilla" in tipo_raw:
                tipo_evento = "doble_amarilla"
            elif "amarilla" in tipo_raw:
                tipo_evento = "amarilla"
            elif "roja" in tipo_raw:
                tipo_evento = "roja"
            else:
                tipo_evento = "mvp" if "mvp" in tipo_raw else "gol"

            jugador_nombre = ev.get("jugador_nombre") or ""
            jugador_id = ev.get("jugador_id")
            lado = ev.get("equipo")  # "local" / "visitante"

            if lado == "local":
                ev_club = club_local_obj
            elif lado == "visitante":
                ev_club = club_visitante_obj
            else:
                ev_club = None

            jugador_obj = None
            if jugador_nombre or jugador_id:
                jugador_obj = self._upsert_jugador(
                    jugador_nombre=jugador_nombre,
                    jugador_id=jugador_id,
                )

            EventoPartido.objects.get_or_create(
                partido=partido_obj,
                minuto=minuto,
                tipo_evento=tipo_evento,
                jugador=jugador_obj,
                club=ev_club,
                nota="",
            )

            if jugador_obj and ev_club:
                goles = 1 if tipo_evento in ("gol",) else 0
                amar = 1 if tipo_evento in ("amarilla", "doble_amarilla") else 0
                roja = 1 if tipo_evento in ("roja",) else 0

                self._upsert_stats_jugador_en_club_temporada(
                    jugador_obj=jugador_obj,
                    club_obj=ev_club,
                    temporada_obj=temporada_obj,
                    stats_fuente={
                        "dorsal": None,
                        "jugó_este_partido": False,
                        "fue_titular": False,
                        "goles_en_este_partido": goles,
                        "amarillas_en_este_partido": amar,
                        "rojas_en_este_partido": roja,
                    },
                )

    # -------------------------
    # SELECCIÓN DE CONFIG
    # -------------------------

    def _select_cfg(self, temporada_cfg: dict, competicion_key: str, grupo_key: str):
        """
        Devuelve:
          - cfg_sel: dict con id_temp, id_modalidad, id_competicion, id_torneo
          - meta: dict con grupo_nombre, provincia, jornadas (si grupo define jornadas)
        Lanza ValueError si no encuentra lo necesario.
        """
        compk = (competicion_key or "TERCERA").upper()
        gkey = (grupo_key or "").upper()

        # 1) TERCERA usa 'grupos' a nivel de temporada
        if compk == "TERCERA":
            if "grupos" in temporada_cfg and gkey in temporada_cfg["grupos"]:
                gcfg = temporada_cfg["grupos"][gkey]
                cfg_sel = {
                    "id_temp": temporada_cfg["id_temp"],
                    "id_modalidad": temporada_cfg["id_modalidad"],
                    "id_competicion": gcfg["id_competicion"],
                    "id_torneo": gcfg["id_torneo"],
                }
                meta = {
                    "grupo_nombre": gcfg.get("grupo_nombre", f"Grupo {gkey}"),
                    "provincia": gcfg.get("provincia", ""),
                    "jornadas": gcfg.get("jornadas", temporada_cfg.get("jornadas", 30)),
                }
                return cfg_sel, meta

            # Fallback compat: usar nivel raíz si no hay grupos definidos
            cfg_sel = {
                "id_temp": temporada_cfg["id_temp"],
                "id_modalidad": temporada_cfg["id_modalidad"],
                "id_competicion": temporada_cfg["id_competicion"],
                "id_torneo": temporada_cfg["id_torneo"],
            }
            meta = {
                "grupo_nombre": f"Grupo {gkey or 'XV'}",
                "provincia": "",
                "jornadas": temporada_cfg.get("jornadas", 30),
            }
            return cfg_sel, meta

        # 2) OTRAS COMPETICIONES (Preferente / Primera / Segunda)
        otras = temporada_cfg.get("otras_competiciones", {})
        comp_node = None
        if compk == "PREFERENTE":
            comp_node = otras.get("Preferente")
        elif compk == "PRIMERA":
            comp_node = otras.get("Primera Regional")
        elif compk == "SEGUNDA":
            comp_node = otras.get("Segunda Regional")

        if comp_node is None:
            raise ValueError(f"No hay configuración para la competición '{competicion_key}' en esta temporada.")

        grupos = comp_node.get("grupos", {})
        if gkey not in grupos:
            raise ValueError(f"No hay configuración para el grupo '{grupo_key}' en competición '{competicion_key}'.")

        gcfg = grupos[gkey]
        cfg_sel = {
            "id_temp": temporada_cfg["id_temp"],
            "id_modalidad": temporada_cfg["id_modalidad"],
            "id_competicion": comp_node["id_competicion"],
            "id_torneo": gcfg["id_torneo"],
        }
        meta = {
            "grupo_nombre": gcfg.get("grupo_nombre", f"{competicion_key.title()} - {gkey}"),
            "provincia": "",
            "jornadas": gcfg.get("jornadas", temporada_cfg.get("jornadas", 30)),
        }
        return cfg_sel, meta

    # --------------
    # HANDLE (MAIN)
    # --------------

    def handle(self, *args, **options):
        temporada_key = options["temporada"]
        jornada = options["jornada"]
        competicion_key = (options["competicion"] or "TERCERA").upper()
        grupo_key = (options["grupo"] or "XV").upper()

        temporada_cfg = TEMPORADAS.get(temporada_key)
        if not temporada_cfg:
            self.stderr.write(self.style.ERROR(f"Temporada '{temporada_key}' no está en config_temporadas"))
            return

        # 0) Selección de configuración por competición+grupo
        try:
            cfg_sel, meta = self._select_cfg(temporada_cfg, competicion_key, grupo_key)
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return

        # 0.1) Overrides por CLI (debug / pruebas)
        if options.get("id_competicion"):
            cfg_sel["id_competicion"] = int(options["id_competicion"])
        if options.get("id_torneo"):
            cfg_sel["id_torneo"] = int(options["id_torneo"])
        if options.get("id_modalidad"):
            cfg_sel["id_modalidad"] = int(options["id_modalidad"])

        # 1) Asegurar Temporada / Competición / Grupo en BD
        temporada_obj = get_or_create_temporada(temporada_key)
        self.stdout.write(f"[temporadas_utils] Temporada en BD: {temporada_obj}")

        competicion_obj = self._get_or_create_competicion(competicion_key)
        self.stdout.write(f"[scrape_jornada] Competición en BD: {competicion_obj}")

        grupo_obj = self._get_or_create_grupo(
            temporada_obj=temporada_obj,
            competicion_obj=competicion_obj,
            grupo_nombre=meta["grupo_nombre"],
            provincia=meta.get("provincia") or "",
        )
        self.stdout.write(f"[scrape_jornada] Grupo en BD: {grupo_obj}")

        # 2) Paths locales
        raw_dir = os.path.join("data_raw", "html")
        clean_dir_jornadas = os.path.join("data_clean", "partidos")
        clean_dir_partidos = os.path.join("data_clean", "partidos_detalle")
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(clean_dir_jornadas, exist_ok=True)
        os.makedirs(clean_dir_partidos, exist_ok=True)

        # 3) Descargar jornada (lista de partidos)
        url_jornada = self._build_url_jornada(cfg_sel, jornada)
        raw_path_jornada = os.path.join(
            raw_dir, f"{temporada_key}_{competicion_key}_{grupo_key}_jornada_{jornada:02d}.html"
        )

        self.stdout.write(
            f"[scrape_jornada] Descargando jornada {jornada} de {temporada_key} ({competicion_key} {grupo_key})..."
        )
        fetch_url(url_jornada, raw_path_jornada)

        with open(raw_path_jornada, "r", encoding="utf-8") as f:
            html_text = f.read()

        jornada_data = parse_jornada_partidos(html_text)

        # guardar json limpio (debug)
        clean_path = os.path.join(
            clean_dir_jornadas, f"jornada_{jornada:02d}_{temporada_key}_{competicion_key}_{grupo_key}.json"
        )
        with open(clean_path, "w", encoding="utf-8") as f:
            json.dump(jornada_data, f, indent=2, ensure_ascii=False)

        # 4) Procesar partidos
        for p in jornada_data.get("partidos", []):
            pid = p.get("id_partido")
            if pid is None:
                continue

            partido_existente = Partido.objects.filter(
                identificador_federacion=str(pid)
            ).first()

            if partido_existente:
                self.stdout.write(self.style.WARNING(
                    f"[scrape_jornada] Partido {pid} ya existe -> se omite completamente ❌"
                ))
                continue

            partido_url = self._build_url_partido(cfg_sel, jornada, pid)
            raw_path_partido = os.path.join(
                raw_dir, f"{temporada_key}_{competicion_key}_{grupo_key}_j{jornada:02d}_partido_{pid}.html"
            )

            self.stdout.write(f"[scrape_jornada] Descargando partido {pid} (nuevo) ...")
            fetch_url(partido_url, raw_path_partido)

            with open(raw_path_partido, "r", encoding="utf-8") as f:
                partido_html = f.read()

            partido_data = parse_partido_detalle(partido_html)

            # clubs
            equipo_local_data = partido_data["equipos"]["local"]
            equipo_visit_data = partido_data["equipos"]["visitante"]

            local_club = self._get_or_create_club_from_equipo_data(equipo_local_data)
            visit_club = self._get_or_create_club_from_equipo_data(equipo_visit_data)

            # info extra partido
            info_partido = partido_data.get("info_partido", {})
            dt_fecha_hora = self._parse_fecha_hora(info_partido)
            pabellon = info_partido.get("pabellon", "") or ""
            arbitros_nombres = info_partido.get("arbitros", [])

            # resultado
            goles_local = partido_data.get("marcador", {}).get("local")
            goles_visit = partido_data.get("marcador", {}).get("visitante")
            jugado = goles_local is not None and goles_visit is not None

            intensidad = self._calcular_indice_intensidad(partido_data)

            # Inserción en BD
            with transaction.atomic():
                partido_obj = Partido.objects.create(
                    identificador_federacion=str(pid),
                    grupo=grupo_obj,
                    jornada_numero=jornada,
                    fecha_hora=dt_fecha_hora,
                    local=local_club,
                    visitante=visit_club,
                    goles_local=goles_local,
                    goles_visitante=goles_visit,
                    jugado=jugado,
                    pabellon=pabellon,
                    arbitros=" | ".join(arbitros_nombres),
                    indice_intensidad=intensidad,
                )

                # alineaciones
                alineacion_local = partido_data["equipos"]["local"]
                alineacion_visit = partido_data["equipos"]["visitante"]

                self._registrar_alineacion_equipo(
                    partido_obj=partido_obj,
                    lado_label="local",
                    alineacion_data=alineacion_local,
                    club_obj=local_club,
                    temporada_obj=temporada_obj,
                )
                self._registrar_alineacion_equipo(
                    partido_obj=partido_obj,
                    lado_label="visitante",
                    alineacion_data=alineacion_visit,
                    club_obj=visit_club,
                    temporada_obj=temporada_obj,
                )

                # eventos
                self._registrar_eventos(
                    partido_obj=partido_obj,
                    partido_data=partido_data,
                    club_local_obj=local_club,
                    club_visitante_obj=visit_club,
                    temporada_obj=temporada_obj,
                )

                # árbitros
                for a_nombre in arbitros_nombres:
                    clean_arbitro_nombre = (a_nombre or "").strip()
                    if not clean_arbitro_nombre:
                        continue

                    arbitro_obj, _ = Arbitro.objects.get_or_create(
                        nombre=clean_arbitro_nombre,
                        defaults={"identificador_federacion": None, "activo": True},
                    )
                    ArbitrajePartido.objects.get_or_create(
                        partido=partido_obj,
                        arbitro=arbitro_obj,
                        defaults={"rol": ""},
                    )

            # guardar json limpio del partido (debug)
            clean_partido_path = os.path.join(
                clean_dir_partidos,
                f"{temporada_key}_{competicion_key}_{grupo_key}_j{jornada:02d}_partido_{pid}.json",
            )
            with open(clean_partido_path, "w", encoding="utf-8") as f:
                json.dump(partido_data, f, indent=2, ensure_ascii=False)

            self.stdout.write(self.style.SUCCESS(f"[scrape_jornada] Partido {pid} creado en BD ✅"))

        self.stdout.write(self.style.SUCCESS(
            f"Jornada {jornada} de {temporada_key} ({competicion_key} {grupo_key}) completada ✅"
        ))
