# management/commands/scrape_jugadores
import os
import json
from typing import Optional, Dict, Any, List

from django.core.management.base import BaseCommand
from django.db import transaction

from scraping.core.config_temporadas import TEMPORADAS
from scraping.core.fetcher import fetch_url
from scraping.core.parser_jugador_ficha import parse_jugador_ficha
from scraping.core.temporadas_utils import get_or_create_temporada

from nucleo.models import Temporada, Competicion, Grupo
from clubes.models import Club
from jugadores.models import Jugador, JugadorEnClubTemporada
from partidos.models import AlineacionPartidoJugador, EventoPartido

RAW_JUGADORES_DIR = os.path.join("data_raw", "html_jugadores")
CLEAN_JUGADORES_DIR = os.path.join("data_clean", "jugadores")
os.makedirs(RAW_JUGADORES_DIR, exist_ok=True)
os.makedirs(CLEAN_JUGADORES_DIR, exist_ok=True)

COMPETICION_NAME_MAP = {
    "TERCERA": "Tercera División",
    "PREFERENTE": "Preferente",
    "PRIMERA": "Primera Regional",
    "SEGUNDA": "Segunda Regional",
}

def _build_url_jugador(cfg: Dict[str, Any], jugador_id: int) -> str:
    from urllib.parse import urlencode
    base = "https://resultadosffcv.isquad.es/jugador_ficha.php"
    params = {
        "id_temp": cfg["id_temp"],
        "id_modalidad": cfg["id_modalidad"],
        "id_competicion": cfg["id_competicion"],
        "id_jugador": jugador_id,
    }
    return base + "?" + urlencode(params)

