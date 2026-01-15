# fantasy/management/commands/calcular_puntos_equipo_jornada.py
"""
Comando para calcular y almacenar puntos fantasy de equipos por jornada.

Uso:
    python manage.py calcular_puntos_equipo_jornada --temporada "2025/2026" --jornada 1
    python manage.py calcular_puntos_equipo_jornada --temporada "2025/2026" --jornada 1 --grupo 5
    python manage.py calcular_puntos_equipo_jornada --temporada "2025/2026" --todas-jornadas
    python manage.py calcular_puntos_equipo_jornada --temporada "2025/2026" --jornada 1 --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from nucleo.models import Temporada, Grupo
from partidos.models import Partido
from clubes.models import ClubEnGrupo, Club
from valoraciones.models import CoeficienteClub
from valoraciones.views import EquipoJornadaView
from fantasy.models import PuntosEquipoJornada, PuntosEquipoTotal
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


def _actualizar_sumatorio_total(club_id: int, temporada_id: int):
    """
    Actualiza el sumatorio total de puntos fantasy para un equipo en una temporada.
    """
    try:
        club = Club.objects.get(id=club_id)
        temporada = Temporada.objects.get(id=temporada_id)
    except (Club.DoesNotExist, Temporada.DoesNotExist):
        logger.warning(
            f"No se encontró club={club_id} o temporada={temporada_id} para actualizar sumatorio."
        )
        return

    # Sumar todos los puntos de jornada para este equipo en esta temporada
    sum_data = (
        PuntosEquipoJornada.objects.filter(
            club=club, temporada=temporada
        )
        .aggregate(
            total_puntos=Sum("puntos"),
            total_partidos=Sum("partidos_jugados"),
            total_victorias=Sum("victorias"),
            total_empates=Sum("empates"),
            total_derrotas=Sum("derrotas"),
            total_goles_favor=Sum("goles_favor"),
            total_goles_contra=Sum("goles_contra"),
        )
    )

    puntos_total = sum_data["total_puntos"] or 0.0
    partidos_total = sum_data["total_partidos"] or 0
    victorias_total = sum_data["total_victorias"] or 0
    empates_total = sum_data["total_empates"] or 0
    derrotas_total = sum_data["total_derrotas"] or 0
    goles_favor_total = sum_data["total_goles_favor"] or 0
    goles_contra_total = sum_data["total_goles_contra"] or 0

    PuntosEquipoTotal.objects.update_or_create(
        club=club,
        temporada=temporada,
        defaults={
            "puntos_total": puntos_total,
            "partidos_total": partidos_total,
            "victorias_total": victorias_total,
            "empates_total": empates_total,
            "derrotas_total": derrotas_total,
            "goles_favor_total": goles_favor_total,
            "goles_contra_total": goles_contra_total,
        },
    )
    logger.debug(
        f"Sumatorio total actualizado para {club} en {temporada}: {puntos_total:.2f} pts"
    )


class Command(BaseCommand):
    help = (
        "Calcula y almacena puntos fantasy de equipos por jornada para optimizar el ranking global.\n"
        "Reutiliza la lógica de cálculo de EquipoJornadaView pero almacena los resultados."
    )

    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6

    def add_arguments(self, parser):
        parser.add_argument(
            "--temporada",
            type=str,
            required=True,
            help='Nombre de la temporada (ej. "2025/2026").',
        )
        parser.add_argument(
            "--jornada",
            type=int,
            help="Número de jornada a calcular. Requerido si no se usa --todas-jornadas.",
        )
        parser.add_argument(
            "--grupo",
            type=int,
            help="ID del grupo específico (opcional). Si no se especifica, se procesan todos.",
        )
        parser.add_argument(
            "--todas-jornadas",
            action="store_true",
            help="Calcula todas las jornadas de la temporada.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No guarda en BD; solo muestra qué haría.",
        )
        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Recalcula incluso si ya existen puntos para esa jornada.",
        )

    def _bonus_rival_fuerte(self, coef_rival: float) -> float:
        """Bonus por enfrentarse a un rival fuerte."""
        if coef_rival >= 0.8:
            return 0.35
        if coef_rival >= 0.6:
            return 0.20
        if coef_rival >= 0.4:
            return 0.10
        return 0.0

    def _bonus_diferencia(self, dif_goles: int) -> float:
        """Bonus por diferencia de goles."""
        if dif_goles >= 3:
            return 0.35
        if dif_goles == 2:
            return 0.20
        if dif_goles == 1:
            return 0.10
        return 0.0

    def _penalizacion_rival_debil(self, pos_rival: int | None) -> float:
        """Penalización por enfrentarse a un rival débil."""
        if not pos_rival:
            return 0.0
        if pos_rival >= 14:
            return -0.15
        return 0.0

    def _bonus_rompe_racha(self, racha_rival: str | None) -> float:
        """Bonus por romper racha del rival."""
        if not racha_rival:
            return 0.0
        r = racha_rival.strip().upper()
        streak_v = 0
        for ch in r:
            if ch == "V":
                streak_v += 1
            else:
                break
        if streak_v >= 3:
            return 0.15
        return 0.0

    def _calcular_puntos_equipo_jornada(
        self,
        grupo: Grupo,
        temporada: Temporada,
        jornada: int,
    ) -> dict[int, dict]:
        """
        Calcula puntos fantasy para todos los equipos de un grupo en una jornada específica.
        
        Retorna: dict[club_id, {puntos, partidos_jugados, victorias, empates, derrotas, goles_favor, goles_contra}]
        """
        # Obtener todos los partidos de esa jornada en ese grupo
        partidos = (
            Partido.objects
            .filter(
                grupo=grupo,
                jornada_numero=jornada,
                jugado=True,
            )
            .select_related("local", "visitante")
            .order_by("fecha_hora", "id")
        )
        
        partidos_list = list(partidos)
        if not partidos_list:
            return {}
        
        # Obtener clasificación del grupo (para posición y racha)
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )
        clasif_lookup = {}
        for c in clasif_rows:
            clasif_lookup[c.club_id] = {
                "pos": c.posicion_actual,
                "racha": (c.racha or "").strip().upper(),
            }
        
        # Obtener coeficientes de clubes
        coef_rows = (
            CoeficienteClub.objects
            .filter(
                temporada_id=self.TEMPORADA_ID_BASE,
                jornada_referencia=self.JORNADA_REF_COEF,
            )
            .select_related("club")
        )
        coef_lookup = {r.club_id: r.valor for r in coef_rows}
        
        # Diccionario para acumular puntos por equipo
        puntos_equipos: dict[int, dict] = {}
        
        for p in partidos_list:
            gl = p.goles_local or 0
            gv = p.goles_visitante or 0
            
            local_id = p.local_id
            visit_id = p.visitante_id
            
            # ===== CÁLCULO PUNTOS LOCAL =====
            if gl > gv:
                base_local = 1.0
                resultado_local = "V"
            elif gl == gv:
                base_local = 0.4
                resultado_local = "E"
            else:
                base_local = 0.0
                resultado_local = "D"
            
            coef_rival_local = coef_lookup.get(visit_id, 0.4)
            bonus_rival_local = self._bonus_rival_fuerte(coef_rival_local)
            
            dif_local = gl - gv
            bonus_dif_local = self._bonus_diferencia(dif_local)
            
            pos_rival_local = clasif_lookup.get(visit_id, {}).get("pos")
            pen_rival_local = self._penalizacion_rival_debil(pos_rival_local)
            
            racha_rival_local = clasif_lookup.get(visit_id, {}).get("racha")
            bonus_rompe_local = self._bonus_rompe_racha(racha_rival_local)
            
            coef_local = coef_lookup.get(local_id, 0.4)
            
            score_local = (
                base_local
                + bonus_rival_local
                + bonus_dif_local
                + bonus_rompe_local
                + pen_rival_local
            )
            score_local *= (0.9 + coef_local)
            
            # Acumular puntos del equipo local
            if local_id not in puntos_equipos:
                puntos_equipos[local_id] = {
                    "puntos": 0.0,
                    "partidos_jugados": 0,
                    "victorias": 0,
                    "empates": 0,
                    "derrotas": 0,
                    "goles_favor": 0,
                    "goles_contra": 0,
                }
            
            puntos_equipos[local_id]["puntos"] += round(score_local, 4)
            puntos_equipos[local_id]["partidos_jugados"] += 1
            puntos_equipos[local_id]["goles_favor"] += gl
            puntos_equipos[local_id]["goles_contra"] += gv
            
            if resultado_local == "V":
                puntos_equipos[local_id]["victorias"] += 1
            elif resultado_local == "E":
                puntos_equipos[local_id]["empates"] += 1
            else:
                puntos_equipos[local_id]["derrotas"] += 1
            
            # ===== CÁLCULO PUNTOS VISITANTE =====
            if gv > gl:
                base_visit = 1.0
                resultado_visit = "V"
            elif gv == gl:
                base_visit = 0.4
                resultado_visit = "E"
            else:
                base_visit = 0.0
                resultado_visit = "D"
            
            coef_rival_visit = coef_lookup.get(local_id, 0.4)
            bonus_rival_visit = self._bonus_rival_fuerte(coef_rival_visit)
            
            dif_visit = gv - gl
            bonus_dif_visit = self._bonus_diferencia(dif_visit)
            
            pos_rival_visit = clasif_lookup.get(local_id, {}).get("pos")
            pen_rival_visit = self._penalizacion_rival_debil(pos_rival_visit)
            
            racha_rival_visit = clasif_lookup.get(local_id, {}).get("racha")
            bonus_rompe_visit = self._bonus_rompe_racha(racha_rival_visit)
            
            coef_visit = coef_lookup.get(visit_id, 0.4)
            
            bonus_fuera = 0.0
            if gv > gl:
                bonus_fuera = 0.25
            
            score_visit = (
                base_visit
                + bonus_rival_visit
                + bonus_dif_visit
                + bonus_rompe_visit
                + pen_rival_visit
                + bonus_fuera
            )
            score_visit *= (0.9 + coef_visit)
            
            # Acumular puntos del equipo visitante
            if visit_id not in puntos_equipos:
                puntos_equipos[visit_id] = {
                    "puntos": 0.0,
                    "partidos_jugados": 0,
                    "victorias": 0,
                    "empates": 0,
                    "derrotas": 0,
                    "goles_favor": 0,
                    "goles_contra": 0,
                }
            
            puntos_equipos[visit_id]["puntos"] += round(score_visit, 4)
            puntos_equipos[visit_id]["partidos_jugados"] += 1
            puntos_equipos[visit_id]["goles_favor"] += gv
            puntos_equipos[visit_id]["goles_contra"] += gl
            
            if resultado_visit == "V":
                puntos_equipos[visit_id]["victorias"] += 1
            elif resultado_visit == "E":
                puntos_equipos[visit_id]["empates"] += 1
            else:
                puntos_equipos[visit_id]["derrotas"] += 1
        
        return puntos_equipos

    def handle(self, *args, **options):
        temporada_nombre = options["temporada"]
        jornada_num = options.get("jornada")
        grupo_id = options.get("grupo")
        todas_jornadas = options.get("todas_jornadas", False)
        dry_run = options.get("dry_run", False)
        forzar = options.get("forzar", False)
        
        # Validar parámetros
        if not todas_jornadas and not jornada_num:
            self.stderr.write(
                self.style.ERROR("Debes especificar --jornada o --todas-jornadas")
            )
            return
        
        # Obtener temporada
        try:
            temporada = Temporada.objects.get(nombre=temporada_nombre)
        except Temporada.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f'Temporada "{temporada_nombre}" no encontrada')
            )
            return
        
        # Obtener grupos a procesar
        grupos_qs = Grupo.objects.filter(temporada=temporada)
        if grupo_id:
            grupos_qs = grupos_qs.filter(id=grupo_id)
        
        grupos = list(grupos_qs.select_related("competicion", "temporada"))
        
        if not grupos:
            self.stderr.write(
                self.style.ERROR(f"No se encontraron grupos para la temporada {temporada_nombre}")
            )
            return
        
        total_creados = 0
        total_actualizados = 0
        total_errores = 0
        
        # Procesar cada grupo
        for grupo in grupos:
            if todas_jornadas:
                # Obtener todas las jornadas disponibles en este grupo
                jornadas = (
                    Partido.objects
                    .filter(grupo=grupo, jugado=True)
                    .values_list("jornada_numero", flat=True)
                    .distinct()
                    .order_by("jornada_numero")
                )
                jornadas = sorted(set(jornadas))
            else:
                jornadas = [jornada_num]
            
            for jornada in jornadas:
                try:
                    # Verificar si ya existe (si no es forzar)
                    if not forzar:
                        existe = PuntosEquipoJornada.objects.filter(
                            temporada=temporada,
                            grupo=grupo,
                            jornada=jornada,
                        ).exists()
                        if existe:
                            continue
                    
                    # Calcular puntos
                    puntos_data = self._calcular_puntos_equipo_jornada(
                        grupo, temporada, jornada
                    )
                    
                    if not puntos_data:
                        continue
                    
                    if dry_run:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"[DRY RUN] Grupo {grupo.nombre} J{jornada}: "
                                f"{len(puntos_data)} equipos calcularían puntos"
                            )
                        )
                        continue
                    
                    # Guardar puntos por equipo
                    with transaction.atomic():
                        for club_id, data in puntos_data.items():
                            obj, created = PuntosEquipoJornada.objects.update_or_create(
                                temporada=temporada,
                                grupo=grupo,
                                jornada=jornada,
                                club_id=club_id,
                                defaults={
                                    "puntos": data["puntos"],
                                    "partidos_jugados": data["partidos_jugados"],
                                    "victorias": data["victorias"],
                                    "empates": data["empates"],
                                    "derrotas": data["derrotas"],
                                    "goles_favor": data["goles_favor"],
                                    "goles_contra": data["goles_contra"],
                                },
                            )
                            if created:
                                total_creados += 1
                            else:
                                total_actualizados += 1
                            
                            # Actualizar sumatorio total del equipo
                            _actualizar_sumatorio_total(club_id, temporada.id)
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {grupo.nombre} J{jornada}: {len(puntos_data)} equipos procesados"
                        )
                    )
                
                except Exception as e:
                    total_errores += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"❌ Error en {grupo.nombre} J{jornada}: {e}"
                        )
                    )
        
        # Resumen
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Proceso completado:\n"
            f"   - Creados: {total_creados}\n"
            f"   - Actualizados: {total_actualizados}\n"
            f"   - Errores: {total_errores}"
        ))

