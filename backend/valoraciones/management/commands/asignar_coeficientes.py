# valoraciones/management/commands/asignar_coeficientes.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from nucleo.models import Temporada, Grupo
from clubes.models import ClubEnGrupo
from valoraciones.models import CoeficienteClub

# Detectamos si existe CSP y qué campos tiene
try:
    from clubes.models import ClubSeasonProgress  # campos posibles: grupo, club, jornada, [temporada?], [posicion|pos_clasif]
    HAS_CSP = True
    # introspección de campos
    _CSP_FIELDS = {f.name for f in ClubSeasonProgress._meta.get_fields()}
    CSP_HAS_TEMPORADA = "temporada" in _CSP_FIELDS
    CSP_POS_FIELD = "posicion" if "posicion" in _CSP_FIELDS else ("pos_clasif" if "pos_clasif" in _CSP_FIELDS else None)
except Exception:
    HAS_CSP = False
    CSP_HAS_TEMPORADA = False
    CSP_POS_FIELD = None


def clamp(x: float, lo: float = 0.1, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# --- Tabla fija original para 16 equipos (modo híbrido) ---
def coef_por_pos_fijo_16(pos: int) -> float:
    rangos = [
        ((1, 2), 1.0),
        ((3, 4), 0.85),
        ((5, 6), 0.7),
        ((7, 8), 0.6),
        ((9, 10), 0.5),
        ((11, 12), 0.4),
        ((13, 14), 0.3),
        ((15, 15), 0.2),
        ((16, 16), 0.1),
    ]
    for (lo, hi), val in rangos:
        if lo <= pos <= hi:
            return val
    return 0.1


def coef_por_pos_proporcional(pos: int, total_equipos: int) -> float:
    """
    Calcula el coeficiente usando escalado lineal proporcional.
    
    El primer equipo (posición 1) tiene coeficiente 1.0, el último tiene 0.1.
    Los equipos intermedios se distribuyen linealmente entre estos valores.
    Esto es útil para grupos con número de equipos diferente a 16.
    """
    if total_equipos <= 1:
        return 1.0
    # Calcular fracción: 0 en 1º, 1 en último
    frac = (pos - 1) / (total_equipos - 1)
    # Aplicar escalado: 1.0 - 0.9 * frac (va de 1.0 a 0.1)
    val = 1.0 - 0.9 * frac
    return clamp(val)


def coef_por_pos(pos: int, total_equipos: int, modo: str = "hibrido") -> float:
    """
    Calcula el coeficiente según la posición en la clasificación.
    
    Modos:
      - "hibrido": Si total==16 usa tabla fija (optimizada para el caso más común),
                   si no usa proporcional (adaptable a cualquier número de equipos)
      - "proporcional": Siempre usa escalado proporcional (útil para grupos no estándar)
    
    El modo híbrido optimiza para el caso más común (16 equipos) mientras mantiene
    flexibilidad para otros tamaños de grupo.
    """
    if modo == "hibrido" and total_equipos == 16:
        return coef_por_pos_fijo_16(pos)
    return coef_por_pos_proporcional(pos, total_equipos)


def _str(s):
    return (s or "").strip()


def es_tercera(competicion_nombre: str) -> bool:
    n = _str(competicion_nombre).lower()
    return "tercera" in n


def es_preferente_o_regional(competicion_nombre: str) -> bool:
    n = _str(competicion_nombre).lower()
    return ("preferent" in n) or ("regional" in n)


def es_grupo_xv(g: Grupo) -> bool:
    """
    Detecta Grupo XV por:
    - atributo numero == 15 (si existe)
    - nombre que contenga 'grupo xv', ' xv ' o ' 15'
    """
    # numero
    try:
        numero = getattr(g, "numero", None)
        if numero is not None and int(numero) == 15:
            return True
    except Exception:
        pass

    # nombre
    n = (_str(getattr(g, "nombre", "")) or "").upper()
    if "GRUPO XV" in n:
        return True
    if n.endswith(" XV") or " XV " in n:
        return True
    if "GRUPO 15" in n or n.endswith(" 15") or " 15 " in n:
        return True

    return False


def obtener_clasificacion_grupo(grupo: Grupo, temporada: Temporada, jornada_ref: int):
    """
    Devuelve lista de dicts [{club: Club, posicion: int}, ...] ordenada por posicion asc.
    Intenta CSP si existe; si no, usa ClubEnGrupo.
    Es robusto a diferencias de esquema:
    - CSP con/ sin campo 'temporada'
    - CSP con 'posicion' o 'pos_clasif'
    - ClubEnGrupo con 'posicion' o 'posicion_actual'
    """
    # 1) ClubSeasonProgress
    if HAS_CSP and CSP_POS_FIELD:
        qs = ClubSeasonProgress.objects.filter(grupo=grupo, jornada=jornada_ref)
        if CSP_HAS_TEMPORADA:
            qs = qs.filter(temporada=temporada)
        try:
            qs = qs.select_related("club").order_by(CSP_POS_FIELD)
            rows = list(qs)
            if rows:
                out = []
                for r in rows:
                    pos_val = getattr(r, CSP_POS_FIELD, None)
                    if pos_val is None:
                        continue
                    out.append({"club": r.club, "posicion": int(pos_val)})
                return out
        except Exception:
            # si algo raro pasa, caemos a fallback
            pass

    # 2) Fallback: ClubEnGrupo
    try:
        # intentamos ordenar por 'posicion'
        ces = list(ClubEnGrupo.objects.filter(grupo=grupo).select_related("club").order_by("posicion"))
        if ces:
            return [{"club": ce.club, "posicion": (i + 1)} for i, ce in enumerate(ces)]
    except Exception:
        pass

    try:
        # intentamos ordenar por 'posicion_actual'
        ces = list(ClubEnGrupo.objects.filter(grupo=grupo).select_related("club").order_by("posicion_actual"))
        if ces:
            return [{"club": ce.club, "posicion": (i + 1)} for i, ce in enumerate(ces)]
    except Exception:
        pass

    # último recurso: ordenar estable por id
    ces = list(ClubEnGrupo.objects.filter(grupo=grupo).select_related("club"))
    if not ces:
        return []
    ces_sorted = sorted(ces, key=lambda x: getattr(x, "posicion", None) or getattr(x, "posicion_actual", None) or 9999)
    return [{"club": ce.club, "posicion": (i + 1)} for i, ce in enumerate(ces_sorted)]


class Command(BaseCommand):
    help = (
        "Asigna CoeficienteClub para todos los grupos de una temporada usando jornadas por división:\n"
        "Tercera=J6 (omitiendo Grupo XV), Preferente/Regional=J5.\n"
        "Idempotente: update_or_create por (club, temporada, jornada_referencia)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--temporada",
            type=str,
            default="2025/2026",
            help='Nombre de la temporada (por defecto "2025/2026").',
        )
        # Modo cálculo coef
        parser.add_argument(
            "--modo",
            type=str,
            choices=["hibrido", "proporcional"],
            default="hibrido",
            help='Modo de cálculo: "hibrido" (tabla fija si 16 equipos) o "proporcional" (siempre lineal).',
        )
        parser.add_argument(
            "--max-pos",
            type=int,
            default=16,
            help="Máximo de posiciones a procesar (por defecto 16). Úsalo alto para cubrir todo.",
        )
        parser.add_argument(
            "--incluir-todos",
            action="store_true",
            help="Ignora --max-pos y procesa todos los equipos del grupo.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No escribe en BD; muestra qué haría.",
        )
        # Jornadas por división (con tus defaults solicitados)
        parser.add_argument(
            "--jornada-tercera",
            type=int,
            default=6,
            help="Jornada de referencia para Tercera División (por defecto 6).",
        )
        parser.add_argument(
            "--jornada-otras",
            type=int,
            default=5,
            help="Jornada de referencia para Preferente y Regional (por defecto 5).",
        )
        # Omitir grupos por id si quieres afinar
        parser.add_argument(
            "--omitir-grupo-ids",
            type=str,
            default="",
            help="IDs de grupos a omitir (coma-separados). Ej: '41,42'.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        temporada_nombre: str = opts["temporada"]
        modo: str = opts["modo"]
        max_pos: int = opts["max_pos"]
        incluir_todos: bool = opts["incluir_todos"]
        dry: bool = opts["dry_run"]
        j_tercera: int = opts["jornada_tercera"]
        j_otras: int = opts["jornada_otras"]
        omitir_ids_raw: str = opts["omitir_grupo_ids"]

        omit_ids = set()
        if omitir_ids_raw.strip():
            try:
                omit_ids = {int(x.strip()) for x in omitir_ids_raw.split(",") if x.strip()}
            except Exception:
                self.stderr.write(self.style.WARNING("No se pudieron parsear --omitir-grupo-ids; se ignora."))

        # 1) Temporada
        try:
            temporada = Temporada.objects.get(nombre=temporada_nombre)
        except Temporada.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No existe Temporada nombre='{temporada_nombre}'"))
            return

        # 2) Grupos de la temporada
        grupos = (
            Grupo.objects
            .filter(temporada=temporada)
            .select_related("competicion")
            .order_by("id")
        )
        if not grupos.exists():
            self.stderr.write(self.style.ERROR(f"No hay grupos para la temporada '{temporada_nombre}'"))
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Temporada: {temporada} · Grupos: {grupos.count()} · Modo coef: {modo} · "
                f"Reglas: Tercera→J{j_tercera}; Preferente/Regional→J{j_otras} · "
                f"{'DRY-RUN' if dry else 'APLICANDO'}"
            )
        )

        creados = actualizados = grupos_sin_datos = total_asignados = 0

        # 3) Recorrer grupos
        for g in grupos:
            comp_nom = _str(getattr(g.competicion, "nombre", ""))

            # Omisiones explícitas
            if g.id in omit_ids:
                self.stdout.write(self.style.WARNING(f"[Grupo {g.id}] Omitido por --omitir-grupo-ids."))
                continue

            # Tercera División → omitir Grupo XV
            if es_tercera(comp_nom) and es_grupo_xv(g):
                self.stdout.write(self.style.WARNING(f"[Grupo {g.id}] Omitido (Tercera · Grupo XV)."))
                continue

            # Jornada de referencia por división
            if es_tercera(comp_nom):
                jornada_ref = j_tercera
            elif es_preferente_o_regional(comp_nom):
                jornada_ref = j_otras
            else:
                jornada_ref = j_otras  # por coherencia para otras divisiones

            # 3.1) Clasificación a la jornada de referencia
            progresiones = obtener_clasificacion_grupo(g, temporada, jornada_ref)

            if not progresiones:
                self.stderr.write(self.style.WARNING(
                    f"[Grupo {g.id}] Sin datos de clasificación para J{jornada_ref}. Omitido."
                ))
                grupos_sin_datos += 1
                continue

            # 3.2) Determinar cuántos equipos procesar
            total_disponibles = len(progresiones)
            total_equipos = total_disponibles if incluir_todos else min(max_pos, total_disponibles)
            if total_equipos <= 0:
                self.stderr.write(self.style.WARNING(f"[Grupo {g.id}] Sin equipos a procesar. Omitido."))
                grupos_sin_datos += 1
                continue

            # 3.3) Asignación
            for idx, row in enumerate(progresiones[:total_equipos], start=1):
                club = row["club"]
                pos = int(row["posicion"])
                coef = coef_por_pos(pos, total_equipos, modo=modo)

                defaults = {
                    "valor": coef,
                    "comentario": (
                        f"Coeficiente por posición {pos} en J{jornada_ref} "
                        f"(grupo {g.id}, total equipos {total_equipos}, modo {modo})"
                    ),
                    "jornada_referencia": jornada_ref,
                }

                if dry:
                    self.stdout.write(
                        f"DRY: Grupo {g.id} · {club} -> pos {pos}/{total_equipos} "
                        f"(J{jornada_ref}) => {coef:.3f}"
                    )
                    total_asignados += 1
                    continue

                obj, created = CoeficienteClub.objects.update_or_create(
                    club=club,
                    temporada=temporada,
                    jornada_referencia=jornada_ref,
                    defaults=defaults,
                )
                total_asignados += 1
                if created:
                    creados += 1
                else:
                    actualizados += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"[Grupo {g.id}] OK · J{jornada_ref} · {total_equipos} equipos procesados"
                )
            )

        # 4) Resumen
        if dry:
            self.stdout.write(
                self.style.NOTICE(
                    f"DRY-RUN completo · Asignaciones simuladas: {total_asignados} · "
                    f"Grupos sin datos: {grupos_sin_datos}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Fin. Creados: {creados} · Actualizados: {actualizados} · "
                    f"Total asignados: {total_asignados} · Grupos sin datos: {grupos_sin_datos}"
                )
            )
