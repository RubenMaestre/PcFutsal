from django.contrib import admin
from .models import PropuestaHistorialJugador


@admin.register(PropuestaHistorialJugador)
class PropuestaHistorialJugadorAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "usuario",
        "temporada_texto",
        "club",
        "goles_reportados",
        "partidos_reportados",
        "estado",
        "moderador",
        "creado_en",
        "resuelto_en",
    )
    list_filter = ("estado", "temporada_texto")
    search_fields = ("jugador__nombre", "jugador__apodo", "usuario__username", "club__nombre_corto")
    readonly_fields = ("creado_en", "resuelto_en")
