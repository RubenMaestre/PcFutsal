from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max

from nucleo.models import Grupo
from clubes.models import Club, ClubEnGrupo
from partidos.models import Partido
from clasificaciones.models import ClasificacionJornada, PosicionJornada


class Command(BaseCommand):
    help = "Recalcula la clasificación (puntos, PJ, racha, posición_actual...) para un grupo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--grupo",
            type=int,
            required=True,
            help="ID del Grupo (nucleo.Grupo) para el que recalcular la clasificación",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        grupo_id = options["grupo"]

        # 1. Obtenemos el grupo
        try:
            grupo = Grupo.objects.select_related("competicion", "temporada").get(id=grupo_id)
        except Grupo.DoesNotExist:
            raise CommandError(f"Grupo con id={grupo_id} no existe")

        self.stdout.write(self.style.NOTICE(
            f"Recalculando clasificación para Grupo {grupo.id} ({grupo.nombre}) / {grupo.competicion.nombre} / {grupo.temporada.nombre}"
        ))

        # 2. Obtenemos todos los clubs que han jugado (o deberían estar en este grupo)
        #    Aquí asumimos que si han jugado algún partido en este grupo, pertenecen al grupo.
        #    Alternativamente podríamos tener ClubEnGrupo creado ya para todos desde el principio.
        clubs_en_partidos_ids = set(
            Partido.objects.filter(grupo=grupo)
            .values_list("local_id", flat=True)
        ) | set(
            Partido.objects.filter(grupo=grupo)
            .values_list("visitante_id", flat=True)
        )

        # También añadimos los que ya están en ClubEnGrupo por si aún no han jugado
        clubs_en_grupo_ids = set(
            ClubEnGrupo.objects.filter(grupo=grupo)
            .values_list("club_id", flat=True)
        )

        club_ids = clubs_en_partidos_ids | clubs_en_grupo_ids

        clubs = Club.objects.filter(id__in=club_ids)

        # 3. Inicializamos stats por club
        #    Estas stats son las que acabaremos guardando en ClubEnGrupo
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
                "resultados_ordenados": [],  # para racha
            }

        # 4. Cogemos TODOS los partidos jugados de este grupo (solo los que tienen marcador válido)
        #    Ordenados por jornada_numero y luego por fecha_hora para construir la racha en orden cronológico
        partidos_jugados = (
            Partido.objects
            .filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            )
            .order_by("jornada_numero", "fecha_hora", "id")
        )

        for partido in partidos_jugados:
            lid = partido.local_id
            vid = partido.visitante_id
            gl = partido.goles_local
            gv = partido.goles_visitante

            # aseguramos que ambos están en stats (por si acaso)
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

            # PJ
            stats[lid]["pj"] += 1
            stats[vid]["pj"] += 1

            # Goles
            stats[lid]["gf"] += gl
            stats[lid]["gc"] += gv
            stats[vid]["gf"] += gv
            stats[vid]["gc"] += gl

            # Resultado y puntos
            if gl > gv:
                # local gana
                stats[lid]["puntos"] += 3
                stats[lid]["ganados"] += 1
                stats[vid]["perdidos"] += 1

                stats[lid]["resultados_ordenados"].append("V")
                stats[vid]["resultados_ordenados"].append("D")

            elif gl < gv:
                # visitante gana
                stats[vid]["puntos"] += 3
                stats[vid]["ganados"] += 1
                stats[lid]["perdidos"] += 1

                stats[vid]["resultados_ordenados"].append("V")
                stats[lid]["resultados_ordenados"].append("D")

            else:
                # empate
                stats[lid]["puntos"] += 1
                stats[vid]["puntos"] += 1

                stats[lid]["empatados"] += 1
                stats[vid]["empatados"] += 1

                stats[lid]["resultados_ordenados"].append("E")
                stats[vid]["resultados_ordenados"].append("E")

        # 5. Calculamos racha (últimos 5 resultados)
        for club_id, s in stats.items():
            # últimos 5 resultados, empezando por el más reciente
            ultimos5 = s["resultados_ordenados"][-5:]
            racha = "".join(ultimos5)
            s["racha"] = racha

        # 6. Creamos una lista ordenable por clasificación
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

        # 7. Orden de la liga:
        #   - puntos DESC
        #   - diferencia de goles DESC
        #   - goles a favor DESC
        #   - nombre club ASC (estabilidad)
        clasificacion_lista.sort(
            key=lambda row: (
                -row["puntos"],
                -row["dif"],
                -row["gf"],
                row["club"].nombre_corto or row["club"].nombre_oficial,
            )
        )

        # 8. Guardamos en DB en ClubEnGrupo
        #    actualizamos (o creamos si no existe) la fila por club+grupo
        posicion = 1
        for row in clasificacion_lista:
            club = row["club"]
            obj, _created = ClubEnGrupo.objects.get_or_create(
                club=club,
                grupo=grupo,
            )

            obj.puntos = row["puntos"]
            obj.partidos_jugados = row["pj"]
            obj.victorias = stats[club.id]["ganados"]
            obj.empates = stats[club.id]["empatados"]
            obj.derrotas = stats[club.id]["perdidos"]
            obj.goles_favor = row["gf"]
            obj.goles_contra = row["gc"]
            obj.posicion_actual = posicion
            obj.racha = row["racha"]
            obj.diferencia_goles = row["dif"]

            obj.save()

            posicion += 1

        # 9. Guardar snapshot histórico de la jornada actual
        if partidos_jugados.exists():
            jornada_actual = partidos_jugados.aggregate(Max('jornada_numero'))['jornada_numero__max']
            
            if jornada_actual:
                # Crear/actualizar ClasificacionJornada
                clasif_jornada, created = ClasificacionJornada.objects.get_or_create(
                    grupo=grupo,
                    jornada=jornada_actual,
                    defaults={
                        'partidos_jugados_total': partidos_jugados.count(),
                        'equipos_participantes': len(clasificacion_lista),
                    }
                )
                
                if not created:
                    # Si ya existe, actualizar metadata
                    clasif_jornada.partidos_jugados_total = partidos_jugados.count()
                    clasif_jornada.equipos_participantes = len(clasificacion_lista)
                    clasif_jornada.save()
                
                # Borrar posiciones existentes (si se recalcula, regeneramos todo)
                PosicionJornada.objects.filter(clasificacion_jornada=clasif_jornada).delete()
                
                # Guardar posiciones
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
                
                # Bulk create para eficiencia
                PosicionJornada.objects.bulk_create(posiciones_a_crear)
                
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Histórico de jornada {jornada_actual} guardado correctamente"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"Clasificación recalculada y guardada para Grupo {grupo.id} ({grupo.nombre})"
        ))