class Command(BaseCommand):
    help = (
        "Scrapea fichas oficiales de jugadores SOLO para la temporada actual "
        "(por defecto 2025-2026). No descarga fotos ni historial. "
        "No actualiza nombre/posición/edad; únicamente estadísticas actuales."
    )

    def add_arguments(self, parser):
        parser.add_argument("--temporada", type=str, default="2025-2026")
        parser.add_argument("--jugador-id", type=int, default=None)
        parser.add_argument("--competicion", type=str, default=None)  # TERCERA|PREFERENTE|PRIMERA|SEGUNDA
        parser.add_argument("--grupo", type=str, default=None)        # XV|XIV|G1..G4

    # ---------- HELPERS ----------

    def _pick_any_cfg_for_temp(self, tcfg: dict) -> Dict[str, Any]:
        """Coge un combo válido (id_temp, id_modalidad, id_competicion, id_torneo) de la temporada."""
        # Preferimos Tercera si está
        if "grupos" in tcfg and tcfg["grupos"]:
            gcfg = next(iter(tcfg["grupos"].values()))
            return {
                "id_temp": tcfg["id_temp"],
                "id_modalidad": tcfg["id_modalidad"],
                "id_competicion": gcfg["id_competicion"],
                "id_torneo": gcfg["id_torneo"],
            }
        # Si no, otras competiciones
        otras = tcfg.get("otras_competiciones", {})
        for node in otras.values():
            grupos = node.get("grupos", {})
            if grupos:
                gcfg = next(iter(grupos.values()))
                return {
                    "id_temp": tcfg["id_temp"],
                    "id_modalidad": tcfg["id_modalidad"],
                    "id_competicion": node["id_competicion"],
                    "id_torneo": gcfg["id_torneo"],
                }
        raise ValueError("No hay configuración válida en la temporada.")

    def _ensure_jugador_min(self, jugador_id: int) -> Jugador:
        """Garantiza que existe el Jugador pero sin tocar nombre/posición/edad si ya existe."""
        obj = Jugador.objects.filter(identificador_federacion=str(jugador_id)).first()
        if obj:
            return obj
        return Jugador.objects.create(
            identificador_federacion=str(jugador_id),
            nombre="DESCONOCIDO",
            activo=True,
        )

    def _get_or_create_club_by_name_soft(self, name: str) -> Optional[Club]:
        """Solo asegura Club por nombre si viene en la ficha (no toca otros campos)."""
        clean = (name or "").strip()
        if not clean:
            return None
        club, created = Club.objects.get_or_create(
            nombre_oficial=clean,
            defaults={"nombre_corto": clean[:100], "activo": True},
        )
        if created is False and not club.nombre_corto:
            club.nombre_corto = clean[:100]
            club.save(update_fields=["nombre_corto"])
        return club

    def _upsert_stats_actuales(
        self, jugador: Jugador, club: Optional[Club], temporada: Temporada, jugador_data: Dict[str, Any]
    ):
        """Actualiza exclusivamente las estadísticas actuales en JugadorEnClubTemporada."""
        if not club:
            return
        stats = jugador_data.get("estadisticas", {}) or {}
        header = jugador_data.get("header", {}) or {}

        valores = {
            "dorsal": (header.get("dorsal_header") or "")[:10],
            "partidos_jugados": stats.get("jugados") or 0,
            "goles": stats.get("total_goles") or 0,
            "tarjetas_amarillas": stats.get("amarillas") or 0,
            "tarjetas_rojas": stats.get("rojas") or 0,
            # mantenemos estos opcionales si existen en tu modelo:
            "convocados": stats.get("convocados") or 0,
            "titular": stats.get("titular") or 0,
            "suplente": stats.get("suplente") or 0,
        }

        rec, created = JugadorEnClubTemporada.objects.get_or_create(
            jugador=jugador, club=club, temporada=temporada, defaults=valores
        )
        if not created:
            dirty = []
            for f, v in valores.items():
                if hasattr(rec, f) and getattr(rec, f) != v:
                    setattr(rec, f, v); dirty.append(f)
            if dirty:
                rec.save(update_fields=dirty)

    def _gather_candidates(self, temporada_obj: Temporada, temporada_cfg: dict, filter_comp: str | None, filter_group: str | None) -> List[int]:
        """IDs de jugadores que aparecen en alineaciones/eventos de esta temporada (todas las competiciones/grupos)."""
        ids = set()
        targets = []

        if "grupos" in temporada_cfg:
            for gkey in temporada_cfg["grupos"].keys():
                if not filter_comp or filter_comp == "TERCERA":
                    if not filter_group or filter_group == gkey:
                        targets.append(("TERCERA", COMPETICION_NAME_MAP["TERCERA"], gkey))

        otras = temporada_cfg.get("otras_competiciones", {})
        for comp_label, node in otras.items():
            comp_cli = "PREFERENTE" if comp_label == "Preferente" else "PRIMERA" if comp_label == "Primera Regional" else "SEGUNDA"
            if filter_comp and comp_cli != filter_comp:
                continue
            for gkey in node.get("grupos", {}).keys():
                if filter_group and gkey != filter_group:
                    continue
                targets.append((comp_cli, COMPETICION_NAME_MAP[comp_cli], gkey))

        for comp_cli, comp_nombre_bd, gkey in targets:
            try:
                comp_obj = Competicion.objects.get(nombre=comp_nombre_bd)
                grupo_obj = Grupo.objects.get(competicion=comp_obj, temporada=temporada_obj, nombre__icontains=gkey)
            except (Competicion.DoesNotExist, Grupo.DoesNotExist):
                continue

            for ali in AlineacionPartidoJugador.objects.filter(partido__grupo=grupo_obj).select_related("jugador"):
                j = ali.jugador
                if j and j.identificador_federacion:
                    try:
                        ids.add(int(j.identificador_federacion))
                    except ValueError:
                        pass

            for ev in EventoPartido.objects.filter(partido__grupo=grupo_obj).select_related("jugador"):
                j = ev.jugador
                if j and j.identificador_federacion:
                    try:
                        ids.add(int(j.identificador_federacion))
                    except ValueError:
                        pass

        return sorted(ids)

    # ---------- MAIN ----------

    def handle(self, *args, **options):
        temporada_key = options["temporada"]
        jugador_forced_id = options["jugador_id"]
        filter_comp = (options["competicion"] or "").upper() or None
        filter_group = (options["grupo"] or "").upper() or None

        tcfg = TEMPORADAS.get(temporada_key)
        if not tcfg:
            self.stderr.write(self.style.ERROR(f"Temporada '{temporada_key}' no está en TEMPORADAS"))
            return

        temporada_obj = get_or_create_temporada(temporada_key)
        self.stdout.write(self.style.SUCCESS(f"[jugadores_actual] Temporada en BD: {temporada_obj}"))

        # Candidatos
        if jugador_forced_id:
            jugadores_ids = [jugador_forced_id]
        else:
            jugadores_ids = self._gather_candidates(temporada_obj, tcfg, filter_comp, filter_group)

        if not jugadores_ids:
            self.stdout.write(self.style.WARNING("[jugadores_actual] No hay jugadores candidatos que scrapear."))
            return

        self.stdout.write(self.style.SUCCESS(f"[jugadores_actual] Jugadores detectados: {len(jugadores_ids)}"))

        # CFG cualquiera válida de la temporada (vale para solicitar jugador_ficha)
        cfg = self._pick_any_cfg_for_temp(tcfg)

        for jugador_id in jugadores_ids:
            self.stdout.write(self.style.HTTP_INFO(f"[jugadores_actual] Jugador {jugador_id}..."))
            try:
                # Descargar y parsear ficha
                url = _build_url_jugador(cfg, jugador_id)
                raw_path = os.path.join(RAW_JUGADORES_DIR, f"{temporada_key}_jugador_{jugador_id}.html")
                clean_out = os.path.join(CLEAN_JUGADORES_DIR, f"{temporada_key}_jugador_{jugador_id}.json")

                fetch_url(url, raw_path)
                with open(raw_path, "r", encoding="utf-8") as f:
                    html = f.read()
                jugador_data = parse_jugador_ficha(html, jugador_id=jugador_id, id_temp=tcfg["id_temp"])

                with open(clean_out, "w", encoding="utf-8") as f:
                    json.dump(jugador_data, f, indent=2, ensure_ascii=False)

                # Persistencia (solo stats)
                with transaction.atomic():
                    jugador_obj = self._ensure_jugador_min(jugador_id)
                    equipo_actual = (jugador_data.get("datos_generales", {}) or {}).get("equipo_actual", "")
                    club_obj = self._get_or_create_club_by_name_soft(equipo_actual)
                    self._upsert_stats_actuales(jugador_obj, club_obj, temporada_obj, jugador_data)

                self.stdout.write(self.style.SUCCESS(f"[jugadores_actual] ✅ {jugador_id} actualizado"))

            except Exception as e:
                self.stderr.write(self.style.WARNING(f"[jugadores_actual] ⚠️ Error con jugador {jugador_id}: {e}"))

        self.stdout.write(self.style.SUCCESS("[jugadores_actual] Scraping temporada actual (solo stats) completado ✅"))
