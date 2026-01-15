# clasificaciones/management/commands/generar_historico_clasificaciones.py
"""
Command para generar el histórico de clasificaciones por jornada.

Uso:
  python manage.py generar_historico_clasificaciones --grupo_id=X  # Todas las jornadas del grupo
  python manage.py generar_historico_clasificaciones --temporada_id=X  # Todos los grupos de la temporada
  python manage.py generar_historico_clasificaciones --retrospectivo  # Todas las temporadas
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max, Q

from nucleo.models import Grupo, Temporada
from clubes.models import Club, ClubEnGrupo
from partidos.models import Partido
from clasificaciones.models import ClasificacionJornada, PosicionJornada


class Command(BaseCommand):
    help = "Genera el histórico de clasificaciones por jornada para grupos y temporadas"

    def add_arguments(self, parser):
        parser.add_argument(
            "--grupo_id",
            type=int,
            help="ID del grupo para generar histórico (todas las jornadas)",
        )
        parser.add_argument(
            "--temporada_id",
            type=int,
            help="ID de la temporada para generar histórico (todos los grupos)",
        )
        parser.add_argument(
            "--retrospectivo",
            action="store_true",
            help="Generar histórico para todas las temporadas",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forzar regeneración incluso si ya existe",
        )

    def _calcular_clasificacion_hasta_jornada(self, grupo: Grupo, hasta_jornada: int):
        """
        Calcula la clasificación de un grupo hasta una jornada específica.
        
        Esta función reutiliza la misma lógica que recalcular_clasificacion.py pero
        permite calcular la clasificación en cualquier punto del tiempo (hasta una jornada específica).
        Esto es crucial para generar el histórico de clasificaciones.
        """
        # 1. Obtener todos los clubs del grupo.
        # Combinamos clubs que aparecen en partidos (local o visitante) con clubs
        # registrados en ClubEnGrupo para asegurar que no se nos escape ningún club.
        clubs_en_partidos_ids = set(
            Partido.objects.filter(grupo=grupo)
            .values_list("local_id", flat=True)
        ) | set(
            Partido.objects.filter(grupo=grupo)
            .values_list("visitante_id", flat=True)
        )

        clubs_en_grupo_ids = set(
            ClubEnGrupo.objects.filter(grupo=grupo)
            .values_list("club_id", flat=True)
        )

        # Unión de ambos sets para obtener todos los clubs posibles
        club_ids = clubs_en_partidos_ids | clubs_en_grupo_ids
        clubs = Club.objects.filter(id__in=club_ids)

        # 2. Inicializar stats por club
        stats = {}
        for club in clubs:
            stats[club.id] = {
                "club": club,
                "puntos": 0,
                "pj": 0,
                "ganados": 0,
                "empatados": 0,
                "perdidos": 0,
                "gf": 0,
                "gc": 0,
                "resultados_ordenados": [],
            }

        # 3. Obtener partidos jugados hasta la jornada indicada.
        # El filtro jornada_numero__lte=hasta_jornada es crucial: permite calcular
        # la clasificación como estaba en ese momento histórico, no la actual.
        partidos_jugados = (
            Partido.objects
            .filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
                jornada_numero__lte=hasta_jornada,  # Solo partidos hasta esta jornada
            )
            .order_by("jornada_numero", "fecha_hora", "id")
        )

        # 4. Calcular estadísticas
        for partido in partidos_jugados:
            lid = partido.local_id
            vid = partido.visitante_id
            gl = partido.goles_local
            gv = partido.goles_visitante

            if lid not in stats:
                stats[lid] = {
                    "club": partido.local,
                    "puntos": 0,
                    "pj": 0,
                    "ganados": 0,
                    "empatados": 0,
                    "perdidos": 0,
                    "gf": 0,
                    "gc": 0,
                    "resultados_ordenados": [],
                }
            if vid not in stats:
                stats[vid] = {
                    "club": partido.visitante,
                    "puntos": 0,
                    "pj": 0,
                    "ganados": 0,
                    "empatados": 0,
                    "perdidos": 0,
                    "gf": 0,
                    "gc": 0,
                    "resultados_ordenados": [],
                }

            stats[lid]["pj"] += 1
            stats[vid]["pj"] += 1

            stats[lid]["gf"] += gl
            stats[lid]["gc"] += gv
            stats[vid]["gf"] += gv
            stats[vid]["gc"] += gl

            if gl > gv:
                stats[lid]["puntos"] += 3
                stats[lid]["ganados"] += 1
                stats[vid]["perdidos"] += 1
                stats[lid]["resultados_ordenados"].append("V")
                stats[vid]["resultados_ordenados"].append("D")
            elif gl < gv:
                stats[vid]["puntos"] += 3
                stats[vid]["ganados"] += 1
                stats[lid]["perdidos"] += 1
                stats[vid]["resultados_ordenados"].append("V")
                stats[lid]["resultados_ordenados"].append("D")
            else:
                stats[lid]["puntos"] += 1
                stats[vid]["puntos"] += 1
                stats[lid]["empatados"] += 1
                stats[vid]["empatados"] += 1
                stats[lid]["resultados_ordenados"].append("E")
                stats[vid]["resultados_ordenados"].append("E")

        # 5. Calcular racha
        for club_id, s in stats.items():
            ultimos5 = s["resultados_ordenados"][-5:]
            s["racha"] = "".join(ultimos5)

        # 6. Crear lista ordenable
        clasificacion_lista = []
        for club_id, s in stats.items():
            dif_goles = s["gf"] - s["gc"]
            clasificacion_lista.append({
                "club": s["club"],
                "puntos": s["puntos"],
                "pj": s["pj"],
                "gf": s["gf"],
                "gc": s["gc"],
                "dif": dif_goles,
                "racha": s["racha"],
            })

        # 7. Ordenar
        clasificacion_lista.sort(
            key=lambda row: (
                -row["puntos"],
                -row["dif"],
                -row["gf"],
                row["club"].nombre_corto or row["club"].nombre_oficial,
            )
        )

        return clasificacion_lista, stats, partidos_jugados.count()

    def _guardar_clasificacion_jornada(self, grupo: Grupo, jornada: int, clasificacion_lista: list, stats: dict, total_partidos: int, force: bool = False):
        """Guarda la clasificación de una jornada específica"""
        # Verificar si ya existe
        if not force:
            if ClasificacionJornada.objects.filter(grupo=grupo, jornada=jornada).exists():
                return False  # Ya existe, no regenerar

        # Crear/actualizar ClasificacionJornada
        clasif_jornada, created = ClasificacionJornada.objects.get_or_create(
            grupo=grupo,
            jornada=jornada,
            defaults={
                'partidos_jugados_total': total_partidos,
                'equipos_participantes': len(clasificacion_lista),
            }
        )

        if not created:
            clasif_jornada.partidos_jugados_total = total_partidos
            clasif_jornada.equipos_participantes = len(clasificacion_lista)
            clasif_jornada.save()

        # Borrar posiciones existentes
        PosicionJornada.objects.filter(clasificacion_jornada=clasif_jornada).delete()

        # Crear posiciones
        posiciones_a_crear = []
        for idx, row in enumerate(clasificacion_lista, start=1):
            club_id = row["club"].id
            posiciones_a_crear.append(
                PosicionJornada(
                    clasificacion_jornada=clasif_jornada,
                    club=row["club"],
                    posicion=idx,
                    puntos=row["puntos"],
                    partidos_jugados=row["pj"],
                    partidos_ganados=stats[club_id]["ganados"],
                    partidos_empatados=stats[club_id]["empatados"],
                    partidos_perdidos=stats[club_id]["perdidos"],
                    goles_favor=row["gf"],
                    goles_contra=row["gc"],
                    diferencia_goles=row["dif"],
                    racha=row["racha"],
                )
            )

        PosicionJornada.objects.bulk_create(posiciones_a_crear)
        return True

    def _procesar_grupo(self, grupo: Grupo, force: bool = False):
        """Procesa todas las jornadas de un grupo"""
        # Obtener jornadas disponibles
        partidos_jugados = Partido.objects.filter(
            grupo=grupo,
            jugado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False,
        )

        if not partidos_jugados.exists():
            self.stdout.write(self.style.WARNING(
                f"  ⚠️  No hay partidos jugados en {grupo.nombre}"
            ))
            return 0

        jornadas_disponibles = sorted(set(
            partidos_jugados.values_list("jornada_numero", flat=True).distinct()
        ))

        self.stdout.write(self.style.NOTICE(
            f"  📊 Procesando {len(jornadas_disponibles)} jornadas..."
        ))

        generadas = 0
        for jornada in jornadas_disponibles:
            clasificacion_lista, stats, total_partidos = self._calcular_clasificacion_hasta_jornada(grupo, jornada)
            
            guardado = self._guardar_clasificacion_jornada(
                grupo, jornada, clasificacion_lista, stats, total_partidos, force
            )
            
            if guardado:
                generadas += 1
                self.stdout.write(self.style.SUCCESS(f"    ✅ Jornada {jornada} guardada"))
            else:
                self.stdout.write(self.style.WARNING(f"    ⏭️  Jornada {jornada} ya existía (usa --force para regenerar)"))

        return generadas

    @transaction.atomic
    def handle(self, *args, **options):
        grupo_id = options.get("grupo_id")
        temporada_id = options.get("temporada_id")
        retrospectivo = options.get("retrospectivo", False)
        force = options.get("force", False)

        grupos_a_procesar = []

        if grupo_id:
            # Procesar un grupo específico
            try:
                grupo = Grupo.objects.select_related("competicion", "temporada").get(id=grupo_id)
                grupos_a_procesar = [grupo]
            except Grupo.DoesNotExist:
                raise CommandError(f"Grupo con id={grupo_id} no existe")

        elif temporada_id:
            # Procesar todos los grupos de una temporada
            try:
                temporada = Temporada.objects.get(id=temporada_id)
                grupos_a_procesar = Grupo.objects.filter(temporada=temporada).select_related("competicion", "temporada")
            except Temporada.DoesNotExist:
                raise CommandError(f"Temporada con id={temporada_id} no existe")

        elif retrospectivo:
            # Procesar todas las temporadas
            temporadas = Temporada.objects.all().order_by("-nombre")
            self.stdout.write(self.style.HTTP_INFO(
                f"🔍 Modo retrospectivo: {temporadas.count()} temporadas encontradas"
            ))
            for temp in temporadas:
                grupos_temp = Grupo.objects.filter(temporada=temp).select_related("competicion", "temporada")
                grupos_a_procesar.extend(grupos_temp)

        else:
            raise CommandError(
                "Debes especificar --grupo_id=X, --temporada_id=X o --retrospectivo"
            )

        if not grupos_a_procesar:
            raise CommandError("No se encontraron grupos para procesar")

        self.stdout.write(self.style.SUCCESS(
            f"🚀 Generando histórico para {len(grupos_a_procesar)} grupo(s)..."
        ))

        total_generadas = 0
        for grupo in grupos_a_procesar:
            self.stdout.write(self.style.NOTICE(
                f"\n📁 {grupo.nombre} ({grupo.competicion.nombre} - {grupo.temporada.nombre})"
            ))
            generadas = self._procesar_grupo(grupo, force=force)
            total_generadas += generadas

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Completado: {total_generadas} clasificaciones generadas"
        ))










