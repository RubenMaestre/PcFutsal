# clasificaciones/admin.py
from django.contrib import admin
from .models import ClasificacionJornada, PosicionJornada


class PosicionJornadaInline(admin.TabularInline):
    """Inline para mostrar posiciones dentro de ClasificacionJornada"""
    model = PosicionJornada
    extra = 0
    readonly_fields = ("posicion", "puntos", "partidos_jugados", "goles_favor", "goles_contra", "diferencia_goles")
    fields = (
        "club",
        "posicion",
        "puntos",
        "partidos_jugados",
        "partidos_ganados",
        "partidos_empatados",
        "partidos_perdidos",
        "goles_favor",
        "goles_contra",
        "diferencia_goles",
        "racha",
    )
    ordering = ("posicion",)


@admin.register(ClasificacionJornada)
class ClasificacionJornadaAdmin(admin.ModelAdmin):
    list_display = (
        "grupo",
        "jornada",
        "equipos_participantes",
        "partidos_jugados_total",
        "fecha_calculo",
    )
    list_filter = (
        "grupo__temporada",
        "grupo__competicion",
        "grupo",
        "jornada",
    )
    search_fields = (
        "grupo__nombre",
        "grupo__competicion__nombre",
    )
    readonly_fields = ("fecha_calculo",)
    inlines = [PosicionJornadaInline]
    ordering = ("grupo__temporada", "grupo", "-jornada")


@admin.register(PosicionJornada)
class PosicionJornadaAdmin(admin.ModelAdmin):
    list_display = (
        "clasificacion_jornada",
        "club",
        "posicion",
        "puntos",
        "partidos_jugados",
        "goles_favor",
        "goles_contra",
        "diferencia_goles",
    )
    list_filter = (
        "clasificacion_jornada__grupo__temporada",
        "clasificacion_jornada__grupo__competicion",
        "clasificacion_jornada__grupo",
        "clasificacion_jornada__jornada",
        "posicion",
    )
    search_fields = (
        "club__nombre_oficial",
        "club__nombre_corto",
        "clasificacion_jornada__grupo__nombre",
    )
    readonly_fields = (
        "clasificacion_jornada",
        "club",
        "posicion",
        "puntos",
        "partidos_jugados",
        "partidos_ganados",
        "partidos_empatados",
        "partidos_perdidos",
        "goles_favor",
        "goles_contra",
        "diferencia_goles",
        "racha",
    )
    ordering = ("clasificacion_jornada", "posicion")
