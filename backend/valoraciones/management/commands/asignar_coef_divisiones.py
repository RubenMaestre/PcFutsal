# valoraciones/management/commands/asignar_coef_divisiones.py
from django.core.management.base import BaseCommand
from django.db import transaction
from statistics import mean

from nucleo.models import Temporada, Grupo, Competicion
from clubes.models import ClubEnGrupo
from valoraciones.models import CoeficienteClub, CoeficienteDivision


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class Command(BaseCommand):
    help = (
        "Asigna CoeficienteDivision por Competición en una Temporada.\n"
        "Dos estrategias:\n"
        " - media_clubes: calcula a partir de la media de CoeficienteClub (data-driven) y normaliza al rango [--min, --max].\n"
        " - mapa_estatico: asigna por nombre de competición usando los valores pasados (p.ej. Primera=2.0, Segunda=1.6...) "
        "   y opcionalmente NO normaliza (usar --no-normalizar para respetar valores absolutos).\n"
        "Idempotente por (competicion, temporada, jornada_referencia)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--temporada", type=str, default="2025/2026", help='Nombre de la temporada (default "2025/2026").')
        parser.add_argument("--jornada", type=int, default=6, help="Jornada de referencia a usar (default 6).")

        # Normalización (solo aplica si estrategia == media_clubes o si se desea normalizar el mapa)
        parser.add_argument("--min", dest="min_val", type=float, default=0.6, help="Valor mínimo del rango (default 0.6).")
        parser.add_argument("--max", dest="max_val", type=float, default=1.0, help="Valor máximo del rango (default 1.0).")
        parser.add_argument("--estrategia", choices=["media_clubes", "mapa_estatico"], default="mapa_estatico",
                            help='Estrategia de cálculo (default "mapa_estatico").')
        parser.add_argument("--no-normalizar", action="store_true",
                            help="Si usas mapa_estatico, no normaliza y guarda los valores tal cual.")

        # ⚙️ Valores del mapa estático (defaults = tus números)
        parser.add_argument("--primera", type=float, default=2.0, help='Coef para nombres que contengan "primera". (default 2.0)')
        parser.add_argument("--segunda", type=float, default=1.6, help='Coef para "segunda" (sin ser Segunda B). (default 1.6)')
        parser.add_argument("--segundab", type=float, default=1.3, help='Coef para "segunda b"/"2b"/"segunda federación". (default 1.3)')
        parser.add_argument("--tercera", type=float, default=1.0, help='Coef para "tercera". (default 1.0)')
        parser.add_argument("--preferente", type=float, default=0.75, help='Coef para "preferente". (default 0.75)')
        parser.add_argument("--regional1", type=float, default=0.7, help='Coef para "regional 1"/"región 1"/"1ª regional". (default 0.7)')
        parser.add_argument("--regional2", type=float, default=0.5, help='Coef para "regional 2"/"región 2"/"2ª regional". (default 0.5)')

        parser.add_argument("--dry-run", action="store_true", help="No escribe en BD, solo muestra.")

    @transaction.atomic
    def handle(self, *args, **opts):
        temporada_nombre = opts["temporada"]
        jornada_ref = int(opts["jornada"])
        estrategia = opts["estrategia"]
        dry = opts["dry_run"]

        vmin = float(opts["min_val"])
        vmax = float(opts["max_val"])
        no_normalizar = bool(opts["no_normalizar"])

        # mapa estático
        mapa = {
            "primera": float(opts["primera"]),
            "segunda": float(opts["segunda"]),
            "segundab": float(opts["segundab"]),
            "tercera": float(opts["tercera"]),
            "preferente": float(opts["preferente"]),
            "regional1": float(opts["regional1"]),
            "regional2": float(opts["regional2"]),
        }

        if vmin >= vmax and not no_normalizar:
            self.stderr.write(self.style.ERROR("--min debe ser < --max (o usa --no-normalizar)."))
            return

        # Temporada
        try:
            temporada = Temporada.objects.get(nombre=temporada_nombre)
        except Temporada.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No existe Temporada nombre='{temporada_nombre}'"))
            return

        grupos = list(Grupo.objects.filter(temporada=temporada).select_related("competicion"))
        if not grupos:
            self.stderr.write(self.style.ERROR(f"No hay grupos en temporada {temporada}"))
            return

        # Agrupar grupos por competición
        grupos_por_comp = {}
        for g in grupos:
            grupos_por_comp.setdefault(g.competicion_id, {"competicion": g.competicion, "grupos": []})
            grupos_por_comp[g.competicion_id]["grupos"].append(g)

        self.stdout.write(self.style.NOTICE(
            f"Temporada: {temporada} · Jornada ref: {jornada_ref} · Competiciones: {len(grupos_por_comp)} · "
            f"Estrategia: {estrategia} · {'DRY' if dry else 'APLICANDO'}"
        ))

        raw_scores = {}  # comp_id -> float

        if estrategia == "media_clubes":
            # Data-driven: media de coeficientes de los clubes de esa competición
            for comp_id, payload in grupos_por_comp.items():
                grupos_comp = payload["grupos"]
                club_ids = list(
                    ClubEnGrupo.objects.filter(grupo__in=grupos_comp).values_list("club_id", flat=True).distinct()
                )
                if not club_ids:
                    continue

                coef_vals = list(
                    CoeficienteClub.objects.filter(
                        club_id__in=club_ids,
                        temporada=temporada,
                        jornada_referencia=jornada_ref,
                    ).values_list("valor", flat=True)
                )
                if not coef_vals:
                    continue
                raw_scores[comp_id] = mean(coef_vals)

        else:
            # Mapa estático por nombre
            for comp_id, payload in grupos_por_comp.items():
                comp: Competicion = payload["competicion"]
                name = (comp.nombre or "").lower()

                # Detectores (ajusta a tu naming real)
                is_segundab = (
                    "segunda b" in name or "2ª b" in name or "2a b" in name or "2 b" in name
                    or "2b" in name or "segunda federación" in name or "segunda rfe" in name
                    or "segunda rfef" in name or "2ª federación" in name or "2a federación" in name
                )
                is_segunda = (
                    ("segunda" in name or "2ª" in name or "2a" in name)
                    and not is_segundab
                )
                is_primera = ("primera" in name or "1ª" in name or "1a" in name)
                is_tercera = ("tercera" in name or "3ª" in name or "3a" in name)
                is_preferente = "preferente" in name
                is_regional1 = ("regional 1" in name or "región 1" in name or "1ª regional" in name or "1a regional" in name)
                is_regional2 = ("regional 2" in name or "región 2" in name or "2ª regional" in name or "2a regional" in name)

                val = None
                if is_primera:
                    val = mapa["primera"]
                elif is_segunda:
                    val = mapa["segunda"]
                elif is_segundab:
                    val = mapa["segundab"]
                elif is_tercera:
                    val = mapa["tercera"]
                elif is_preferente:
                    val = mapa["preferente"]
                elif is_regional1:
                    val = mapa["regional1"]
                elif is_regional2:
                    val = mapa["regional2"]

                if val is not None:
                    raw_scores[comp_id] = float(val)

        if not raw_scores:
            self.stderr.write(self.style.ERROR("No se pudo calcular ningún coeficiente de división. Revisa nombres/estrategia."))
            return

        # Normalización (si procede)
        coef_divisiones = {}

        if estrategia == "mapa_estatico" and no_normalizar:
            # Respetar valores absolutos del mapa
            coef_divisiones = raw_scores.copy()
        else:
            min_raw = min(raw_scores.values())
            max_raw = max(raw_scores.values())
            if min_raw == max_raw:
                # todo igual
                for comp_id in raw_scores.keys():
                    coef_divisiones[comp_id] = vmax
            else:
                for comp_id, score in raw_scores.items():
                    norm = vmin + (score - min_raw) * (vmax - vmin) / (max_raw - min_raw)
                    coef_divisiones[comp_id] = clamp(norm, vmin, vmax)

        # Escribir/mostrar
        creados = actualizados = 0
        for comp_id, valor in coef_divisiones.items():
            comp = grupos_por_comp[comp_id]["competicion"]
            defaults = {
                "valor": float(valor),
                "comentario": (
                    "Mapa estático (sin normalizar)"
                    if (estrategia == "mapa_estatico" and no_normalizar)
                    else f"Normalizado [{vmin}, {vmax}] (estrategia={estrategia})"
                ),
                "jornada_referencia": jornada_ref,
            }

            if dry:
                self.stdout.write(f"DRY: {comp.nombre} -> {valor:.3f}")
            else:
                obj, created = CoeficienteDivision.objects.update_or_create(
                    competicion=comp,
                    temporada=temporada,
                    jornada_referencia=jornada_ref,
                    defaults=defaults,
                )
                if created:
                    creados += 1
                else:
                    actualizados += 1

        if dry:
            self.stdout.write(self.style.NOTICE("DRY-RUN completo (no se escribieron cambios)."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Listo. Creados: {creados} · Actualizados: {actualizados} · Total divisiones: {len(coef_divisiones)}"
            ))
