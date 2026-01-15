from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time
from django.utils import timezone

from clubes.models import ClubEnGrupo, Club
from nucleo.models import Grupo, Temporada
from partidos.models import Partido, EventoPartido
from jugadores.models import Jugador
from arbitros.models import ArbitrajePartido
from valoraciones.views import _coef_division_lookup, _get_temporada_id, _get_int, _abs_media

class ClasificacionMiniView(APIView):
    """
    GET /api/estadisticas/clasificacion-mini/?grupo_id=15
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grupo = Grupo.objects.select_related("competicion").get(id=grupo_id)
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        posiciones = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )

        # Ordenar por posición actual, usando 9999 para equipos sin posición (van al final)
        # Si hay empate en posición, ordenar por puntos descendente
        posiciones = sorted(
            posiciones,
            key=lambda row: (
                row.posicion_actual if row.posicion_actual is not None else 9999,
                -(row.puntos or 0),
            )
        )

        tabla = []
        for row in posiciones:
            raw_racha = getattr(row, "racha", "") or ""
            racha_list = list(raw_racha.strip().upper())[:5]

            club = row.club
            if club:
                nombre_club = getattr(club, "nombre_corto", None) or getattr(club, "nombre_oficial", "") or ""
                escudo = getattr(club, "escudo_url", "") or ""
            else:
                nombre_club = ""
                escudo = ""

            tabla.append({
                "pos": row.posicion_actual,
                "club_id": club.id if club else None,
                "nombre": nombre_club,
                "escudo": escudo,
                "slug": club.slug if club else None,
                "pj": row.partidos_jugados or 0,
                "puntos": row.puntos or 0,
                "racha": racha_list,
            })

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
            },
            "tabla": tabla,
        }

        return Response(payload, status=status.HTTP_200_OK)

class ResultadosJornadaView(APIView):
    """
    GET /api/estadisticas/resultados-jornada/?grupo_id=15
    GET /api/estadisticas/resultados-jornada/?grupo_id=15&jornada=6
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grupo = Grupo.objects.select_related("competicion", "temporada").get(id=grupo_id)
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
        )

        jornadas_disponibles = sorted(set(
            qs_partidos_grupo.values_list("jornada_numero", flat=True).distinct()
        ))

        if not jornadas_disponibles:
            return Response({
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": None,
                "jornadas_disponibles": [],
                "partidos": [],
            }, status=status.HTTP_200_OK)

        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response({"detail": "jornada debe ser número"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            jugadas = (
                qs_partidos_grupo
                .filter(jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
            )
            jugadas = sorted(set(jugadas))
            if jugadas:
                jornada_num = jugadas[-1]
            else:
                jornada_num = max(jornadas_disponibles)

        partidos_jornada = (
            qs_partidos_grupo
            .filter(jornada_numero=jornada_num)
            .order_by("fecha_hora", "id")
        )

        arbitrajes = (
            ArbitrajePartido.objects
            .filter(partido__in=partidos_jornada)
            .select_related("arbitro", "partido")
        )
        arbitros_por_partido = {}
        for arb in arbitrajes:
            pid = arb.partido_id
            arbitros_por_partido.setdefault(pid, [])
            if arb.arbitro and arb.arbitro.nombre:
                arbitros_por_partido[pid].append(arb.arbitro.nombre)

        partidos_payload = []
        for p in partidos_jornada:
            local = p.local
            visit = p.visitante

            # pabellón defensivo
            if getattr(p, "pabellon", None):
                pabellon = p.pabellon
            elif local and getattr(local, "pabellon", None):
                pabellon = local.pabellon
            else:
                pabellon = ""

            partidos_payload.append({
                "id": p.identificador_federacion or p.id,
                "jornada": p.jornada_numero,
                "jugado": p.jugado,
                "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
                "pabellon": pabellon,
                "arbitros": arbitros_por_partido.get(p.id, []),

                "local": {
                    "id": local.id if local else None,
                    "nombre": (getattr(local, "nombre_corto", None) or getattr(local, "nombre_oficial", "") or "") if local else "",
                    "escudo": getattr(local, "escudo_url", "") or "" if local else "",
                    "slug": local.slug if local else None,
                    "goles": p.goles_local if p.goles_local is not None else None,
                },
                "visitante": {
                    "id": visit.id if visit else None,
                    "nombre": (getattr(visit, "nombre_corto", None) or getattr(visit, "nombre_oficial", "") or "") if visit else "",
                    "escudo": getattr(visit, "escudo_url", "") or "" if visit else "",
                    "slug": visit.slug if visit else None,
                    "goles": p.goles_visitante if p.goles_visitante is not None else None,
                },
            })

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "jornadas_disponibles": jornadas_disponibles,
            "partidos": partidos_payload,
        }

        return Response(payload, status=status.HTTP_200_OK)
    
class GoleadoresJornadaView(APIView):
    """
    GET /api/estadisticas/goleadores-jornada/?grupo_id=15&jornada=6
    Devuelve ahora también:
      - club_escudo
      - pabellon
      - fecha_hora
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grupo = Grupo.objects.select_related("competicion", "temporada").get(id=grupo_id)
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Partidos del grupo
        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
        )

        # Jornadas disponibles
        jornadas_disponibles = sorted(set(
            qs_partidos_grupo.values_list("jornada_numero", flat=True).distinct()
        ))

        if not jornadas_disponibles:
            return Response({
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": None,
                "goleadores": [],
            }, status=status.HTTP_200_OK)

        # Jornada a usar
        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response({"detail": "jornada debe ser número"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            jugadas = (
                qs_partidos_grupo
                .filter(jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
            )
            jugadas = sorted(set(jugadas))
            if jugadas:
                jornada_num = jugadas[-1]
            else:
                jornada_num = max(jornadas_disponibles)

        # 👇 partidos concretos de esa jornada
        partidos_de_jornada = list(
            qs_partidos_grupo
            .filter(jornada_numero=jornada_num)
        )

        if not partidos_de_jornada:
            return Response({
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "goleadores": [],
            }, status=status.HTTP_200_OK)

        # Mapa rápido: club_id -> partido_de_esa_jornada.
        # En una jornada, cada club juega exactamente 1 partido, por lo que este mapa
        # permite acceso O(1) al partido de un club sin tener que iterar.
        partido_por_club = {}
        for p in partidos_de_jornada:
            # Pabellón: prioridad al pabellón específico del partido (puede diferir del del club).
            # Si no hay, usar el pabellón del club local como fallback.
            if getattr(p, "pabellon", None):
                pab = p.pabellon
            elif p.local and getattr(p.local, "pabellon", None):
                pab = p.local.pabellon
            else:
                pab = ""

            base_partido = {
                "partido_id": p.id,
                "pabellon": pab,
                "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
            }

            if p.local_id:
                partido_por_club[p.local_id] = base_partido
            if p.visitante_id:
                partido_por_club[p.visitante_id] = base_partido

        # ⬇️ Eventos de gol de ESA jornada
        eventos_gol = (
            EventoPartido.objects
            .filter(
                partido_id__in=[p.id for p in partidos_de_jornada],
                tipo_evento="gol",
                jugador__isnull=False,
                club__isnull=False,
            )
            .values("jugador_id", "club_id")
            .annotate(goles_jornada=Count("id"))
        )

        if not eventos_gol:
            return Response({
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "goleadores": [],
            }, status=status.HTTP_200_OK)

        # ⚽ goles del club en la liga (para % contribución) – igual que tenías
        partidos_validos_grupo = (
            Partido.objects.filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            )
            .values("local_id", "visitante_id", "goles_local", "goles_visitante")
        )

        goles_favor_por_club = {}
        for p in partidos_validos_grupo:
            gl = p["goles_local"] or 0
            gv = p["goles_visitante"] or 0
            lid = p["local_id"]
            vid = p["visitante_id"]
            goles_favor_por_club[lid] = goles_favor_por_club.get(lid, 0) + gl
            goles_favor_por_club[vid] = goles_favor_por_club.get(vid, 0) + gv

        # lookup de clasificación para nombre corto y posición
        clubs_ids = [row["club_id"] for row in eventos_gol]
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo, club_id__in=clubs_ids)
            .select_related("club")
        )
        clasif_lookup = {}
        for c in clasif_rows:
            goles_favor_guardado = c.goles_favor or 0
            goles_favor_calculado = goles_favor_por_club.get(c.club_id, 0)
            goles_favor_final = goles_favor_guardado or goles_favor_calculado

            clasif_lookup[c.club_id] = {
                "posicion_actual": c.posicion_actual if c.posicion_actual is not None else 9999,
                "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                "goles_favor": goles_favor_final,
                "club_escudo": c.club.escudo_url or "",   # 👈 AQUÍ el ESCUDO
                "slug": c.club.slug if c.club else None,
            }

        # lookup de jugadores
        jugadores_ids = [row["jugador_id"] for row in eventos_gol]
        jugadores_objs = Jugador.objects.filter(id__in=jugadores_ids)
        jugadores_lookup = {}
        for j in jugadores_objs:
            raw_rel = j.foto_url or ""
            if raw_rel:
                foto_final = raw_rel if raw_rel.startswith("/media/") else "/media/" + raw_rel.lstrip("/")
            else:
                foto_final = ""
            jugadores_lookup[j.id] = {
                "nombre": j.nombre,
                "apodo": j.apodo or "",
                "foto": foto_final,
            }

        # construir respuesta final
        goleadores_lista = []
        for row in eventos_gol:
            jug_id = row["jugador_id"]
            club_id = row["club_id"]
            goles_jornada = row["goles_jornada"]

            jugador_info = jugadores_lookup.get(jug_id, {})
            club_info = clasif_lookup.get(club_id, {
                "posicion_actual": 9999,
                "club_nombre": "",
                "goles_favor": 0,
                "club_escudo": "",
            })

            # 👇 partido de esa jornada donde jugó su club
            partido_info = partido_por_club.get(club_id, {
                "partido_id": None,
                "pabellon": "",
                "fecha_hora": None,
            })

            goles_equipo_total = club_info.get("goles_favor", 0)
            if goles_equipo_total > 0:
                contrib = (goles_jornada / goles_equipo_total) * 100.0
            else:
                contrib = 0.0

            goleadores_lista.append({
                "jugador_id": jug_id,
                "nombre": jugador_info.get("nombre", ""),
                "apodo": jugador_info.get("apodo", ""),
                "club_id": club_id,
                "club_nombre": club_info["club_nombre"],
                "club_escudo": club_info["club_escudo"],     # 👈 NUEVO
                "club_slug": club_info.get("slug"),
                "goles_jornada": goles_jornada,
                "goles_equipo_total": goles_equipo_total,
                "contribucion_pct": round(contrib),
                "club_posicion": club_info["posicion_actual"],
                "foto": jugador_info.get("foto", ""),
                "pabellon": partido_info["pabellon"],         # 👈 NUEVO
                "fecha_hora": partido_info["fecha_hora"],     # 👈 NUEVO
                "partido_id": partido_info["partido_id"],     # 👈 opcional pero útil
            })

        # ordenar igual que antes
        goleadores_lista.sort(
            key=lambda x: (
                -x["goles_jornada"],
                x["club_posicion"],
                x["nombre"].lower(),
            )
        )

        return Response({
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "goleadores": goleadores_lista,
        }, status=status.HTTP_200_OK)


class PichichiTemporadaView(APIView):
    """
    GET /api/estadisticas/pichichi-temporada/?grupo_id=15

    Ranking de máximos goleadores ACUMULADO en la temporada para ese grupo.

    Para cada jugador:
      - goles_total (acumulado en toda la liga)
      - goles_equipo_total (goles a favor totales del club en la liga)
      - contribucion_pct (porcentaje de los goles del equipo que son suyos)
      - foto
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")

        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Grupo
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Todos los partidos jugados con marcador válido
        partidos_grupo_jugados = list(
            Partido.objects.filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            ).values_list("id", flat=True)
        )

        if not partidos_grupo_jugados:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "goleadores": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 3. Eventos de gol (excluye propia puerta)
        eventos_gol = (
            EventoPartido.objects
            .filter(
                partido_id__in=partidos_grupo_jugados,
                tipo_evento="gol",
                jugador__isnull=False,
                club__isnull=False,
            )
            .values(
                "jugador_id",
                "club_id",
            )
            .annotate(goles_total=Count("id"))
        )
        # [{'jugador_id': 12, 'club_id': 3, 'goles_total': 7}, ...]

        if not eventos_gol:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "goleadores": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # === Helper: fallback para goles_favor si ClubEnGrupo no lo tiene bien ===
        # Calculamos todos los goles a favor por club en este grupo.
        partidos_validos_grupo = (
            Partido.objects.filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            )
            .values(
                "id",
                "local_id",
                "visitante_id",
                "goles_local",
                "goles_visitante",
            )
        )

        goles_favor_por_club = {}
        for p in partidos_validos_grupo:
            lid = p["local_id"]
            vid = p["visitante_id"]
            gl = p["goles_local"]
            gv = p["goles_visitante"]

            goles_favor_por_club[lid] = goles_favor_por_club.get(lid, 0) + (gl or 0)
            goles_favor_por_club[vid] = goles_favor_por_club.get(vid, 0) + (gv or 0)

        # 4. Lookup de club (posición, nombre, goles_favor)
        clubs_ids = [row["club_id"] for row in eventos_gol]
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo, club_id__in=clubs_ids)
            .select_related("club")
        )
        clasif_lookup = {}
        for c in clasif_rows:
            goles_favor_guardado = c.goles_favor or 0
            goles_favor_calculado = goles_favor_por_club.get(c.club_id, 0)
            goles_favor_final = goles_favor_guardado or goles_favor_calculado

            clasif_lookup[c.club_id] = {
                "posicion_actual": (
                    c.posicion_actual if c.posicion_actual is not None else 9999
                ),
                "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                "club_slug": c.club.slug or None,
                "goles_favor": goles_favor_final,
            }

        # 5. Lookup jugadores
        jugadores_ids = [row["jugador_id"] for row in eventos_gol]
        jugadores_objs = Jugador.objects.filter(id__in=jugadores_ids)
        jugadores_lookup = {}
        for j in jugadores_objs:
            raw_rel = j.foto_url or ""  # ej "jugadores/9812817.png"
            if raw_rel:
                if raw_rel.startswith("/media/"):
                    foto_final = raw_rel
                else:
                    foto_final = "/media/" + raw_rel.lstrip("/")
            else:
                foto_final = ""

            jugadores_lookup[j.id] = {
                "nombre": j.nombre,
                "apodo": j.apodo or "",
                "slug": getattr(j, "slug", None),
                "foto": foto_final,
            }

        # 6. Construir respuesta final
        goleadores_lista = []
        for row in eventos_gol:
            jug_id = row["jugador_id"]
            club_id = row["club_id"]
            goles_total = row["goles_total"]

            jugador_info = jugadores_lookup.get(jug_id, {})
            club_info = clasif_lookup.get(
                club_id,
                {
                    "posicion_actual": 9999,
                    "club_nombre": "",
                    "goles_favor": 0,
                },
            )

            goles_equipo_total = club_info.get("goles_favor", 0)
            contrib = 0.0
            if goles_equipo_total > 0:
                contrib = (goles_total / goles_equipo_total) * 100.0

            goleadores_lista.append({
                "jugador_id": jug_id,
                "nombre": jugador_info.get("nombre", ""),
                "apodo": jugador_info.get("apodo", ""),
                "slug": jugador_info.get("slug"),
                "club_id": club_id,
                "club_nombre": club_info["club_nombre"],
                "club_slug": club_info.get("club_slug"),

                "goles_total": goles_total,
                "goles_equipo_total": goles_equipo_total,
                "contribucion_pct": round(contrib),

                "club_posicion": club_info["posicion_actual"],
                "foto": jugador_info.get("foto", ""),
            })

        # 7. Orden ranking
        goleadores_lista.sort(
            key=lambda x: (
                -x["goles_total"],
                x["club_posicion"],
                x["nombre"].lower(),
            )
        )

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "goleadores": goleadores_lista,
        }

        return Response(payload, status=status.HTTP_200_OK)

