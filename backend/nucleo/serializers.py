# nucleo/serializers.py

from rest_framework import serializers
from .models import Temporada, Competicion, Grupo


class GrupoMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = ["id", "nombre", "slug"] 


class CompeticionWithGruposSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    slug = serializers.CharField(allow_null=True, allow_blank=True, required=False)  # ← add allow_blank
    tiene_grupos = serializers.BooleanField()
    grupos = GrupoMiniSerializer(many=True)


class TemporadaMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporada
        fields = ["id", "nombre"]


class FilterContextResponseSerializer(serializers.Serializer):
    # La temporada activa puede ser None si no hay temporadas en la base de datos.
    # Esto permite que el frontend maneje el caso de una base de datos vacía sin errores.
    temporada_activa = TemporadaMiniSerializer(allow_null=True)
    # El nombre 'competiciones' es el que espera el frontend para los filtros.
    # Mantener este nombre es crucial para la compatibilidad con el código existente.
    competiciones = CompeticionWithGruposSerializer(many=True)
