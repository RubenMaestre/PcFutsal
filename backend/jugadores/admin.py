from django.contrib import admin
from .models import Jugador, JugadorEnClubTemporada, HistorialJugadorScraped


@admin.display(description="Edad (estimada)")
def edad_publica(obj: Jugador):
    # prioridad: edad_estimacion; si no, calculable a futuro con fecha_nacimiento
    if obj.edad_estimacion is not None:
        return obj.edad_estimacion
    return "—"


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "apodo",
        "posicion_principal",
        edad_publica,
        "identificador_federacion",
        "activo",
    )
    list_filter = ("posicion_principal", "activo")
    search_fields = (
        "nombre",
        "apodo",
        "identificador_federacion",
    )
    ordering = ("nombre",)
    list_editable = ("activo",)


@admin.display(description="Club")
def club_nombre(obj):
    return obj.club.nombre_corto or obj.club.nombre_oficial


@admin.register(JugadorEnClubTemporada)
class JugadorEnClubTemporadaAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        club_nombre,
        "temporada",
        "dorsal",
        "partidos_jugados",
        "goles",
        "tarjetas_amarillas",
        "tarjetas_rojas",
        "titular",
        "suplente",
        "convocados",
    )
    list_filter = (
        "temporada",
        "club",
        "jugador__posicion_principal",
    )
    search_fields = (
        "jugador__nombre",
        "jugador__apodo",
        "club__nombre_corto",
        "club__nombre_oficial",
        "temporada__nombre",
        "dorsal",
    )
    ordering = ("temporada", "club", "jugador")


@admin.register(HistorialJugadorScraped)
class HistorialJugadorScrapedAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "temporada_texto",
        "competicion_texto",
        "equipo_texto",
    )
    search_fields = (
        "jugador__nombre",
        "jugador__apodo",
        "temporada_texto",
        "competicion_texto",
        "equipo_texto",
    )
    list_filter = ("temporada_texto",)
    ordering = ("jugador", "temporada_texto")
