import time
import random
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

from scraping.core.config_temporadas import TEMPORADAS
from scraping.core.temporadas_utils import get_or_create_temporada

from status.models import DataSyncStatus
from nucleo.models import Grupo

# Mapa de nombres exactos de config → clave --competicion
COMP_KEYS = {
    "Tercera División": "TERCERA",
    "Preferente": "PREFERENTE",
    "Primera Regional": "PRIMERA",
    "Segunda Regional": "SEGUNDA",
}

def _sortable_group_key(k: str) -> tuple:
    """
    Ordena G1..G9 por número y deja otros (XIV/XV/…) alfabéticamente.
    """
    k = (k or "").upper()
    if k.startswith("G"):
        try:
            return (0, int(k[1:]))
        except Exception:
            return (0, 9999)
    return (1, k)

def _descubrir_comp_grupos_por_temporada(cfg: dict) -> List[Tuple[str, str]]:
    """
    Devuelve pares (competicion_key, grupo_key) a ejecutar para la temporada dada.
    - Tercera: lee cfg["grupos"] si existe; si no, usa fallback ["XV"].
    - Preferente/Primera/Segunda: lee cfg["otras_competiciones"][...]["grupos"].
    """
    pares: List[Tuple[str, str]] = []

    # --- Tercera ---
    tercera_grupos = (cfg.get("grupos") or {})
    if tercera_grupos:
        for gk in sorted(tercera_grupos.keys(), key=_sortable_group_key):
            pares.append(("TERCERA", gk.upper()))
    else:
        # compat con temporadas antiguas sin 'grupos'
        pares.append(("TERCERA", "XV"))

    # --- Otras competiciones ---
    otras = cfg.get("otras_competiciones", {}) or {}
    for nombre_comp, node in otras.items():
        comp_key = COMP_KEYS.get(nombre_comp)
        if not comp_key:
            continue
        grupos = (node.get("grupos") or {}).keys()
        for gk in sorted(grupos, key=_sortable_group_key):
            pares.append((comp_key, gk.upper()))

    return pares


