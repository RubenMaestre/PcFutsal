# management/commands/scrape_jugadores.py
import os
import json
import base64
from typing import Optional, Dict, Any, List

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from scraping.core.config_temporadas import TEMPORADAS
from scraping.core.fetcher import fetch_url
from scraping.core.parser_jugador_ficha import parse_jugador_ficha
from scraping.core.temporadas_utils import get_or_create_temporada

from nucleo.models import Temporada, Competicion, Grupo
from clubes.models import Club
from jugadores.models import (
    Jugador,
    JugadorEnClubTemporada,
    HistorialJugadorScraped,
)
from staff.models import StaffClub
from partidos.models import AlineacionPartidoJugador, EventoPartido

RAW_JUGADORES_DIR = os.path.join("data_raw", "html_jugadores")
CLEAN_JUGADORES_DIR = os.path.join("data_clean", "jugadores")
MEDIA_JUGADORES_DIR = os.path.join("media", "jugadores")

os.makedirs(RAW_JUGADORES_DIR, exist_ok=True)
os.makedirs(CLEAN_JUGADORES_DIR, exist_ok=True)
os.makedirs(MEDIA_JUGADORES_DIR, exist_ok=True)

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
        raise ValueError(f"No hay configuración para la competición '{competicion_key}' en esta temporada.")

    grupos = node.get("grupos", {})
    if gkey not in grupos:
        raise ValueError(f"No hay configuración para el grupo '{grupo_key}' en '{competicion_key}'.")

    gcfg = grupos[gkey]
    cfg_sel = {
        "id_temp": temporada_cfg["id_temp"],
        "id_modalidad": temporada_cfg["id_modalidad"],
        "id_competicion": node["id_competicion"],
        "id_torneo": gcfg["id_torneo"],
    }
    meta = {
        "competicion_nombre": COMPETICION_NAME_MAP[compk],
        "grupo_nombre": gcfg.get("grupo_nombre", f"{competicion_key.title()} - {gkey}"),
        "jornadas": gcfg.get("jornadas", temporada_cfg.get("jornadas", 30)),
    }
    return cfg_sel, meta

def _build_url_jugador(cfg: Dict[str, Any], jugador_id: int) -> str:
    from urllib.parse import urlencode
    params = {
        "id_temp": cfg["id_temp"],
        "id_modalidad": cfg["id_modalidad"],
        "id_competicion": cfg["id_competicion"],
        "id_jugador": jugador_id,
    }
    base = "https://resultadosffcv.isquad.es/jugador_ficha.php"
    return base + "?" + urlencode(params)

def _save_player_image_and_get_local_path(jugador_id: int, foto_source: str, is_base64: bool) -> Optional[str]:
    if not foto_source:
        return None
    if is_base64:
        try:
            _, b64data = foto_source.split(",", 1)
        except ValueError:
            b64data = foto_source
        img_bytes = base64.b64decode(b64data)
        out_rel = f"jugadores/{jugador_id}.png"
        out_abs = os.path.join(MEDIA_JUGADORES_DIR, f"{jugador_id}.png")
        with open(out_abs, "wb") as f:
            f.write(img_bytes)
        return out_rel
    if foto_source.lower().startswith("http"):
        ext = ".png" if ".png" in foto_source.lower() else ".jpg"
        out_rel = f"jugadores/{jugador_id}{ext}"
        out_abs = os.path.join(MEDIA_JUGADORES_DIR, f"{jugador_id}{ext}")
        try:
            resp = requests.get(foto_source, timeout=10)
            resp.raise_for_status()
            with open(out_abs, "wb") as f:
                f.write(resp.content)
            return out_rel
        except Exception:
            return None
    return None

