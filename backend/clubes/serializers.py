# clubes/serializers.py
from rest_framework import serializers
from django.apps import apps as django_apps

from .models import Club, ClubEnGrupo
from jugadores.models import JugadorEnClubTemporada
from staff.models import StaffClub

# --------------------------------------------
# Helpers
# --------------------------------------------
def _norm_media(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/media/"):
        return u
    return "/media/" + u.lstrip("/")


# --------------------------------------------
# Clubes (compat con modelo nuevo)
# --------------------------------------------
class ClubLiteSerializer(serializers.ModelSerializer):
    # localidad en el front → ciudad en el modelo
    localidad = serializers.CharField(source="ciudad", allow_blank=True, required=False)
    escudo_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            "id",
            "slug",          # Slug para URLs SEO-friendly
            "nombre_oficial",
            "nombre_corto",
            "localidad",     # alias de ciudad
            "pabellon",
            "escudo_url",
        ]

    def get_escudo_url(self, obj):
        return _norm_media(getattr(obj, "escudo_url", ""))


class ClubEnGrupoSerializer(serializers.ModelSerializer):
    club = ClubLiteSerializer()

    # 👇 Campos legacy que usa el frontend
    partidos_ganados = serializers.IntegerField(source="victorias", read_only=True)
    partidos_empatados = serializers.IntegerField(source="empates", read_only=True)
    partidos_perdidos = serializers.IntegerField(source="derrotas", read_only=True)

    class Meta:
        model = ClubEnGrupo
        fields = [
            "club",
            "puntos",
            "partidos_jugados",
            "partidos_ganados",
            "partidos_empatados",
            "partidos_perdidos",
            "goles_favor",
            "goles_contra",
            "posicion_actual",
            "racha",
        ]


# --------------------------------------------
# Valoración de Club (condicional)
# --------------------------------------------
ValoracionClub = None
try:
    ValoracionClub = django_apps.get_model("clubes", "ValoracionClub")
except LookupError:
    ValoracionClub = None

if ValoracionClub:
    class ValoracionClubSerializer(serializers.ModelSerializer):
        class Meta:
            model = ValoracionClub
            fields = [
                "historia_tradicion",
                "cantera_talento",
                "intensidad_competitiva",
                "solidez_tactica",
                "proyecto_seriedad",
                "reputacion_respecto",
                "media_global",
            ]
else:
    # Stub para no romper imports si aún no existe el modelo/migración
    class ValoracionClubSerializer(serializers.Serializer):
        historia_tradicion = serializers.FloatField(required=False, allow_null=True)
        cantera_talento = serializers.FloatField(required=False, allow_null=True)
        intensidad_competitiva = serializers.FloatField(required=False, allow_null=True)
        solidez_tactica = serializers.FloatField(required=False, allow_null=True)
        proyecto_seriedad = serializers.FloatField(required=False, allow_null=True)
        reputacion_respecto = serializers.FloatField(required=False, allow_null=True)
        media_global = serializers.FloatField(required=False, allow_null=True)

        def to_representation(self, obj):
            def getf(name):
                return getattr(obj, name, None)
            return {
                "historia_tradicion": getf("historia_tradicion"),
                "cantera_talento": getf("cantera_talento"),
                "intensidad_competitiva": getf("intensidad_competitiva"),
                "solidez_tactica": getf("solidez_tactica"),
                "proyecto_seriedad": getf("proyecto_seriedad"),
                "reputacion_respecto": getf("reputacion_respecto"),
                "media_global": getf("media_global"),
            }


# --------------------------------------------
# Plantilla y Staff (lo que ya funcionaba)
# --------------------------------------------
class JugadorEnClubTemporadaSerializer(serializers.ModelSerializer):
    jugador_nombre = serializers.CharField(source="jugador.nombre", default="", allow_blank=True)
    jugador_apodo = serializers.CharField(source="jugador.apodo", default="", allow_blank=True)
    jugador_foto = serializers.SerializerMethodField()
    jugador_posicion = serializers.CharField(
        source="jugador.posicion_principal", default="", allow_blank=True
    )

    class Meta:
        model = JugadorEnClubTemporada
        fields = [
            "id",
            "jugador_nombre",
            "jugador_apodo",
            "jugador_foto",
            "jugador_posicion",
            "dorsal",
            "partidos_jugados",
            "goles",
            "tarjetas_amarillas",
            "tarjetas_rojas",
        ]

    def get_jugador_foto(self, obj):
        return _norm_media(getattr(obj.jugador, "foto_url", ""))


class StaffClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffClub
        fields = [
            "id",
            "nombre",
            "rol",
            "activo",
        ]