class KPIsJornadaView(APIView):
    """
    GET /api/estadisticas/kpis-jornada/?grupo_id=15
    GET /api/estadisticas/kpis-jornada/?grupo_id=15&jornada=6

    Devuelve KPIs agregados de esa jornada dentro de un grupo concreto:

    {
      "grupo": {
        "id": ...,
        "nombre": "Grupo XV",
        "competicion": "Tercera División Nacional Futsal",
        "temporada": "2025/2026"
      },
      "jornada": 6,
      "stats": {
        "goles_totales": 42,
        "amarillas_totales": 19,
        "rojas_totales": 3,
        "victorias_local": 4,
        "empates": 1,
        "victorias_visitante": 2
      }
    }
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Buscar el grupo (incluimos competicion y temporada para el header)
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Partidos del grupo
        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
        )

        # 3. Jornadas existentes en este grupo
        jornadas_disponibles = sorted(set(
            qs_partidos_grupo.values_list("jornada_numero", flat=True).distinct()
        ))

        if not jornadas_disponibles:
            # No hay partidos cargados en este grupo
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": None,
                "stats": {
                    "goles_totales": 0,
                    "amarillas_totales": 0,
                    "rojas_totales": 0,
                    "victorias_local": 0,
                    "empates": 0,
                    "victorias_visitante": 0,
                },
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 4. Determinar qué jornada usar
        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response(
                    {"detail": "jornada debe ser número"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # misma lógica que ResultadosJornadaView
            jugadas = (
                qs_partidos_grupo
                .filter(jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
            )
            jugadas = sorted(set(jugadas))
            if jugadas:
                jornada_num = jugadas[-1]  # última jornada jugada
            else:
                jornada_num = max(jornadas_disponibles)  # la más alta disponible (la próxima)

        # 5. Partidos concretos de esa jornada
        partidos_de_jornada = list(
            qs_partidos_grupo
            .filter(jornada_numero=jornada_num)
        )

        if not partidos_de_jornada:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "stats": {
                    "goles_totales": 0,
                    "amarillas_totales": 0,
                    "rojas_totales": 0,
                    "victorias_local": 0,
                    "empates": 0,
                    "victorias_visitante": 0,
                },
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # IDs de esos partidos para filtrar eventos
        partido_ids = [p.id for p in partidos_de_jornada]

        # 6. KPI: goles_totales y resultados
        goles_totales = 0
        vict_local = 0
        vict_visit = 0
        empates = 0

        for p in partidos_de_jornada:
            # solo contamos marcador si está jugado y tiene goles válidos
            if (
                p.jugado
                and p.goles_local is not None
                and p.goles_visitante is not None
            ):
                gl = p.goles_local or 0
                gv = p.goles_visitante or 0
                goles_totales += (gl + gv)

                if gl > gv:
                    vict_local += 1
                elif gv > gl:
                    vict_visit += 1
                else:
                    empates += 1

        # 7. KPI: tarjetas amarillas / rojas
        #    - amarillas_totales: tipo_evento="amarilla"
        #    - rojas_totales: tipo_evento="roja" o "doble_amarilla"
        eventos_disciplina = (
            EventoPartido.objects
            .filter(partido_id__in=partido_ids)
            .values("tipo_evento")
            .annotate(cnt=Count("id"))
        )

        amarillas_totales = 0
        rojas_totales = 0

        for ev in eventos_disciplina:
            tipo = ev["tipo_evento"]
            cnt = ev["cnt"] or 0
            if tipo == "amarilla":
                amarillas_totales += cnt
            elif tipo in ("roja", "doble_amarilla"):
                rojas_totales += cnt

        # 8. Montar payload final
        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "stats": {
                "goles_totales": goles_totales,
                "amarillas_totales": amarillas_totales,
                "rojas_totales": rojas_totales,
                "victorias_local": vict_local,
                "empates": empates,
                "victorias_visitante": vict_visit,
            },
        }

        return Response(payload, status=status.HTTP_200_OK)

class GolesPorEquipoView(APIView):
    """
    GET /api/estadisticas/goles-por-equipo/?grupo_id=15

    Devuelve ranking ofensivo de los equipos del grupo:
    - goles_total
    - media goles por partido
    - goles_local / goles_visitante
    - goles 1ª parte / goles 2ª parte
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")

        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Grupo
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Partidos válidos: jugados y con marcador
        partidos_grupo = (
            Partido.objects
            .filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            )
            .select_related("local", "visitante")
            .values(
                "id",
                "local_id",
                "visitante_id",
                "goles_local",
                "goles_visitante",
            )
        )
        # partidos_grupo = [
        #   { "id": 123, "local_id": 5, "visitante_id": 9, "goles_local": 4, "goles_visitante": 2 },
        #   ...
        # ]

        if not partidos_grupo:
            # No hay partidos jugados aún
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "equipos": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 3. Inicializamos stats por club
        #    Vamos a ir rellenando todo aquí y luego convertimos a lista
        clubes_stats = {}
        # estructura intermedia:
        # clubes_stats[club_id] = {
        #   "club_id": ...,
        #   "goles_total": 0,
        #   "goles_local": 0,
        #   "goles_visitante": 0,
        #   "goles_1parte": 0,
        #   "goles_2parte": 0,
        #   "partidos_jugados": 0,
        # }

        # 4. Recorrer cada partido para acumular:
        #    - GF local para el local
        #    - GF visitante para el visitante
        #    - sumar partidos jugados a ambos
        partido_ids = []
        for p in partidos_grupo:
            partido_ids.append(p["id"])

            local_id = p["local_id"]
            visit_id = p["visitante_id"]
            gl = p["goles_local"] or 0
            gv = p["goles_visitante"] or 0

            if local_id not in clubes_stats:
                clubes_stats[local_id] = {
                    "club_id": local_id,
                    "goles_total": 0,
                    "goles_local": 0,
                    "goles_visitante": 0,
                    "goles_1parte": 0,
                    "goles_2parte": 0,
                    "partidos_jugados": 0,
                }
            if visit_id not in clubes_stats:
                clubes_stats[visit_id] = {
                    "club_id": visit_id,
                    "goles_total": 0,
                    "goles_local": 0,
                    "goles_visitante": 0,
                    "goles_1parte": 0,
                    "goles_2parte": 0,
                    "partidos_jugados": 0,
                }

            # goles totales y split local/visitante
            clubes_stats[local_id]["goles_total"] += gl
            clubes_stats[local_id]["goles_local"] += gl

            clubes_stats[visit_id]["goles_total"] += gv
            clubes_stats[visit_id]["goles_visitante"] += gv

            # partidos jugados suman para ambos
            clubes_stats[local_id]["partidos_jugados"] += 1
            clubes_stats[visit_id]["partidos_jugados"] += 1

        # 5. Goles por parte usando EventoPartido (minuto)
        #    Solo tipo_evento gol NORMAL ("gol"), y club no nulo.
        #    (Si quieres incluir goles en propia puerta a favor del rival habría que decidir:
        #     tipo_evento="gol_pp". Por ahora seguimos tu misma filosofía de pichichi: ignorar "gol_pp").
        eventos_gol_por_parte = (
            EventoPartido.objects
            .filter(
                partido_id__in=partido_ids,
                tipo_evento="gol",
                club__isnull=False,
            )
            .values("club_id", "minuto")
        )

        for ev in eventos_gol_por_parte:
            cid = ev["club_id"]
            minuto = ev["minuto"] or None

            if cid not in clubes_stats:
                # puede pasar si por algún bug hay evento de un club que no hemos metido arriba,
                # pero lo normal es que ya exista
                clubes_stats[cid] = {
                    "club_id": cid,
                    "goles_total": 0,
                    "goles_local": 0,
                    "goles_visitante": 0,
                    "goles_1parte": 0,
                    "goles_2parte": 0,
                    "partidos_jugados": 0,
                }

            if minuto is not None:
                if 1 <= minuto <= 20:
                    clubes_stats[cid]["goles_1parte"] += 1
                elif 21 <= minuto <= 40:
                    clubes_stats[cid]["goles_2parte"] += 1
                else:
                    # minutos raros (prórroga, portero-jugador 40+ etc.). 
                    # De momento no los metemos ni en 1ª ni en 2ª parte.
                    pass

        # 6. Lookup de info del club para nombre y escudo
        club_ids = list(clubes_stats.keys())
        # usamos ClubEnGrupo para sacar nombre corto y escudo
        club_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo, club_id__in=club_ids)
            .select_related("club")
        )

        club_info_lookup = {}
        for c in club_rows:
            club_info_lookup[c.club.id] = {
                "nombre": c.club.nombre_corto or c.club.nombre_oficial,
                "escudo": c.club.escudo_url or "",
                "slug": c.club.slug or None,
            }

        # 7. Construir lista final para respuesta
        equipos_list = []
        for cid, stats in clubes_stats.items():
            pj = stats["partidos_jugados"] or 0
            goles_totales = stats["goles_total"] or 0
            media = 0.0
            if pj > 0:
                media = goles_totales / pj

            info = club_info_lookup.get(cid, {"nombre": "", "escudo": "", "slug": None})

            equipos_list.append({
                "club_id": cid,
                "club_nombre": info["nombre"],
                "club_escudo": info["escudo"],
                "club_slug": info.get("slug"),

                "partidos_jugados": pj,

                "goles_total": goles_totales,
                "goles_por_partido": round(media, 2),

                "goles_local": stats["goles_local"],
                "goles_visitante": stats["goles_visitante"],

                "goles_1parte": stats["goles_1parte"],
                "goles_2parte": stats["goles_2parte"],
            })

        # 8. Ordenar por potencia ofensiva (goles_total DESC, luego media DESC)
        equipos_list.sort(
            key=lambda row: (-row["goles_total"], -row["goles_por_partido"], row["club_nombre"].lower())
        )

        # 9. Payload final
        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "equipos": equipos_list,
        }

        return Response(payload, status=status.HTTP_200_OK)

