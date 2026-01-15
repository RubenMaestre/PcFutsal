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
    # 👇 muy importante: puede venir sin temporada
    temporada_activa = TemporadaMiniSerializer(allow_null=True)
    # 👇 y aquí el nombre CORRECTO que usa el frontend
    competiciones = CompeticionWithGruposSerializer(many=True)
