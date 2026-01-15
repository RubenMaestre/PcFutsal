# management/commands/scrape_equipos.py
import os
import json
import time
from urllib.parse import urlencode

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import DataError

from scraping.core.config_temporadas import TEMPORADAS
from scraping.core.fetcher import fetch_url
from scraping.core.fetch_binary import fetch_binary
from scraping.core.utils_equipo import collect_equipo_ids_from_jornada
from scraping.core.parser_equipo_plantilla import parse_equipo_plantilla
from scraping.core.parser_partidos import parse_jornada_partidos
from scraping.core.temporadas_utils import get_or_create_temporada

from nucleo.models import Temporada
from clubes.models import Club
from jugadores.models import Jugador, JugadorEnClubTemporada
from staff.models import StaffClub


COMPETICION_NAME_MAP = {
    "TERCERA": "Tercera División",
    "PREFERENTE": "Preferente",
    "PRIMERA": "Primera Regional",
    "SEGUNDA": "Segunda Regional",
}

def _select_cfg(temporada_cfg: dict, competicion_key: str, grupo_key: str):
    """
    Devuelve (cfg_sel, meta):
      cfg_sel = { id_temp, id_modalidad, id_competicion, id_torneo }
      meta    = { grupo_nombre, jornadas }
    """
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
                "grupo_nombre": gcfg.get("grupo_nombre", f"Grupo {gkey}"),
                "jornadas": gcfg.get("jornadas", temporada_cfg.get("jornadas", 30)),
            }
            return cfg_sel, meta

        # Fallback compat si no hay 'grupos'
        cfg_sel = {
            "id_temp": temporada_cfg["id_temp"],
            "id_modalidad": temporada_cfg["id_modalidad"],
            "id_competicion": temporada_cfg["id_competicion"],
            "id_torneo": temporada_cfg["id_torneo"],
        }
        meta = {
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
        "grupo_nombre": gcfg.get("grupo_nombre", f"{competicion_key.title()} - {gkey}"),
        "jornadas": gcfg.get("jornadas", temporada_cfg.get("jornadas", 30)),
    }
    return cfg_sel, meta


def build_equipo_plantilla_url(cfg_sel: dict, id_equipo: int) -> str:
    params = {
        "id_temp":        cfg_sel["id_temp"],
        "id_modalidad":   cfg_sel["id_modalidad"],
        "id_competicion": cfg_sel["id_competicion"],
        "id_equipo":      id_equipo,
        "torneo_equipo":  "",
        "id_torneo":      cfg_sel["id_torneo"],
    }
    return "https://resultadosffcv.isquad.es/equipo_plantilla.php?" + urlencode(params)


def build_url_jornada(cfg_sel: dict, jornada_num: int) -> str:
    params = {
        "id_torneo":      cfg_sel["id_torneo"],
        "jornada":        jornada_num,
        "id_temp":        cfg_sel["id_temp"],
        "id_modalidad":   cfg_sel["id_modalidad"],
        "id_competicion": cfg_sel["id_competicion"],
    }
    return "https://resultadosffcv.isquad.es/total_partidos.php?" + urlencode(params)


