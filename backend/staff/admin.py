from django.contrib import admin
from .models import StaffClub, StaffEnPartido


@admin.register(StaffClub)
class StaffClubAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rol", "club", "temporada", "activo")
    search_fields = (
        "nombre",
        "rol",
        "club__nombre_oficial",
        "club__nombre_corto",
    )
    list_filter = ("rol", "temporada", "club", "activo")
    ordering = ("club", "nombre")
    list_editable = ("activo",)


@admin.register(StaffEnPartido)
class StaffEnPartidoAdmin(admin.ModelAdmin):
    list_display = ("partido", "club", "nombre", "rol", "staff")
    list_filter = (
        "rol",
        "partido__grupo",
        "partido__grupo__temporada",
        "partido__jornada_numero",
        "club",
    )
    search_fields = (
        "nombre",
        "rol",
        "staff__nombre",
        "club__nombre_oficial",
        "club__nombre_corto",
        "partido__local__nombre_oficial",
        "partido__visitante__nombre_oficial",
    )
    autocomplete_fields = ("partido", "club", "staff")
    ordering = ("partido", "club", "rol")
