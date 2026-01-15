import os
import json
from urllib.parse import urlencode
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from scraping.core.config_temporadas import TEMPORADAS
from scraping.core.fetcher import fetch_url
from scraping.core.parser_partidos import parse_jornada_partidos
from scraping.core.parser_partido_detalle import parse_partido_detalle
from scraping.core.temporadas_utils import get_or_create_temporada

from scraping.models import EstadoScraping

from nucleo.models import Competicion, Grupo
from clubes.models import Club
from partidos.models import Partido, EventoPartido, AlineacionPartidoJugador
from jugadores.models import Jugador, JugadorEnClubTemporada
from arbitros.models import Arbitro, ArbitrajePartido
from staff.models import StaffClub, StaffEnPartido


# ===== Mapa y selector de configuración =====
COMPETICION_NAME_MAP = {
    "TERCERA": "Tercera División",
    "PREFERENTE": "Preferente",
    "PRIMERA": "Primera Regional",
    "SEGUNDA": "Segunda Regional",
}

def _select_cfg(temporada_cfg: dict, competicion_key: str, grupo_key: str):
    compk = (competicion_key or "TERCERA").upper()
    gkey = (grupo_key or "").upper()

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
                "competicion_nombre": COMPETICION_NAME_MAP[compk],
                "grupo_nombre": gcfg.get("grupo_nombre", f"Grupo {gkey}"),
                "jornadas": gcfg.get("jornadas", temporada_cfg.get("jornadas", 30)),
            }
            return cfg_sel, meta

        # fallback compat
        cfg_sel = {
            "id_temp": temporada_cfg["id_temp"],
            "id_modalidad": temporada_cfg["id_modalidad"],
            "id_competicion": temporada_cfg["id_competicion"],
            "id_torneo": temporada_cfg["id_torneo"],
        }
        meta = {
            "competicion_nombre": COMPETICION_NAME_MAP[compk],
            "grupo_nombre": f"Grupo {gkey or 'XV'}",
            "jornadas": temporada_cfg.get("jornadas", 30),
        }
        return cfg_sel, meta

    otras = temporada_cfg.get("otras_competiciones", {})
    node = (
        otras.get("Preferente") if compk == "PREFERENTE"
        else otras.get("Primera Regional") if compk == "PRIMERA"
        else otras.get("Segunda Regional") if compk == "SEGUNDA"
        else None
    )
    if not node:
        raise ValueError(f"No hay configuración para la competición '{compk}' en esta temporada.")

    grupos = node.get("grupos", {})
    if gkey not in grupos:
        raise ValueError(f"No hay configuración para el grupo '{gkey}' en '{compk}'.")

    gcfg = grupos[gkey]
    cfg_sel = {
        "id_temp": temporada_cfg["id_temp"],
        "id_modalidad": temporada_cfg["id_modalidad"],
        "id_competicion": node["id_competicion"],
        "id_torneo": gcfg["id_torneo"],
    }
    meta = {
        "competicion_nombre": COMPETICION_NAME_MAP[compk],
        "grupo_nombre": gcfg.get("grupo_nombre", f"{compk.title()} - {gkey}"),
        "jornadas": gcfg.get("jornadas", temporada_cfg.get("jornadas", 30)),
    }
    return cfg_sel, meta


