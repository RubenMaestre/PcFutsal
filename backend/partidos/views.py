from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Partido, EventoPartido, AlineacionPartidoJugador
from staff.models import StaffEnPartido
from arbitros.models import ArbitrajePartido
from nucleo.models import Grupo
from clubes.models import Club
from jugadores.models import Jugador


class PartidoDetalleView(APIView):
    """
    GET /api/partidos/detalle/?partido_id=XX
    GET /api/partidos/detalle/?identificador_federacion=YY
    
    Devuelve el detalle completo de un partido:
    - Información básica del partido
    - Eventos ordenados por minuto
    - Alineaciones (titulares y suplentes) por equipo
    - Goles y tarjetas por jugador en ese partido
    - Staff técnico
    - Árbitros
    - Estadísticas agregadas
    """

    def _norm_media(self, path: str | None) -> str:
        """Normaliza rutas de media."""
        if not path:
            return ""
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if path.startswith("/media/"):
            return path
        return "/media/" + path.lstrip("/")

    def _get_parte(self, minuto: int | None) -> str:
        """Determina la parte del partido según el minuto."""
        if minuto is None:
            return "desconocida"
        if 1 <= minuto <= 20:
            return "primera"
        elif 21 <= minuto <= 40:
            return "segunda"
        else:
            return "prorroga"

    def get(self, request, format=None):
        partido_id = request.GET.get("partido_id")
        identificador_federacion = request.GET.get("identificador_federacion")

        if not partido_id and not identificador_federacion:
            return Response(
                {"detail": "Falta partido_id o identificador_federacion"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Obtener partido
        try:
            if identificador_federacion:
                partido = (
                    Partido.objects
                    .select_related(
                        "grupo",
                        "grupo__competicion",
                        "grupo__temporada",
                        "local",
                        "visitante",
                    )
                    .get(identificador_federacion=identificador_federacion)
                )
            else:
                partido = (
                    Partido.objects
                    .select_related(
                        "grupo",
                        "grupo__competicion",
                        "grupo__temporada",
                        "local",
                        "visitante",
                    )
                    .get(id=partido_id)
                )
        except Partido.DoesNotExist:
            return Response(
                {"detail": "Partido no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Información básica del partido
        grupo = partido.grupo
        competicion = grupo.competicion if grupo else None
        temporada = grupo.temporada if grupo else None

        partido_data = {
            "id": partido.id,
            "identificador_federacion": partido.identificador_federacion,
            "jornada_numero": partido.jornada_numero,
            "fecha_hora": partido.fecha_hora.isoformat() if partido.fecha_hora else None,
            "jugado": partido.jugado,
            "pabellon": partido.pabellon or "",
            "indice_intensidad": partido.indice_intensidad,
            "grupo": {
                "id": grupo.id if grupo else None,
                "nombre": grupo.nombre if grupo else None,
                "slug": getattr(grupo, "slug", None) if grupo else None,
                "competicion": {
                    "id": competicion.id if competicion else None,
                    "nombre": competicion.nombre if competicion else None,
                    "slug": getattr(competicion, "slug", None) if competicion else None,
                } if competicion else None,
                "temporada": {
                    "id": temporada.id if temporada else None,
                    "nombre": temporada.nombre if temporada else None,
                } if temporada else None,
            } if grupo else None,
            "local": {
                "id": partido.local.id if partido.local else None,
                "nombre": (
                    partido.local.nombre_corto or partido.local.nombre_oficial
                    if partido.local
                    else ""
                ),
                "escudo": self._norm_media(
                    partido.local.escudo_url if partido.local else None
                ),
                "slug": getattr(partido.local, "slug", None) if partido.local else None,
            },
            "visitante": {
                "id": partido.visitante.id if partido.visitante else None,
                "nombre": (
                    partido.visitante.nombre_corto or partido.visitante.nombre_oficial
                    if partido.visitante
                    else ""
                ),
                "escudo": self._norm_media(
                    partido.visitante.escudo_url if partido.visitante else None
                ),
                "slug": getattr(partido.visitante, "slug", None) if partido.visitante else None,
            },
            "goles_local": partido.goles_local,
            "goles_visitante": partido.goles_visitante,
        }

        # Árbitros
        arbitrajes = (
            ArbitrajePartido.objects
            .filter(partido=partido)
            .select_related("arbitro")
            .order_by("id")
        )
        arbitros_data = []
        for arb in arbitrajes:
            if arb.arbitro:
                arbitros_data.append({
                    "id": arb.arbitro.id,
                    "nombre": arb.arbitro.nombre,
                    "rol": arb.rol or "",
                    "slug": getattr(arb.arbitro, "slug", None),
                })
            else:
                arbitros_data.append({
                    "id": None,
                    "nombre": "",
                    "rol": arb.rol or "",
                    "slug": None,
                })

        # Eventos ordenados por minuto
        eventos = (
            EventoPartido.objects
            .filter(partido=partido)
            .select_related("jugador", "club")
            .order_by("minuto", "id")
        )
        eventos_data = []
        for ev in eventos:
            # Determinar lado (local o visitante)
            lado = None
            if ev.club:
                if ev.club.id == partido.local_id:
                    lado = "local"
                elif ev.club.id == partido.visitante_id:
                    lado = "visitante"

            eventos_data.append({
                "id": ev.id,
                "minuto": ev.minuto,
                "tipo_evento": ev.tipo_evento,
                "parte": self._get_parte(ev.minuto),
                "jugador": {
                    "id": ev.jugador.id if ev.jugador else None,
                    "nombre": (
                        ev.jugador.apodo or ev.jugador.nombre
                        if ev.jugador
                        else None
                    ),
                    "slug": getattr(ev.jugador, "slug", None) if ev.jugador else None,
                    "foto": self._norm_media(
                        ev.jugador.foto_url if ev.jugador else None
                    ),
                } if ev.jugador else None,
                "club": {
                    "id": ev.club.id if ev.club else None,
                    "nombre": (
                        ev.club.nombre_corto or ev.club.nombre_oficial
                        if ev.club
                        else None
                    ),
                    "slug": getattr(ev.club, "slug", None) if ev.club else None,
                    "lado": lado,
                } if ev.club else None,
                "nota": ev.nota or "",
            })

        # Alineaciones
        alineaciones = (
            AlineacionPartidoJugador.objects
            .filter(partido=partido)
            .select_related("jugador", "club")
            .order_by("club_id", "titular", "-titular", "dorsal")
        )

        # Contar goles y tarjetas por jugador en este partido
        jugador_stats = {}
        for ev in eventos:
            if ev.jugador_id:
                jug_id = ev.jugador_id
                if jug_id not in jugador_stats:
                    jugador_stats[jug_id] = {
                        "goles": 0,
                        "tarjetas_amarillas": 0,
                        "tarjetas_dobles_amarillas": 0,
                        "tarjetas_rojas": 0,
                        "mvp": False,
                    }
                
                if ev.tipo_evento == "gol":
                    jugador_stats[jug_id]["goles"] += 1
                elif ev.tipo_evento == "amarilla":
                    jugador_stats[jug_id]["tarjetas_amarillas"] += 1
                elif ev.tipo_evento == "doble_amarilla":
                    jugador_stats[jug_id]["tarjetas_dobles_amarillas"] += 1
                elif ev.tipo_evento == "roja":
                    jugador_stats[jug_id]["tarjetas_rojas"] += 1
                elif ev.tipo_evento == "mvp":
                    jugador_stats[jug_id]["mvp"] = True

        # Organizar alineaciones por equipo (separando titulares y suplentes)
        titulares_local = []
        suplentes_local = []
        titulares_visitante = []
        suplentes_visitante = []
        
        for al in alineaciones:
            jugador_info = {
                "jugador_id": al.jugador.id if al.jugador else None,
                "nombre": (
                    al.jugador.apodo or al.jugador.nombre
                    if al.jugador
                    else ""
                ),
                "slug": getattr(al.jugador, "slug", None) if al.jugador else None,
                "foto": self._norm_media(
                    al.jugador.foto_url if al.jugador else None
                ),
                "dorsal": al.dorsal or "",
                "etiqueta": al.etiqueta or "",
                "titular": al.titular,
            }
            
            # Añadir estadísticas del jugador en este partido
            if al.jugador_id and al.jugador_id in jugador_stats:
                stats = jugador_stats[al.jugador_id]
                jugador_info["goles"] = stats["goles"]
                jugador_info["tarjetas_amarillas"] = stats["tarjetas_amarillas"]
                jugador_info["tarjetas_dobles_amarillas"] = stats["tarjetas_dobles_amarillas"]
                jugador_info["tarjetas_rojas"] = stats["tarjetas_rojas"]
                jugador_info["mvp"] = stats["mvp"]
            else:
                jugador_info["goles"] = 0
                jugador_info["tarjetas_amarillas"] = 0
                jugador_info["tarjetas_dobles_amarillas"] = 0
                jugador_info["tarjetas_rojas"] = 0
                jugador_info["mvp"] = False

            if al.club_id == partido.local_id:
                if al.titular:
                    titulares_local.append(jugador_info)
                else:
                    suplentes_local.append(jugador_info)
            elif al.club_id == partido.visitante_id:
                if al.titular:
                    titulares_visitante.append(jugador_info)
                else:
                    suplentes_visitante.append(jugador_info)

        # Staff técnico
        staff_partido = (
            StaffEnPartido.objects
            .filter(partido=partido)
            .select_related("staff", "club")
            .order_by("club_id", "id")
        )
        
        staff_local = []
        staff_visitante = []
        for st in staff_partido:
            staff_info = {
                "nombre": st.nombre,
                "rol": st.rol or "",
                "staff_id": st.staff.id if st.staff else None,
            }
            if st.club_id == partido.local_id:
                staff_local.append(staff_info)
            elif st.club_id == partido.visitante_id:
                staff_visitante.append(staff_info)

        # Estadísticas agregadas
        goles_total = (partido.goles_local or 0) + (partido.goles_visitante or 0)
        goles_primera_parte = len([
            ev for ev in eventos
            if ev.tipo_evento == "gol" and ev.minuto and 1 <= ev.minuto <= 20
        ])
        goles_segunda_parte = len([
            ev for ev in eventos
            if ev.tipo_evento == "gol" and ev.minuto and 21 <= ev.minuto <= 40
        ])
        amarillas_total = len([
            ev for ev in eventos if ev.tipo_evento == "amarilla"
        ])
        dobles_amarillas_total = len([
            ev for ev in eventos if ev.tipo_evento == "doble_amarilla"
        ])
        rojas_total = len([
            ev for ev in eventos if ev.tipo_evento == "roja"
        ])
        mvps = len([
            ev for ev in eventos if ev.tipo_evento == "mvp"
        ])

        estadisticas = {
            "goles_total": goles_total,
            "goles_local": partido.goles_local or 0,
            "goles_visitante": partido.goles_visitante or 0,
            "goles_primera_parte": goles_primera_parte,
            "goles_segunda_parte": goles_segunda_parte,
            "amarillas_total": amarillas_total,
            "dobles_amarillas_total": dobles_amarillas_total,
            "rojas_total": rojas_total,
            "mvps": mvps,
        }

        # Construir respuesta final
        payload = {
            "partido": partido_data,
            "arbitros": arbitros_data,
            "eventos": eventos_data,
            "alineaciones": {
                "local": {
                    "club_id": partido.local_id,
                    "titulares": titulares_local,
                    "suplentes": suplentes_local,
                    "staff": staff_local,
                },
                "visitante": {
                    "club_id": partido.visitante_id,
                    "titulares": titulares_visitante,
                    "suplentes": suplentes_visitante,
                    "staff": staff_visitante,
                },
            },
            "estadisticas": estadisticas,
        }

        return Response(payload, status=status.HTTP_200_OK)


class PartidosListView(APIView):
    """
    GET /api/partidos/lista/
      ?scope=GLOBAL|COMPETICIONES
      &competicion_id=XX (si scope=COMPETICIONES)
      &grupo_id=YY (si scope=COMPETICIONES)
      &jornada=ZZ (opcional)
      &random=true (si queremos aleatorios de última semana)
      &limit=12
    
    Devuelve lista de partidos con filtros.
    """

    def _norm_media(self, path: str | None) -> str:
        """Normaliza rutas de media."""
        if not path:
            return ""
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if path.startswith("/media/"):
            return path
        return "/media/" + path.lstrip("/")

    def get(self, request, format=None):
        scope = request.GET.get("scope", "GLOBAL").upper()
        competicion_id = request.GET.get("competicion_id")
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")
        random = request.GET.get("random") in ["true", "True", "1"]
        week_param = request.GET.get("week")  # fecha del martes en formato YYYY-MM-DD
        limit_param = request.GET.get("limit")

        limit = 12
        if limit_param:
            try:
                limit = int(limit_param)
            except ValueError:
                pass

        # Filtros base
        qs = Partido.objects.select_related(
            "grupo",
            "grupo__competicion",
            "grupo__temporada",
            "local",
            "visitante",
        )

        if scope == "COMPETICIONES":
            if grupo_id:
                try:
                    grupo = Grupo.objects.get(id=grupo_id)
                    qs = qs.filter(grupo=grupo)
                except Grupo.DoesNotExist:
                    return Response(
                        {"detail": "Grupo no encontrado"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            elif competicion_id:
                qs = qs.filter(grupo__competicion_id=competicion_id)

            if jornada_param:
                try:
                    jornada_num = int(jornada_param)
                    qs = qs.filter(jornada_numero=jornada_num)
                except ValueError:
                    pass

        # Filtro por semana (GLOBAL)
        if week_param and scope == "GLOBAL":
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            try:
                # week_param es la fecha del martes en formato YYYY-MM-DD
                tuesday_date = datetime.strptime(week_param, "%Y-%m-%d").date()
                # El miércoles de esa semana es 6 días antes
                wednesday_date = tuesday_date - timedelta(days=6)
                # El martes termina a las 23:59:59
                tuesday_end = datetime.combine(tuesday_date, datetime.max.time())
                # El miércoles comienza a las 19:00
                wednesday_start = datetime.combine(wednesday_date, datetime.min.time().replace(hour=19))
                
                # Convertir a timezone-aware
                if timezone.is_naive(wednesday_start):
                    wednesday_start = timezone.make_aware(wednesday_start)
                if timezone.is_naive(tuesday_end):
                    tuesday_end = timezone.make_aware(tuesday_end)
                
                qs = qs.filter(
                    jugado=True,
                    fecha_hora__gte=wednesday_start,
                    fecha_hora__lte=tuesday_end,
                )
                qs = qs.order_by("?")[:limit] if random else qs.order_by("-fecha_hora", "-id")
            except ValueError:
                # Si el formato de fecha es inválido, usar comportamiento por defecto
                pass
        
        # Modo aleatorio de última semana (si no hay filtro de semana)
        if random and not week_param:
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # Últimos 7 días
            fecha_limite = timezone.now() - timedelta(days=7)
            qs = qs.filter(
                jugado=True,
                fecha_hora__gte=fecha_limite,
            )
            qs = qs.order_by("?")[:limit]
        elif not week_param:
            qs = qs.order_by("-fecha_hora", "-id")

        if limit:
            qs = qs[:limit]

        # Construir respuesta
        partidos_data = []
        for p in qs:
            grupo = p.grupo
            competicion = grupo.competicion if grupo else None
            temporada = grupo.temporada if grupo else None

            partidos_data.append({
                "id": p.id,
                "identificador_federacion": p.identificador_federacion,
                "jornada_numero": p.jornada_numero,
                "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
                "jugado": p.jugado,
                "local": {
                    "id": p.local.id if p.local else None,
                    "nombre": (
                        p.local.nombre_corto or p.local.nombre_oficial
                        if p.local
                        else ""
                    ),
                    "escudo": self._norm_media(
                        p.local.escudo_url if p.local else None
                    ),
                    "slug": getattr(p.local, "slug", None) if p.local else None,
                },
                "visitante": {
                    "id": p.visitante.id if p.visitante else None,
                    "nombre": (
                        p.visitante.nombre_corto or p.visitante.nombre_oficial
                        if p.visitante
                        else ""
                    ),
                    "escudo": self._norm_media(
                        p.visitante.escudo_url if p.visitante else None
                    ),
                    "slug": getattr(p.visitante, "slug", None) if p.visitante else None,
                },
                "goles_local": p.goles_local,
                "goles_visitante": p.goles_visitante,
                "grupo": {
                    "id": grupo.id if grupo else None,
                    "nombre": grupo.nombre if grupo else None,
                    "slug": getattr(grupo, "slug", None) if grupo else None,
                    "competicion": {
                        "id": competicion.id if competicion else None,
                        "nombre": competicion.nombre if competicion else None,
                        "slug": getattr(competicion, "slug", None) if competicion else None,
                    } if competicion else None,
                    "temporada": {
                        "id": temporada.id if temporada else None,
                        "nombre": temporada.nombre if temporada else None,
                    } if temporada else None,
                } if grupo else None,
            })

        payload = {
            "scope": scope,
            "filtros": {
                "competicion_id": int(competicion_id) if competicion_id else None,
                "grupo_id": int(grupo_id) if grupo_id else None,
                "jornada": int(jornada_param) if jornada_param else None,
            },
            "partidos": partidos_data,
        }

        return Response(payload, status=status.HTTP_200_OK)
