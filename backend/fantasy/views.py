# fantasy/views.py
"""
Vistas para el sistema de reconocimientos MVP y Fantasy.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch

from jugadores.models import Jugador
from clubes.models import Club, ClubEnGrupo
from partidos.models import Partido, EventoPartido, AlineacionPartidoJugador
from nucleo.models import Grupo, Temporada
from fantasy.models import (
    MVPPartido, MVPJornadaDivision, MVPJornadaGlobal,
    GoleadorJornadaDivision, MejorEquipoJornadaDivision, MejorEquipoJornadaGlobal,
    PuntosEquipoTotal, PuntosEquipoJornada,
    PuntosMVPJornada, PuntosMVPTotalJugador
)
from valoraciones.views import _coef_division_lookup, _coef_club_lookup, _get_temporada_id, _get_int, _get_bool
from valoraciones.views import _norm_media, _abs_media


class ReconocimientosJugadorView(APIView):
    """
    GET /api/fantasy/jugador/{jugador_id}/reconocimientos/
    
    Devuelve todos los reconocimientos de un jugador:
    - MVP del partido (contador y detalle)
    - MVP de jornada por división (contador y detalle)
    - MVP global de la semana (contador y detalle)
    - Goleador de jornada por división (contador y detalle)
    """
    
    def get(self, request, jugador_id, format=None):
        try:
            jugador = Jugador.objects.get(id=jugador_id)
        except Jugador.DoesNotExist:
            return Response(
                {"detail": "Jugador no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # MVP del partido
        mvp_partidos_qs = MVPPartido.objects.filter(jugador=jugador).select_related(
            "partido__local", "partido__visitante", "partido__grupo__temporada"
        ).order_by("-partido__fecha_hora")
        mvp_partidos_count = mvp_partidos_qs.count()
        
        # MVP jornada división
        mvp_jornadas_division_qs = MVPJornadaDivision.objects.filter(
            jugador=jugador
        ).select_related("grupo__competicion", "temporada").order_by("-temporada", "-jornada")
        mvp_jornadas_division_count = mvp_jornadas_division_qs.count()
        
        # MVP global
        mvp_jornadas_global_qs = MVPJornadaGlobal.objects.filter(
            jugador=jugador
        ).select_related("grupo__competicion", "temporada").order_by("-temporada", "-semana")
        mvp_jornadas_global_count = mvp_jornadas_global_qs.count()
        
        # Goleador jornada división
        goleador_jornadas_qs = GoleadorJornadaDivision.objects.filter(
            jugador=jugador
        ).select_related("grupo__competicion", "temporada").order_by("-temporada", "-jornada")
        goleador_jornadas_count = goleador_jornadas_qs.count()
        
        # Construir detalle de MVP partidos
        mvp_partidos_detalle = []
        for mvp in mvp_partidos_qs[:50]:  # Limitar a 50 más recientes
            partido = mvp.partido
            mvp_partidos_detalle.append({
                "partido_id": partido.id,
                "fecha": partido.fecha_hora.isoformat() if partido.fecha_hora else None,
                "puntos": float(mvp.puntos),
                "local": partido.local.nombre_oficial if partido.local else "",
                "visitante": partido.visitante.nombre_oficial if partido.visitante else "",
                "goles": mvp.goles,
                "tarjetas_amarillas": mvp.tarjetas_amarillas,
                "tarjetas_rojas": mvp.tarjetas_rojas,
            })
        
        # Construir detalle de MVP jornadas división
        mvp_jornadas_division_detalle = []
        for mvp in mvp_jornadas_division_qs:
            # Obtener fecha de algún partido de esa jornada
            partido_ref = Partido.objects.filter(
                grupo=mvp.grupo,
                jornada_numero=mvp.jornada,
                jugado=True
            ).first()
            
            mvp_jornadas_division_detalle.append({
                "temporada": mvp.temporada.nombre,
                "grupo": mvp.grupo.nombre,
                "jornada": mvp.jornada,
                "fecha": partido_ref.fecha_hora.isoformat() if partido_ref and partido_ref.fecha_hora else None,
                "puntos": float(mvp.puntos_con_coef),
                "puntos_base": float(mvp.puntos),
            })
        
        # Construir detalle de MVP global
        mvp_jornadas_global_detalle = []
        for mvp in mvp_jornadas_global_qs:
            # Calcular fechas de inicio y fin de la semana (Miércoles - Domingo)
            from datetime import timedelta, time
            from django.utils import timezone
            
            fecha_martes = mvp.semana
            miercoles = fecha_martes + timedelta(days=1)
            domingo = fecha_martes + timedelta(days=5)
            
            tz = timezone.get_current_timezone()
            from datetime import datetime
            fecha_inicio = timezone.make_aware(
                datetime.combine(miercoles, time(19, 0, 0)), tz
            )
            fecha_fin = timezone.make_aware(
                datetime.combine(domingo, time(21, 0, 0)), tz
            )
            
            mvp_jornadas_global_detalle.append({
                "temporada": mvp.temporada.nombre,
                "semana": fecha_martes.strftime("%Y-%m-%d"),
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat(),
                "puntos": float(mvp.puntos),
                "puntos_base": float(mvp.puntos_base),
                "coef_division": float(mvp.coef_division),
                "grupo": mvp.grupo.nombre,
            })
        
        # Construir detalle de goleador jornadas
        goleador_jornadas_detalle = []
        for goleador in goleador_jornadas_qs:
            partido_ref = Partido.objects.filter(
                grupo=goleador.grupo,
                jornada_numero=goleador.jornada,
                jugado=True
            ).first()
            
            goleador_jornadas_detalle.append({
                "temporada": goleador.temporada.nombre,
                "grupo": goleador.grupo.nombre,
                "jornada": goleador.jornada,
                "fecha": partido_ref.fecha_hora.isoformat() if partido_ref and partido_ref.fecha_hora else None,
                "goles": goleador.goles,
            })
        
        return Response({
            "jugador": {
                "id": jugador.id,
                "nombre": jugador.nombre,
                "apodo": jugador.apodo,
                "slug": getattr(jugador, "slug", None),
            },
            "mvp_partidos": mvp_partidos_count,
            "mvp_jornadas_division": mvp_jornadas_division_count,
            "mvp_jornadas_global": mvp_jornadas_global_count,
            "goleador_jornadas_division": goleador_jornadas_count,
            "detalle": {
                "mvp_partidos": mvp_partidos_detalle,
                "mvp_jornadas_division": mvp_jornadas_division_detalle,
                "mvp_jornadas_global": mvp_jornadas_global_detalle,
                "goleador_jornadas_division": goleador_jornadas_detalle,
            }
        }, status=status.HTTP_200_OK)


class ReconocimientosEquipoView(APIView):
    """
    GET /api/fantasy/equipo/{club_id}/reconocimientos/
    
    Devuelve todos los reconocimientos de un equipo/club:
    - Mejor equipo de jornada por división (contador y detalle)
    - Mejor equipo global de la semana (contador y detalle)
    """
    
    def get(self, request, club_id, format=None):
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return Response(
                {"detail": "Club no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mejor equipo jornada división
        mejores_equipos_division_qs = MejorEquipoJornadaDivision.objects.filter(
            club=club
        ).select_related("grupo__competicion", "temporada").order_by("-temporada", "-jornada")
        mejores_equipos_division_count = mejores_equipos_division_qs.count()
        
        # Mejor equipo global
        mejores_equipos_global_qs = MejorEquipoJornadaGlobal.objects.filter(
            club=club
        ).select_related("grupo__competicion", "temporada").order_by("-temporada", "-semana")
        mejores_equipos_global_count = mejores_equipos_global_qs.count()
        
        # Construir detalle de mejor equipo división
        mejores_equipos_division_detalle = []
        for mejor_equipo in mejores_equipos_division_qs:
            partido_ref = Partido.objects.filter(
                grupo=mejor_equipo.grupo,
                jornada_numero=mejor_equipo.jornada,
                jugado=True
            ).first()
            
            mejores_equipos_division_detalle.append({
                "temporada": mejor_equipo.temporada.nombre,
                "grupo": mejor_equipo.grupo.nombre,
                "jornada": mejor_equipo.jornada,
                "fecha": partido_ref.fecha_hora.isoformat() if partido_ref and partido_ref.fecha_hora else None,
                "puntos": float(mejor_equipo.puntos),
                "victorias": mejor_equipo.victorias,
                "empates": mejor_equipo.empates,
                "derrotas": mejor_equipo.derrotas,
                "goles_favor": mejor_equipo.goles_favor,
                "goles_contra": mejor_equipo.goles_contra,
            })
        
        # Construir detalle de mejor equipo global
        mejores_equipos_global_detalle = []
        for mejor_equipo in mejores_equipos_global_qs:
            # Calcular fechas de inicio y fin de la semana
            from datetime import timedelta, time, datetime
            from django.utils import timezone
            
            fecha_martes = mejor_equipo.semana
            miercoles = fecha_martes + timedelta(days=1)
            domingo = fecha_martes + timedelta(days=5)
            
            tz = timezone.get_current_timezone()
            fecha_inicio = timezone.make_aware(
                datetime.combine(miercoles, time(19, 0, 0)), tz
            )
            fecha_fin = timezone.make_aware(
                datetime.combine(domingo, time(21, 0, 0)), tz
            )
            
            mejores_equipos_global_detalle.append({
                "temporada": mejor_equipo.temporada.nombre,
                "semana": fecha_martes.strftime("%Y-%m-%d"),
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat(),
                "puntos": float(mejor_equipo.puntos),
                "puntos_base": float(mejor_equipo.puntos_base),
                "coef_division": float(mejor_equipo.coef_division),
                "grupo": mejor_equipo.grupo.nombre,
                "victorias": mejor_equipo.victorias,
                "empates": mejor_equipo.empates,
                "derrotas": mejor_equipo.derrotas,
            })
        
        return Response({
            "club": {
                "id": club.id,
                "nombre": club.nombre_oficial,
                "nombre_corto": club.nombre_corto,
                "slug": getattr(club, "slug", None),
            },
            "mejor_equipo_jornadas_division": mejores_equipos_division_count,
            "mejor_equipo_jornadas_global": mejores_equipos_global_count,
            "detalle": {
                "mejor_equipo_jornadas_division": mejores_equipos_division_detalle,
                "mejor_equipo_jornadas_global": mejores_equipos_global_detalle,
            }
        }, status=status.HTTP_200_OK)


class MVPPartidoView(APIView):
    """
    GET /api/fantasy/partido/{partido_id}/mvp/
    
    Devuelve el MVP de un partido específico.
    """
    
    def get(self, request, partido_id, format=None):
        try:
            partido = Partido.objects.select_related(
                "local", "visitante", "grupo__competicion"
            ).get(id=partido_id)
        except Partido.DoesNotExist:
            return Response(
                {"detail": "Partido no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            mvp = MVPPartido.objects.select_related(
                "jugador", "partido__local", "partido__visitante"
            ).get(partido=partido)
        except MVPPartido.DoesNotExist:
            return Response({
                "partido": {
                    "id": partido.id,
                    "local": partido.local.nombre_oficial if partido.local else "",
                    "visitante": partido.visitante.nombre_oficial if partido.visitante else "",
                    "fecha": partido.fecha_hora.isoformat() if partido.fecha_hora else None,
                },
                "mvp": None,
                "detail": "Este partido aún no tiene MVP calculado."
            }, status=status.HTTP_200_OK)
        
        # Obtener foto del jugador
        foto_url = ""
        if hasattr(mvp.jugador, "foto_url") and mvp.jugador.foto_url:
            foto_url = mvp.jugador.foto_url
            if not foto_url.startswith("http") and not foto_url.startswith("/"):
                foto_url = "/media/" + foto_url.lstrip("/")
        
        return Response({
            "partido": {
                "id": partido.id,
                "local": partido.local.nombre_oficial if partido.local else "",
                "visitante": partido.visitante.nombre_oficial if partido.visitante else "",
                "fecha": partido.fecha_hora.isoformat() if partido.fecha_hora else None,
            },
            "mvp": {
                "jugador": {
                    "id": mvp.jugador.id,
                    "nombre": mvp.jugador.nombre,
                    "apodo": mvp.jugador.apodo,
                    "slug": getattr(mvp.jugador, "slug", None),
                    "foto": foto_url,
                },
                "puntos": float(mvp.puntos),
                "goles": mvp.goles,
                "tarjetas_amarillas": mvp.tarjetas_amarillas,
                "tarjetas_rojas": mvp.tarjetas_rojas,
                "mvp_evento": mvp.mvp_evento,
                "equipo_ganador": mvp.equipo_ganador,
            }
        }, status=status.HTTP_200_OK)


class EquipoGlobalOptimizedView(APIView):
    """
    GET /api/fantasy/equipo-global-optimized/?temporada_id=4&top=200
    
    Endpoint optimizado que lee de PuntosEquipoTotal y PuntosEquipoJornada
    para devolver el ranking global de equipos de forma rápida.
    
    Parámetros:
    - temporada_id (requerido): ID de la temporada
    - from (opcional): Fecha inicio YYYY-MM-DD (para filtrar puntos de semana)
    - to (opcional): Fecha fin YYYY-MM-DD (para filtrar puntos de semana)
    - top (opcional): Número máximo de equipos a devolver (default: 100)
    - strict (opcional): 1 para modo estricto (no usar fallback)
    
    Devuelve:
    - ranking_global: Lista de equipos ordenados por puntos totales (con coeficiente aplicado)
    - score_global: Puntos totales acumulados con coeficiente de división aplicado
    - score/score_semana: Puntos de la semana seleccionada (si hay filtro)
    """
    
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6
    
    def _wed_sun_window_from_date(self, d):
        """Ventana semanal: Miércoles 19:00 → Domingo 21:00 de la semana de 'd'."""
        from datetime import datetime, time, timedelta
        from django.utils import timezone
        monday = d - timedelta(days=d.weekday())
        wednesday = monday + timedelta(days=2)
        sunday = monday + timedelta(days=6)
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.combine(wednesday, time(19, 0, 0)), tz)
        end = timezone.make_aware(datetime.combine(sunday, time(21, 0, 0)), tz)
        return start, end
    
    def _parse_date(self, s: str | None):
        if not s:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None
    
    def get(self, request, format=None):
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        top_n = _get_int(request, "top", 100)
        
        # Obtener coeficientes de división
        coef_division = _coef_division_lookup(temporada_id, self.JORNADA_REF_COEF)
        
        # Obtener todos los puntos totales de la temporada
        puntos_totales_qs = (
            PuntosEquipoTotal.objects
            .filter(temporada_id=temporada_id)
            .select_related("club", "temporada")
            .prefetch_related("club__grupos")
        )
        
        # Obtener grupos para mapear competición y aplicar coeficiente
        grupos_lookup = {}
        for grupo in Grupo.objects.filter(temporada_id=temporada_id).select_related("competicion"):
            grupos_lookup[grupo.id] = {
                "competicion_id": grupo.competicion_id,
                "competicion_nombre": grupo.competicion.nombre,
                "grupo_nombre": grupo.nombre,
            }
        
        # Obtener puntos de semana si hay filtro
        from_date = self._parse_date(request.GET.get("from"))
        to_date = self._parse_date(request.GET.get("to"))
        puntos_semana = {}
        
        if from_date and to_date:
            # Buscar puntos de jornadas en ese rango de fechas
            from datetime import datetime, time
            from django.utils import timezone
            start_dt = timezone.make_aware(
                datetime.combine(from_date, time.min)
            )
            end_dt = timezone.make_aware(
                datetime.combine(to_date, time.max)
            )
            
            # Obtener TODOS los partidos en ese rango (no solo jugados) para determinar jornadas
            # Esto es importante porque la última semana puede tener partidos aún no jugados
            partidos_rango = Partido.objects.filter(
                grupo__temporada_id=temporada_id,
                fecha_hora__gte=start_dt,
                fecha_hora__lte=end_dt
            ).values_list("grupo_id", "jornada_numero").distinct()
            
            jornadas_grupo = {}
            for grupo_id, jornada in partidos_rango:
                if grupo_id not in jornadas_grupo:
                    jornadas_grupo[grupo_id] = []
                if jornada not in jornadas_grupo[grupo_id]:
                    jornadas_grupo[grupo_id].append(jornada)
            
            # Obtener puntos almacenados de esas jornadas
            for grupo_id, jornadas in jornadas_grupo.items():
                puntos_jornada_qs = PuntosEquipoJornada.objects.filter(
                    temporada_id=temporada_id,
                    grupo_id=grupo_id,
                    jornada__in=jornadas
                ).select_related("club", "grupo__competicion")
                
                # Sumar puntos almacenados
                for pj in puntos_jornada_qs:
                    club_id = pj.club_id
                    competicion_id = pj.grupo.competicion_id
                    coef_div = float(coef_division.get(competicion_id, 1.0))
                    puntos_con_coef = round(float(pj.puntos) * coef_div, 4)
                    
                    if club_id not in puntos_semana:
                        puntos_semana[club_id] = 0.0
                    puntos_semana[club_id] += puntos_con_coef
                
                # Calcular en tiempo real puntos de partidos jugados en el rango
                # (útil para la última semana que puede no tener puntos almacenados aún)
                try:
                    grupo = Grupo.objects.get(id=grupo_id, temporada_id=temporada_id)
                except Grupo.DoesNotExist:
                    continue
                
                # Obtener partidos jugados de esas jornadas en ese grupo dentro del rango
                partidos_jugados = Partido.objects.filter(
                    grupo=grupo,
                    jornada_numero__in=jornadas,
                    jugado=True,
                    fecha_hora__gte=start_dt,
                    fecha_hora__lte=end_dt
                ).select_related("local", "visitante")
                
                if partidos_jugados.exists():
                    # Calcular puntos en tiempo real usando la misma lógica
                    from valoraciones.views import EquipoJornadaGlobalView
                    view_equipo = EquipoJornadaGlobalView()
                    clasif_rows = ClubEnGrupo.objects.filter(grupo=grupo).select_related("club")
                    clasif_lookup = {
                        c.club_id: {
                            "pos": c.posicion_actual,
                            "racha": (c.racha or "").strip().upper(),
                        }
                        for c in clasif_rows
                    }
                    
                    coef_club = _coef_club_lookup(temporada_id, self.JORNADA_REF_COEF)
                    competicion_id = grupo.competicion_id
                    coef_div = float(coef_division.get(competicion_id, 1.0))
                    
                    # Mapear qué clubes ya tienen puntos almacenados para estas jornadas
                    clubes_con_puntos_almacenados = {pj.club_id for pj in puntos_jornada_qs}
                    
                    for p in partidos_jugados:
                        gl = p.goles_local or 0
                        gv = p.goles_visitante or 0
                        lid = p.local_id
                        vid = p.visitante_id
                        
                        # Solo calcular si no tiene puntos almacenados para esta jornada
                        # (para evitar duplicar si ya están almacenados)
                        if lid not in clubes_con_puntos_almacenados:
                            # Calcular puntos local
                            base_local = 1.0 if gl > gv else (0.4 if gl == gv else 0.0)
                            score_local = (
                                base_local
                                + view_equipo._bonus_rival_fuerte(coef_club.get(vid, 0.5))
                                + view_equipo._bonus_diferencia(gl - gv)
                                + view_equipo._bonus_rompe_racha(clasif_lookup.get(vid, {}).get("racha"))
                                + view_equipo._penalizacion_rival_debil(clasif_lookup.get(vid, {}).get("pos"))
                            )
                            score_local *= (0.9 + coef_club.get(lid, 0.5))
                            
                            if lid not in puntos_semana:
                                puntos_semana[lid] = 0.0
                            puntos_semana[lid] += round(score_local * coef_div, 4)
                        
                        if vid not in clubes_con_puntos_almacenados:
                            # Calcular puntos visitante
                            base_visit = 1.0 if gv > gl else (0.4 if gv == gl else 0.0)
                            bonus_fuera = 0.25 if gv > gl else 0.0
                            score_visit = (
                                base_visit
                                + view_equipo._bonus_rival_fuerte(coef_club.get(lid, 0.5))
                                + view_equipo._bonus_diferencia(gv - gl)
                                + view_equipo._bonus_rompe_racha(clasif_lookup.get(lid, {}).get("racha"))
                                + view_equipo._penalizacion_rival_debil(clasif_lookup.get(lid, {}).get("pos"))
                                + bonus_fuera
                            )
                            score_visit *= (0.9 + coef_club.get(vid, 0.5))
                            
                            if vid not in puntos_semana:
                                puntos_semana[vid] = 0.0
                            puntos_semana[vid] += round(score_visit * coef_div, 4)
        
        # Construir ranking
        # Necesitamos calcular puntos por grupo y aplicar coeficiente correctamente
        # porque un club puede estar en múltiples grupos con diferentes coeficientes
        ranking_data = []
        clubes_procesados = {}
        
        # Obtener todos los puntos por jornada agrupados por club y grupo
        puntos_por_club_grupo = {}
        puntos_jornada_qs = (
            PuntosEquipoJornada.objects
            .filter(temporada_id=temporada_id)
            .select_related("club", "grupo__competicion")
        )
        
        for pj in puntos_jornada_qs:
            club_id = pj.club_id
            grupo_id = pj.grupo_id
            competicion_id = pj.grupo.competicion_id
            coef_div = float(coef_division.get(competicion_id, 1.0))
            
            # Clave única: club_id
            if club_id not in puntos_por_club_grupo:
                puntos_por_club_grupo[club_id] = {
                    "club": pj.club,
                    "puntos_total_con_coef": 0.0,
                    "grupos": [],
                }
            
            # Sumar puntos con coeficiente aplicado
            puntos_con_coef = round(float(pj.puntos) * coef_div, 4)
            puntos_por_club_grupo[club_id]["puntos_total_con_coef"] += puntos_con_coef
            
            # Guardar info del grupo (para mostrar en la respuesta)
            if grupo_id not in [g["grupo_id"] for g in puntos_por_club_grupo[club_id]["grupos"]]:
                puntos_por_club_grupo[club_id]["grupos"].append({
                    "grupo_id": grupo_id,
                    "grupo_nombre": pj.grupo.nombre,
                    "competicion_id": competicion_id,
                    "competicion_nombre": pj.grupo.competicion.nombre,
                })
        
        # Construir ranking final
        for club_id, data in puntos_por_club_grupo.items():
            club = data["club"]
            puntos_total_con_coef = round(data["puntos_total_con_coef"], 4)
            
            # Obtener grupo principal (el primero o el más reciente)
            grupo_principal = data["grupos"][0] if data["grupos"] else None
            if not grupo_principal:
                continue
            
            # Puntos de la semana (si hay filtro)
            # Ya están con coeficiente aplicado desde el cálculo anterior
            puntos_semana_val = puntos_semana.get(club_id, None)
            if puntos_semana_val is not None:
                puntos_semana_val = round(puntos_semana_val, 4)
            
            # Obtener escudo
            escudo_url = _norm_media(club.escudo_url or "")
            
            ranking_data.append({
                "club_id": club_id,
                "nombre": club.nombre_corto or club.nombre_oficial,
                "escudo": escudo_url,
                "slug": club.slug or None,
                "competicion_nombre": grupo_principal["competicion_nombre"],
                "grupo_nombre": grupo_principal["grupo_nombre"],
                "score_global": puntos_total_con_coef,
                "score_total": puntos_total_con_coef,
                "total_score": puntos_total_con_coef,
                "acumulado": puntos_total_con_coef,
                "score": puntos_semana_val,
                "score_week": puntos_semana_val,
                "score_semana": puntos_semana_val,
                "puntos": puntos_semana_val,
            })
        
        # Ordenar por puntos totales con coeficiente aplicado (descendente)
        ranking_data.sort(key=lambda x: x["score_global"] or 0, reverse=True)
        
        # Limitar a top_n
        if top_n > 0:
            ranking_data = ranking_data[:top_n]
        
        # URLs absolutas
        for row in ranking_data:
            row["escudo"] = _abs_media(request, row.get("escudo", ""))
        
        # Construir respuesta
        window_meta = {}
        if from_date and to_date:
            window_meta = {
                "start": from_date.isoformat(),
                "end": to_date.isoformat(),
                "status": "ok",
                "matched_games": len(puntos_semana),
            }
        
        return Response({
            "temporada_id": temporada_id,
            "window": window_meta,
            "equipo_de_la_jornada_global": ranking_data[0] if ranking_data else None,
            "ranking_global": ranking_data,
        }, status=status.HTTP_200_OK)


class MVPGlobalOptimizedView(APIView):
    """
    GET /api/fantasy/mvp-global-optimized/?temporada_id=4&from=2025-11-24&to=2025-11-30&top=200
    
    Endpoint optimizado que lee directamente de PuntosMVPJornada y PuntosMVPTotalJugador
    sin recalcular nada. Mucho más rápido que el endpoint original.
    
    - puntos_semana: puntos de la semana seleccionada (suma de jornadas en el rango)
    - puntos_global: puntos totales acumulados de toda la temporada
    """
    
    TEMPORADA_ID_BASE = 4
    
    def _parse_date(self, s: str | None):
        if not s:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None
    
    def get(self, request, format=None):
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        top_n = _get_int(request, "top", 200)
        from_date = self._parse_date(request.GET.get("from"))
        to_date = self._parse_date(request.GET.get("to"))
        only_porteros = _get_bool(request, "only_porteros", False)
        
        # Obtener coeficientes de división (para mostrar en la respuesta)
        coef_division = _coef_division_lookup(temporada_id, 6)
        
        # 1. Obtener puntos TOTALES de todos los jugadores (de toda la temporada)
        puntos_totales_qs = (
            PuntosMVPTotalJugador.objects
            .filter(temporada_id=temporada_id)
            .select_related("jugador")
        )
        
        # Si hay filtro de porteros, filtrar
        if only_porteros:
            puntos_totales_qs = puntos_totales_qs.filter(
                jugador__posicion_principal="portero"
            )
        
        # Construir diccionario de puntos totales por jugador
        puntos_totales_dict = {}
        for pt in puntos_totales_qs:
            puntos_totales_dict[pt.jugador_id] = {
                "puntos_global": round(float(pt.puntos_con_coef_total)),
                "goles_total": pt.goles_total,
                "partidos_total": pt.partidos_total,
            }
        
        # 2. Si hay filtro de fechas, obtener puntos de la semana
        puntos_semana_dict = {}
        partidos_semana_ids = []
        
        if from_date and to_date:
            from datetime import datetime, time
            from django.utils import timezone
            
            start_dt = timezone.make_aware(datetime.combine(from_date, time.min))
            end_dt = timezone.make_aware(datetime.combine(to_date, time.max))
            
            # Obtener partidos en el rango de fechas
            partidos_semana = (
                Partido.objects
                .filter(
                    grupo__temporada_id=temporada_id,
                    jugado=True,
                    fecha_hora__gte=start_dt,
                    fecha_hora__lte=end_dt
                )
                .values_list("grupo_id", "jornada_numero")
                .distinct()
            )
            
            # Agrupar jornadas por grupo
            jornadas_por_grupo = {}
            for grupo_id, jornada in partidos_semana:
                if grupo_id not in jornadas_por_grupo:
                    jornadas_por_grupo[grupo_id] = set()
                jornadas_por_grupo[grupo_id].add(jornada)
            
            # Obtener puntos de esas jornadas desde PuntosMVPJornada
            for grupo_id, jornadas in jornadas_por_grupo.items():
                puntos_jornada_qs = (
                    PuntosMVPJornada.objects
                    .filter(
                        temporada_id=temporada_id,
                        grupo_id=grupo_id,
                        jornada__in=jornadas
                    )
                    .select_related("jugador", "grupo__competicion")
                )
                
                if only_porteros:
                    puntos_jornada_qs = puntos_jornada_qs.filter(
                        jugador__posicion_principal="portero"
                    )
                
                for pj in puntos_jornada_qs:
                    jugador_id = pj.jugador_id
                    if jugador_id not in puntos_semana_dict:
                        puntos_semana_dict[jugador_id] = {
                            "puntos_semana": 0.0,
                            "goles_semana": 0,
                            "partidos_semana": 0,
                        }
                    
                    puntos_semana_dict[jugador_id]["puntos_semana"] += float(pj.puntos_con_coef)
                    puntos_semana_dict[jugador_id]["goles_semana"] += pj.goles
                    puntos_semana_dict[jugador_id]["partidos_semana"] += pj.partidos_jugados
                
                # Redondear puntos de la semana después de sumar todas las jornadas
                for jug_id in puntos_semana_dict:
                    puntos_semana_dict[jug_id]["puntos_semana"] = round(puntos_semana_dict[jug_id]["puntos_semana"])
            
            # Contar partidos para el window_meta
            partidos_semana_ids = list(
                Partido.objects
                .filter(
                    grupo__temporada_id=temporada_id,
                    jugado=True,
                    fecha_hora__gte=start_dt,
                    fecha_hora__lte=end_dt
                )
                .values_list("id", flat=True)
            )
        
        # 3. Obtener información de jugadores y clubs
        jugador_ids = set(puntos_totales_dict.keys())
        if puntos_semana_dict:
            jugador_ids.update(puntos_semana_dict.keys())
        
        jugador_ids = list(jugador_ids)
        
        jugadores_lookup = {}
        for j in Jugador.objects.filter(id__in=jugador_ids):
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
                "slug": getattr(j, "slug", None),
                "foto": foto_final,
                "posicion_principal": j.posicion_principal or "",
            }
        
        # Obtener clubes de los jugadores (necesitamos buscar en alineaciones o partidos recientes)
        # Para optimizar, usamos el último partido de cada jugador para obtener su club
        club_ids = set()
        club_por_jugador = {}
        
        # Buscar clubes desde PuntosMVPJornada (última jornada de cada jugador)
        ultimas_jornadas = (
            PuntosMVPJornada.objects
            .filter(temporada_id=temporada_id, jugador_id__in=jugador_ids)
            .select_related("jugador", "grupo")
            .order_by("jugador_id", "-jornada")
            .distinct("jugador_id")
        )
        
        # Obtener clubes desde partidos recientes
        for jugador_id in jugador_ids:
            # Buscar en alineaciones recientes
            alineacion_reciente = (
                AlineacionPartidoJugador.objects
                .filter(
                    jugador_id=jugador_id,
                    partido__grupo__temporada_id=temporada_id,
                    partido__jugado=True
                )
                .select_related("partido__grupo__competicion")
                .order_by("-partido__fecha_hora")
                .first()
            )
            
            if alineacion_reciente:
                club_id = alineacion_reciente.club_id
                club_por_jugador[jugador_id] = club_id
                club_ids.add(club_id)
        
        clubs_lookup = {}
        if club_ids:
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
                "competicion_id": grupo.competicion_id,
            }
        
        # 4. Construir ranking combinando datos
        ranking_data = []
        for jugador_id in jugador_ids:
            jugador_info = jugadores_lookup.get(jugador_id, {})
            puntos_totales = puntos_totales_dict.get(jugador_id, {
                "puntos_global": 0.0,
                "goles_total": 0,
                "partidos_total": 0,
            })
            puntos_semana = puntos_semana_dict.get(jugador_id, {
                "puntos_semana": None,
                "goles_semana": 0,
                "partidos_semana": 0,
            })
            
            club_id = club_por_jugador.get(jugador_id)
            club_info = clubs_lookup.get(club_id, {}) if club_id else {}
            
            # Obtener grupo principal (del último partido o de la última jornada con puntos)
            grupo_id = None
            grupo_info = {}
            coef_div = 1.0
            
            # Buscar grupo desde PuntosMVPJornada (última jornada)
            ultima_jornada = (
                PuntosMVPJornada.objects
                .filter(temporada_id=temporada_id, jugador_id=jugador_id)
                .select_related("grupo__competicion")
                .order_by("-jornada")
                .first()
            )
            
            if ultima_jornada:
                grupo_id = ultima_jornada.grupo_id
                coef_div = float(ultima_jornada.coef_division)
                grupo_info = grupos_lookup.get(grupo_id, {})
            
            # Asegurar que los puntos estén redondeados
            puntos_semana_redondeado = round(puntos_semana["puntos_semana"]) if puntos_semana["puntos_semana"] is not None else None
            puntos_global_redondeado = round(puntos_totales["puntos_global"])
            
            ranking_data.append({
                "jugador_id": jugador_id,
                "nombre": jugador_info.get("nombre", ""),
                "slug": jugador_info.get("slug"),
                "foto": jugador_info.get("foto", ""),
                "club_id": club_id,
                "club_nombre": club_info.get("club_nombre", ""),
                "club_escudo": club_info.get("club_escudo", ""),
                "puntos": puntos_semana_redondeado,
                "puntos_semana": puntos_semana_redondeado,
                "puntos_global": puntos_global_redondeado,
                "puntos_totales": puntos_global_redondeado,
                "total_points": puntos_global_redondeado,
                "coef_division": round(coef_div, 2),  # Coeficiente con 2 decimales para mostrar
                "goles_jornada": puntos_semana.get("goles_semana", 0) if puntos_semana["puntos_semana"] is not None else None,
                "grupo_id": grupo_id,
                "grupo_nombre": grupo_info.get("grupo_nombre", ""),
                "competicion_id": grupo_info.get("competicion_id"),
                "competicion_nombre": grupo_info.get("competicion_nombre", ""),
            })
        
        # 5. Ordenar por puntos totales (descendente)
        ranking_data.sort(key=lambda x: x["puntos_global"], reverse=True)
        
        # 6. Si hay offset, saltar los primeros (para empezar desde el 4º)
        offset = _get_int(request, "offset", 0)
        if offset > 0:
            ranking_data = ranking_data[offset:]
        
        # 7. Limitar a top_n
        if top_n > 0:
            ranking_data = ranking_data[:top_n]
        
        # 7. Construir respuesta
        window_meta = {
            "start": from_date.isoformat() if from_date else None,
            "end": to_date.isoformat() if to_date else None,
            "status": "ok",
            "matched_games": len(partidos_semana_ids) if (from_date and to_date) else 0,
        }
        
        # Jugador de la jornada global (el primero del ranking de la semana)
        jugador_jornada_global = None
        if from_date and to_date and ranking_data:
            # Ordenar por puntos de la semana para encontrar el mejor
            ranking_semana = [r for r in ranking_data if r["puntos_semana"] is not None]
            if ranking_semana:
                ranking_semana.sort(key=lambda x: x["puntos_semana"] or 0, reverse=True)
                jugador_jornada_global = ranking_semana[0]
        
        return Response({
            "temporada_id": temporada_id,
            "window": window_meta,
            "jugador_de_la_jornada_global": jugador_jornada_global,
            "ranking_global": ranking_data,
        }, status=status.HTTP_200_OK)


class MVPTop3OptimizedView(APIView):
    """
    GET /api/fantasy/mvp-top3-optimized/?temporada_id=4&from=2025-11-24&to=2025-11-30
    
    Endpoint optimizado que devuelve SOLO los 3 primeros jugadores del ranking MVP.
    Diseñado para mostrar en un podio destacado.
    
    - puntos_semana: puntos de la semana seleccionada (suma de jornadas en el rango)
    - puntos_global: puntos totales acumulados de toda la temporada
    """
    
    TEMPORADA_ID_BASE = 4
    
    def _parse_date(self, s: str | None):
        if not s:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None
    
    def get(self, request, format=None):
        from datetime import datetime, time
        from django.utils import timezone
        
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        from_date = self._parse_date(request.GET.get("from"))
        to_date = self._parse_date(request.GET.get("to"))
        only_porteros = _get_bool(request, "only_porteros", False)
        
        # Obtener coeficientes de división (para mostrar en la respuesta)
        coef_division = _coef_division_lookup(temporada_id, 6)
        
        # 1. Obtener puntos TOTALES de todos los jugadores (de toda la temporada)
        # Ordenados por puntos totales descendente, limitado a 3
        puntos_totales_qs = (
            PuntosMVPTotalJugador.objects
            .filter(temporada_id=temporada_id)
            .select_related("jugador")
            .order_by("-puntos_con_coef_total")
        )
        
        # Si hay filtro de porteros, filtrar
        if only_porteros:
            puntos_totales_qs = puntos_totales_qs.filter(
                jugador__posicion_principal="portero"
            )
        
        # Limitar a los 3 primeros
        puntos_totales_qs = puntos_totales_qs[:3]
        
        # Construir diccionario de puntos totales por jugador
        puntos_totales_dict = {}
        for pt in puntos_totales_qs:
            puntos_totales_dict[pt.jugador_id] = {
                "puntos_global": round(float(pt.puntos_con_coef_total)),
                "goles_total": pt.goles_total,
                "partidos_total": pt.partidos_total,
            }
        
        if not puntos_totales_dict:
            return Response({
                "temporada_id": temporada_id,
                "window": {"status": "ok", "matched_games": 0} if (from_date and to_date) else None,
                "top3": [],
            }, status=status.HTTP_200_OK)
        
        # 2. Si hay filtro de fechas, obtener puntos de la semana
        puntos_semana_dict = {}
        partidos_semana_ids = []
        
        if from_date and to_date:
            start_dt = timezone.make_aware(datetime.combine(from_date, time.min))
            end_dt = timezone.make_aware(datetime.combine(to_date, time.max))
            
            # Obtener partidos en el rango de fechas
            partidos_semana = (
                Partido.objects
                .filter(
                    grupo__temporada_id=temporada_id,
                    jugado=True,
                    fecha_hora__gte=start_dt,
                    fecha_hora__lte=end_dt
                )
                .values_list("grupo_id", "jornada_numero")
                .distinct()
            )
            
            # Agrupar jornadas por grupo
            jornadas_por_grupo = {}
            for grupo_id, jornada in partidos_semana:
                if grupo_id not in jornadas_por_grupo:
                    jornadas_por_grupo[grupo_id] = set()
                jornadas_por_grupo[grupo_id].add(jornada)
            
            # Obtener puntos de esas jornadas desde PuntosMVPJornada
            for grupo_id, jornadas in jornadas_por_grupo.items():
                puntos_jornada_qs = (
                    PuntosMVPJornada.objects
                    .filter(
                        temporada_id=temporada_id,
                        grupo_id=grupo_id,
                        jornada__in=jornadas,
                        jugador_id__in=list(puntos_totales_dict.keys())  # Solo los top 3
                    )
                    .select_related("jugador", "grupo__competicion")
                )
                
                if only_porteros:
                    puntos_jornada_qs = puntos_jornada_qs.filter(
                        jugador__posicion_principal="portero"
                    )
                
                for pj in puntos_jornada_qs:
                    jugador_id = pj.jugador_id
                    if jugador_id not in puntos_semana_dict:
                        puntos_semana_dict[jugador_id] = {
                            "puntos_semana": 0.0,
                            "goles_semana": 0,
                            "partidos_semana": 0,
                        }
                    
                    puntos_semana_dict[jugador_id]["puntos_semana"] += float(pj.puntos_con_coef)
                    puntos_semana_dict[jugador_id]["goles_semana"] += pj.goles
                    puntos_semana_dict[jugador_id]["partidos_semana"] += pj.partidos_jugados
                
                # Redondear puntos de la semana después de sumar todas las jornadas
                for jug_id in puntos_semana_dict:
                    puntos_semana_dict[jug_id]["puntos_semana"] = round(puntos_semana_dict[jug_id]["puntos_semana"])
            
            # Contar partidos para el window_meta
            partidos_semana_ids = list(
                Partido.objects
                .filter(
                    grupo__temporada_id=temporada_id,
                    jugado=True,
                    fecha_hora__gte=start_dt,
                    fecha_hora__lte=end_dt
                )
                .values_list("id", flat=True)
            )
        
        # 3. Obtener información de jugadores y clubs
        jugador_ids = list(puntos_totales_dict.keys())
        
        jugadores_lookup = {}
        for j in Jugador.objects.filter(id__in=jugador_ids):
            # Usar _norm_media para formatear la foto (igual que en otros endpoints)
            foto_final = _norm_media(j.foto_url or "")
            
            jugadores_lookup[j.id] = {
                "nombre": j.apodo or j.nombre,  # Usar apodo si existe, sino nombre
                "slug": getattr(j, "slug", None),
                "foto": foto_final,
                "posicion_principal": j.posicion_principal or "",
            }
        
        # Obtener clubes de los jugadores
        club_ids = set()
        club_por_jugador = {}
        
        for jugador_id in jugador_ids:
            alineacion_reciente = (
                AlineacionPartidoJugador.objects
                .filter(
                    jugador_id=jugador_id,
                    partido__grupo__temporada_id=temporada_id,
                    partido__jugado=True
                )
                .select_related("partido__grupo__competicion")
                .order_by("-partido__fecha_hora")
                .first()
            )
            
            if alineacion_reciente:
                club_id = alineacion_reciente.club_id
                club_por_jugador[jugador_id] = club_id
                club_ids.add(club_id)
        
        clubs_lookup = {}
        if club_ids:
            for c in Club.objects.filter(id__in=club_ids):
                # Usar _norm_media para formatear el escudo (igual que en EquipoGlobalOptimizedView)
                escudo_final = _norm_media(c.escudo_url or "")
                
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
                "competicion_id": grupo.competicion_id,
            }
        
        # 4. Construir ranking top 3
        top3_data = []
        for jugador_id in jugador_ids:
            jugador_info = jugadores_lookup.get(jugador_id, {})
            puntos_totales = puntos_totales_dict.get(jugador_id, {
                "puntos_global": 0.0,
                "goles_total": 0,
                "partidos_total": 0,
            })
            puntos_semana = puntos_semana_dict.get(jugador_id, {
                "puntos_semana": None,
                "goles_semana": 0,
                "partidos_semana": 0,
            })
            
            club_id = club_por_jugador.get(jugador_id)
            club_info = clubs_lookup.get(club_id, {}) if club_id else {}
            
            # Obtener grupo principal
            grupo_id = None
            grupo_info = {}
            coef_div = 1.0
            
            ultima_jornada = (
                PuntosMVPJornada.objects
                .filter(temporada_id=temporada_id, jugador_id=jugador_id)
                .select_related("grupo__competicion")
                .order_by("-jornada")
                .first()
            )
            
            if ultima_jornada:
                grupo_id = ultima_jornada.grupo_id
                coef_div = float(ultima_jornada.coef_division)
                grupo_info = grupos_lookup.get(grupo_id, {})
            
            # Asegurar que los puntos estén redondeados
            puntos_semana_redondeado = round(puntos_semana["puntos_semana"]) if puntos_semana["puntos_semana"] is not None else None
            puntos_global_redondeado = round(puntos_totales["puntos_global"])
            
            top3_data.append({
                "jugador_id": jugador_id,
                "nombre": jugador_info.get("nombre", ""),
                "slug": jugador_info.get("slug"),
                "foto": jugador_info.get("foto", ""),
                "club_id": club_id,
                "club_nombre": club_info.get("club_nombre", ""),
                "club_escudo": club_info.get("club_escudo", ""),
                "puntos": puntos_semana_redondeado,
                "puntos_semana": puntos_semana_redondeado,
                "puntos_global": puntos_global_redondeado,
                "puntos_totales": puntos_global_redondeado,
                "total_points": puntos_global_redondeado,
                "coef_division": round(coef_div, 2),
                "goles_jornada": puntos_semana.get("goles_semana", 0) if puntos_semana["puntos_semana"] is not None else None,
                "grupo_id": grupo_id,
                "grupo_nombre": grupo_info.get("grupo_nombre", ""),
                "competicion_id": grupo_info.get("competicion_id"),
                "competicion_nombre": grupo_info.get("competicion_nombre", ""),
            })
        
        # Ordenar por puntos totales (descendente) - ya debería estar ordenado pero por si acaso
        top3_data.sort(key=lambda x: x["puntos_global"], reverse=True)
        
        # Convertir fotos y escudos a URLs absolutas (igual que en EquipoGlobalOptimizedView)
        for row in top3_data:
            row["foto"] = _abs_media(request, row.get("foto", ""))
            row["club_escudo"] = _abs_media(request, row.get("club_escudo", ""))
        
        # Construir respuesta
        window_meta = {
            "start": from_date.isoformat() if from_date else None,
            "end": to_date.isoformat() if to_date else None,
            "status": "ok",
            "matched_games": len(partidos_semana_ids) if (from_date and to_date) else 0,
        }
        
        return Response({
            "temporada_id": temporada_id,
            "window": window_meta,
            "top3": top3_data,
        }, status=status.HTTP_200_OK)