class Command(BaseCommand):
    help = "Scrape por jornada para una temporada+competición+grupo. Mantiene jornada_actual y jornada_pendiente_minima (aplazados)."

    def add_arguments(self, parser):
        parser.add_argument("--temporada", type=str, default="2025-2026",
                            help="Temporada (por defecto: 2025-2026)")
        parser.add_argument("--competicion", type=str, default="TERCERA",
                            help="TERCERA | PREFERENTE | PRIMERA | SEGUNDA")
        parser.add_argument("--grupo", type=str, default="XV",
                            help="TERCERA: XIV/XV; otras: G1..G4")

    # ------------------- utilidades comunes -------------------

    def _build_url_jornada(self, cfg, jornada_num: int) -> str:
        params = {
            "id_torneo": cfg["id_torneo"],
            "jornada": jornada_num,
            "id_temp": cfg["id_temp"],
            "id_modalidad": cfg["id_modalidad"],
            "id_competicion": cfg["id_competicion"],
        }
        return "https://resultadosffcv.isquad.es/total_partidos.php?" + urlencode(params)

    def _build_url_partido(self, cfg, jornada_num: int, id_partido: int) -> str:
        params = {
            "id_temp": cfg["id_temp"],
            "id_modalidad": cfg["id_modalidad"],
            "id_competicion": cfg["id_competicion"],
            "id_partido": id_partido,
            "id_torneo": cfg["id_torneo"],
            "jornada": jornada_num,
        }
        return "https://resultadosffcv.isquad.es/partido.php?" + urlencode(params)

    def _get_or_create_competicion(self, nombre_comp: str):
        comp, _ = Competicion.objects.get_or_create(
            nombre=nombre_comp,
            defaults={"ambito": "", "categoria": ""},
        )
        return comp

    def _get_or_create_grupo(self, temporada_obj, competicion_obj, nombre_grupo: str, provincia: str = ""):
        grupo, created = Grupo.objects.get_or_create(
            temporada=temporada_obj,
            competicion=competicion_obj,
            nombre=nombre_grupo,
            defaults={"provincia": provincia},
        )
        if (not created) and provincia and not grupo.provincia:
            grupo.provincia = provincia
            grupo.save(update_fields=["provincia"])
        return grupo

    def _get_or_create_club_from_equipo_data(self, equipo_dict: dict):
        club_id_fed = equipo_dict.get("id_equipo")
        nombre_equipo = (equipo_dict.get("nombre") or "").strip() or "DESCONOCIDO"

        club_obj = None
        if club_id_fed:
            club_obj = Club.objects.filter(
                identificador_federacion=str(club_id_fed)
            ).first()

        if club_obj is None:
            club_obj, _created = Club.objects.get_or_create(
                nombre_oficial=nombre_equipo,
                defaults={
                    "nombre_corto": nombre_equipo[:100],
                    "identificador_federacion": str(club_id_fed) if club_id_fed else None,
                    "activo": True,
                },
            )
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

    def _parse_fecha_hora(self, info_partido):
        from datetime import datetime
        fecha_txt = info_partido.get("fecha", "")
        hora_txt = info_partido.get("hora", "")
        if not fecha_txt:
            return None
        try:
            if hora_txt:
                return datetime.strptime(f"{fecha_txt} {hora_txt}", "%d-%m-%Y %H:%M")
            return datetime.strptime(fecha_txt, "%d-%m-%Y")
        except ValueError:
            return None

    def _calcular_indice_intensidad(self, partido_data):
        eventos = partido_data.get("eventos", [])
        total_ev = len(eventos)
        if total_ev == 0:
            return 0
        if total_ev >= 50:
            return 100
        return int((total_ev / 50) * 100)

    def _upsert_jugador(self, jugador_nombre: str, jugador_id: int | None):
        clean_name = (jugador_nombre or "").strip() or "DESCONOCIDO"
        j = None
        if jugador_id is not None:
            j = Jugador.objects.filter(identificador_federacion=str(jugador_id)).first()
            if j and not j.nombre:
                j.nombre = clean_name
                j.save(update_fields=["nombre"])
        if not j:
            j, _created = Jugador.objects.get_or_create(
                nombre=clean_name,
                defaults={
                    "identificador_federacion": str(jugador_id) if jugador_id is not None else None,
                    "activo": True,
                },
            )
            if not j.identificador_federacion and jugador_id is not None:
                j.identificador_federacion = str(jugador_id)
                j.save(update_fields=["identificador_federacion"])
        return j

    def _upsert_stats_jugador_en_club_temporada(self, jugador_obj, club_obj, temporada_obj, stats_fuente: dict):
        rec, _created = JugadorEnClubTemporada.objects.get_or_create(
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
        dirty = False
        if stats_fuente.get("dorsal") and not rec.dorsal:
            rec.dorsal = str(stats_fuente["dorsal"]); dirty = True
        if stats_fuente.get("jugó_este_partido", False):
            rec.partidos_jugados += 1; dirty = True
        if stats_fuente.get("fue_titular"):
            rec.titular += 1; dirty = True
        else:
            if stats_fuente.get("jugó_este_partido", False):
                rec.suplente += 1; dirty = True
        rec.goles += stats_fuente.get("goles_en_este_partido", 0)
        rec.tarjetas_amarillas += stats_fuente.get("amarillas_en_este_partido", 0)
        rec.tarjetas_rojas += stats_fuente.get("rojas_en_este_partido", 0)
        if dirty:
            rec.save()

    def _registrar_alineacion_equipo(self, partido_obj, alineacion_data: dict, club_obj, temporada_obj):
        for es_titular, bloque in (
            (True, alineacion_data.get("titulares", [])),
            (False, alineacion_data.get("suplentes", [])),
        ):
            for jinfo in bloque:
                j_obj = self._upsert_jugador(jinfo.get("nombre"), jinfo.get("jugador_id"))
                AlineacionPartidoJugador.objects.get_or_create(
                    partido=partido_obj,
                    club=club_obj,
                    jugador=j_obj,
                    dorsal=str(jinfo.get("dorsal") or "")[:10],
                    titular=es_titular,
                    etiqueta=jinfo.get("etiqueta") or "",
                )
                self._upsert_stats_jugador_en_club_temporada(
                    jugador_obj=j_obj,
                    club_obj=club_obj,
                    temporada_obj=temporada_obj,
                    stats_fuente={
                        "dorsal": jinfo.get("dorsal"),
                        "jugó_este_partido": True,
                        "fue_titular": es_titular,
                        "goles_en_este_partido": 0,
                        "amarillas_en_este_partido": 0,
                        "rojas_en_este_partido": 0,
                    },
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

    def _registrar_eventos(self, partido_obj, partido_data: dict, club_local_obj, club_visitante_obj, temporada_obj):
        for ev in (partido_data.get("eventos", []) or []):
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

            lado = ev.get("equipo")  # "local"/"visitante"
            ev_club = club_local_obj if lado == "local" else club_visitante_obj if lado == "visitante" else None

            jugador_obj = None
            if ev.get("jugador_nombre") or ev.get("jugador_id"):
                jugador_obj = self._upsert_jugador(ev.get("jugador_nombre") or "", ev.get("jugador_id"))

            EventoPartido.objects.get_or_create(
                partido=partido_obj,
                minuto=minuto,
                tipo_evento=tipo_evento,
                jugador=jugador_obj,
                club=ev_club,
                nota="",
            )

            if jugador_obj and ev_club:
                self._upsert_stats_jugador_en_club_temporada(
                    jugador_obj=jugador_obj,
                    club_obj=ev_club,
                    temporada_obj=temporada_obj,
                    stats_fuente={
                        "dorsal": None,
                        "jugó_este_partido": False,
                        "fue_titular": False,
                        "goles_en_este_partido": 1 if tipo_evento == "gol" else 0,
                        "amarillas_en_este_partido": 1 if tipo_evento in ("amarilla", "doble_amarilla") else 0,
                        "rojas_en_este_partido": 1 if tipo_evento == "roja" else 0,
                    },
                )

    def _decidir_resultado_y_estado(self, partido_data, info_partido):
        marcador = partido_data.get("marcador", {}) or {}
        gL = marcador.get("local")
        gV = marcador.get("visitante")

        estado_txt_candidates = [
            info_partido.get("hora", ""),
            info_partido.get("estado", ""),
            info_partido.get("detalle_estado", ""),
            marcador.get("estado", ""),
        ]
        estado_lower = " ".join([t for t in estado_txt_candidates if t]).lower()
        palabras_aplazado = ["susp", "suspend", "aplaz", "apl.", "cancel", "posp", "pospuesto", "no disputado", "sin jugar"]
        if any(pal in estado_lower for pal in palabras_aplazado):
            return None, None, False

        eventos_list = partido_data.get("eventos", []) or []
        if gL is None or gV is None:
            return None, None, False
        if gL == 0 and gV == 0 and not eventos_list:
            return None, None, False
        return gL, gV, True

    # ------------------- lógica jornada -------------------

    def _scrape_una_jornada_si_hace_falta(self, temporada_key, temporada_obj, grupo_obj, cfg, jornada_num, prefix_suffix):
        raw_dir = os.path.join("data_raw", "html")
        clean_dir_partidos = os.path.join("data_clean", "partidos_detalle")
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(clean_dir_partidos, exist_ok=True)

        url_jornada = self._build_url_jornada(cfg, jornada_num)
        raw_path_jornada = os.path.join(raw_dir, f"{temporada_key}_{prefix_suffix}_J{jornada_num:02d}_LIVE.html")
        fetch_url(url_jornada, raw_path_jornada)

        with open(raw_path_jornada, "r", encoding="utf-8") as f:
            jornada_html = f.read()

        jornada_data = parse_jornada_partidos(jornada_html)
        partidos_list = jornada_data.get("partidos", [])
        if not partidos_list:
            return 0, 0, 0

        for p in partidos_list:
            pid = p.get("id_partido")
            if pid is None:
                continue

            partido_url = self._build_url_partido(cfg, jornada_num, pid)
            raw_path_partido = os.path.join(raw_dir, f"{temporada_key}_{prefix_suffix}_J{jornada_num:02d}_P{pid}_LIVE.html")
            fetch_url(partido_url, raw_path_partido)

            with open(raw_path_partido, "r", encoding="utf-8") as f:
                partido_html = f.read()

            partido_data = parse_partido_detalle(partido_html)

            equipo_local_data = partido_data["equipos"]["local"]
            equipo_visit_data = partido_data["equipos"]["visitante"]

            local_club = self._get_or_create_club_from_equipo_data(equipo_local_data)
            visit_club = self._get_or_create_club_from_equipo_data(equipo_visit_data)

            info_partido = partido_data.get("info_partido", {})
            dt_fecha_hora = self._parse_fecha_hora(info_partido)
            pabellon = info_partido.get("pabellon", "") or ""
            arbitros_nombres = info_partido.get("arbitros", [])

            goles_local, goles_visit, jugado = self._decidir_resultado_y_estado(partido_data, info_partido)
            intensidad = self._calcular_indice_intensidad(partido_data)

            with transaction.atomic():
                partido_obj, creado = Partido.objects.get_or_create(
                    identificador_federacion=str(pid),
                    defaults={
                        "grupo": grupo_obj,
                        "jornada_numero": jornada_num,
                        "fecha_hora": dt_fecha_hora,
                        "local": local_club,
                        "visitante": visit_club,
                        "goles_local": goles_local,
                        "goles_visitante": goles_visit,
                        "jugado": jugado,
                        "pabellon": pabellon,
                        "arbitros": " | ".join(arbitros_nombres),
                        "indice_intensidad": intensidad,
                    },
                )
                if not creado:
                    dirty = []
                    if partido_obj.grupo_id != grupo_obj.id:
                        partido_obj.grupo = grupo_obj; dirty.append("grupo")
                    if partido_obj.jornada_numero != jornada_num:
                        partido_obj.jornada_numero = jornada_num; dirty.append("jornada_numero")
                    if dt_fecha_hora and partido_obj.fecha_hora != dt_fecha_hora:
                        partido_obj.fecha_hora = dt_fecha_hora; dirty.append("fecha_hora")
                    if partido_obj.local_id != local_club.id:
                        partido_obj.local = local_club; dirty.append("local")
                    if partido_obj.visitante_id != visit_club.id:
                        partido_obj.visitante = visit_club; dirty.append("visitante")
                    if partido_obj.goles_local != goles_local:
                        partido_obj.goles_local = goles_local; dirty.append("goles_local")
                    if partido_obj.goles_visitante != goles_visit:
                        partido_obj.goles_visitante = goles_visit; dirty.append("goles_visitante")
                    if partido_obj.jugado != jugado:
                        partido_obj.jugado = jugado; dirty.append("jugado")
                    if partido_obj.pabellon != pabellon:
                        partido_obj.pabellon = pabellon; dirty.append("pabellon")
                    nuevos_arbis = " | ".join(arbitros_nombres)
                    if partido_obj.arbitros != nuevos_arbis:
                        partido_obj.arbitros = nuevos_arbis; dirty.append("arbitros")
                    if partido_obj.indice_intensidad != intensidad:
                        partido_obj.indice_intensidad = intensidad; dirty.append("indice_intensidad")
                    if dirty:
                        partido_obj.save(update_fields=dirty)

                self._registrar_alineacion_equipo(partido_obj, partido_data["equipos"]["local"], local_club, temporada_obj)
                self._registrar_alineacion_equipo(partido_obj, partido_data["equipos"]["visitante"], visit_club, temporada_obj)

                self._registrar_eventos(partido_obj, partido_data, local_club, visit_club, temporada_obj)

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

            clean_partido_path = os.path.join(
                clean_dir_partidos,
                f"{temporada_key}_{prefix_suffix}_J{jornada_num:02d}_P{pid}_LIVE.json",
            )
            with open(clean_partido_path, "w", encoding="utf-8") as f:
                json.dump(partido_data, f, indent=2, ensure_ascii=False)

            self.stdout.write(self.style.SUCCESS(f"[live] Partido {pid} actualizado en BD (J{jornada_num}) ✅"))

        ids_esperados = [str(p.get("id_partido")) for p in partidos_list if p.get("id_partido") is not None]
        partidos_en_bd = Partido.objects.filter(identificador_federacion__in=ids_esperados)
        total_partidos_scraping = len(ids_esperados)
        total_en_bd = partidos_en_bd.count()
        total_jugados_en_bd = partidos_en_bd.filter(jugado=True).count()
        return total_partidos_scraping, total_jugados_en_bd, total_en_bd

    def handle(self, *args, **options):
        temporada_key = options["temporada"]
        competicion_key = (options["competicion"] or "TERCERA").upper()
        grupo_key = (options["grupo"] or "XV").upper()

        tcfg = TEMPORADAS.get(temporada_key)
        if not tcfg:
            self.stderr.write(self.style.ERROR(f"Temporada '{temporada_key}' no está en config_temporadas"))
            return

        try:
            cfg, meta = _select_cfg(tcfg, competicion_key, grupo_key)
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return

        # asegurar temporada/competicion/grupo en BD
        temporada_obj = get_or_create_temporada(temporada_key)
        comp_obj = self._get_or_create_competicion(meta["competicion_nombre"])
        grupo_obj = self._get_or_create_grupo(temporada_obj, comp_obj, meta["grupo_nombre"], provincia="")

        prefix_suffix = f"{competicion_key}_{grupo_key}"

        # 🔑 Clave corta y única por (temporada, división/grupo) → evita Data too long
        # Suficiente con id_temp + id_torneo (IDs numéricos estables)
        scoped_temp_key = f"{tcfg['id_temp']}:{cfg['id_torneo']}"

        estado, _ = EstadoScraping.objects.get_or_create(
            temporada_texto=scoped_temp_key,
            defaults={"jornada_actual": 1, "jornada_pendiente_minima": 1, "status": ""},
        )

        self.stdout.write(self.style.HTTP_INFO(
            f"[live] {temporada_key} · {meta['competicion_nombre']} · {meta['grupo_nombre']} "
            f"→ clave={scoped_temp_key} · pendiente_min={estado.jornada_pendiente_minima} / actual={estado.jornada_actual}"
        ))

        # 1) cerrar aplazados desde pendiente_minima
        jp = estado.jornada_pendiente_minima
        total_scr_p, jug_p, _ = self._scrape_una_jornada_si_hace_falta(
            temporada_key=temporada_key,
            temporada_obj=temporada_obj,
            grupo_obj=grupo_obj,
            cfg=cfg,
            jornada_num=jp,
            prefix_suffix=prefix_suffix,
        )
        if total_scr_p > 0 and jug_p == total_scr_p:
            estado.jornada_pendiente_minima = max(estado.jornada_pendiente_minima, jp + 1)
            estado.save(update_fields=["jornada_pendiente_minima", "ultima_actualizacion"])
            self.stdout.write(self.style.SUCCESS(
                f"[live] Jornada {jp} CERRADA. pendiente_min → J{estado.jornada_pendiente_minima} ✅"
            ))
        else:
            estado.save(update_fields=["ultima_actualizacion"])
            if total_scr_p > 0:
                self.stdout.write(self.style.WARNING(
                    f"[live] Jornada {jp} con aplazados ({jug_p}/{total_scr_p}). Seguimos vigilando. ⏳"
                ))
            else:
                self.stdout.write(self.style.WARNING(f"[live] Jornada {jp} sin partidos listados."))

        # 2) jornada_actual
        ja = estado.jornada_actual
        total_scr_a, jug_a, _ = self._scrape_una_jornada_si_hace_falta(
            temporada_key=temporada_key,
            temporada_obj=temporada_obj,
            grupo_obj=grupo_obj,
            cfg=cfg,
            jornada_num=ja,
            prefix_suffix=prefix_suffix,
        )

        if total_scr_a == 0:
            self.stdout.write(self.style.WARNING(f"[live] Jornada {ja} sin partidos listados. Mantengo jornada_actual."))
            estado.save(update_fields=["ultima_actualizacion"])
            return

        porcentaje = jug_a / total_scr_a if total_scr_a > 0 else 0.0
        if porcentaje >= 0.60:
            nuevo_actual = ja + 1
            estado.jornada_actual = max(estado.jornada_actual, nuevo_actual)

            if jug_a < total_scr_a:
                if estado.jornada_pendiente_minima > ja:
                    estado.jornada_pendiente_minima = ja
            else:
                estado.jornada_pendiente_minima = max(estado.jornada_pendiente_minima, ja + 1)

            estado.save(update_fields=["jornada_actual", "jornada_pendiente_minima", "ultima_actualizacion"])
            self.stdout.write(self.style.SUCCESS(
                f"[live] Jornada {ja} ≥60% ({jug_a}/{total_scr_a}). Avanzamos jornada_actual a J{estado.jornada_actual} 🚀"
            ))
        else:
            estado.save(update_fields=["ultima_actualizacion"])
            self.stdout.write(self.style.WARNING(
                f"[live] Jornada {ja}: {jug_a}/{total_scr_a} ({int(porcentaje*100)}%). "
                f"Mantengo jornada_actual en J{estado.jornada_actual} ⏳"
            ))
