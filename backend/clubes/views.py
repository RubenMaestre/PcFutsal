# clubes/views.py
"""
Vistas para el API de clubes.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Club, ClubEnGrupo
from nucleo.models import Grupo, Temporada
from .serializers import ClubLiteSerializer, ClubEnGrupoSerializer
from clasificaciones.models import ClasificacionJornada, PosicionJornada
from partidos.models import Partido


def _calcular_goles_desde_partidos(grupo_id: int, club_ids: list[int]) -> dict[int, dict[str, int]]:
    """
    Calcula goles_favor y goles_contra para cada club desde los partidos jugados.
    Esta función es útil cuando los datos de clasificación no están sincronizados
    o cuando necesitamos recalcular estadísticas desde los partidos reales.
    Retorna un diccionario: {club_id: {"goles_favor": X, "goles_contra": Y}}
    """
    partidos = Partido.objects.filter(
        grupo_id=grupo_id,
        jugado=True,
        goles_local__isnull=False,
        goles_visitante__isnull=False,
    ).values("local_id", "visitante_id", "goles_local", "goles_visitante")
    
    goles_por_club = {}
    for club_id in club_ids:
        goles_por_club[club_id] = {"goles_favor": 0, "goles_contra": 0}
    
    # Recorremos todos los partidos y acumulamos goles a favor y en contra
    # según si el club jugó como local o visitante
    for p in partidos:
        local_id = p["local_id"]
        visitante_id = p["visitante_id"]
        goles_local = p["goles_local"] or 0
        goles_visitante = p["goles_visitante"] or 0
        
        # Goles del equipo local: a favor = goles_local, en contra = goles_visitante
        if local_id in goles_por_club:
            goles_por_club[local_id]["goles_favor"] += goles_local
            goles_por_club[local_id]["goles_contra"] += goles_visitante
        
        # Goles del equipo visitante: a favor = goles_visitante, en contra = goles_local
        if visitante_id in goles_por_club:
            goles_por_club[visitante_id]["goles_favor"] += goles_visitante
            goles_por_club[visitante_id]["goles_contra"] += goles_local
    
    return goles_por_club


class ClubesListaView(APIView):
    """
    GET /api/clubes/lista/?club_id=XX
    GET /api/clubes/lista/?slug=xx
    GET /api/clubes/lista/?grupo_id=XX
    GET /api/clubes/lista/?random=true
    """
    
    def get(self, request, format=None):
        club_id = request.GET.get("club_id")
        slug = request.GET.get("slug")
        grupo_id = request.GET.get("grupo_id")
        random = request.GET.get("random", "").lower() == "true"
        
        if club_id:
            try:
                club = Club.objects.get(id=club_id)
                serializer = ClubLiteSerializer(club)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Club.DoesNotExist:
                return Response(
                    {"detail": "Club no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if slug:
            try:
                club = Club.objects.get(slug=slug)
                serializer = ClubLiteSerializer(club)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Club.DoesNotExist:
                return Response(
                    {"detail": "Club no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if grupo_id:
            try:
                grupo = Grupo.objects.select_related("competicion", "temporada").get(id=grupo_id)
                clubes_en_grupo = ClubEnGrupo.objects.filter(grupo_id=grupo_id).select_related("club").order_by("posicion_actual")
                clubes = [ceg.club for ceg in clubes_en_grupo]
                serializer = ClubLiteSerializer(clubes, many=True)
                
                # Enriquecer con datos de clasificación
                clubes_data = list(serializer.data)
                
                # Calcular goles desde partidos si no están disponibles o están en 0
                club_ids_grupo = [ceg.club_id for ceg in clubes_en_grupo]
                goles_calculados = _calcular_goles_desde_partidos(grupo_id, club_ids_grupo)
                
                for idx, ceg in enumerate(clubes_en_grupo):
                    if idx < len(clubes_data):
                        # Usar goles calculados desde partidos si los del modelo están en 0 o no disponibles
                        goles_calc = goles_calculados.get(ceg.club_id, {})
                        goles_favor_final = ceg.goles_favor if ceg.goles_favor and ceg.goles_favor > 0 else goles_calc.get("goles_favor", 0)
                        goles_contra_final = ceg.goles_contra if ceg.goles_contra and ceg.goles_contra > 0 else goles_calc.get("goles_contra", 0)
                        
                        clubes_data[idx]["posicion_actual"] = ceg.posicion_actual
                        clubes_data[idx]["puntos"] = ceg.puntos
                        clubes_data[idx]["goles_favor"] = goles_favor_final
                        clubes_data[idx]["goles_contra"] = goles_contra_final
                        clubes_data[idx]["diferencia_goles"] = goles_favor_final - goles_contra_final
                        clubes_data[idx]["racha"] = ceg.racha
                        clubes_data[idx]["competicion_nombre"] = grupo.competicion.nombre
                        clubes_data[idx]["grupo_nombre"] = grupo.nombre
                
                return Response({
                    "grupo": {
                        "id": grupo.id,
                        "nombre": grupo.nombre,
                        "competicion": grupo.competicion.nombre,
                        "temporada": grupo.temporada.nombre,
                    },
                    "count": len(clubes_data),
                    "results": clubes_data
                }, status=status.HTTP_200_OK)
            except Grupo.DoesNotExist:
                return Response(
                    {"detail": "Grupo no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if random:
            # Devolver clubes aleatorios SOLO de la temporada activa (limitado a 20 para no sobrecargar)
            import random as random_module
            
            # Obtener temporada activa (más reciente)
            temporada_activa = Temporada.objects.order_by("-id").first()
            
            if not temporada_activa:
                return Response({
                    "random": True,
                    "count": 0,
                    "results": []
                }, status=status.HTTP_200_OK)
            
            # Obtener solo los clubes que están participando en la temporada activa
            clubes_en_temporada_activa = ClubEnGrupo.objects.filter(
                grupo__temporada_id=temporada_activa.id
            ).select_related("club", "grupo__competicion", "grupo__temporada")
            
            # Obtener IDs únicos de clubes (puede haber clubes en múltiples grupos de la misma temporada)
            club_ids_unicos = list(set(ceg.club_id for ceg in clubes_en_temporada_activa))
            
            if not club_ids_unicos:
                return Response({
                    "random": True,
                    "count": 0,
                    "results": []
                }, status=status.HTTP_200_OK)
            
            # Obtener los clubes activos que están en la temporada activa
            clubes = list(Club.objects.filter(
                activo=True,
                id__in=club_ids_unicos
            ))
            
            if clubes:
                # Seleccionar aleatoriamente hasta 20 clubes
                clubes_random = random_module.sample(clubes, min(20, len(clubes)))
                serializer = ClubLiteSerializer(clubes_random, many=True)
                clubes_data = list(serializer.data)
                
                # Enriquecer con datos de clasificación de cada club (solo de temporada activa)
                club_ids_random = [c.id for c in clubes_random]
                
                # Crear lookup por club_id solo de la temporada activa
                ceg_lookup = {}
                for ceg in clubes_en_temporada_activa:
                    if ceg.club_id in club_ids_random:
                        club_id = ceg.club_id
                        if club_id not in ceg_lookup:
                            ceg_lookup[club_id] = []
                        ceg_lookup[club_id].append(ceg)
                
                # Calcular goles desde partidos si no están disponibles o están en 0
                # Agrupar clubes por grupo para calcular goles eficientemente
                grupos_por_club = {}
                for ceg in clubes_en_temporada_activa:
                    if ceg.club_id in club_ids_random:
                        if ceg.club_id not in grupos_por_club:
                            grupos_por_club[ceg.club_id] = []
                        grupos_por_club[ceg.club_id].append(ceg)
                
                # Calcular goles por grupo
                goles_calculados = {}
                grupos_procesados = set()
                for club_id, cegs_list in grupos_por_club.items():
                    ceg = cegs_list[0]  # Usar el primero
                    grupo_id = ceg.grupo_id
                    
                    # Calcular goles solo una vez por grupo
                    if grupo_id not in grupos_procesados:
                        club_ids_grupo = [ceg.club_id for ceg in clubes_en_temporada_activa if ceg.grupo_id == grupo_id]
                        goles_grupo = _calcular_goles_desde_partidos(grupo_id, club_ids_grupo)
                        goles_calculados.update(goles_grupo)
                        grupos_procesados.add(grupo_id)
                
                # Enriquecer cada club con sus datos de clasificación de la temporada activa
                for idx, club in enumerate(clubes_random):
                    if idx < len(clubes_data) and club.id in ceg_lookup:
                        # Si un club está en múltiples grupos de la temporada activa, usar el primero
                        # (o se podría priorizar por algún criterio, pero por ahora el primero)
                        cegs = ceg_lookup[club.id]
                        ceg = cegs[0]  # Tomar el primero (todos son de la temporada activa)
                        
                        # Usar goles calculados desde partidos si los del modelo están en 0 o no disponibles
                        goles_calc = goles_calculados.get(club.id, {})
                        goles_favor_final = ceg.goles_favor if ceg.goles_favor and ceg.goles_favor > 0 else goles_calc.get("goles_favor", 0)
                        goles_contra_final = ceg.goles_contra if ceg.goles_contra and ceg.goles_contra > 0 else goles_calc.get("goles_contra", 0)
                        
                        clubes_data[idx]["posicion_actual"] = ceg.posicion_actual
                        clubes_data[idx]["puntos"] = ceg.puntos
                        clubes_data[idx]["goles_favor"] = goles_favor_final
                        clubes_data[idx]["goles_contra"] = goles_contra_final
                        clubes_data[idx]["diferencia_goles"] = goles_favor_final - goles_contra_final
                        clubes_data[idx]["racha"] = ceg.racha
                        clubes_data[idx]["competicion_nombre"] = ceg.grupo.competicion.nombre
                        clubes_data[idx]["grupo_nombre"] = ceg.grupo.nombre
                
                return Response({
                    "random": True,
                    "count": len(clubes_random),
                    "results": clubes_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "random": True,
                    "count": 0,
                    "results": []
                }, status=status.HTTP_200_OK)
        
        # Sin parámetros: devolver todos los clubes de la temporada activa
        temporada_activa = Temporada.objects.order_by("-id").first()
        
        if not temporada_activa:
            return Response({
                "count": 0,
                "results": []
            }, status=status.HTTP_200_OK)
        
        # Obtener solo los clubes que están participando en la temporada activa
        clubes_en_temporada_activa = ClubEnGrupo.objects.filter(
            grupo__temporada_id=temporada_activa.id
        ).select_related("club", "grupo__competicion", "grupo__temporada")
        
        # Obtener IDs únicos de clubes (puede haber clubes en múltiples grupos de la misma temporada)
        club_ids_unicos = list(set(ceg.club_id for ceg in clubes_en_temporada_activa))
        
        if not club_ids_unicos:
            return Response({
                "count": 0,
                "results": []
            }, status=status.HTTP_200_OK)
        
        # Obtener los clubes activos que están en la temporada activa
        clubes = Club.objects.filter(
            activo=True,
            id__in=club_ids_unicos
        )
        
        serializer = ClubLiteSerializer(clubes, many=True)
        clubes_data = list(serializer.data)
        
        # Enriquecer con datos de clasificación de cada club (solo de temporada activa)
        club_ids = [c.id for c in clubes]
        
        # Crear lookup por club_id solo de la temporada activa
        ceg_lookup = {}
        for ceg in clubes_en_temporada_activa:
            if ceg.club_id in club_ids:
                club_id = ceg.club_id
                if club_id not in ceg_lookup:
                    ceg_lookup[club_id] = []
                ceg_lookup[club_id].append(ceg)
        
        # Calcular goles desde partidos si no están disponibles o están en 0
        # Agrupar clubes por grupo para calcular goles eficientemente
        grupos_por_club = {}
        for ceg in clubes_en_temporada_activa:
            if ceg.club_id in club_ids:
                if ceg.club_id not in grupos_por_club:
                    grupos_por_club[ceg.club_id] = []
                grupos_por_club[ceg.club_id].append(ceg)
        
        # Calcular goles por grupo
        goles_calculados = {}
        grupos_procesados = set()
        for club_id, cegs_list in grupos_por_club.items():
            ceg = cegs_list[0]  # Usar el primero
            grupo_id = ceg.grupo_id
            
            # Calcular goles solo una vez por grupo
            if grupo_id not in grupos_procesados:
                club_ids_grupo = [ceg.club_id for ceg in clubes_en_temporada_activa if ceg.grupo_id == grupo_id]
                goles_grupo = _calcular_goles_desde_partidos(grupo_id, club_ids_grupo)
                goles_calculados.update(goles_grupo)
                grupos_procesados.add(grupo_id)
        
        # Enriquecer cada club con sus datos de clasificación de la temporada activa
        for idx, club in enumerate(clubes):
            if idx < len(clubes_data) and club.id in ceg_lookup:
                # Si un club está en múltiples grupos de la temporada activa, usar el primero
                cegs = ceg_lookup[club.id]
                ceg = cegs[0]  # Tomar el primero (todos son de la temporada activa)
                
                # Usar goles calculados desde partidos si los del modelo están en 0 o no disponibles
                goles_calc = goles_calculados.get(club.id, {})
                goles_favor_final = ceg.goles_favor if ceg.goles_favor and ceg.goles_favor > 0 else goles_calc.get("goles_favor", 0)
                goles_contra_final = ceg.goles_contra if ceg.goles_contra and ceg.goles_contra > 0 else goles_calc.get("goles_contra", 0)
                
                clubes_data[idx]["posicion_actual"] = ceg.posicion_actual
                clubes_data[idx]["puntos"] = ceg.puntos
                clubes_data[idx]["goles_favor"] = goles_favor_final
                clubes_data[idx]["goles_contra"] = goles_contra_final
                clubes_data[idx]["diferencia_goles"] = goles_favor_final - goles_contra_final
                clubes_data[idx]["racha"] = ceg.racha
                clubes_data[idx]["competicion_nombre"] = ceg.grupo.competicion.nombre
                clubes_data[idx]["grupo_nombre"] = ceg.grupo.nombre
        
        return Response({
            "count": len(clubes_data),
            "results": clubes_data
        }, status=status.HTTP_200_OK)


class ClubDetalleView(APIView):
    """
    GET /api/clubes/detalle/?club_id=XX
    GET /api/clubes/detalle/?slug=xx
    """
    
    def get(self, request, format=None):
        club_id = request.GET.get("club_id")
        slug = request.GET.get("slug")
        
        if not club_id and not slug:
            return Response(
                {"detail": "Falta club_id o slug"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if club_id:
                club = Club.objects.get(id=club_id)
            else:
                club = Club.objects.get(slug=slug)
        except Club.DoesNotExist:
            return Response(
                {"detail": "Club no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ClubLiteSerializer(club)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClubFullView(APIView):
    """
    GET /api/clubes/full/?club_id=XX
    GET /api/clubes/full/?slug=xx
    """
    
    def get(self, request, format=None):
        club_id = request.GET.get("club_id")
        slug = request.GET.get("slug")
        
        if not club_id and not slug:
            return Response(
                {"detail": "Falta club_id o slug"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if club_id:
                club = Club.objects.select_related().get(id=club_id)
            else:
                club = Club.objects.select_related().get(slug=slug)
        except Club.DoesNotExist:
                return Response(
                {"detail": "Club no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Construir respuesta completa con contexto
        from clubes.serializers_full import club_full_serializer
        data = club_full_serializer(club, request)
        return Response(data, status=status.HTTP_200_OK)


class ClubHistoricoView(APIView):
    """
    GET /api/clubes/historico/?club_id=XX
    GET /api/clubes/historico/?slug=xx
    """
    
    def get(self, request, format=None):
        club_id = request.GET.get("club_id")
        slug = request.GET.get("slug")
        
        if not club_id and not slug:
            return Response(
                {"detail": "Falta club_id o slug"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if club_id:
                club = Club.objects.get(id=club_id)
            else:
                club = Club.objects.get(slug=slug)
        except Club.DoesNotExist:
            return Response(
                {"detail": "Club no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener historial
        historial_qs = club.historial.all().select_related("temporada").order_by("-temporada__nombre")
        
        historial_data = []
        for h in historial_qs:
            historial_data.append({
                "temporada": h.temporada.nombre,
                "division": f"{h.competicion} {h.grupo_text}".strip(),
                "posicion": h.pos_final,
                "puntos": h.puntos,
                "pj": h.pj,
                "v": h.v,
                "e": h.e,
                "d": h.d,
                "gf": h.gf,
                "gc": h.gc,
            })
        
        return Response({
            "club": {
            "id": club.id,
                "nombre": club.nombre_oficial,
                "slug": club.slug,
            },
            "historico": historial_data
        }, status=status.HTTP_200_OK)


class ClasificacionEvolucionView(APIView):
    """
    GET /api/clubes/clasificacion-evolucion/?grupo_id=XX
    
    Devuelve la evolución de posiciones por jornada para todos los equipos de un grupo.
    Útil para gráficas de evolución de clasificación.
    """
    
    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        
        if not grupo_id:
            return Response(
                {"detail": "Falta grupo_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            grupo = Grupo.objects.select_related("competicion", "temporada").get(id=grupo_id)
        except Grupo.DoesNotExist:
            return Response(
                {"detail": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todas las clasificaciones históricas del grupo
        clasificaciones = ClasificacionJornada.objects.filter(
            grupo=grupo
        ).prefetch_related("posiciones__club").order_by("jornada")
        
        # Obtener equipos actuales del grupo para estructura base
        clubes_en_grupo = ClubEnGrupo.objects.filter(grupo=grupo).select_related("club").order_by("posicion_actual")
        
        # Construir estructura de datos por equipo
        equipos_data = {}
        for ceg in clubes_en_grupo:
            equipos_data[ceg.club_id] = {
                "club_id": ceg.club_id,
                "nombre": ceg.club.nombre_oficial or ceg.club.nombre_corto,
                "escudo": ceg.club.escudo_url or "",
                "slug": ceg.club.slug,
                "posicion_actual": ceg.posicion_actual,
                "evolucion": [],  # Array de {jornada, posicion, puntos}
            }
        
        # Llenar evolución jornada por jornada desde las clasificaciones históricas
        jornadas_unicas = []
        
        for clasif in clasificaciones:
            jornadas_unicas.append(clasif.jornada)
            
            # Obtener todas las posiciones de esta jornada
            for posicion in clasif.posiciones.all():
                club_id = posicion.club_id
                
                # Si el equipo no está en equipos_data (puede haber cambiado de grupo), añadirlo
                if club_id not in equipos_data:
                    equipos_data[club_id] = {
                        "club_id": club_id,
                        "nombre": posicion.club.nombre_oficial or posicion.club.nombre_corto,
                        "escudo": posicion.club.escudo_url or "",
                        "slug": posicion.club.slug,
                        "posicion_actual": posicion.posicion,
                        "evolucion": [],
                    }
                
                equipos_data[club_id]["evolucion"].append({
                    "jornada": clasif.jornada,
                    "posicion": posicion.posicion,
                    "puntos": posicion.puntos,
                    "goles_favor": posicion.goles_favor,
                    "goles_contra": posicion.goles_contra,
                })
        
        # Convertir a array y ordenar por posición actual
        equipos_array = list(equipos_data.values())
        equipos_array.sort(key=lambda x: x["posicion_actual"] or 999)
        
        return Response({
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornadas": sorted(set(jornadas_unicas)),
            "equipos": equipos_array,
        }, status=status.HTTP_200_OK)
