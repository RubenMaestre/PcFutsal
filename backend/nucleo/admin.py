from django.contrib import admin
from .models import Temporada, Competicion, Grupo


@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_inicio", "fecha_fin")
    search_fields = ("nombre",)
    ordering = ("-nombre",)  # ej. 2025/2026 primero


@admin.register(Competicion)
class CompeticionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ambito", "categoria")
    search_fields = ("nombre", "ambito", "categoria")
    list_filter = ("ambito", "categoria")
    ordering = ("nombre",)


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "provincia", "competicion", "temporada")
    list_filter = ("competicion", "temporada", "provincia")
    search_fields = ("nombre", "provincia", "competicion__nombre")
    ordering = ("temporada", "competicion", "nombre")