class SancionesJornadaView(APIView):
    """
    GET /api/estadisticas/sanciones-jornada/?grupo_id=15
    GET /api/estadisticas/sanciones-jornada/?grupo_id=15&jornada=6

    Devuelve los jugadores sancionados en ESA jornada del grupo,
    ordenados por severidad de la sanción:
    - roja (5 pts)
    - doble_amarilla (3 pts)
    - amarilla (1 pt)

    Respuesta:
    {
      "grupo": {...},
      "jornada": 6,
      "sancionados": [
        {
          "jugador_id": ...,
          "nombre": "...",
          "apodo": "...",
          "foto": "/media/...",
          "club_id": ...,
          "club_nombre": "...",

          "amarillas": 2,
          "dobles_amarillas": 1,
          "rojas": 0,

          "severidad_puntos": 5*rojas + 3*dobles + 1*amarillas
        },
        ...
      ]
    }
    (máx 10 jugadores)
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Grupo
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Partidos del grupo
        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
        )

        # Jornadas disponibles
        jornadas_disponibles = sorted(set(
            qs_partidos_grupo
            .values_list("jornada_numero", flat=True)
            .distinct()
        ))

        if not jornadas_disponibles:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": None,
                "sancionados": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # Determinar jornada_num (misma lógica que ResultadosJornadaView)
        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response(
                    {"detail": "jornada debe ser número"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            jugadas = (
                qs_partidos_grupo
                .filter(jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
            )
            jugadas = sorted(set(jugadas))
            if jugadas:
                jornada_num = jugadas[-1]  # última jornada jugada
            else:
                jornada_num = max(jornadas_disponibles)  # próxima

        # 3. Partidos concretos de esa jornada
        partidos_de_jornada_ids = list(
            qs_partidos_grupo
            .filter(jornada_numero=jornada_num)
            .values_list("id", flat=True)
        )

        if not partidos_de_jornada_ids:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "sancionados": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 4. Eventos disciplinarios de ESA jornada (amarilla, doble_amarilla, roja)
        eventos_disciplina = (
            EventoPartido.objects
            .filter(
                partido_id__in=partidos_de_jornada_ids,
                tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                jugador__isnull=False,
                club__isnull=False,
            )
            .values(
                "jugador_id",
                "club_id",
                "tipo_evento",
            )
            .annotate(cnt=Count("id"))
        )
        # formato intermedio:
        # [{"jugador_id":1,"club_id":10,"tipo_evento":"roja","cnt":1}, ...]

        if not eventos_disciplina:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "sancionados": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 5. Agregamos por jugador+club
        sanciones_por_jugador = {}
        for ev in eventos_disciplina:
            jid = ev["jugador_id"]
            cid = ev["club_id"]
            tipo = ev["tipo_evento"]
            cnt = ev["cnt"] or 0

            key = (jid, cid)
            if key not in sanciones_por_jugador:
                sanciones_por_jugador[key] = {
                    "jugador_id": jid,
                    "club_id": cid,
                    "amarillas": 0,
                    "dobles_amarillas": 0,
                    "rojas": 0,
                }

            if tipo == "amarilla":
                sanciones_por_jugador[key]["amarillas"] += cnt
            elif tipo == "doble_amarilla":
                sanciones_por_jugador[key]["dobles_amarillas"] += cnt
            elif tipo == "roja":
                sanciones_por_jugador[key]["rojas"] += cnt

        # 6. Calculamos severidad
        for key, data_row in sanciones_por_jugador.items():
            puntos = (
                5 * data_row["rojas"]
                + 3 * data_row["dobles_amarillas"]
                + 1 * data_row["amarillas"]
            )
            data_row["severidad_puntos"] = puntos

        # 7. Lookups de jugadores y clubs
        jugador_ids = [k[0] for k in sanciones_por_jugador.keys()]
        club_ids = [k[1] for k in sanciones_por_jugador.keys()]

        jugadores_objs = (
            Jugador.objects
            .filter(id__in=jugador_ids)
        )
        jugadores_lookup = {}
        for j in jugadores_objs:
            raw_rel = j.foto_url or ""
            if raw_rel:
                if raw_rel.startswith("/media/"):
                    foto_final = raw_rel
                else:
                    foto_final = "/media/" + raw_rel.lstrip("/")
            else:
                foto_final = ""
            jugadores_lookup[j.id] = {
                "nombre": j.nombre,
                "apodo": j.apodo or "",
                "foto": foto_final,
                "slug": getattr(j, "slug", None),
            }

        # usamos ClubEnGrupo para pillar nombre corto del club dentro del grupo
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo, club_id__in=club_ids)
            .select_related("club")
        )
        clubs_lookup = {}
        for c in clasif_rows:
            clubs_lookup[c.club_id] = {
                "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
            }

        # 8. Montamos la lista
        sancionados_lista = []
        for (jid, cid), rowdata in sanciones_por_jugador.items():
            jugador_info = jugadores_lookup.get(jid, {})
            club_info = clubs_lookup.get(cid, {"club_nombre": ""})

            sancionados_lista.append({
                "jugador_id": jid,
                "nombre": jugador_info.get("nombre", ""),
                "apodo": jugador_info.get("apodo", ""),
                "foto": jugador_info.get("foto", ""),
                "slug": jugador_info.get("slug"),

                "club_id": cid,
                "club_nombre": club_info["club_nombre"],

                "amarillas": rowdata["amarillas"],
                "dobles_amarillas": rowdata["dobles_amarillas"],
                "rojas": rowdata["rojas"],

                "severidad_puntos": rowdata["severidad_puntos"],
            })

        # 9. Orden:
        #   primero más severo:
        #   - por tener roja/doble_amarilla/amarilla (puntos altos)
        #   - y luego por nombre
        sancionados_lista.sort(
            key=lambda x: (
                -x["severidad_puntos"],
                -x["rojas"],
                -x["dobles_amarillas"],
                -x["amarillas"],
                x["nombre"].lower(),
            )
        )

        # top10
        sancionados_lista = sancionados_lista[:12]

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "sancionados": sancionados_lista,
        }

        return Response(payload, status=status.HTTP_200_OK)


class SancionesJugadoresAcumuladoView(APIView):
    """
    GET /api/estadisticas/sanciones-jugadores/?grupo_id=15

    Ranking acumulado de jugadores más sancionados en la temporada.

    Puntuación disciplina:
    roja = 5
    doble_amarilla = 3
    amarilla = 1

    Respuesta:
    {
      "grupo": {...},
      "jugadores": [
        {
          "jugador_id": ...,
          "nombre": "...",
          "apodo": "...",
          "foto": "...",
          "club_id": ...,
          "club_nombre": "...",

          "amarillas": 4,
          "dobles_amarillas": 1,
          "rojas": 2,
          "puntos_disciplina": 5*rojas + 3*dobles + 1*amarillas
        },
        ...
      ]
    }
    (máx 10)
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")

        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Grupo
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Partidos válidos del grupo (jugados con marcador, como referencia de que ya se disputaron)
        partidos_ids = list(
            Partido.objects.filter(
                grupo=grupo,
                jugado=True,
            ).values_list("id", flat=True)
        )

        if not partidos_ids:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jugadores": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 3. Eventos disciplinarios acumulados
        eventos_disciplina = (
            EventoPartido.objects
            .filter(
                partido_id__in=partidos_ids,
                tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                jugador__isnull=False,
                club__isnull=False,
            )
            .values("jugador_id", "club_id", "tipo_evento")
            .annotate(cnt=Count("id"))
        )

        if not eventos_disciplina:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jugadores": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 4. Agregamos por jugador
        sanciones_por_jugador = {}
        for ev in eventos_disciplina:
            jid = ev["jugador_id"]
            cid = ev["club_id"]
            tipo = ev["tipo_evento"]
            cnt = ev["cnt"] or 0

            if jid not in sanciones_por_jugador:
                sanciones_por_jugador[jid] = {
                    "jugador_id": jid,
                    "club_id": cid,  # OJO: si el jugador ha jugado en varios clubs en la misma temporada cambiar esto si hace falta
                    "amarillas": 0,
                    "dobles_amarillas": 0,
                    "rojas": 0,
                }

            if tipo == "amarilla":
                sanciones_por_jugador[jid]["amarillas"] += cnt
            elif tipo == "doble_amarilla":
                sanciones_por_jugador[jid]["dobles_amarillas"] += cnt
            elif tipo == "roja":
                sanciones_por_jugador[jid]["rojas"] += cnt

        # 5. Calcular puntos disciplina
        for jid, rowdata in sanciones_por_jugador.items():
            puntos = (
                5 * rowdata["rojas"]
                + 3 * rowdata["dobles_amarillas"]
                + 1 * rowdata["amarillas"]
            )
            rowdata["puntos_disciplina"] = puntos

        # 6. Lookups jugador y club
        jugador_ids = list(sanciones_por_jugador.keys())
        jugadores_objs = Jugador.objects.filter(id__in=jugador_ids)
        jugadores_lookup = {}
        for j in jugadores_objs:
            raw_rel = j.foto_url or ""
            if raw_rel:
                if raw_rel.startswith("/media/"):
                    foto_final = raw_rel
                else:
                    foto_final = "/media/" + raw_rel.lstrip("/")
            else:
                foto_final = ""
            jugadores_lookup[j.id] = {
                "nombre": j.nombre,
                "apodo": j.apodo or "",
                "foto": foto_final,
                "slug": getattr(j, "slug", None),
            }

        club_ids = [row["club_id"] for row in sanciones_por_jugador.values()]
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo, club_id__in=club_ids)
            .select_related("club")
        )
        clubs_lookup = {}
        for c in clasif_rows:
            clubs_lookup[c.club_id] = {
                "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
            }

        # 7. Montar lista final
        jugadores_lista = []
        for jid, rowdata in sanciones_por_jugador.items():
            jugador_info = jugadores_lookup.get(jid, {})
            club_info = clubs_lookup.get(
                rowdata["club_id"],
                {"club_nombre": ""},
            )

            jugadores_lista.append({
                "jugador_id": jid,
                "nombre": jugador_info.get("nombre", ""),
                "apodo": jugador_info.get("apodo", ""),
                "slug": jugador_info.get("slug"),
                "foto": jugador_info.get("foto", ""),

                "club_id": rowdata["club_id"],
                "club_nombre": club_info["club_nombre"],
                "club_slug": club_info.get("slug"),

                "amarillas": rowdata["amarillas"],
                "dobles_amarillas": rowdata["dobles_amarillas"],
                "rojas": rowdata["rojas"],
                "puntos_disciplina": rowdata["puntos_disciplina"],
            })

        # 8. Ordenamos: más conflictivos arriba
        jugadores_lista.sort(
            key=lambda x: (
                -x["puntos_disciplina"],
                -x["rojas"],
                -x["dobles_amarillas"],
                -x["amarillas"],
                x["nombre"].lower(),
            )
        )

        # top10
        jugadores_lista = jugadores_lista[:12]

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jugadores": jugadores_lista,
        }

        return Response(payload, status=status.HTTP_200_OK)


