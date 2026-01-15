# /backend/estadisticas/views_grupo_info.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Count

from nucleo.models import Grupo, Competicion
from clubes.models import ClubEnGrupo
from partidos.models import Partido, EventoPartido
from jugadores.models import Jugador
from arbitros.models import ArbitrajePartido


class GrupoInfoFullView(APIView):
    """
    GET /api/estadisticas/grupo-info/?competicion_slug=tercera-division&grupo_slug=grupo-xv
    Opcionales:
      &temporada=2025/2026
      &jornada=6

    Devuelve TODO el paquete de datos necesario para pintar la pantalla pública del grupo.
    """

    def get(self, request, format=None):
        competicion_slug = request.GET.get("competicion_slug")
        grupo_slug = request.GET.get("grupo_slug")
        temporada_param = request.GET.get("temporada")  # ej "2025/2026"
        jornada_param = request.GET.get("jornada")

        if not competicion_slug or not grupo_slug:
            return Response(
                {"detail": "Faltan parámetros competicion_slug o grupo_slug"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Competición
        try:
            competicion = Competicion.objects.get(slug=competicion_slug)
        except Competicion.DoesNotExist:
            return Response(
                {"detail": f"Competición '{competicion_slug}' no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Grupos candidatos (misma competición y mismo slug de grupo)
        grupos_qs = (
            Grupo.objects
            .select_related("competicion", "temporada")
            .filter(competicion=competicion, slug=grupo_slug)
        )

        if not grupos_qs.exists():
            return Response(
                {"detail": f"Grupo '{grupo_slug}' no encontrado para esa competición"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 3. Si el usuario ha pasado temporada=..., filtramos por esa temporada exacta
        if temporada_param:
            grupos_qs = grupos_qs.filter(temporada__nombre=temporada_param)

            if not grupos_qs.exists():
                return Response(
                    {"detail": f"No hay grupo '{grupo_slug}' en temporada '{temporada_param}'"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # 4. Elegir un grupo definitivo.
        # Si hay varios grupos con el mismo slug pero de diferentes temporadas,
        # nos quedamos con la "más reciente" (temporada más actual).
        # Esto es útil cuando se accede a una URL sin especificar temporada:
        # automáticamente muestra los datos de la temporada actual.
        grupos_ordenados = sorted(
            grupos_qs,
            key=lambda g: g.temporada.nombre,  # Ordenar por nombre de temporada (ej: "2025/2026")
            reverse=True,  # Más reciente primero
        )
        grupo = grupos_ordenados[0]

        grupo_id = grupo.id

        # ---------------------------------------------------------------------
        # A partir de aquí REPLICAMOS la lógica de otras views inline.
        # Esto evita tener que instanciar múltiples subclases DRF y hacer
        # múltiples peticiones HTTP, mejorando el rendimiento al consolidar
        # toda la información del grupo en una sola respuesta.
        # ---------------------------------------------------------------------

        # ========== CLASIFICACION (similar a ClasificacionMiniView) ==========
        # Obtenemos todas las posiciones del grupo ordenadas por posición actual.
        # Usamos select_related para optimizar las consultas y evitar N+1 queries.
        posiciones = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )

        # Ordenar por posición actual (si es None, ponerlo al final con 9999).
        # Si hay empate en posición, desempatar por puntos (más puntos = mejor).
        posiciones_ordenadas = sorted(
            posiciones,
            key=lambda row: (
                row.posicion_actual if row.posicion_actual is not None else 9999,
                -row.puntos,  # Negativo para orden descendente (más puntos primero)
            )
        )

        tabla_clasificacion = []
        for row in posiciones_ordenadas:
            raw_racha = getattr(row, "racha", "") or ""
            racha_list = list(raw_racha.strip().upper())[:5]

            tabla_clasificacion.append({
                "pos": row.posicion_actual,
                "club_id": row.club.id,
                "nombre": row.club.nombre_corto or row.club.nombre_oficial,
                "escudo": row.club.escudo_url or "",
                "pj": row.partidos_jugados,
                "puntos": row.puntos,
                "racha": racha_list,
                "gf": row.goles_favor,
                "gc": row.goles_contra,
            })

        clasificacion_payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "tabla": tabla_clasificacion,
        }

        # ========== PARTIDOS Y JORNADAS (similar a ResultadosJornadaView) ==========

        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
        )

        jornadas_disponibles = sorted(set(
            qs_partidos_grupo.values_list("jornada_numero", flat=True).distinct()
        ))

        # determinar jornada activa
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
                jornada_num = jugadas[-1]  # última jugada
            else:
                jornada_num = max(jornadas_disponibles) if jornadas_disponibles else None

        partidos_payload = []
        partidos_de_jornada_qs = Partido.objects.none()
        if jornada_num is not None:
            partidos_de_jornada_qs = (
                qs_partidos_grupo
                .filter(jornada_numero=jornada_num)
                .order_by("fecha_hora", "id")
            )

            # árbitros en bloque
            arbitrajes = (
                ArbitrajePartido.objects
                .filter(partido__in=partidos_de_jornada_qs)
                .select_related("arbitro", "partido")
            )
            arbitros_por_partido = {}
            for arb in arbitrajes:
                pid = arb.partido_id
                arbitros_por_partido.setdefault(pid, [])
                if arb.arbitro and arb.arbitro.nombre:
                    arbitros_por_partido[pid].append(arb.arbitro.nombre)

            for p in partidos_de_jornada_qs:
                partidos_payload.append({
                    "id": p.identificador_federacion or p.id,
                    "jornada": p.jornada_numero,
                    "jugado": p.jugado,
                    "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
                    "pabellon": p.pabellon or p.local.pabellon or "",
                    "arbitros": arbitros_por_partido.get(p.id, []),

                    "local": {
                        "id": p.local.id,
                        "nombre": p.local.nombre_corto or p.local.nombre_oficial,
                        "escudo": p.local.escudo_url or "",
                        "goles": p.goles_local if p.goles_local is not None else None,
                    },
                    "visitante": {
                        "id": p.visitante.id,
                        "nombre": p.visitante.nombre_corto or p.visitante.nombre_oficial,
                        "escudo": p.visitante.escudo_url or "",
                        "goles": p.goles_visitante if p.goles_visitante is not None else None,
                    },
                })

        resultados_payload = {
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

        # ========== KPIs jornada (similar a KPIsJornadaView) ==========

        goles_totales = 0
        vict_local = 0
        vict_visit = 0
        empates = 0

        partidos_de_jornada_list = list(partidos_de_jornada_qs)

        for p in partidos_de_jornada_list:
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

        eventos_disciplina = EventoPartido.objects.filter(
            partido_id__in=[pp.id for pp in partidos_de_jornada_list],
            tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
        ).values("tipo_evento").annotate(cnt=Count("id"))

        amarillas_totales = 0
        rojas_totales = 0
        for ev in eventos_disciplina:
            tipo = ev["tipo_evento"]
            cnt = ev["cnt"] or 0
            if tipo == "amarilla":
                amarillas_totales += cnt
            elif tipo in ("roja", "doble_amarilla"):
                rojas_totales += cnt

        kpis_payload = {
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

        # ========== Goleadores jornada (similar a GoleadoresJornadaView) ==========

        goleadores_jornada_list = []
        if jornada_num is not None:
            # partidos concretos de ESA jornada (ids)
            partidos_ids = [pp.id for pp in partidos_de_jornada_list]

            eventos_gol = (
                EventoPartido.objects
                .filter(
                    partido_id__in=partidos_ids,
                    tipo_evento="gol",
                    jugador__isnull=False,
                    club__isnull=False,
                )
                .values("jugador_id", "club_id")
                .annotate(goles_jornada=Count("id"))
            )

            # fallback GF por club en el grupo entero
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
                lid = p["local_id"]
                vid = p["visitante_id"]
                gl = p["goles_local"] or 0
                gv = p["goles_visitante"] or 0

                goles_favor_por_club[lid] = goles_favor_por_club.get(lid, 0) + gl
                goles_favor_por_club[vid] = goles_favor_por_club.get(vid, 0) + gv

            clubs_ids = [row["club_id"] for row in eventos_gol]
            clasif_rows = (
                ClubEnGrupo.objects
                .filter(grupo=grupo, club_id__in=clubs_ids)
                .select_related("club")
            )
            clasif_lookup = {}
            for c in clasif_rows:
                gf_guardado = c.goles_favor or 0
                gf_calc = goles_favor_por_club.get(c.club_id, 0)
                gf_final = gf_guardado or gf_calc
                clasif_lookup[c.club_id] = {
                    "posicion_actual": c.posicion_actual if c.posicion_actual is not None else 9999,
                    "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                    "goles_favor": gf_final,
                }

            jugadores_ids = [row["jugador_id"] for row in eventos_gol]
            jugadores_objs = Jugador.objects.filter(id__in=jugadores_ids)
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
                }

            for row in eventos_gol:
                jug_id = row["jugador_id"]
                club_id = row["club_id"]
                goles_j = row["goles_jornada"]

                jugador_info = jugadores_lookup.get(jug_id, {})
                club_info = clasif_lookup.get(
                    club_id,
                    {"posicion_actual": 9999, "club_nombre": "", "goles_favor": 0},
                )

                goles_equipo_total = club_info["goles_favor"]
                contrib = 0.0
                if goles_equipo_total > 0:
                    contrib = (goles_j / goles_equipo_total) * 100.0

                goleadores_jornada_list.append({
                    "jugador_id": jug_id,
                    "nombre": jugador_info.get("nombre", ""),
                    "apodo": jugador_info.get("apodo", ""),
                    "foto": jugador_info.get("foto", ""),
                    "club_id": club_id,
                    "club_nombre": club_info["club_nombre"],
                    "goles_jornada": goles_j,
                    "goles_equipo_total": goles_equipo_total,
                    "contribucion_pct": round(contrib),
                    "club_posicion": club_info["posicion_actual"],
                })

            goleadores_jornada_list.sort(
                key=lambda x: (-x["goles_jornada"], x["club_posicion"], x["nombre"].lower())
            )

        goleadores_jornada_payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "goleadores": goleadores_jornada_list,
        }

        # ========== Pichichi temporada (similar a PichichiTemporadaView) ==========

        partidos_grupo_jugados = list(
            Partido.objects.filter(
                grupo=grupo,
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            ).values_list("id", flat=True)
        )

        pichichi_list = []
        if partidos_grupo_jugados:
            eventos_gol_totales = (
                EventoPartido.objects
                .filter(
                    partido_id__in=partidos_grupo_jugados,
                    tipo_evento="gol",
                    jugador__isnull=False,
                    club__isnull=False,
                )
                .values("jugador_id", "club_id")
                .annotate(goles_total=Count("id"))
            )

            # build goles_favor_por_club
            partidos_validos_grupo = (
                Partido.objects.filter(
                    grupo=grupo,
                    jugado=True,
                    goles_local__isnull=False,
                    goles_visitante__isnull=False,
                )
                .values("local_id", "visitante_id", "goles_local", "goles_visitante")
            )

            goles_favor_por_club_total = {}
            for p in partidos_validos_grupo:
                lid = p["local_id"]
                vid = p["visitante_id"]
                gl = p["goles_local"] or 0
                gv = p["goles_visitante"] or 0
                goles_favor_por_club_total[lid] = goles_favor_por_club_total.get(lid, 0) + gl
                goles_favor_por_club_total[vid] = goles_favor_por_club_total.get(vid, 0) + gv

            clubs_ids_total = [row["club_id"] for row in eventos_gol_totales]
            clasif_rows_total = (
                ClubEnGrupo.objects
                .filter(grupo=grupo, club_id__in=clubs_ids_total)
                .select_related("club")
            )
            clasif_lookup_total = {}
            for c in clasif_rows_total:
                gf_guardado = c.goles_favor or 0
                gf_calc = goles_favor_por_club_total.get(c.club_id, 0)
                gf_final = gf_guardado or gf_calc

                clasif_lookup_total[c.club_id] = {
                    "posicion_actual": c.posicion_actual if c.posicion_actual is not None else 9999,
                    "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                    "goles_favor": gf_final,
                }

            jugadores_ids_total = [row["jugador_id"] for row in eventos_gol_totales]
            jugadores_objs_total = Jugador.objects.filter(id__in=jugadores_ids_total)
            jugadores_lookup_total = {}
            for j in jugadores_objs_total:
                raw_rel = j.foto_url or ""
                if raw_rel:
                    if raw_rel.startswith("/media/"):
                        foto_final = raw_rel
                    else:
                        foto_final = "/media/" + raw_rel.lstrip("/")
                else:
                    foto_final = ""
                jugadores_lookup_total[j.id] = {
                    "nombre": j.nombre,
                    "apodo": j.apodo or "",
                    "foto": foto_final,
                }

            for row in eventos_gol_totales:
                jug_id = row["jugador_id"]
                club_id = row["club_id"]
                goles_total = row["goles_total"]

                jugador_info = jugadores_lookup_total.get(jug_id, {})
                club_info = clasif_lookup_total.get(
                    club_id,
                    {"posicion_actual": 9999, "club_nombre": "", "goles_favor": 0},
                )

                goles_equipo_total = club_info["goles_favor"]
                contrib = 0.0
                if goles_equipo_total > 0:
                    contrib = (goles_total / goles_equipo_total) * 100.0

                pichichi_list.append({
                    "jugador_id": jug_id,
                    "nombre": jugador_info.get("nombre", ""),
                    "apodo": jugador_info.get("apodo", ""),
                    "foto": jugador_info.get("foto", ""),
                    "club_id": club_id,
                    "club_nombre": club_info["club_nombre"],
                    "goles_total": goles_total,
                    "goles_equipo_total": goles_equipo_total,
                    "contribucion_pct": round(contrib),
                    "club_posicion": club_info["posicion_actual"],
                })

            pichichi_list.sort(
                key=lambda x: (-x["goles_total"], x["club_posicion"], x["nombre"].lower())
            )

        pichichi_payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "goleadores": pichichi_list,
        }

        # ========== Sanciones jornada (similar a SancionesJornadaView) ==========

        sancionados_lista = []
        if jornada_num is not None:
            partidos_de_jornada_ids = [pp.id for pp in partidos_de_jornada_list]

            eventos_disciplina_jornada = (
                EventoPartido.objects
                .filter(
                    partido_id__in=partidos_de_jornada_ids,
                    tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                    jugador__isnull=False,
                    club__isnull=False,
                )
                .values("jugador_id", "club_id", "tipo_evento")
                .annotate(cnt=Count("id"))
            )

            sanciones_por_jugador = {}
            for ev in eventos_disciplina_jornada:
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

            for key, rowdata in sanciones_por_jugador.items():
                puntos = (
                    5 * rowdata["rojas"]
                    + 3 * rowdata["dobles_amarillas"]
                    + 1 * rowdata["amarillas"]
                )
                rowdata["severidad_puntos"] = puntos

            jugador_ids = [k[0] for k in sanciones_por_jugador.keys()]
            club_ids = [k[1] for k in sanciones_por_jugador.keys()]

            jugadores_objs_jornada = Jugador.objects.filter(id__in=jugador_ids)
            jugadores_lookup_jornada = {}
            for j in jugadores_objs_jornada:
                raw_rel = j.foto_url or ""
                if raw_rel:
                    if raw_rel.startswith("/media/"):
                        foto_final = raw_rel
                    else:
                        foto_final = "/media/" + raw_rel.lstrip("/")
                else:
                    foto_final = ""
                jugadores_lookup_jornada[j.id] = {
                    "nombre": j.nombre,
                    "apodo": j.apodo or "",
                    "foto": foto_final,
                }

            clasif_rows_sanc = (
                ClubEnGrupo.objects
                .filter(grupo=grupo, club_id__in=club_ids)
                .select_related("club")
            )
            clubs_lookup = {}
            for c in clasif_rows_sanc:
                clubs_lookup[c.club_id] = {
                    "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                }

            for (jid, cid), rowdata in sanciones_por_jugador.items():
                jugador_info = jugadores_lookup_jornada.get(jid, {})
                club_info = clubs_lookup.get(cid, {"club_nombre": ""})

                sancionados_lista.append({
                    "jugador_id": jid,
                    "nombre": jugador_info.get("nombre", ""),
                    "apodo": jugador_info.get("apodo", ""),
                    "foto": jugador_info.get("foto", ""),

                    "club_id": cid,
                    "club_nombre": club_info["club_nombre"],

                    "amarillas": rowdata["amarillas"],
                    "dobles_amarillas": rowdata["dobles_amarillas"],
                    "rojas": rowdata["rojas"],
                    "severidad_puntos": rowdata["severidad_puntos"],
                })

            sancionados_lista.sort(
                key=lambda x: (
                    -x["severidad_puntos"],
                    -x["rojas"],
                    -x["dobles_amarillas"],
                    -x["amarillas"],
                    x["nombre"].lower(),
                )
            )
            sancionados_lista = sancionados_lista[:12]

        sanciones_jornada_payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "sancionados": sancionados_lista,
        }

        # ========== Sanciones acumuladas / jugadores más sancionados ==========
        # (similar a SancionesJugadoresAcumuladoView)

        sanciones_acum_list = []
        partidos_ids_all = list(
            Partido.objects.filter(
                grupo=grupo,
                jugado=True,
            ).values_list("id", flat=True)
        )
        if partidos_ids_all:
            eventos_disciplina_total = (
                EventoPartido.objects
                .filter(
                    partido_id__in=partidos_ids_all,
                    tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                    jugador__isnull=False,
                    club__isnull=False,
                )
                .values("jugador_id", "club_id", "tipo_evento")
                .annotate(cnt=Count("id"))
            )

            sanciones_por_jugador_total = {}
            for ev in eventos_disciplina_total:
                jid = ev["jugador_id"]
                cid = ev["club_id"]
                tipo = ev["tipo_evento"]
                cnt = ev["cnt"] or 0

                if jid not in sanciones_por_jugador_total:
                    sanciones_por_jugador_total[jid] = {
                        "jugador_id": jid,
                        "club_id": cid,
                        "amarillas": 0,
                        "dobles_amarillas": 0,
                        "rojas": 0,
                    }

                if tipo == "amarilla":
                    sanciones_por_jugador_total[jid]["amarillas"] += cnt
                elif tipo == "doble_amarilla":
                    sanciones_por_jugador_total[jid]["dobles_amarillas"] += cnt
                elif tipo == "roja":
                    sanciones_por_jugador_total[jid]["rojas"] += cnt

            for jid, rowdata in sanciones_por_jugador_total.items():
                puntos = (
                    5 * rowdata["rojas"]
                    + 3 * rowdata["dobles_amarillas"]
                    + 1 * rowdata["amarillas"]
                )
                rowdata["puntos_disciplina"] = puntos

            jugador_ids_total = list(sanciones_por_jugador_total.keys())
            jugadores_objs_total2 = Jugador.objects.filter(id__in=jugador_ids_total)
            jugadores_lookup_total2 = {}
            for j in jugadores_objs_total2:
                raw_rel = j.foto_url or ""
                if raw_rel:
                    if raw_rel.startswith("/media/"):
                        foto_final = raw_rel
                    else:
                        foto_final = "/media/" + raw_rel.lstrip("/")
                else:
                    foto_final = ""
                jugadores_lookup_total2[j.id] = {
                    "nombre": j.nombre,
                    "apodo": j.apodo or "",
                    "foto": foto_final,
                }

            club_ids_total2 = [row["club_id"] for row in sanciones_por_jugador_total.values()]
            clasif_rows_total2 = (
                ClubEnGrupo.objects
                .filter(grupo=grupo, club_id__in=club_ids_total2)
                .select_related("club")
            )
            clubs_lookup_total2 = {}
            for c in clasif_rows_total2:
                clubs_lookup_total2[c.club_id] = {
                    "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                }

            for jid, rowdata in sanciones_por_jugador_total.items():
                jugador_info = jugadores_lookup_total2.get(jid, {})
                club_info = clubs_lookup_total2.get(
                    rowdata["club_id"],
                    {"club_nombre": ""},
                )

                sanciones_acum_list.append({
                    "jugador_id": jid,
                    "nombre": jugador_info.get("nombre", ""),
                    "apodo": jugador_info.get("apodo", ""),
                    "foto": jugador_info.get("foto", ""),

                    "club_id": rowdata["club_id"],
                    "club_nombre": club_info["club_nombre"],

                    "amarillas": rowdata["amarillas"],
                    "dobles_amarillas": rowdata["dobles_amarillas"],
                    "rojas": rowdata["rojas"],
                    "puntos_disciplina": rowdata["puntos_disciplina"],
                })

            sanciones_acum_list.sort(
                key=lambda x: (
                    -x["puntos_disciplina"],
                    -x["rojas"],
                    -x["dobles_amarillas"],
                    -x["amarillas"],
                    x["nombre"].lower(),
                )
            )
            sanciones_acum_list = sanciones_acum_list[:12]

        sanciones_acum_payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jugadores": sanciones_acum_list,
        }

        # ========== Fair play equipos (similar a FairPlayEquiposView) ==========
        fair_play_equipos_list = []
        if partidos_ids_all:
            eventos_disciplina_total_fp = (
                EventoPartido.objects
                .filter(
                    partido_id__in=partidos_ids_all,
                    tipo_evento__in=["amarilla", "doble_amarilla", "roja"],
                    club__isnull=False,
                )
                .values("club_id", "tipo_evento")
                .annotate(cnt=Count("id"))
            )

            sanciones_por_club = {}
            for ev in eventos_disciplina_total_fp:
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

            for cid, rowdata in sanciones_por_club.items():
                puntos = (
                    5 * rowdata["rojas"]
                    + 3 * rowdata["dobles_amarillas"]
                    + 1 * rowdata["amarillas"]
                )
                rowdata["puntos_fair_play"] = puntos

            clasif_rows_fp = (
                ClubEnGrupo.objects
                .filter(grupo=grupo, club_id__in=sanciones_por_club.keys())
                .select_related("club")
            )
            clubs_lookup_fp = {}
            for c in clasif_rows_fp:
                clubs_lookup_fp[c.club_id] = {
                    "club_nombre": c.club.nombre_corto or c.club.nombre_oficial,
                    "club_escudo": c.club.escudo_url or "",
                }

            for cid, rowdata in sanciones_por_club.items():
                club_info = clubs_lookup_fp.get(
                    cid,
                    {"club_nombre": "", "club_escudo": ""},
                )
                fair_play_equipos_list.append({
                    "club_id": cid,
                    "club_nombre": club_info["club_nombre"],
                    "club_escudo": club_info["club_escudo"],
                    "amarillas": rowdata["amarillas"],
                    "dobles_amarillas": rowdata["dobles_amarillas"],
                    "rojas": rowdata["rojas"],
                    "puntos_fair_play": rowdata["puntos_fair_play"],
                })

            fair_play_equipos_list.sort(
                key=lambda x: (
                    x["puntos_fair_play"],
                    x["rojas"],
                    x["dobles_amarillas"],
                    x["amarillas"],
                    x["club_nombre"].lower(),
                )
            )

        fair_play_payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "equipos": fair_play_equipos_list,
        }

        # ========== Potencia ofensiva equipos (similar a GolesPorEquipoView) ==========
        equipos_ofensivos_list = []
        if partidos_ids_all:
            # construir stats básicos
            clubes_stats = {}
            partidos_grupo_vals = (
                Partido.objects
                .filter(
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

            partido_ids_all2 = []
            for p in partidos_grupo_vals:
                partido_ids_all2.append(p["id"])

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

                clubes_stats[local_id]["goles_total"] += gl
                clubes_stats[local_id]["goles_local"] += gl

                clubes_stats[visit_id]["goles_total"] += gv
                clubes_stats[visit_id]["goles_visitante"] += gv

                clubes_stats[local_id]["partidos_jugados"] += 1
                clubes_stats[visit_id]["partidos_jugados"] += 1

            # goles por parte (1ª/2ª)
            eventos_gol_por_parte = (
                EventoPartido.objects
                .filter(
                    partido_id__in=partido_ids_all2,
                    tipo_evento="gol",
                    club__isnull=False,
                )
                .values("club_id", "minuto")
            )

            for ev in eventos_gol_por_parte:
                cid = ev["club_id"]
                minuto = ev["minuto"] or None
                if cid not in clubes_stats:
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

            # lookup club
            club_ids_all = list(clubes_stats.keys())
            club_rows = (
                ClubEnGrupo.objects
                .filter(grupo=grupo, club_id__in=club_ids_all)
                .select_related("club")
            )
            club_info_lookup = {}
            for c in club_rows:
                club_info_lookup[c.club.id] = {
                    "nombre": c.club.nombre_corto or c.club.nombre_oficial,
                    "escudo": c.club.escudo_url or "",
                }

            for cid, stats in clubes_stats.items():
                pj = stats["partidos_jugados"] or 0
                goles_totales = stats["goles_total"] or 0
                media = round(goles_totales / pj, 2) if pj > 0 else 0.0
                info = club_info_lookup.get(cid, {"nombre": "", "escudo": ""})

                equipos_ofensivos_list.append({
                    "club_id": cid,
                    "club_nombre": info["nombre"],
                    "club_escudo": info["escudo"],
                    "partidos_jugados": pj,
                    "goles_total": goles_totales,
                    "goles_por_partido": media,
                    "goles_local": stats["goles_local"],
                    "goles_visitante": stats["goles_visitante"],
                    "goles_1parte": stats["goles_1parte"],
                    "goles_2parte": stats["goles_2parte"],
                })

            equipos_ofensivos_list.sort(
                key=lambda row: (
                    -row["goles_total"],
                    -row["goles_por_partido"],
                    row["club_nombre"].lower(),
                )
            )

        goles_por_equipo_payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "equipos": equipos_ofensivos_list,
        }

        # ---------------------------------------------------------------------
        # RESPUESTA FINAL
        # ---------------------------------------------------------------------

        meta = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "slug": grupo.slug,
                "competicion": grupo.competicion.nombre,
                "competicion_slug": grupo.competicion.slug,
                "temporada": grupo.temporada.nombre,
            },
            "jornada_actual": jornada_num,
            "jornadas_disponibles": jornadas_disponibles,
        }

        data = {
            "clasificacion": clasificacion_payload,
            "resultados_jornada": resultados_payload,
            "kpis_jornada": kpis_payload,
            "goleadores_jornada": goleadores_jornada_payload,
            "pichichi_temporada": pichichi_payload,
            "sanciones_jornada": sanciones_jornada_payload,
            "jugadores_mas_sancionados": sanciones_acum_payload,
            "fair_play_equipos": fair_play_payload,
            "goles_por_equipo": goles_por_equipo_payload,
        }

        return Response({"meta": meta, "data": data}, status=status.HTTP_200_OK)
