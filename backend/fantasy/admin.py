from django.contrib import admin
from .models import (
    JornadaFantasy, EquipoFantasyUsuario, PuntosFantasyJugador,
    PuntosMVPJornada, PuntosMVPTotalJugador, PuntosEquipoJornada, PuntosEquipoTotal,
    MVPPartido, MVPJornadaDivision, MVPJornadaGlobal,
    GoleadorJornadaDivision, MejorEquipoJornadaDivision, MejorEquipoJornadaGlobal
)


@admin.register(JornadaFantasy)
class JornadaFantasyAdmin(admin.ModelAdmin):
    list_display = ("grupo", "temporada", "numero_jornada", "estado")
    list_filter = ("estado", "temporada", "grupo")
    search_fields = ("grupo__nombre",)


@admin.register(EquipoFantasyUsuario)
class EquipoFantasyUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "jornada_fantasy",
        "usuario",
        "jugador_portero",
        "jugador_cierre",
        "jugador_ala",
        "jugador_pivot",
        "jugador_extra",
        "puntos_totales_semana",
        "posicion_en_ranking_semana",
    )
    list_filter = ("jornada_fantasy", "usuario")
    search_fields = ("usuario__username",)


@admin.register(PuntosFantasyJugador)
class PuntosFantasyJugadorAdmin(admin.ModelAdmin):
    list_display = (
        "jornada_fantasy",
        "jugador",
        "goles",
        "tarjetas",
        "mvp",
        "victoria_equipo",
        "puntos_resultado_final_calculado",
    )
    list_filter = ("jornada_fantasy", "mvp", "victoria_equipo")
    search_fields = ("jugador__nombre", "jugador__apodo")


@admin.register(PuntosMVPJornada)
class PuntosMVPJornadaAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "grupo",
        "temporada",
        "jornada",
        "puntos_base",
        "puntos_con_coef",
        "coef_division",
        "partidos_jugados",
        "goles",
        "fecha_calculo",
    )
    list_filter = ("temporada", "grupo", "jornada")
    search_fields = ("jugador__nombre", "jugador__apodo", "grupo__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")


@admin.register(PuntosEquipoJornada)
class PuntosEquipoJornadaAdmin(admin.ModelAdmin):
    list_display = (
        "club",
        "grupo",
        "temporada",
        "jornada",
        "puntos",
        "partidos_jugados",
        "victorias",
        "empates",
        "derrotas",
        "goles_favor",
        "goles_contra",
        "fecha_calculo",
    )
    list_filter = ("temporada", "grupo", "jornada")
    search_fields = ("club__nombre_oficial", "club__nombre_corto", "grupo__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")


@admin.register(PuntosEquipoTotal)
class PuntosEquipoTotalAdmin(admin.ModelAdmin):
    list_display = (
        "club",
        "temporada",
        "puntos_total",
        "partidos_total",
        "victorias_total",
        "empates_total",
        "derrotas_total",
        "goles_favor_total",
        "goles_contra_total",
        "fecha_actualizacion",
    )
    list_filter = ("temporada",)
    search_fields = ("club__nombre_oficial", "club__nombre_corto")
    readonly_fields = ("fecha_creacion", "fecha_actualizacion")


# ============================================================================
# ADMIN PARA MODELOS DE RECONOCIMIENTOS
# ============================================================================

@admin.register(MVPPartido)
class MVPPartidoAdmin(admin.ModelAdmin):
    list_display = (
        "partido",
        "jugador",
        "puntos",
        "goles",
        "equipo_ganador",
        "fecha_calculo",
    )
    list_filter = ("equipo_ganador", "mvp_evento", "fecha_creacion")
    search_fields = ("jugador__nombre", "jugador__apodo", "partido__local__nombre", "partido__visitante__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")
    raw_id_fields = ("partido", "jugador")


@admin.register(MVPJornadaDivision)
class MVPJornadaDivisionAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "grupo",
        "temporada",
        "jornada",
        "puntos",
        "puntos_con_coef",
        "coef_division",
        "partidos_jugados",
        "goles",
        "fecha_calculo",
    )
    list_filter = ("temporada", "grupo", "jornada")
    search_fields = ("jugador__nombre", "jugador__apodo", "grupo__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")
    raw_id_fields = ("jugador", "grupo", "temporada")


@admin.register(MVPJornadaGlobal)
class MVPJornadaGlobalAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "grupo",
        "temporada",
        "semana",
        "puntos",
        "puntos_base",
        "coef_division",
        "partidos_jugados",
        "goles",
        "fecha_calculo",
    )
    list_filter = ("temporada", "semana", "grupo")
    search_fields = ("jugador__nombre", "jugador__apodo", "grupo__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")
    raw_id_fields = ("jugador", "grupo", "temporada")


@admin.register(GoleadorJornadaDivision)
class GoleadorJornadaDivisionAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "grupo",
        "temporada",
        "jornada",
        "goles",
        "partidos_jugados",
        "fecha_calculo",
    )
    list_filter = ("temporada", "grupo", "jornada")
    search_fields = ("jugador__nombre", "jugador__apodo", "grupo__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")
    raw_id_fields = ("jugador", "grupo", "temporada")


@admin.register(MejorEquipoJornadaDivision)
class MejorEquipoJornadaDivisionAdmin(admin.ModelAdmin):
    list_display = (
        "club",
        "grupo",
        "temporada",
        "jornada",
        "puntos",
        "partidos_jugados",
        "victorias",
        "empates",
        "derrotas",
        "goles_favor",
        "goles_contra",
        "fecha_calculo",
    )
    list_filter = ("temporada", "grupo", "jornada")
    search_fields = ("club__nombre_oficial", "club__nombre_corto", "grupo__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")
    raw_id_fields = ("club", "grupo", "temporada")


@admin.register(MejorEquipoJornadaGlobal)
class MejorEquipoJornadaGlobalAdmin(admin.ModelAdmin):
    list_display = (
        "club",
        "grupo",
        "temporada",
        "semana",
        "puntos",
        "puntos_base",
        "coef_division",
        "partidos_jugados",
        "victorias",
        "empates",
        "derrotas",
        "fecha_calculo",
    )
    list_filter = ("temporada", "semana", "grupo")
    search_fields = ("club__nombre_oficial", "club__nombre_corto", "grupo__nombre")
    readonly_fields = ("fecha_creacion", "fecha_calculo")
    raw_id_fields = ("club", "grupo", "temporada")