class FairPlayEquiposView(APIView):
    """
    GET /api/estadisticas/fair-play-equipos/?grupo_id=15

    Ranking de fair play entre equipos (menos puntos = mejor comportamiento)

    puntos_fair_play = 5*rojas + 3*doble_amarilla + 1*amarilla

    Respuesta:
    {
      "grupo": {...},
      "equipos": [
        {
          "club_id": ...,
          "club_nombre": "...",
          "club_escudo": "...",

          "amarillas": 10,
          "dobles_amarillas": 2,
          "rojas": 1,

          "puntos_fair_play": 5*rojas + 3*dobles + 1*amarillas
        },
        ...
      ]
    }

    Orden ASC por puntos_fair_play (el más limpio primero)
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")

        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Grupo
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Partidos válidos del grupo (jugados=True)
        partidos_ids = list(
            Partido.objects.filter(
                grupo=grupo,
                jugado=True,
            ).values_list("id", flat=True)
        )

        if not partidos_ids:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "equipos": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 3. Eventos disciplinarios acumulados por club
        eventos_disciplina = (
            EventoPartido.objects
            .filter(
                partido_id__in=partidos_ids,
                tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                club__isnull=False,
            )
            .values("club_id", "tipo_evento")
            .annotate(cnt=Count("id"))
        )

        if not eventos_disciplina:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "equipos": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 4. Agregamos por club
        sanciones_por_club = {}
        for ev in eventos_disciplina:
            cid = ev["club_id"]
            tipo = ev["tipo_evento"]
            cnt = ev["cnt"] or 0

            if cid not in sanciones_por_club:
                sanciones_por_club[cid] = {
                    "club_id": cid,
                    "amarillas": 0,
                    "dobles_amarillas": 0,
                    "rojas": 0,
                }

            if tipo == "amarilla":
                sanciones_por_club[cid]["amarillas"] += cnt
            elif tipo == "doble_amarilla":
                sanciones_por_club[cid]["dobles_amarillas"] += cnt
            elif tipo == "roja":
                sanciones_por_club[cid]["rojas"] += cnt

        # 5. Calcular puntos fair play
        for cid, rowdata in sanciones_por_club.items():
            puntos = (
                5 * rowdata["rojas"]
                + 3 * rowdata["dobles_amarillas"]
                + 1 * rowdata["amarillas"]
            )
            rowdata["puntos_fair_play"] = puntos

        # 6. Lookup club info (nombre y escudo para pintar frontend)
        club_ids = list(sanciones_por_club.keys())
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo, club_id__in=club_ids)
            .select_related("club")
        )
        clubs_lookup = {}
        for c in clasif_rows:
            clubs_lookup[c.club_id] = {
                "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                "club_escudo": c.club.escudo_url or "",
                "slug": c.club.slug if c.club else None,
            }

        # 7. Montar lista final
        equipos_lista = []
        for cid, rowdata in sanciones_por_club.items():
            club_info = clubs_lookup.get(
                cid,
                {"club_nombre": "", "club_escudo": ""},
            )

            equipos_lista.append({
                "club_id": cid,
                "club_nombre": club_info["club_nombre"],
                "club_escudo": club_info["club_escudo"],
                "club_slug": club_info.get("slug"),

                "amarillas": rowdata["amarillas"],
                "dobles_amarillas": rowdata["dobles_amarillas"],
                "rojas": rowdata["rojas"],
                "puntos_fair_play": rowdata["puntos_fair_play"],
            })

        # 8. Orden ascendente (menos puntos = más limpio)
        equipos_lista.sort(
            key=lambda x: (
                x["puntos_fair_play"],
                x["rojas"],
                x["dobles_amarillas"],
                x["amarillas"],
                x["club_nombre"].lower(),
            )
        )

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "equipos": equipos_lista,
        }

        return Response(payload, status=status.HTTP_200_OK)


class ClasificacionCompletaView(APIView):
    """
    GET /api/estadisticas/clasificacion-completa/?grupo_id=15&scope=overall|home|away&jornada=6

    - scope=overall -> todos los partidos (hasta la jornada indicada)
    - scope=home    -> solo partidos como local
    - scope=away    -> solo partidos como visitante

    Además ahora devolvemos, por cada club:
      - racha: lista de resultados en orden cronológico hasta esa jornada,
               ej: ["V","V","E","D","V"]
               (NO limitamos a 5, se devuelven todos)
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        scope = (request.GET.get("scope") or "overall").lower()
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. grupo
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. filas base (clubes inscritos en el grupo)
        filas = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )

        # 3. partidos jugados con marcador
        partidos_qs = (
            Partido.objects
            .filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            )
            .select_related("local", "visitante")
            .order_by("jornada_numero", "fecha_hora", "id")
        )

        # 4. jornadas disponibles
        jornadas_disponibles = sorted(
            set(
                partidos_qs.values_list("jornada_numero", flat=True)
            )
        )

        # ⬇️ CASO SIN PARTIDOS: devolvemos lo que hay en ClubEnGrupo y APROVECHAMOS su racha
        if not jornadas_disponibles:
            resultado = []
            for c in filas:
                # aquí intentamos sacar racha del modelo, igual que en la mini
                raw_racha = getattr(c, "racha", "") or ""
                racha_list = list(raw_racha.strip().upper())  # aquí NO recortamos

                resultado.append({
                    "club_id": c.club_id,
                    "nombre": (getattr(c.club, "nombre_corto", None) or getattr(c.club, "nombre_oficial", "")) if c.club else "",
                    "escudo": getattr(c.club, "escudo_url", "") or "",
                    "slug": c.club.slug if c.club else None,
                    "pj": c.partidos_jugados or 0,
                    "pg": c.partidos_ganados or 0,
                    "pe": c.partidos_empatados or 0,
                    "pp": c.partidos_perdidos or 0,
                    "gf": c.goles_favor or 0,
                    "gc": c.goles_contra or 0,
                    "dg": (c.goles_favor or 0) - (c.goles_contra or 0),
                    "puntos": c.puntos or 0,
                    "racha": racha_list,  # 👈 NUEVO
                })


            resultado.sort(
                key=lambda r: (
                    -r["puntos"],
                    -r["dg"],
                    -r["gf"],
                    r["nombre"].lower(),
                )
            )

            payload = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "scope": scope,
                "jornadas_disponibles": [],
                "jornada_aplicada": None,
                "tabla": resultado,
            }
            return Response(payload, status=status.HTTP_200_OK)

        # 5. determinar jornada a aplicar
        if jornada_param:
            try:
                jornada_aplicada = int(jornada_param)
            except ValueError:
                return Response(
                    {"detail": "jornada debe ser número"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if jornada_aplicada not in jornadas_disponibles:
                jornada_aplicada = jornadas_disponibles[-1]
        else:
            jornada_aplicada = jornadas_disponibles[-1]

        # 6. diccionario inicial de stats
        # 👇 puntos = 0 siempre; racha la iremos rellenando luego
        stats_por_club = {}
        for c in filas:
            stats_por_club[c.club_id] = {
                "club_id": c.club_id,
                "nombre": c.club.nombre_corto or c.club.nombre_oficial,
                "escudo": c.club.escudo_url or "",
                "slug": c.club.slug or None,
                "pj": 0,
                "pg": 0,
                "pe": 0,
                "pp": 0,
                "gf": 0,
                "gc": 0,
                "dg": 0,
                "puntos": 0,
                "racha": [],    # 👈 AQUÍ la dejamos lista
            }

        # 7. filtrar partidos hasta la jornada elegida
        partidos_hasta_jornada = [
            p for p in partidos_qs if p.jornada_numero <= jornada_aplicada
        ]

        # vamos a recorrerlos en orden y a ir metiendo la letra de resultado
        for p in partidos_hasta_jornada:
            local_id = p.local_id
            visit_id = p.visitante_id
            gl = p.goles_local or 0
            gv = p.goles_visitante or 0

            # asegurar que existen en el dict (por si hay partido con club no inscrito)
            if local_id not in stats_por_club:
                stats_por_club[local_id] = {
                    "club_id": local_id,
                    "nombre": p.local.nombre_corto or p.local.nombre_oficial,
                    "escudo": p.local.escudo_url or "",
                    "slug": p.local.slug if p.local else None,
                    "pj": 0,
                    "pg": 0,
                    "pe": 0,
                    "pp": 0,
                    "gf": 0,
                    "gc": 0,
                    "dg": 0,
                    "puntos": 0,
                    "racha": [],
                }
            if visit_id not in stats_por_club:
                stats_por_club[visit_id] = {
                    "club_id": visit_id,
                    "nombre": p.visitante.nombre_corto or p.visitante.nombre_oficial,
                    "escudo": p.visitante.escudo_url or "",
                    "slug": p.visitante.slug if p.visitante else None,
                    "pj": 0,
                    "pg": 0,
                    "pe": 0,
                    "pp": 0,
                    "gf": 0,
                    "gc": 0,
                    "dg": 0,
                    "puntos": 0,
                    "racha": [],
                }

            # === aplicar scope + construir racha ===
            # OVERALL cuenta los dos
            # HOME solo local
            # AWAY solo visitante

            # resultado real del partido (para racha)
            # local
            if scope in ("overall", "home"):
                stats_por_club[local_id]["pj"] += 1
                stats_por_club[local_id]["gf"] += gl
                stats_por_club[local_id]["gc"] += gv

                if gl > gv:
                    stats_por_club[local_id]["pg"] += 1
                    stats_por_club[local_id]["puntos"] += 3
                    stats_por_club[local_id]["racha"].append("V")
                elif gl == gv:
                    stats_por_club[local_id]["pe"] += 1
                    stats_por_club[local_id]["puntos"] += 1
                    stats_por_club[local_id]["racha"].append("E")
                else:
                    stats_por_club[local_id]["pp"] += 1
                    stats_por_club[local_id]["racha"].append("D")

            # visitante
            if scope in ("overall", "away"):
                stats_por_club[visit_id]["pj"] += 1
                stats_por_club[visit_id]["gf"] += gv
                stats_por_club[visit_id]["gc"] += gl

                if gv > gl:
                    stats_por_club[visit_id]["pg"] += 1
                    stats_por_club[visit_id]["puntos"] += 3
                    stats_por_club[visit_id]["racha"].append("V")
                elif gv == gl:
                    stats_por_club[visit_id]["pe"] += 1
                    stats_por_club[visit_id]["puntos"] += 1
                    stats_por_club[visit_id]["racha"].append("E")
                else:
                    stats_por_club[visit_id]["pp"] += 1
                    stats_por_club[visit_id]["racha"].append("D")

        # 8. calcular DG y pasar a lista
        resultado = []
        for cid, row in stats_por_club.items():
            row["dg"] = row["gf"] - row["gc"]
            resultado.append(row)

        # 9. ordenar
        resultado.sort(
            key=lambda r: (
                -r["puntos"],
                -r["dg"],
                -r["gf"],
                r["nombre"].lower(),
            )
        )

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "scope": scope,
            "jornadas_disponibles": jornadas_disponibles,
            "jornada_aplicada": jornada_aplicada,
            "tabla": resultado,
        }

        return Response(payload, status=status.HTTP_200_OK)


class ClasificacionEvolucionView(APIView):
    """
    GET /api/estadisticas/clasificacion-evolucion/?grupo_id=15
    GET /api/estadisticas/clasificacion-evolucion/?grupo_id=15&parameter=pts
    GET /api/estadisticas/clasificacion-evolucion/?grupo_id=15&scope=home

    Devuelve, por club, la serie jornada→valor para pintar líneas.
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        scope = (request.GET.get("scope") or "overall").lower()
        param = request.GET.get("parameter") or "pts"   # pts | gf | gc

        try:
            grupo = Grupo.objects.select_related("competicion", "temporada").get(id=grupo_id)
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        partidos = (
            Partido.objects
            .filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            )
            .select_related("local", "visitante")
            .order_by("jornada_numero", "fecha_hora", "id")
        )

        # jornadas existentes
        jornadas = sorted(set(p.jornada_numero for p in partidos))

        # clubs en el grupo
        club_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )
        # estructura: series[club_id] = { "club_nombre": ..., "data": [ (jornada, valor) ... ] }
        series = {}
        for cr in club_rows:
            series[cr.club_id] = {
                "club_id": cr.club_id,
                "club_nombre": cr.club.nombre_corto or cr.club.nombre_oficial,
                "club_escudo": cr.club.escudo_url or "",
                "values": {},   # jornada -> valor acumulado
            }

        # acumuladores jornada a jornada
        # usamos dict: acc[club_id] = {"pts":0,"gf":0,"gc":0}
        acc = {cid: {"pts": 0, "gf": 0, "gc": 0} for cid in series.keys()}

        for j in jornadas:
            # partidos de esta jornada
            part_j = [p for p in partidos if p.jornada_numero == j]

            for p in part_j:
                gl = p.goles_local or 0
                gv = p.goles_visitante or 0

                # local
                if scope in ("overall", "home"):
                    acc[p.local_id]["gf"] += gl
                    acc[p.local_id]["gc"] += gv
                    if gl > gv:
                        acc[p.local_id]["pts"] += 3
                    elif gl == gv:
                        acc[p.local_id]["pts"] += 1
                # visitante
                if scope in ("overall", "away"):
                    acc[p.visitante_id]["gf"] += gv
                    acc[p.visitante_id]["gc"] += gl
                    if gv > gl:
                        acc[p.visitante_id]["pts"] += 3
                    elif gv == gl:
                        acc[p.visitante_id]["pts"] += 1

            # una vez procesada la jornada j, guardamos el estado para todos
            for cid in series.keys():
                series[cid]["values"][j] = {
                    "pts": acc[cid]["pts"],
                    "gf": acc[cid]["gf"],
                    "gc": acc[cid]["gc"],
                }

        # lo llevamos a formato fácil para el frontend
        out_series = []
        for cid, row in series.items():
            puntos = []
            for j in jornadas:
                val = row["values"].get(j, {"pts": 0, "gf": 0, "gc": 0})
                puntos.append({
                    "jornada": j,
                    "value": val.get(param, 0),
                })

            out_series.append({
                "club_id": cid,
                "club_nombre": row["club_nombre"],
                "club_escudo": row["club_escudo"],
                "parameter": param,
                "data": puntos,
            })

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornadas": jornadas,
            "parameter": param,
            "scope": scope,
            "series": out_series,
        }

        return Response(payload, status=status.HTTP_200_OK)


class GoleadoresGlobalOptimizedView(APIView):
    """
    GET /api/estadisticas/goleadores-global-optimized/?temporada_id=4&from=2025-11-24&to=2025-11-30&top=200
    
    Ranking global de goleadores de todas las divisiones de la temporada, con opción de filtrar por ventana de fechas.
    Aplica coeficientes de división a los goles (goles * coef_division * 3.1416 = puntos).
    """
    
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6
    
    def _parse_date(self, s: str | None):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None
    
    def get(self, request, format=None):
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        top_n = _get_int(request, "top", 200)
        from_date = self._parse_date(request.GET.get("from"))
        to_date = self._parse_date(request.GET.get("to"))
        
        # Obtener coeficientes de división
        coef_division = _coef_division_lookup(temporada_id, self.JORNADA_REF_COEF)
        
        # Partidos de toda la temporada (para totales)
        partidos_temporada_qs = Partido.objects.filter(
            grupo__temporada_id=temporada_id,
            jugado=True
        ).select_related("grupo__competicion")
        
        partidos_temporada_ids = list(partidos_temporada_qs.values_list("id", flat=True))
        
        if not partidos_temporada_ids:
            return Response({
                "temporada_id": temporada_id,
                "window": {"status": "ok", "matched_games": 0} if (from_date and to_date) else None,
                "ranking_global": [],
            }, status=status.HTTP_200_OK)
        
        # Obtener goles TOTALES de toda la temporada (tipo 'gol' y 'gol_pp')
        goles_totales_qs = (
            EventoPartido.objects
            .filter(
                partido_id__in=partidos_temporada_ids,
                tipo_evento__in=["gol", "gol_pp"],
                jugador__isnull=False
            )
            .select_related("jugador", "club", "partido__grupo__competicion")
        )
        
        # Agregar goles TOTALES por jugador y grupo
        goleadores_data = {}
        for gol in goles_totales_qs:
            jugador_id = gol.jugador_id
            grupo_id = gol.partido.grupo_id
            competicion_id = gol.partido.grupo.competicion_id
            club_id = gol.club_id if gol.club_id else None
            
            if jugador_id not in goleadores_data:
                goleadores_data[jugador_id] = {
                    "jugador_id": jugador_id,
                    "club_id": club_id,
                    "goles_por_grupo": {},
                    "goles_total": 0,
                    "goles_semana": 0,
                    "puntos_total": 0.0,
                }
            
            # Contar goles por grupo (totales)
            if grupo_id not in goleadores_data[jugador_id]["goles_por_grupo"]:
                goleadores_data[jugador_id]["goles_por_grupo"][grupo_id] = {
                    "grupo_id": grupo_id,
                    "competicion_id": competicion_id,
                    "goles": 0,
                }
            
            goleadores_data[jugador_id]["goles_por_grupo"][grupo_id]["goles"] += 1
            goleadores_data[jugador_id]["goles_total"] += 1
        
        # Si hay filtro de fechas, calcular también goles de la semana
        if from_date and to_date:
            start_dt = timezone.make_aware(datetime.combine(from_date, time.min))
            end_dt = timezone.make_aware(datetime.combine(to_date, time.max))
            partidos_semana_qs = partidos_temporada_qs.filter(fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
            partidos_semana_ids = list(partidos_semana_qs.values_list("id", flat=True))
            
            if partidos_semana_ids:
                goles_semana_qs = (
                    EventoPartido.objects
                    .filter(
                        partido_id__in=partidos_semana_ids,
                        tipo_evento__in=["gol", "gol_pp"],
                        jugador__isnull=False
                    )
                    .select_related("jugador", "club", "partido__grupo__competicion")
                )
                
                for gol in goles_semana_qs:
                    jugador_id = gol.jugador_id
                    if jugador_id in goleadores_data:
                        goleadores_data[jugador_id]["goles_semana"] += 1
        
        # Calcular puntos totales (goles * coef_division * 3.1416)
        for jugador_id, data in goleadores_data.items():
            puntos_total = 0.0
            for grupo_id, grupo_data in data["goles_por_grupo"].items():
                competicion_id = grupo_data["competicion_id"]
                coef_div = float(coef_division.get(competicion_id, 1.0))
                puntos_grupo = grupo_data["goles"] * coef_div * 3.1416
                puntos_total += puntos_grupo
            
            data["puntos_total"] = round(puntos_total, 2)
        
        # Obtener información de jugadores y clubs
        jugador_ids = list(goleadores_data.keys())
        club_ids = list(set([data["club_id"] for data in goleadores_data.values() if data["club_id"]]))
        
        jugadores_lookup = {}
        for j in Jugador.objects.filter(id__in=jugador_ids):
            raw_rel = j.foto_url or ""  # ej "jugadores/9812817.png"
            if raw_rel:
                if raw_rel.startswith("/media/"):
                    foto_final = raw_rel
                else:
                    foto_final = "/media/" + raw_rel.lstrip("/")
            else:
                foto_final = ""
            
            jugadores_lookup[j.id] = {
                "nombre": j.nombre,
                "slug": getattr(j, "slug", None),
                "foto": foto_final,
            }
        
        clubs_lookup = {}
        for c in Club.objects.filter(id__in=club_ids):
            raw_rel_escudo = c.escudo_url or ""
            if raw_rel_escudo:
                if raw_rel_escudo.startswith("/media/"):
                    escudo_final = raw_rel_escudo
                else:
                    escudo_final = "/media/" + raw_rel_escudo.lstrip("/")
            else:
                escudo_final = ""
            
            clubs_lookup[c.id] = {
                "club_nombre": c.nombre_corto or c.nombre_oficial,
                "club_escudo": escudo_final,
            }
        
        # Obtener grupos para información adicional
        grupos_lookup = {}
        for grupo in Grupo.objects.filter(temporada_id=temporada_id).select_related("competicion"):
            grupos_lookup[grupo.id] = {
                "grupo_nombre": grupo.nombre,
                "competicion_nombre": grupo.competicion.nombre,
            }
        
        # Construir ranking
        ranking_data = []
        for jugador_id, data in goleadores_data.items():
            jugador_info = jugadores_lookup.get(jugador_id, {})
            club_info = clubs_lookup.get(data["club_id"], {}) if data["club_id"] else {}
            
            # Obtener grupo principal (el que tiene más goles)
            grupo_principal = None
            if data["goles_por_grupo"]:
                grupo_id_max = max(data["goles_por_grupo"].keys(), 
                                 key=lambda gid: data["goles_por_grupo"][gid]["goles"])
                grupo_info = grupos_lookup.get(grupo_id_max, {})
                grupo_data = data["goles_por_grupo"][grupo_id_max]
                grupo_principal = {
                    "grupo_id": grupo_id_max,
                    "grupo_nombre": grupo_info.get("grupo_nombre", ""),
                    "competicion_id": grupo_data["competicion_id"],
                    "competicion_nombre": grupo_info.get("competicion_nombre", ""),
                }
            
            # Goles de la semana (si hay filtro)
            goles_semana = data["goles_semana"] if (from_date and to_date) else None
            
            ranking_data.append({
                "jugador_id": jugador_id,
                "nombre": jugador_info.get("nombre", ""),
                "slug": jugador_info.get("slug"),
                "foto": jugador_info.get("foto"),
                "club_id": data["club_id"],
                "club_nombre": club_info.get("club_nombre"),
                "club_escudo": club_info.get("club_escudo"),
                "goles_semana": goles_semana,
                "goles_total": data["goles_total"],
                "puntos_total": data["puntos_total"],
                "coef_division": float(coef_division.get(grupo_principal["competicion_id"], 1.0)) if grupo_principal else 1.0,
                "grupo_id": grupo_principal["grupo_id"] if grupo_principal else None,
                "grupo_nombre": grupo_principal["grupo_nombre"] if grupo_principal else None,
                "competicion_id": grupo_principal["competicion_id"] if grupo_principal else None,
                "competicion_nombre": grupo_principal["competicion_nombre"] if grupo_principal else None,
            })
        
        # Ordenar por puntos totales (descendente)
        ranking_data.sort(key=lambda x: x["puntos_total"], reverse=True)
        
        # Limitar a top_n
        if top_n > 0:
            ranking_data = ranking_data[:top_n]
        
        # Construir respuesta
        window_meta = {}
        if from_date and to_date:
            start_dt = timezone.make_aware(datetime.combine(from_date, time.min))
            end_dt = timezone.make_aware(datetime.combine(to_date, time.max))
            partidos_semana_ids_for_meta = list(
                partidos_temporada_qs.filter(fecha_hora__gte=start_dt, fecha_hora__lte=end_dt).values_list("id", flat=True)
            )
            window_meta = {
                "status": "ok",
                "matched_games": len(partidos_semana_ids_for_meta),
            }
        
        return Response({
            "temporada_id": temporada_id,
            "window": window_meta,
            "ranking_global": ranking_data,
        }, status=status.HTTP_200_OK)


class SancionesGlobalOptimizedView(APIView):
    """
    GET /api/estadisticas/sanciones-global-optimized/?temporada_id=4&from=2025-11-26&to=2025-12-02&top=200
    
    Ranking global de jugadores más sancionados de todas las divisiones de la temporada, con opción de filtrar por ventana de fechas.
    Puntos: roja=5, doble_amarilla=3, amarilla=1
    """
    
    TEMPORADA_ID_BASE = 4
    
    def _parse_date(self, s: str | None):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None
    
    def get(self, request, format=None):
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        top_n = _get_int(request, "top", 200)
        from_date = self._parse_date(request.GET.get("from"))
        to_date = self._parse_date(request.GET.get("to"))
        
        # Partidos de toda la temporada (para totales)
        partidos_temporada_qs = Partido.objects.filter(
            grupo__temporada_id=temporada_id,
            jugado=True
        ).select_related("grupo__competicion")
        
        partidos_temporada_ids = list(partidos_temporada_qs.values_list("id", flat=True))
        
        if not partidos_temporada_ids:
            return Response({
                "temporada_id": temporada_id,
                "window": {"status": "ok", "matched_games": 0} if (from_date and to_date) else None,
                "ranking_global": [],
            }, status=status.HTTP_200_OK)
        
        # Obtener sanciones TOTALES de toda la temporada (amarilla, doble_amarilla, roja)
        sanciones_totales_qs = (
            EventoPartido.objects
            .filter(
                partido_id__in=partidos_temporada_ids,
                tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                jugador__isnull=False
            )
            .select_related("jugador", "club", "partido__grupo__competicion")
        )
        
        # Agregar sanciones TOTALES por jugador
        sanciones_data = {}
        for sancion in sanciones_totales_qs:
            jugador_id = sancion.jugador_id
            club_id = sancion.club_id if sancion.club_id else None
            grupo_id = sancion.partido.grupo_id
            competicion_id = sancion.partido.grupo.competicion_id
            tipo = sancion.tipo_evento
            
            if jugador_id not in sanciones_data:
                sanciones_data[jugador_id] = {
                    "jugador_id": jugador_id,
                    "club_id": club_id,
                    "grupo_id": grupo_id,
                    "competicion_id": competicion_id,
                    "amarillas_semana": 0 if (from_date and to_date) else None,
                    "dobles_amarillas_semana": 0 if (from_date and to_date) else None,
                    "rojas_semana": 0 if (from_date and to_date) else None,
                    "puntos_semana": 0.0 if (from_date and to_date) else None,
                    "amarillas_total": 0,
                    "dobles_amarillas_total": 0,
                    "rojas_total": 0,
                    "puntos_total": 0.0,
                }
            
            # Contar sanciones TOTALES
            if tipo == "amarilla":
                sanciones_data[jugador_id]["amarillas_total"] += 1
            elif tipo == "doble_amarilla":
                sanciones_data[jugador_id]["dobles_amarillas_total"] += 1
            elif tipo == "roja":
                sanciones_data[jugador_id]["rojas_total"] += 1
        
        # Si hay filtro de fechas, calcular también sanciones de la semana
        if from_date and to_date:
            start_dt = timezone.make_aware(datetime.combine(from_date, time.min))
            end_dt = timezone.make_aware(datetime.combine(to_date, time.max))
            partidos_semana_qs = partidos_temporada_qs.filter(fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
            partidos_semana_ids = list(partidos_semana_qs.values_list("id", flat=True))
            
            if partidos_semana_ids:
                sanciones_semana_qs = (
                    EventoPartido.objects
                    .filter(
                        partido_id__in=partidos_semana_ids,
                        tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                        jugador__isnull=False
                    )
                    .select_related("jugador", "club", "partido__grupo__competicion")
                )
                
                for sancion in sanciones_semana_qs:
                    jugador_id = sancion.jugador_id
                    tipo = sancion.tipo_evento
                    
                    if jugador_id in sanciones_data:
                        if tipo == "amarilla":
                            sanciones_data[jugador_id]["amarillas_semana"] += 1
                        elif tipo == "doble_amarilla":
                            sanciones_data[jugador_id]["dobles_amarillas_semana"] += 1
                        elif tipo == "roja":
                            sanciones_data[jugador_id]["rojas_semana"] += 1
        
        # Calcular puntos TOTALES (roja=5, doble_amarilla=3, amarilla=1)
        for jugador_id, data in sanciones_data.items():
            puntos_total = (
                5 * data["rojas_total"]
                + 3 * data["dobles_amarillas_total"]
                + 1 * data["amarillas_total"]
            )
            data["puntos_total"] = puntos_total
            
            # Calcular puntos de la semana (si hay filtro)
            if data["puntos_semana"] is not None:
                puntos_semana = (
                    5 * data["rojas_semana"]
                    + 3 * data["dobles_amarillas_semana"]
                    + 1 * data["amarillas_semana"]
                )
                data["puntos_semana"] = puntos_semana
        
        # Obtener información de jugadores y clubs
        jugador_ids = list(sanciones_data.keys())
        club_ids = list(set([data["club_id"] for data in sanciones_data.values() if data["club_id"]]))
        
        jugadores_lookup = {}
        for j in Jugador.objects.filter(id__in=jugador_ids):
            raw_rel = j.foto_url or ""  # ej "jugadores/9812817.png"
            if raw_rel:
                if raw_rel.startswith("/media/"):
                    foto_final = raw_rel
                else:
                    foto_final = "/media/" + raw_rel.lstrip("/")
            else:
                foto_final = ""
            
            jugadores_lookup[j.id] = {
                "nombre": j.nombre,
                "slug": getattr(j, "slug", None),
                "foto": foto_final,
            }
        
        clubs_lookup = {}
        for c in Club.objects.filter(id__in=club_ids):
            raw_rel_escudo = c.escudo_url or ""
            if raw_rel_escudo:
                if raw_rel_escudo.startswith("/media/"):
                    escudo_final = raw_rel_escudo
                else:
                    escudo_final = "/media/" + raw_rel_escudo.lstrip("/")
            else:
                escudo_final = ""
            
            clubs_lookup[c.id] = {
                "club_nombre": c.nombre_corto or c.nombre_oficial,
                "club_escudo": escudo_final,
            }
        
        # Obtener grupos para información adicional
        grupos_lookup = {}
        for grupo in Grupo.objects.filter(temporada_id=temporada_id).select_related("competicion"):
            grupos_lookup[grupo.id] = {
                "grupo_nombre": grupo.nombre,
                "competicion_nombre": grupo.competicion.nombre,
            }
        
        # Construir ranking
        ranking_data = []
        for jugador_id, data in sanciones_data.items():
            jugador_info = jugadores_lookup.get(jugador_id, {})
            club_info = clubs_lookup.get(data["club_id"], {}) if data["club_id"] else {}
            grupo_info = grupos_lookup.get(data["grupo_id"], {})
            
            ranking_data.append({
                "jugador_id": jugador_id,
                "nombre": jugador_info.get("nombre", ""),
                "slug": jugador_info.get("slug"),
                "foto": jugador_info.get("foto"),
                "club_id": data["club_id"],
                "club_nombre": club_info.get("club_nombre"),
                "club_escudo": club_info.get("club_escudo"),
                "amarillas_semana": data["amarillas_semana"],
                "dobles_amarillas_semana": data["dobles_amarillas_semana"],
                "rojas_semana": data["rojas_semana"],
                "puntos_semana": data["puntos_semana"],
                "amarillas_total": data["amarillas_total"],
                "dobles_amarillas_total": data["dobles_amarillas_total"],
                "rojas_total": data["rojas_total"],
                "puntos_total": data["puntos_total"],
                "grupo_id": data["grupo_id"],
                "grupo_nombre": grupo_info.get("grupo_nombre"),
                "competicion_id": data["competicion_id"],
                "competicion_nombre": grupo_info.get("competicion_nombre"),
            })
        
        # Ordenar por puntos totales (descendente)
        ranking_data.sort(key=lambda x: x["puntos_total"], reverse=True)
        
        # Limitar a top_n
        if top_n > 0:
            ranking_data = ranking_data[:top_n]
        
        # Construir respuesta
        window_meta = {}
        if from_date and to_date:
            start_dt = timezone.make_aware(datetime.combine(from_date, time.min))
            end_dt = timezone.make_aware(datetime.combine(to_date, time.max))
            partidos_semana_ids_for_meta = list(
                partidos_temporada_qs.filter(fecha_hora__gte=start_dt, fecha_hora__lte=end_dt).values_list("id", flat=True)
            )
            window_meta = {
                "status": "ok",
                "matched_games": len(partidos_semana_ids_for_meta),
            }
        
        return Response({
            "temporada_id": temporada_id,
            "window": window_meta,
            "ranking_global": ranking_data,
        }, status=status.HTTP_200_OK)