class Command(BaseCommand):
    help = (
        "Scrapea fichas oficiales de jugadores.\n"
        "Ahora: **agrega candidatos de TODAS las competiciones/grupos** definidos en TEMPORADAS para la temporada base.\n"
        "Para cada jugador, recorre TODAS las temporadas definidas para completar histórico."
    )

    def add_arguments(self, parser):
        parser.add_argument("--temporada", type=str, default="2025-2026", help="Clave temporada base (p.e. 2025-2026)")
        parser.add_argument("--jugador-id", type=int, default=None, help="Opcional: solo este jugador_id federación")
        # Los dos siguientes se mantienen por compatibilidad, pero ya no limitan candidatos si no los pasas.
        parser.add_argument("--competicion", type=str, default=None, help="TERCERA | PREFERENTE | PRIMERA | SEGUNDA (opcional)")
        parser.add_argument("--grupo", type=str, default=None, help="TERCERA: XIV/XV; otras: G1..G4 (opcional)")

    # -------- Helpers internos --------

    def _get_current_year(self) -> int:
        import datetime
        return datetime.date.today().year

    def _normalize_posicion(self, raw_pos: Optional[str]) -> str:
        if not raw_pos:
            return ""
        txt = raw_pos.strip().lower()
        mapping = {
            "portero": "portero", "porter": "portero",
            "cierre": "cierre",
            "ala": "ala",
            "pivot": "pivot", "pívot": "pivot",
            "universal": "universal",
        }
        return mapping.get(txt, "")

    def _parse_fecha_nac_from_ficha(self, jugador_data) -> Optional[str]:
        # Si tu parser expone fecha, parsea aquí. Lo dejamos como None si no llega en la ficha.
        return None

    def _upsert_club_from_equipo_actual(self, equipo_nombre: str, escudo_url: str | None) -> Optional[Club]:
        clean_name = (equipo_nombre or "").strip()
        if not clean_name:
            return None
        club_obj, _ = Club.objects.get_or_create(
            nombre_oficial=clean_name,
            defaults={"nombre_corto": clean_name[:100], "identificador_federacion": None, "activo": True},
        )
        dirty = []
        if not club_obj.nombre_corto:
            club_obj.nombre_corto = clean_name[:100]; dirty.append("nombre_corto")
        if escudo_url and club_obj.escudo_url != escudo_url:
            club_obj.escudo_url = escudo_url; dirty.append("escudo_url")
        if dirty:
            club_obj.save(update_fields=dirty)
        return club_obj

    def _upsert_jugador_obj(self, jugador_id: int, jugador_data) -> Jugador:
        header = jugador_data.get("header", {}) or {}
        datos_generales = jugador_data.get("datos_generales", {}) or {}
        foto_info = jugador_data.get("foto", {}) or {}

        nombre_header = (header.get("nombre_header") or "").strip()
        nombre_completo = (datos_generales.get("nombre_completo") or "").strip()
        nombre_final = nombre_header or nombre_completo or "DESCONOCIDO"

        edad_scrapeada = datos_generales.get("edad")
        # ✅ ahora sí usamos la posición de la ficha si existe
        posicion_norm = self._normalize_posicion(datos_generales.get("posicion"))
        fecha_nac = self._parse_fecha_nac_from_ficha(jugador_data)

        foto_local_rel = _save_player_image_and_get_local_path(
            jugador_id=jugador_id,
            foto_source=foto_info.get("source", ""),
            is_base64=foto_info.get("is_base64", False),
        )

        jugador_obj = Jugador.objects.filter(identificador_federacion=str(jugador_id)).first()
        if jugador_obj is None:
            jugador_obj = Jugador(
                identificador_federacion=str(jugador_id),
                nombre=nombre_final,
                apodo="",
                posicion_principal=posicion_norm,
                fecha_nacimiento=fecha_nac,
                foto_url=foto_local_rel or "",
                activo=True,
            )
            if fecha_nac is None and isinstance(edad_scrapeada, int):
                jugador_obj.edad_estimacion = edad_scrapeada
                jugador_obj.edad_estimacion_base_year = self._get_current_year()
            jugador_obj.save()
            return jugador_obj

        dirty = []
        if nombre_final and jugador_obj.nombre != nombre_final:
            jugador_obj.nombre = nombre_final; dirty.append("nombre")
        if posicion_norm and jugador_obj.posicion_principal != posicion_norm:
            jugador_obj.posicion_principal = posicion_norm; dirty.append("posicion_principal")
        if fecha_nac and jugador_obj.fecha_nacimiento != fecha_nac:
            jugador_obj.fecha_nacimiento = fecha_nac; dirty.append("fecha_nacimiento")
        if foto_local_rel and jugador_obj.foto_url != foto_local_rel:
            jugador_obj.foto_url = foto_local_rel; dirty.append("foto_url")
        if (jugador_obj.fecha_nacimiento is None and not getattr(jugador_obj, "edad_estimacion_bloqueada", False)
            and isinstance(edad_scrapeada, int)):
            if jugador_obj.edad_estimacion != edad_scrapeada:
                jugador_obj.edad_estimacion = edad_scrapeada; dirty.append("edad_estimacion")
            if getattr(jugador_obj, "edad_estimacion_base_year", None) is None:
                jugador_obj.edad_estimacion_base_year = self._get_current_year(); dirty.append("edad_estimacion_base_year")
        if dirty:
            jugador_obj.save(update_fields=dirty)
        return jugador_obj

    def _upsert_jugador_en_club_temporada(
        self,
        jugador_obj: Jugador,
        club_obj: Optional[Club],
        temporada_obj: Temporada,
        jugador_data: Dict[str, Any],
    ):
        if club_obj is None:
            return
        stats_info = jugador_data.get("estadisticas", {}) or {}
        header = jugador_data.get("header", {}) or {}
        valores = {
            "dorsal": (header.get("dorsal_header") or "")[:10],
            "partidos_jugados": stats_info.get("jugados") or 0,
            "goles": stats_info.get("total_goles") or 0,
            "tarjetas_amarillas": stats_info.get("amarillas") or 0,
            "tarjetas_rojas": stats_info.get("rojas") or 0,
            "convocados": stats_info.get("convocados") or 0,
            "titular": stats_info.get("titular") or 0,
            "suplente": stats_info.get("suplente") or 0,
        }
        rec, created = JugadorEnClubTemporada.objects.get_or_create(
            jugador=jugador_obj, club=club_obj, temporada=temporada_obj, defaults=valores
        )
        if not created:
            dirty = []
            for field, new_val in valores.items():
                if getattr(rec, field) != new_val:
                    setattr(rec, field, new_val); dirty.append(field)
            if dirty:
                rec.save(update_fields=dirty)

    def _upsert_staff_desde_ficha(self, club_obj: Optional[Club], temporada_obj: Temporada, jugador_data: Dict[str, Any]):
        if club_obj is None:
            return
        for s in jugador_data.get("staff_equipo", []):
            nombre_staff = (s.get("nombre") or "").strip()
            rol_staff = (s.get("rol") or "").strip() or "Cuerpo técnico"
            if not nombre_staff:
                continue
            StaffClub.objects.get_or_create(
                club=club_obj, temporada=temporada_obj, nombre=nombre_staff,
                defaults={"rol": rol_staff, "activo": True},
            )

    def _sync_historial_scraped_global(self, jugador_obj: Jugador, jugador_data_any_temporada: Dict[str, Any]):
        hist_list = jugador_data_any_temporada.get("historico", []) or []
        HistorialJugadorScraped.objects.filter(jugador=jugador_obj).delete()
        bulk_objs = []
        for h in hist_list:
            bulk_objs.append(
                HistorialJugadorScraped(
                    jugador=jugador_obj,
                    temporada_texto=(h.get("temporada") or "").strip(),
                    competicion_texto=(h.get("competicion") or "").strip(),
                    equipo_texto=(h.get("equipo") or "").strip(),
                )
            )
        if bulk_objs:
            HistorialJugadorScraped.objects.bulk_create(bulk_objs)

    # ===== NUEVO: recolectar candidatos de TODAS las divisiones/grupos =====

    def _build_targets_from_config(self, temporada_cfg: dict) -> List[tuple[str, str, str]]:
        """
        Devuelve lista de tuplas: (competicion_nombre_bd, competicion_cli, grupo_nombre_bd)
        """
        targets: List[tuple[str, str, str]] = []

        # Tercera
        if "grupos" in temporada_cfg:
            for gkey, gnode in temporada_cfg["grupos"].items():
                targets.append((
                    COMPETICION_NAME_MAP["TERCERA"],  # nombre en BD
                    "TERCERA",                        # clave CLI
                    gnode.get("grupo_nombre", f"Grupo {gkey}"),
                ))

        # Otras
        otras = temporada_cfg.get("otras_competiciones", {})
        for comp_label, comp_node in otras.items():
            comp_cli = ("PREFERENTE" if comp_label == "Preferente"
                        else "PRIMERA" if comp_label == "Primera Regional"
                        else "SEGUNDA")
            for gkey, gnode in (comp_node.get("grupos") or {}).items():
                targets.append((
                    COMPETICION_NAME_MAP[comp_cli],   # nombre en BD
                    comp_cli,
                    gnode.get("grupo_nombre", f"{comp_label} - {gkey}"),
                ))
        return targets

    def _gather_candidate_ids_for_group(
        self,
        temporada_obj: Temporada,
        competicion_nombre_bd: str,
        grupo_nombre_bd: str,
    ) -> List[int]:
        """
        Usa BD (alineaciones y eventos) filtrando por Grupo (competición + temporada + nombre).
        Busca por nombre exacto (no slug) para evitar desajustes.
        """
        ids = set()
        try:
            comp_obj = Competicion.objects.get(nombre=competicion_nombre_bd)
        except Competicion.DoesNotExist:
            return []

        try:
            grupo_obj = Grupo.objects.get(
                competicion=comp_obj,
                temporada=temporada_obj,
                nombre=grupo_nombre_bd,
            )
        except Grupo.DoesNotExist:
            return []

        qs_ali = (
            AlineacionPartidoJugador.objects
            .select_related("partido", "jugador", "partido__grupo")
            .filter(partido__grupo=grupo_obj)
        )
        for ali in qs_ali:
            j = ali.jugador
            if j and j.identificador_federacion:
                try:
                    ids.add(int(j.identificador_federacion))
                except ValueError:
                    pass

        qs_ev = (
            EventoPartido.objects
            .select_related("partido", "jugador", "partido__grupo")
            .filter(partido__grupo=grupo_obj)
        )
        for ev in qs_ev:
            j = ev.jugador
            if j and j.identificador_federacion:
                try:
                    ids.add(int(j.identificador_federacion))
                except ValueError:
                    pass

        return sorted(ids)

    # ---------------- MAIN ----------------

    def handle(self, *args, **options):
        temporada_base_key = options["temporada"]
        jugador_forced_id = options["jugador_id"]
        tcfg = TEMPORADAS.get(temporada_base_key)
        if not tcfg:
            self.stderr.write(self.style.ERROR(f"Temporada base '{temporada_base_key}' no está en TEMPORADAS"))
            return

        # Temporada base en BD
        temporada_base_obj = get_or_create_temporada(temporada_base_key)
        self.stdout.write(self.style.SUCCESS(f"[jugadores] Temporada base en BD: {temporada_base_obj}"))

        # 1) Candidatos (todos los grupos/competiciones de la temporada base)
        if jugador_forced_id:
            jugadores_ids = [jugador_forced_id]
            self.stdout.write(self.style.SUCCESS(f"[jugadores] Forzado solo jugador {jugador_forced_id}"))
        else:
            candidatos_all: set[int] = set()
            targets = self._build_targets_from_config(tcfg)
            if not targets:
                self.stdout.write(self.style.WARNING("[jugadores] No hay grupos definidos en el config para esta temporada."))
                return

            for competicion_nombre_bd, comp_cli, grupo_nombre_bd in targets:
                ids_group = self._gather_candidate_ids_for_group(
                    temporada_obj=temporada_base_obj,
                    competicion_nombre_bd=competicion_nombre_bd,
                    grupo_nombre_bd=grupo_nombre_bd,
                )
                if ids_group:
                    self.stdout.write(self.style.NOTICE(
                        f"[jugadores] {competicion_nombre_bd} · {grupo_nombre_bd}: {len(ids_group)} jugadores"
                    ))
                candidatos_all.update(ids_group)

            jugadores_ids = sorted(candidatos_all)
            self.stdout.write(self.style.SUCCESS(
                f"[jugadores] IDs candidatos totales ({len(jugadores_ids)}): {jugadores_ids}"
            ))

        if not jugadores_ids:
            self.stdout.write(self.style.WARNING("[jugadores] No hay jugadores candidatos que scrapear."))
            return

        # 2) Para cada jugador, recorremos TODAS las TEMPORADAS (histórico completo)
        for jugador_id in jugadores_ids:
            self.stdout.write(self.style.SUCCESS(f"[jugadores] Procesando jugador {jugador_id} ..."))
            ultima_ficha_data = None

            for temporada_key, cfg_temp in TEMPORADAS.items():
                temporada_obj = get_or_create_temporada(temporada_key)
                jugador_url = _build_url_jugador(cfg_temp, jugador_id)

                # Prefijos de archivo
                prefix = f"{temporada_key}_jugador_{jugador_id}"
                raw_path = os.path.join(RAW_JUGADORES_DIR, f"{prefix}.html")
                clean_out_path = os.path.join(CLEAN_JUGADORES_DIR, f"{prefix}.json")

                self.stdout.write(self.style.HTTP_INFO(
                    f"[jugadores]   Descargando ficha {jugador_id} en {temporada_key} ..."
                ))
                try:
                    fetch_url(jugador_url, raw_path)
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f"[jugadores]   ⚠️  No pude bajar ficha {jugador_id} en {temporada_key}: {e}"
                    ))
                    continue

                try:
                    with open(raw_path, "r", encoding="utf-8") as f:
                        html_text = f.read()
                    jugador_data = parse_jugador_ficha(
                        html_text,
                        jugador_id=jugador_id,
                        id_temp=cfg_temp["id_temp"],
                    )
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f"[jugadores]   ⚠️  No pude parsear ficha {jugador_id} en {temporada_key}: {e}"
                    ))
                    continue

                try:
                    with open(clean_out_path, "w", encoding="utf-8") as f:
                        json.dump(jugador_data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f"[jugadores]   ⚠️  No pude guardar JSON limpio para {jugador_id} en {temporada_key}: {e}"
                    ))

                ultima_ficha_data = jugador_data

                with transaction.atomic():
                    jugador_obj = self._upsert_jugador_obj(jugador_id, jugador_data)

                    equipo_actual_nombre = jugador_data.get("datos_generales", {}).get("equipo_actual", "")
                    escudo_equipo_url = jugador_data.get("header", {}).get("escudo_equipo_url", "")
                    club_obj = self._upsert_club_from_equipo_actual(equipo_actual_nombre, escudo_equipo_url)

                    self._upsert_jugador_en_club_temporada(
                        jugador_obj=jugador_obj,
                        club_obj=club_obj,
                        temporada_obj=temporada_obj,
                        jugador_data=jugador_data,
                    )

                    self._upsert_staff_desde_ficha(
                        club_obj=club_obj,
                        temporada_obj=temporada_obj,
                        jugador_data=jugador_data,
                    )

            if ultima_ficha_data is not None:
                try:
                    with transaction.atomic():
                        jugador_obj = Jugador.objects.get(identificador_federacion=str(jugador_id))
                        self._sync_historial_scraped_global(
                            jugador_obj=jugador_obj,
                            jugador_data_any_temporada=ultima_ficha_data,
                        )
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f"[jugadores]   ⚠️  No pude actualizar historial global para {jugador_id}: {e}"
                    ))

            self.stdout.write(self.style.SUCCESS(
                f"[jugadores] ✅ Jugador {jugador_id} actualizado (histórico completo)"
            ))

        self.stdout.write(self.style.SUCCESS("[jugadores] Scrape multitemporada completado ✅"))
