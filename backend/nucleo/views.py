# nucleo/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Temporada, Competicion, Grupo
from .serializers import (
    FilterContextResponseSerializer,
)

class FilterContextAPIView(APIView):
    def get(self, request, format=None):
        temporada_activa = Temporada.objects.order_by("-id").first()

        if not temporada_activa:
            payload = {
                "temporada_activa": None,
                "competiciones": [],
            }
            ser = FilterContextResponseSerializer(payload)
            return Response(ser.data, status=status.HTTP_200_OK)

        competiciones_qs = Competicion.objects.all().order_by("id")

        competiciones_data = []
        for comp in competiciones_qs:
            grupos_qs = Grupo.objects.filter(
                competicion=comp,
                temporada=temporada_activa
            ).order_by("id")

            grupos_serializados = [
                {
                    "id": g.id,
                    "nombre": g.nombre,
                    "slug": g.slug,
                }
                for g in grupos_qs
            ]

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
