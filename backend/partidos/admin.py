from django.contrib import admin
from .models import Partido, EventoPartido, AlineacionPartidoJugador
from arbitros.models import ArbitrajePartido


@admin.display(description="Marcador")
def marcador(obj: Partido):
    if obj.jugado and obj.goles_local is not None and obj.goles_visitante is not None:
        return f"{obj.goles_local}-{obj.goles_visitante}"
    return "—"


@admin.display(description="Árbitros")
def arbitros_list(obj: Partido):
    return ", ".join(
        f"{ap.arbitro.nombre}{(' (' + ap.rol + ')') if ap.rol else ''}"
        for ap in obj.arbitrajes.all()
    ) or "—"


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = (
        "grupo",
        "jornada_numero",
        "fecha_hora",
        "local",
        "visitante",
        marcador,
        "jugado",
        "indice_intensidad",
        arbitros_list,
    )
    list_filter = (
        "grupo",
        "grupo__temporada",
        "jornada_numero",
        "jugado",
    )
    search_fields = (
        "local__nombre_corto",
        "local__nombre_oficial",
        "visitante__nombre_corto",
        "visitante__nombre_oficial",
        "identificador_federacion",
        "pabellon",
        "arbitros",
    )
    date_hierarchy = "fecha_hora"
    ordering = ("-fecha_hora",)
    autocomplete_fields = ("grupo", "local", "visitante")


@admin.register(EventoPartido)
class EventoPartidoAdmin(admin.ModelAdmin):
    list_display = ("partido", "minuto", "tipo_evento", "jugador", "club", "nota", "creado_en")
    list_filter = ("tipo_evento", "club", "partido__grupo", "partido__jornada_numero")
    search_fields = (
        "partido__local__nombre_oficial",
        "partido__visitante__nombre_oficial",
        "jugador__nombre",
        "jugador__apodo",
        "nota",
    )
    ordering = ("-creado_en",)
    autocomplete_fields = ("partido", "jugador", "club")


@admin.register(AlineacionPartidoJugador)
class AlineacionPartidoJugadorAdmin(admin.ModelAdmin):
    list_display = (
        "partido",
        "club",
        "jugador",
        "dorsal",
        "titular",
        "etiqueta",
    )
    list_filter = (
        "titular",
        "etiqueta",
        "club",
        "partido__grupo",
        "partido__jornada_numero",
    )
    search_fields = (
        "jugador__nombre",
        "jugador__apodo",
        "club__nombre_corto",
        "club__nombre_oficial",
        "partido__local__nombre_oficial",
        "partido__visitante__nombre_oficial",
        "dorsal",
    )
    autocomplete_fields = ("partido", "club", "jugador")
    ordering = ("partido", "club", "titular", "dorsal")