class Command(BaseCommand):
    help = (
        "Scrapea plantillas de equipos de TODAS las competiciones/grupos definidos en config para una temporada. "
        "Extrae ids de equipo desde partidos_detalle si existen; si no, cae a listar jornadas (1..N) para obtenerlos."
    )

    def add_arguments(self, parser):
        parser.add_argument("--temporada", type=str, default="2025-2026")
        parser.add_argument("--j_inicio", type=int, default=1, help="Jornada inicio para fallback (sin partidos_detalle).")
        parser.add_argument("--j_fin", type=int, default=5, help="Jornada fin para fallback (sin partidos_detalle).")

    # -----------------------
    # Helpers internos (BD)
    # -----------------------
    def _get_or_create_club_full(self, equipo_info: dict) -> Club:
        club_id_federacion = equipo_info.get("id_equipo")
        nombre_equipo = (equipo_info.get("nombre_equipo") or "").strip() or "DESCONOCIDO"
        pabellon = (equipo_info.get("pabellon", "") or "")[:200]
        escudo_url = (equipo_info.get("escudo_url", "") or "")
        telefono = (equipo_info.get("telefono") or "")[:50]
        email_contacto = (equipo_info.get("email") or "")[:200]

        club_obj = None
        if club_id_federacion:
            club_obj = Club.objects.filter(
                identificador_federacion=str(club_id_federacion)
            ).first()

        if club_obj is None:
            try:
                club_obj, _ = Club.objects.get_or_create(
                    nombre_oficial=nombre_equipo,
                    defaults={
                        "nombre_corto": nombre_equipo[:100],
                        # "localidad": "",  # ← QUITADO: no existe en tu modelo actual
                        "pabellon": pabellon,
                        "escudo_url": escudo_url,
                        "telefono": telefono,
                        "email_contacto": email_contacto,
                        "identificador_federacion": str(club_id_federacion) if club_id_federacion else None,
                        "activo": True,
                    },
                )
            except DataError:
                # Si peta por teléfono, recortamos agresivo y reintentamos
                club_obj, _ = Club.objects.get_or_create(
                    nombre_oficial=nombre_equipo,
                    defaults={
                        "nombre_corto": nombre_equipo[:100],
                        "pabellon": pabellon,
                        "escudo_url": escudo_url,
                        "telefono": (telefono or "")[:20],
                        "email_contacto": email_contacto,
                        "identificador_federacion": str(club_id_federacion) if club_id_federacion else None,
                        "activo": True,
                    },
                )
        else:
            dirty_fields = []
            if not club_obj.nombre_corto:
                club_obj.nombre_corto = nombre_equipo[:100]
                dirty_fields.append("nombre_corto")
            if pabellon and club_obj.pabellon != pabellon:
                club_obj.pabellon = pabellon
                dirty_fields.append("pabellon")
            if escudo_url and club_obj.escudo_url != escudo_url:
                club_obj.escudo_url = escudo_url
                dirty_fields.append("escudo_url")
            if telefono and club_obj.telefono != telefono:
                club_obj.telefono = telefono
                dirty_fields.append("telefono")
            if email_contacto and club_obj.email_contacto != email_contacto:
                club_obj.email_contacto = email_contacto
                dirty_fields.append("email_contacto")
            if club_id_federacion and not club_obj.identificador_federacion:
                club_obj.identificador_federacion = str(club_id_federacion)
                dirty_fields.append("identificador_federacion")
            if dirty_fields:
                try:
                    club_obj.save(update_fields=dirty_fields)
                except DataError:
                    # Si falla por longitud (típicamente teléfono), corta y reintenta sin frenar el scraping
                    if "telefono" in dirty_fields:
                        club_obj.telefono = (club_obj.telefono or "")[:20]
                        # quitamos 'telefono' del update_fields y reintenta el resto
                        dirty_fields = [f for f in dirty_fields if f != "telefono"]
                    if dirty_fields:
                        club_obj.save(update_fields=dirty_fields)

        return club_obj

    def _upsert_jugador_desde_plantilla(self, jugador_info: dict) -> tuple[Jugador, str | None]:
        jugador_id = jugador_info.get("jugador_id")
        nombre = (jugador_info.get("nombre") or "").strip() or "DESCONOCIDO"
        jugador_obj = None
        if jugador_id:
            jugador_obj = Jugador.objects.filter(
                identificador_federacion=str(jugador_id)
            ).first()
        if jugador_obj is None:
            jugador_obj, _ = Jugador.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "apodo": "",
                    "posicion_principal": "",
                    "identificador_federacion": str(jugador_id) if jugador_id else None,
                    "activo": True,
                },
            )
        else:
            if jugador_id and not jugador_obj.identificador_federacion:
                jugador_obj.identificador_federacion = str(jugador_id)
                jugador_obj.save(update_fields=["identificador_federacion"])
        return jugador_obj, None

    def _upsert_jugador_en_club_temporada_base(
        self,
        jugador_obj: Jugador,
        club_obj: Club,
        temporada_obj: Temporada,
        dorsal: str | None,
    ):
        rec, created = JugadorEnClubTemporada.objects.get_or_create(
            jugador=jugador_obj,
            club=club_obj,
            temporada=temporada_obj,
            defaults={
                "dorsal": (dorsal or "")[:10],
                "partidos_jugados": 0,
                "goles": 0,
                "tarjetas_amarillas": 0,
                "tarjetas_rojas": 0,
                "convocados": 0,
                "titular": 0,
                "suplente": 0,
            },
        )
        if dorsal and not rec.dorsal:
            rec.dorsal = (dorsal or "")[:10]
            rec.save(update_fields=["dorsal"])

    def _upsert_staffclub(self, staff_info_list: list[dict], club_obj: Club, temporada_obj: Temporada):
        for s in staff_info_list:
            nombre_staff = (s.get("nombre") or "").strip()
            rol_staff = (s.get("cargo") or "").strip() or "Cuerpo técnico"
            if not nombre_staff:
                continue
            StaffClub.objects.get_or_create(
                club=club_obj,
                temporada=temporada_obj,
                nombre=nombre_staff,
                defaults={"rol": rol_staff, "activo": True},
            )

    # -----------------------
    # ID equipos por grupo
    # -----------------------
    def _collect_equipo_ids_para_grupo(
        self, temporada_key: str, competicion_key: str, grupo_key: str,
        cfg_sel: dict, j_inicio: int, j_fin: int
    ) -> list[int]:
        """
        1) Busca ids en data_clean/partidos_detalle (prefijo nuevo/antiguo).
        2) Si no hay, baja listados de jornada J[j_inicio..j_fin] y parsea equipos.
        """
        detalle_dir = os.path.join("data_clean", "partidos_detalle")
        equipo_ids: set[int] = set()

        # 1) Prefijos de partidos_detalle (nuevo y antiguo)
        if os.path.isdir(detalle_dir):
            for j in range(j_inicio, j_fin + 1):
                new_prefix = f"{temporada_key}_{competicion_key}_{grupo_key}_j{j:02d}_partido_"
                old_prefix = f"{temporada_key}_jornada_{j:02d}_partido_"
                for fname in os.listdir(detalle_dir):
                    if fname.startswith(new_prefix) or fname.startswith(old_prefix):
                        fpath = os.path.join(detalle_dir, fname)
                        try:
                            with open(fpath, "r", encoding="utf-8") as f:
                                datos = json.load(f)
                                ids = collect_equipo_ids_from_jornada([datos])
                                for eid in ids:
                                    if isinstance(eid, int):
                                        equipo_ids.add(eid)
                        except Exception:
                            pass

        if equipo_ids:
            return sorted(equipo_ids)

        # 2) Fallback: listar jornadas y extraer equipos del HTML de jornada
        raw_dir = os.path.join("data_raw", "html_listados")
        os.makedirs(raw_dir, exist_ok=True)

        for j in range(j_inicio, j_fin + 1):
            url_j = build_url_jornada(cfg_sel, j)
            raw_path = os.path.join(
                raw_dir, f"{temporada_key}_{competicion_key}_{grupo_key}_jornada_{j:02d}.html"
            )
            # Intento 1
            try:
                fetch_url(url_j, raw_path)
            except Exception as e1:
                # Espera 3s y reintenta
                time.sleep(3)
                try:
                    fetch_url(url_j, raw_path)
                except Exception as e2:
                    # Saltamos esta jornada y seguimos
                    self.stderr.write(self.style.WARNING(
                        f"[equipos] Falló listado J{j} ({competicion_key} {grupo_key}): {e2}"
                    ))
                    continue

            try:
                with open(raw_path, "r", encoding="utf-8") as f:
                    html_text = f.read()
                jornada_data = parse_jornada_partidos(html_text)
            except Exception:
                jornada_data = {}

            for p in (jornada_data.get("partidos", []) or []):
                # intentos robustos según estructura del parser
                for side_key in ("local", "visitante", "home", "away"):
                    team = p.get(side_key) or {}
                    eid = team.get("id_equipo") or team.get("id")
                    if isinstance(eid, int):
                        equipo_ids.add(eid)

        return sorted(equipo_ids)

    # -----------------------
    # MAIN
    # -----------------------
    def handle(self, *args, **options):
        temporada_key = options["temporada"]
        j_inicio = int(options["j_inicio"])
        j_fin = int(options["j_fin"])

        tcfg = TEMPORADAS.get(temporada_key)
        if not tcfg:
            self.stderr.write(self.style.ERROR(f"[equipos] Temporada '{temporada_key}' no está en config_temporadas"))
            return

        # Temporada en BD
        temporada_obj = get_or_create_temporada(temporada_key)
        self.stdout.write(self.style.MIGRATE_HEADING(f"[equipos] Temporada en BD: {temporada_obj}"))

        # Construir listado de (competicion_cli, grupo_key) a recorrer
        targets: list[tuple[str, str]] = []

        # TERCERA
        if "grupos" in tcfg:
            for gkey in sorted(tcfg["grupos"].keys()):
                targets.append(("TERCERA", gkey))

        # Otras competiciones
        otras = tcfg.get("otras_competiciones", {})
        for comp_name, comp_node in otras.items():
            comp_cli = ("PREFERENTE" if comp_name == "Preferente"
                        else "PRIMERA" if comp_name == "Primera Regional"
                        else "SEGUNDA")
            for gkey in sorted((comp_node.get("grupos") or {}).keys()):
                targets.append((comp_cli, gkey))

        if not targets:
            self.stderr.write(self.style.ERROR("[equipos] No hay grupos definidos en la temporada."))
            return

        raw_equipo_dir = os.path.join("data_raw", "html_equipos")
        os.makedirs(raw_equipo_dir, exist_ok=True)
        clean_equipo_dir = os.path.join("data_clean", "equipos")
        os.makedirs(clean_equipo_dir, exist_ok=True)
        escudos_dir = os.path.join("media", "escudos")
        os.makedirs(escudos_dir, exist_ok=True)

        for competicion_key, grupo_key in targets:
            # Selección de cfg por grupo
            try:
                cfg_sel, meta = _select_cfg(tcfg, competicion_key, grupo_key)
            except ValueError as e:
                self.stderr.write(self.style.ERROR(f"[equipos] {e}"))
                continue

            self.stdout.write(self.style.HTTP_INFO(
                f"[equipos] {temporada_key} · {competicion_key} · {grupo_key} — "
                f"colectando equipos (J{j_inicio}..J{j_fin})…"
            ))

            equipo_ids = self._collect_equipo_ids_para_grupo(
                temporada_key, competicion_key, grupo_key, cfg_sel, j_inicio, j_fin
            )

            if not equipo_ids:
                self.stderr.write(self.style.WARNING(
                    f"[equipos] Sin equipos detectados en {competicion_key} {grupo_key} (J{j_inicio}-{j_fin})."
                ))
                continue

            self.stdout.write(self.style.NOTICE(
                f"[equipos] {competicion_key} {grupo_key}: {len(equipo_ids)} equipos → {equipo_ids}"
            ))

            # ---- Procesar cada equipo de este grupo ----
            for eid in equipo_ids:
                url_equipo = build_equipo_plantilla_url(cfg_sel, eid)
                raw_equipo_path = os.path.join(
                    raw_equipo_dir, f"{temporada_key}_{competicion_key}_{grupo_key}_equipo_{eid}.html"
                )

                self.stdout.write(self.style.HTTP_INFO(f"[equipos] Descargando equipo {eid} …"))

                # Intento 1
                try:
                    fetch_url(url_equipo, raw_equipo_path)
                except Exception as e1:
                    time.sleep(3)
                    # Intento 2
                    try:
                        fetch_url(url_equipo, raw_equipo_path)
                    except Exception as e2:
                        self.stderr.write(self.style.WARNING(
                            f"[equipos] FALLÓ equipo {eid} (saltado): {e2}"
                        ))
                        continue

                # Abrir y parsear
                try:
                    with open(raw_equipo_path, "r", encoding="utf-8") as f:
                        equipo_html = f.read()
                    equipo_clean = parse_equipo_plantilla(equipo_html)
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f"[equipos] No parseable equipo {eid} (saltado): {e}"
                    ))
                    continue

                # Guardar JSON limpio (debug)
                clean_equipo_path = os.path.join(
                    clean_equipo_dir,
                    f"{temporada_key}_{competicion_key}_{grupo_key}_equipo_{eid}.json",
                )
                try:
                    with open(clean_equipo_path, "w", encoding="utf-8") as f:
                        json.dump(equipo_clean, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass

                # ==== Persistencia en BD ====
                try:
                    with transaction.atomic():
                        equipo_info = (equipo_clean.get("equipo") or {})
                        club_obj = self._get_or_create_club_full(equipo_info)

                        for jugador_info in (equipo_clean.get("jugadores") or []):
                            jugador_obj, dorsal = self._upsert_jugador_desde_plantilla(jugador_info)
                            self._upsert_jugador_en_club_temporada_base(
                                jugador_obj=jugador_obj,
                                club_obj=club_obj,
                                temporada_obj=temporada_obj,
                                dorsal=dorsal,
                            )

                        self._upsert_staffclub(
                            staff_info_list=(equipo_clean.get("tecnicos") or []),
                            club_obj=club_obj,
                            temporada_obj=temporada_obj,
                        )
                except DataError as de:
                    # si el problema vuelve a ser teléfono u otro campo largo, lo dejamos log y seguimos
                    self.stderr.write(self.style.WARNING(
                        f"[equipos] DataError guardando equipo {eid} (saltado): {de}"
                    ))
                    continue
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f"[equipos] Error guardando equipo {eid} (saltado): {e}"
                    ))
                    continue

                # Escudo (best-effort)
                escudo_url = (equipo_clean.get("equipo") or {}).get("escudo_url", "")
                if escudo_url:
                    escudo_path = os.path.join(escudos_dir, f"{eid}.png")
                    try:
                        self.stdout.write(self.style.NOTICE(f"[equipos] Descargando escudo {eid} …"))
                        fetch_binary(escudo_url, escudo_path)
                    except Exception as e:
                        self.stderr.write(self.style.WARNING(
                            f"[equipos] No se pudo bajar escudo {eid} desde {escudo_url}: {e}"
                        ))

                self.stdout.write(self.style.SUCCESS(
                    f"[equipos] Equipo {eid} procesado OK → {club_obj}"
                ))

        self.stdout.write(self.style.SUCCESS("[equipos] Todo listo 👌"))
