# /backend/destacados/admin.py
from django.contrib import admin
from .models import Distintivo, DistintivoAsignado


@admin.register(Distintivo)
class DistintivoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo_aplicable")
    list_filter = ("tipo_aplicable",)
    search_fields = ("nombre",)


@admin.register(DistintivoAsignado)
class DistintivoAsignadoAdmin(admin.ModelAdmin):
    list_display = (
        "distintivo",
        "jugador",
        "club",
        "usuario_manager",
        "temporada",
        "jornada",
        "comentario_publico",
        "creado_en",
    )
    list_filter = ("temporada", "jornada", "distintivo")
    search_fields = (
        "jugador__nombre",
        "jugador__apodo",
        "club__nombre_corto",
        "club__nombre_oficial",
        "usuario_manager__username",
        "comentario_publico",
    )
    readonly_fields = ("creado_en",)