class Command(BaseCommand):
    help = (
        "Pipeline semanal/de jornada:\n"
        " 1) scrape_live_jornada para TODAS las competiciones/grupos de la temporada actual\n"
        " 2) scrape_jugadores (multitemporada)\n"
        " 3) recalcular_clasificacion SOLO de los grupos de la temporada actual\n"
        " 4) calcular_puntos_mvp_jornada para actualizar puntos MVP y sumatorios\n"
        " 5) calcular_puntos_equipo_jornada para actualizar puntos de equipos y sumatorios"
    )

    # Usa el mismo formato de clave que en TEMPORADAS (ej. '2025-2026')
    TEMPORADA_ACTUAL = "2025-2026"

    def handle(self, *args, **options):
        temporada_key = self.TEMPORADA_ACTUAL
        cfg = TEMPORADAS.get(temporada_key)
        if not cfg:
            self.stderr.write(self.style.ERROR(f"⛔ La temporada '{temporada_key}' no está en config_temporadas.py"))
            return

        temporada_obj = get_or_create_temporada(temporada_key)

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"🗓  scrape_semana: actualización automática para {temporada_key}"
        ))

        # Descubrir combinaciones competicion+grupo desde el config
        comp_grupos = _descubrir_comp_grupos_por_temporada(cfg)
        if not comp_grupos:
            self.stderr.write(self.style.ERROR("⚠️ No hay competiciones/grupos configurados para esta temporada."))
            return

        # -------------------------------
        # Paso 1: Scrape LIVE por grupo
        # -------------------------------
        self.stdout.write(self.style.HTTP_INFO(
            "📡 Paso 1/3: scrape_live_jornada (partidos en curso / aplazados / avance de jornada)"
        ))

        for idx, (comp_key, grupo_key) in enumerate(comp_grupos, start=1):
            self.stdout.write(self.style.HTTP_INFO(
                f"   → {idx}/{len(comp_grupos)} · {temporada_key} · {comp_key} · {grupo_key}"
            ))
            try:
                # Requiere que scrape_live_jornada acepte --competicion y --grupo
                call_command(
                    "scrape_live_jornada",
                    temporada=temporada_key,
                    competicion=comp_key,
                    grupo=grupo_key,
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"   ❌ scrape_live_jornada falló en {comp_key} · {grupo_key}: {e}"
                ))

            # Pequeña pausa para ser amable con el origen
            time.sleep(random.uniform(0.7, 1.5))

        # Suave pausa antes de jugadores
        sleep_secs = random.uniform(2.0, 4.0)
        self.stdout.write(self.style.NOTICE(f"⏳ Esperando {sleep_secs:.1f}s antes de actualizar jugadores..."))
        time.sleep(sleep_secs)

        # -------------------------------
        # Paso 2: Scrape de jugadores
        # -------------------------------
        self.stdout.write(self.style.HTTP_INFO(
            "📊 Paso 2/3: scrape_jugadores (actualiza Jugador y JugadorEnClubTemporada)"
        ))
        try:
            call_command("scrape_jugadores", temporada=temporada_key)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"⚠️ scrape_jugadores lanzó excepción: {e}"))

        # -------------------------------
        # Paso 3: Recalcular clasificaciones
        # -------------------------------
        self.stdout.write(self.style.HTTP_INFO(
            "📈 Paso 3/4: recalculando clasificaciones por grupo de la temporada actual"
        ))

        try:
            grupos_qs = Grupo.objects.filter(temporada=temporada_obj)
            total = grupos_qs.count()
            self.stdout.write(self.style.NOTICE(f"Se recalcularán {total} grupos de {temporada_obj.nombre}..."))

            for g in grupos_qs.iterator():
                try:
                    call_command("recalcular_clasificacion", grupo=g.id)
                except Exception as inner_e:
                    self.stderr.write(self.style.ERROR(
                        f"❌ Error al recalcular grupo {g.id} ({g.nombre}): {inner_e}"
                    ))

                time.sleep(random.uniform(0.4, 0.9))

            self.stdout.write(self.style.SUCCESS("✅ Todas las clasificaciones recalculadas correctamente."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"⚠️ Error global al recalcular clasificaciones: {e}"))

        # -------------------------------
        # Paso 4: Calcular puntos MVP y actualizar sumatorios
        # -------------------------------
        self.stdout.write(self.style.HTTP_INFO(
            "⭐ Paso 4/5: calculando puntos MVP por jornada y actualizando sumatorios"
        ))

        try:
            # Calcular puntos MVP para todas las jornadas completadas de la temporada
            # Esto actualizará automáticamente los sumatorios
            # Usar el nombre de la temporada directamente del objeto (formato: "2025/2026")
            temporada_nombre = temporada_obj.nombre
            
            self.stdout.write(self.style.NOTICE(
                f"Calculando puntos MVP para todas las jornadas completadas de {temporada_nombre}..."
            ))
            
            call_command(
                "calcular_puntos_mvp_jornada",
                temporada=temporada_nombre,
                todas_jornadas=True,
            )
            
            self.stdout.write(self.style.SUCCESS("✅ Puntos MVP calculados y sumatorios actualizados correctamente."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"⚠️ Error al calcular puntos MVP: {e}\n"
                "   Los sumatorios se actualizarán automáticamente cuando terminen las jornadas."
            ))

        # -------------------------------
        # Paso 5: Calcular puntos de equipos y actualizar sumatorios
        # -------------------------------
        self.stdout.write(self.style.HTTP_INFO(
            "⭐ Paso 5/5: calculando puntos de equipos por jornada y actualizando sumatorios"
        ))

        try:
            # Calcular puntos de equipos para todas las jornadas completadas de la temporada
            # Esto actualizará automáticamente los sumatorios
            temporada_nombre = temporada_obj.nombre
            
            self.stdout.write(self.style.NOTICE(
                f"Calculando puntos de equipos para todas las jornadas completadas de {temporada_nombre}..."
            ))
            
            call_command(
                "calcular_puntos_equipo_jornada",
                temporada=temporada_nombre,
                todas_jornadas=True,
            )
            
            self.stdout.write(self.style.SUCCESS("✅ Puntos de equipos calculados y sumatorios actualizados correctamente."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"⚠️ Error al calcular puntos de equipos: {e}\n"
                "   Los sumatorios se actualizarán automáticamente cuando terminen las jornadas."
            ))

        # -------------------------------
        # Status
        # -------------------------------
        DataSyncStatus.objects.update_or_create(
            fuente="scrape_semana",
            defaults={
                "last_success": timezone.now(),
                "detalle": f"Actualización semanal completada correctamente ({temporada_key})",
            },
        )

        self.stdout.write(self.style.SUCCESS("✅ scrape_semana terminado y status actualizado"))
