# jugadores/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Prefetch, Sum, Case, When, IntegerField, BooleanField
from django.db.models.functions import Coalesce

from .models import Jugador, JugadorEnClubTemporada, HistorialJugadorScraped
from .serializers import (
    JugadorSerializer,
    JugadorEnClubTemporadaSerializer,
    ValoracionJugadorSerializer,
    HistorialCompletoSerializer,
)
from nucleo.models import Temporada, Grupo
from clubes.models import Club
from valoraciones.models import ValoracionJugador, VotoValoracionJugador
from partidos.models import Partido, EventoPartido, AlineacionPartidoJugador


# Helper para normalizar media URLs
def _norm_media(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/media/"):
        return u
    return "/media/" + u.lstrip("/")


# Helper para obtener jugador por ID o slug
def _get_jugador_by_id_or_slug(id_or_slug: str | None = None, slug: str | None = None):
    """
    Si llega slug explícito -> por slug.
    Si llega id_or_slug:
       - si es dígito -> por id (int)
       - si no es dígito -> por slug
    Lanza Jugador.DoesNotExist si no lo encuentra.
    """
    if slug:
        return Jugador.objects.get(slug=slug)

    if id_or_slug:
        s = str(id_or_slug).strip()
        if s.isdigit():
            return Jugador.objects.get(id=int(s))
        # si llega algo no numérico en 'jugador_id', lo tomamos como slug
        return Jugador.objects.get(slug=s)

    raise Jugador.DoesNotExist


# ============================================================
# 1. GET /api/jugadores/detalle/?jugador_id=XX
# ============================================================
class JugadorDetalleView(APIView):
    """
    Detalle básico del jugador con club actual y temporada.
    """
    def get(self, request, format=None):
        jugador_id = request.GET.get("jugador_id")
        
        if not jugador_id:
            return Response(
                {"detail": "Falta jugador_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            jugador = _get_jugador_by_id_or_slug(jugador_id)
        except Jugador.DoesNotExist:
            return Response(
                {"detail": "Jugador no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Obtener club actual (última temporada activa)
        club_actual = None
        temporada_actual = None
        dorsal_actual = None

        ultima_participacion = (
            JugadorEnClubTemporada.objects
            .filter(jugador=jugador)
            .select_related("club", "temporada")
            .order_by("-temporada__nombre")
            .first()
        )

        if ultima_participacion:
            club_actual = {
                "id": ultima_participacion.club.id,
                "nombre": ultima_participacion.club.nombre_oficial,
                "nombre_corto": ultima_participacion.club.nombre_corto or "",
                "escudo_url": _norm_media(ultima_participacion.club.escudo_url),
                "slug": ultima_participacion.club.slug or "",
            }
            temporada_actual = {
                "id": ultima_participacion.temporada.id,
                "nombre": ultima_participacion.temporada.nombre,
            }
            dorsal_actual = ultima_participacion.dorsal or None

        jugador_ser = JugadorSerializer(jugador)

        return Response({
            "jugador": jugador_ser.data,
            "club_actual": club_actual,
            "temporada_actual": temporada_actual,
            "dorsal_actual": dorsal_actual,
        })


# ============================================================
# 2. GET /api/jugadores/full/?jugador_id=XX&temporada_id=YY&include=valoraciones,historial,partidos,stats
# ============================================================
class JugadorFullView(APIView):
    """
    Ficha completa del jugador con todos los bloques opcionales.
    Similar a /api/clubes/full/
    """
    DEFAULT_INCLUDE = {"valoraciones", "historial", "stats"}

    def get(self, request, format=None):
        jugador_id = request.GET.get("jugador_id")
        temporada_id = request.GET.get("temporada_id")
        include_param = request.GET.get("include", "")

        if not jugador_id:
            return Response(
                {"detail": "Falta jugador_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            jugador = _get_jugador_by_id_or_slug(jugador_id)
        except Jugador.DoesNotExist:
            return Response(
                {"detail": "Jugador no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Parse include
        include = set(include_param.split(",")) if include_param else self.DEFAULT_INCLUDE
        include = {x.strip() for x in include if x.strip()}

        # Datos básicos
        jugador_ser = JugadorSerializer(jugador)

        # Club actual
        club_actual = None
        temporada_actual = None
        dorsal_actual = None
        stats_actuales = None

        try:
            # Obtener temporada activa para filtrar stats
            temporada_activa = Temporada.objects.order_by("-id").first()
            
            # Buscar participación: primero en temporada activa si está disponible, sino la más reciente
            participacion_query = JugadorEnClubTemporada.objects.filter(jugador=jugador)
            
            if temporada_activa:
                # Intentar primero con temporada activa
                participacion_activa = participacion_query.filter(
                    temporada=temporada_activa
                ).select_related("club", "temporada").first()
                
                if participacion_activa:
                    ultima_participacion = participacion_activa
                else:
                    # Si no hay en temporada activa, usar la más reciente
                    ultima_participacion = participacion_query.select_related(
                        "club", "temporada"
                    ).order_by("-temporada__nombre").first()
            else:
                # Si no hay temporada activa, usar la más reciente
                ultima_participacion = participacion_query.select_related(
                    "club", "temporada"
                ).order_by("-temporada__nombre").first()

            if ultima_participacion:
                club_actual = {
                    "id": ultima_participacion.club.id,
                    "nombre": ultima_participacion.club.nombre_oficial,
                    "nombre_corto": ultima_participacion.club.nombre_corto or "",
                    "escudo_url": _norm_media(ultima_participacion.club.escudo_url),
                    "slug": ultima_participacion.club.slug or "",
                }
                temporada_actual = {
                    "id": ultima_participacion.temporada.id,
                    "nombre": ultima_participacion.temporada.nombre,
                }
                dorsal_actual = ultima_participacion.dorsal or None

                if "stats" in include:
                    # Stats de la temporada actual (o más reciente si no hay activa)
                    # NOTA: Estos datos vienen de JugadorEnClubTemporada (consolidado)
                    # Pueden diferir de fantasy.goles_total (calculado desde eventos)
                    # y de partidos.totales (calculado desde EventoPartido en tiempo real)
                    stats_actuales = {
                        "partidos_jugados": ultima_participacion.partidos_jugados,
                        "goles": ultima_participacion.goles,
                        "tarjetas_amarillas": ultima_participacion.tarjetas_amarillas,
                        "tarjetas_rojas": ultima_participacion.tarjetas_rojas,
                        "convocados": ultima_participacion.convocados,
                        "titular": ultima_participacion.titular,
                        "suplente": ultima_participacion.suplente,
                    }
        except Exception:
            pass

        # Valoraciones
        valoraciones_data = None
        if "valoraciones" in include:
            qs_valoraciones = ValoracionJugador.objects.filter(jugador=jugador)
            if temporada_id:
                try:
                    temporada_obj = Temporada.objects.get(id=temporada_id)
                    qs_valoraciones = qs_valoraciones.filter(temporada=temporada_obj)
                except Temporada.DoesNotExist:
                    pass

            valoracion = qs_valoraciones.select_related("temporada").order_by("-temporada__nombre").first()
            if valoracion:
                valoraciones_data = ValoracionJugadorSerializer(valoracion).data
                # Añadir total de votos
                total_votos = VotoValoracionJugador.objects.filter(
                    jugador=jugador,
                    temporada=valoracion.temporada
                ).count()
                valoraciones_data["total_votos"] = total_votos

        # Historial
        historial_data = None
        if "historial" in include:
            historial_data = self._get_historial_completo(jugador)

        # Partidos
        partidos_data = None
        if "partidos" in include:
            partidos_data = self._get_partidos_jugador(jugador, temporada_id)

        response = {
            "jugador": jugador_ser.data,
            "club_actual": club_actual,
            "temporada_actual": temporada_actual,
            "dorsal_actual": dorsal_actual,
        }

        if stats_actuales:
            response["stats_actuales"] = stats_actuales
        if valoraciones_data:
            response["valoraciones"] = valoraciones_data
        if historial_data:
            response["historial"] = historial_data
        if partidos_data:
            response["partidos"] = partidos_data

        return Response(response)

    def _get_historial_completo(self, jugador):
        """Consolida JugadorEnClubTemporada + HistorialJugadorScraped"""
        historial = []

        # De JugadorEnClubTemporada (datos reales)
        participaciones = (
            JugadorEnClubTemporada.objects
            .filter(jugador=jugador)
            .select_related("club", "temporada")
            .prefetch_related("club__participaciones")
            .order_by("-temporada__nombre", "-id")
        )

        for part in participaciones:
            # Intentar obtener grupo
            grupo = None
            grupo_id = None
            competicion = None
            competicion_id = None

            # Buscar grupo a través de ClubEnGrupo
            club_en_grupo = (
                part.club.participaciones
                .filter(grupo__temporada=part.temporada)
                .select_related("grupo", "grupo__competicion")
                .first()
            )

            if club_en_grupo and club_en_grupo.grupo:
                grupo = club_en_grupo.grupo.nombre
                grupo_id = club_en_grupo.grupo.id
                competicion = club_en_grupo.grupo.competicion.nombre
                competicion_id = club_en_grupo.grupo.competicion.id

            historial.append({
                "temporada": part.temporada.nombre,
                "temporada_id": part.temporada.id,
                "competicion": competicion or "",
                "competicion_id": competicion_id,
                "grupo": grupo or "",
                "grupo_id": grupo_id,
                "club": part.club.nombre_oficial,
                "club_id": part.club.id,
                "club_nombre": part.club.nombre_corto or part.club.nombre_oficial,
                "club_slug": part.club.slug or "",
                "dorsal": part.dorsal or None,
                "partidos_jugados": part.partidos_jugados,
                "goles": part.goles,
                "tarjetas_amarillas": part.tarjetas_amarillas,
                "tarjetas_rojas": part.tarjetas_rojas,
                "es_scraped": False,
            })

        # De HistorialJugadorScraped (datos brutos)
        historial_scraped = (
            HistorialJugadorScraped.objects
            .filter(jugador=jugador)
            .order_by("-temporada_texto")
        )

        for hist in historial_scraped:
            # Verificar si ya está en participaciones (evitar duplicados)
            ya_existe = any(
                h["temporada"] == hist.temporada_texto and
                h["club"] == hist.equipo_texto
                for h in historial
            )

            if not ya_existe:
                historial.append({
                    "temporada": hist.temporada_texto,
                    "temporada_id": None,
                    "competicion": hist.competicion_texto,
                    "competicion_id": None,
                    "grupo": "",
                    "grupo_id": None,
                    "club": hist.equipo_texto,
                    "club_id": None,
                    "club_nombre": hist.equipo_texto,
                    "club_slug": None,
                    "dorsal": None,
                    "partidos_jugados": 0,
                    "goles": 0,
                    "tarjetas_amarillas": 0,
                    "tarjetas_rojas": 0,
                    "es_scraped": True,
                })

        # Ordenar por temporada descendente
        historial.sort(key=lambda x: x["temporada"], reverse=True)

        return historial

    def _get_partidos_jugador(self, jugador, temporada_id=None, limit=20):
        """Obtiene partidos del jugador con estadísticas"""
        # Obtener eventos del jugador
        eventos_qs = EventoPartido.objects.filter(jugador=jugador).select_related(
            "partido", "partido__local", "partido__visitante", "partido__grupo"
        )

        if temporada_id:
            eventos_qs = eventos_qs.filter(partido__grupo__temporada_id=temporada_id)

        # Obtener partidos únicos
        partidos_ids = list(eventos_qs.values_list("partido_id", flat=True).distinct()[:limit])
        
        if not partidos_ids:
            return {
                "partidos": [],
                "totales": {
                    "partidos_jugados": 0,
                    "goles": 0,
                    "tarjetas_amarillas": 0,
                    "tarjetas_rojas": 0,
                    "partidos_titular": 0,
                    "mvps": 0,
                },
            }

        # Obtener alineaciones para saber si fue titular
        alineaciones = AlineacionPartidoJugador.objects.filter(
            jugador=jugador,
            partido_id__in=partidos_ids
        ).values_list("partido_id", "titular")

        titular_map = {pid: titular for pid, titular in alineaciones}

        # Obtener partidos
        partidos = Partido.objects.filter(id__in=partidos_ids).select_related(
            "local", "visitante", "grupo", "grupo__competicion", "grupo__temporada"
        ).order_by("-fecha_hora", "-jornada_numero")[:limit]

        partidos_list = []
        for partido in partidos:
            # Contar eventos del jugador en este partido
            eventos_partido = eventos_qs.filter(partido=partido)
            goles_jugador = eventos_partido.filter(tipo_evento__in=["gol", "gol_pp"]).count()
            amarillas = eventos_partido.filter(tipo_evento="amarilla").count()
            rojas = eventos_partido.filter(tipo_evento__in=["doble_amarilla", "roja"]).count()
            mvp = eventos_partido.filter(tipo_evento="mvp").exists()

            partidos_list.append({
                "partido_id": partido.id,
                "fecha": partido.fecha_hora.date().isoformat() if partido.fecha_hora else None,
                "jornada": partido.jornada_numero or None,
                "local": partido.local.nombre_oficial if partido.local else "",
                "local_id": partido.local.id if partido.local else None,
                "visitante": partido.visitante.nombre_oficial if partido.visitante else "",
                "visitante_id": partido.visitante.id if partido.visitante else None,
                "goles_local": partido.goles_local or 0,
                "goles_visitante": partido.goles_visitante or 0,
                "goles_jugador": goles_jugador,
                "tarjetas_amarillas": amarillas,
                "tarjetas_rojas": rojas,
                "titular": titular_map.get(partido.id, False),
                "mvp": mvp,
                "grupo_id": partido.grupo.id if partido.grupo else None,
            })

        # Totales
        totales = {
            "partidos_jugados": len(partidos_list),
            "goles": sum(p["goles_jugador"] for p in partidos_list),
            "tarjetas_amarillas": sum(p["tarjetas_amarillas"] for p in partidos_list),
            "tarjetas_rojas": sum(p["tarjetas_rojas"] for p in partidos_list),
            "partidos_titular": sum(1 for p in partidos_list if p["titular"]),
            "mvps": sum(1 for p in partidos_list if p["mvp"]),
        }

        return {
            "partidos": partidos_list,
            "totales": totales,
        }

# ============================================================
# 3. GET /api/jugadores/historial/?jugador_id=XX
# ============================================================
class JugadorHistorialView(APIView):
    """
    Historial completo consolidado del jugador.
    """
    def get(self, request, format=None):
        jugador_id = request.GET.get("jugador_id")

        if not jugador_id:
            return Response(
                {"detail": "Falta jugador_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            jugador = _get_jugador_by_id_or_slug(jugador_id)
        except Jugador.DoesNotExist:
            return Response(
                {"detail": "Jugador no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Reutilizar método de JugadorFullView
        full_view = JugadorFullView()
        historial = full_view._get_historial_completo(jugador)

        return Response({
            "jugador_id": jugador.id,
            "jugador_nombre": jugador.nombre,
            "historico": historial,
        })


# ============================================================
# 4. GET /api/jugadores/valoraciones/?jugador_id=XX&temporada_id=YY
# ============================================================
class JugadorValoracionesView(APIView):
    """
    Valoraciones FIFA del jugador.
    """
    def get(self, request, format=None):
        jugador_id = request.GET.get("jugador_id")
        temporada_id = request.GET.get("temporada_id")

        if not jugador_id:
            return Response(
                {"detail": "Falta jugador_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            jugador = _get_jugador_by_id_or_slug(jugador_id)
        except Jugador.DoesNotExist:
            return Response(
                {"detail": "Jugador no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Obtener valoración
        qs = ValoracionJugador.objects.filter(jugador=jugador).select_related("temporada")

        if temporada_id:
            try:
                temporada_obj = Temporada.objects.get(id=temporada_id)
                qs = qs.filter(temporada=temporada_obj)
            except Temporada.DoesNotExist:
                pass

        valoracion = qs.order_by("-temporada__nombre").first()

        if not valoracion:
            return Response({
                "jugador_id": jugador.id,
                "temporada": None,
                "valoracion": None,
                "total_votos": 0,
                "ultima_actualizacion": None,
            })

        # Contar votos
        total_votos = VotoValoracionJugador.objects.filter(
            jugador=jugador,
            temporada=valoracion.temporada
        ).count()

        valoracion_ser = ValoracionJugadorSerializer(valoracion)

        return Response({
            "jugador_id": jugador.id,
            "temporada": {
                "id": valoracion.temporada.id,
                "nombre": valoracion.temporada.nombre,
            },
            "valoracion": valoracion_ser.data,
            "total_votos": total_votos,
            "ultima_actualizacion": valoracion.temporada.nombre,  # Por ahora, usar nombre de temporada
        })


# ============================================================
# 5. GET /api/jugadores/partidos/?jugador_id=XX&temporada_id=YY&grupo_id=ZZ&limit=NN
# ============================================================
class JugadorPartidosView(APIView):
    """
    Partidos del jugador con estadísticas.
    """
    def get(self, request, format=None):
        jugador_id = request.GET.get("jugador_id")
        temporada_id = request.GET.get("temporada_id")
        grupo_id = request.GET.get("grupo_id")
        limit = int(request.GET.get("limit", 20))

        if not jugador_id:
            return Response(
                {"detail": "Falta jugador_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            jugador = _get_jugador_by_id_or_slug(jugador_id)
        except Jugador.DoesNotExist:
            return Response(
                {"detail": "Jugador no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Reutilizar método de JugadorFullView
        full_view = JugadorFullView()
        partidos_data = full_view._get_partidos_jugador(jugador, temporada_id, limit)

        # Aplicar filtro de grupo si existe
        if grupo_id and partidos_data["partidos"]:
            partidos_data["partidos"] = [
                p for p in partidos_data["partidos"]
                if p.get("grupo_id") == int(grupo_id)
            ]

        return Response({
            "jugador_id": jugador.id,
            "filtros": {
                "temporada_id": int(temporada_id) if temporada_id else None,
                "grupo_id": int(grupo_id) if grupo_id else None,
            },
            **partidos_data,
        })


# ============================================================
# 6. GET /api/jugadores/lista/?club_id=XX o ?random=true
# ============================================================
class JugadoresListaView(APIView):
    """
    Lista de jugadores:
    - Por club: ?club_id=XX
    - Aleatorios: ?random=true
    """
    
    def get(self, request, format=None):
        club_id = request.GET.get("club_id")
        random = request.GET.get("random", "false").lower() == "true"
        
        # Helper para calcular edad
        def calcular_edad(jugador):
            if jugador.fecha_nacimiento:
                from datetime import date
                today = date.today()
                return today.year - jugador.fecha_nacimiento.year - (
                    (today.month, today.day) < (jugador.fecha_nacimiento.month, jugador.fecha_nacimiento.day)
                )
            return jugador.edad_estimacion
        
        # Caso: jugadores de un club
        if club_id:
            try:
                club = Club.objects.get(id=club_id)
            except Club.DoesNotExist:
                return Response(
                    {"detail": "Club no encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            # Obtener temporada activa o más reciente
            temporada_activa = Temporada.objects.order_by("-id").first()
            
            if not temporada_activa:
                return Response(
                    {"detail": "No hay temporada activa."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            # Obtener jugadores del club en la temporada activa
            participaciones = (
                JugadorEnClubTemporada.objects
                .filter(club=club, temporada=temporada_activa)
                .select_related("jugador", "club", "temporada")
                .order_by("jugador__nombre")
            )
            
            results = []
            for jct in participaciones:
                j = jct.jugador
                edad = calcular_edad(j)
                
                results.append({
                    "id": j.id,
                    "nombre": j.nombre,
                    "apodo": j.apodo or "",
                    "slug": getattr(j, "slug", None),
                    "foto_url": _norm_media(getattr(j, "foto_url", "")),
                    "posicion_principal": j.posicion_principal or "",
                    "edad_display": edad,
                    "club_id": club.id,
                    "club_nombre": club.nombre_oficial,
                    "club_slug": getattr(club, "slug", None),
                    "club_escudo_url": _norm_media(getattr(club, "escudo_url", "")),
                    "temporada_nombre": temporada_activa.nombre,
                    "dorsal": jct.dorsal or "",
                    "partidos_jugados": jct.partidos_jugados,
                    "goles": jct.goles,
                })
            
            return Response({
                "club": {
                    "id": club.id,
                    "nombre": club.nombre_oficial,
                    "slug": getattr(club, "slug", None),
                },
                "temporada": {
                    "id": temporada_activa.id,
                    "nombre": temporada_activa.nombre,
                },
                "count": len(results),
                "results": results,
            })
        
        # Caso: jugadores aleatorios o búsqueda
        search_query = request.GET.get("search", "").strip()
        is_search = bool(search_query)
        
        if random or not club_id:
            # Obtener temporada activa
            temporada_activa = Temporada.objects.order_by("-id").first()
            
            if not temporada_activa:
                return Response(
                    {"detail": "No hay temporada activa."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            # Obtener todas las participaciones de la temporada activa
            participaciones = (
                JugadorEnClubTemporada.objects
                .filter(temporada=temporada_activa)
                .select_related("jugador", "club", "temporada")
            )
            
            # Si hay búsqueda, filtrar por nombre o apodo
            if is_search:
                search_lower = search_query.lower()
                participaciones = participaciones.filter(
                    Q(jugador__nombre__icontains=search_query) |
                    Q(jugador__apodo__icontains=search_query) |
                    Q(club__nombre_oficial__icontains=search_query) |
                    Q(club__nombre_corto__icontains=search_query)
                )
            
            # Agrupar por jugador (una participación por jugador, la más reciente)
            by_jugador = {}
            for jct in participaciones.order_by("jugador_id", "-temporada_id"):
                if jct.jugador_id not in by_jugador:
                    by_jugador[jct.jugador_id] = jct
            
            # Convertir a lista
            entries = []
            for jct in by_jugador.values():
                j = jct.jugador
                c = jct.club
                edad = calcular_edad(j)
                
                entries.append({
                    "id": j.id,
                    "nombre": j.nombre,
                    "apodo": j.apodo or "",
                    "slug": getattr(j, "slug", None),
                    "foto_url": _norm_media(getattr(j, "foto_url", "")),
                    "posicion_principal": j.posicion_principal or "",
                    "edad_display": edad,
                    "club_id": c.id,
                    "club_nombre": c.nombre_oficial,
                    "club_slug": getattr(c, "slug", None),
                    "club_escudo_url": _norm_media(getattr(c, "escudo_url", "")),
                    "temporada_nombre": temporada_activa.nombre,
                    "dorsal": jct.dorsal or "",
                    "partidos_jugados": jct.partidos_jugados,  # Solo de la temporada activa
                    "goles": jct.goles,  # Solo de la temporada activa
                })
            
            # Si es búsqueda, ordenar por nombre; si no, mezclar aleatoriamente y limitar a 24
            if is_search:
                entries.sort(key=lambda x: (x["nombre"] or "").lower())
            else:
                import random as random_module
                random_module.shuffle(entries)
                entries = entries[:24]
            
            return Response({
                "random": not is_search,
                "search": search_query if is_search else None,
                "temporada": {
                    "id": temporada_activa.id,
                    "nombre": temporada_activa.nombre,
                },
                "count": len(entries),
                "results": entries,
            })
        
        # Faltan parámetros
        return Response(
            {"detail": "Debes indicar club_id o random=true."},
            status=status.HTTP_400_BAD_REQUEST,
        )
