# nucleo/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Temporada, Competicion, Grupo
from .serializers import (
    FilterContextResponseSerializer,
)

class FilterContextAPIView(APIView):
    """
    Devuelve el contexto de filtros necesario para los componentes del frontend.
    
    Este endpoint proporciona:
    - La temporada activa (la más reciente por ID)
    - Todas las competiciones con sus grupos asociados a esa temporada
    
    Es usado por componentes como filtros de competición/grupo para poblar
    los dropdowns sin necesidad de múltiples peticiones.
    """
    def get(self, request, format=None):
        # Obtener la temporada más reciente (ordenando por ID descendente).
        # Asumimos que el ID más alto corresponde a la temporada más actual.
        temporada_activa = Temporada.objects.order_by("-id").first()

        # Si no hay temporadas, devolver respuesta vacía pero válida.
        # Esto permite que el frontend maneje el caso de una base de datos vacía.
        if not temporada_activa:
            payload = {
                "temporada_activa": None,
                "competiciones": [],
            }
            ser = FilterContextResponseSerializer(payload)
            return Response(ser.data, status=status.HTTP_200_OK)

        # Obtener todas las competiciones ordenadas por ID para mantener consistencia.
        competiciones_qs = Competicion.objects.all().order_by("id")

        competiciones_data = []
        for comp in competiciones_qs:
            # Filtrar grupos de esta competición en la temporada activa.
            # Esto asegura que solo se muestren grupos relevantes para la temporada actual.
            grupos_qs = Grupo.objects.filter(
                competicion=comp,
                temporada=temporada_activa
            ).order_by("id")

            # Serializar grupos con solo los campos necesarios para los filtros.
            grupos_serializados = [
                {
                    "id": g.id,
                    "nombre": g.nombre,
                    "slug": g.slug,
                }
                for g in grupos_qs
            ]

            # Construir datos de competición con flag 'tiene_grupos' para facilitar
            # la lógica del frontend (mostrar/ocultar competiciones sin grupos).
            competiciones_data.append(
                {
                    "id": comp.id,
                    "nombre": comp.nombre,
                    "slug": comp.slug,
                    "tiene_grupos": len(grupos_serializados) > 0,
                    "grupos": grupos_serializados,
                }
            )

        payload = {
            "temporada_activa": {
                "id": temporada_activa.id,
                "nombre": temporada_activa.nombre,
            },
            "competiciones": competiciones_data,
        }

        ser = FilterContextResponseSerializer(payload)
        return Response(ser.data, status=status.HTTP_200_OK)
