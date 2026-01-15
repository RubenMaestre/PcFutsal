from django.contrib import admin
from .models import Arbitro, ArbitrajePartido


@admin.register(Arbitro)
class ArbitroAdmin(admin.ModelAdmin):
    list_display = ("nombre", "identificador_federacion", "activo")
    search_fields = ("nombre", "identificador_federacion")
    list_filter = ("activo",)
    ordering = ("nombre",)


@admin.register(ArbitrajePartido)
class ArbitrajePartidoAdmin(admin.ModelAdmin):
    list_display = ("partido", "arbitro", "rol")
    list_filter = ("rol", "arbitro", "partido__grupo")
    search_fields = (
        "arbitro__nombre",
        "partido__local__nombre_oficial",
        "partido__visitante__nombre_oficial",
    )
    autocomplete_fields = ("partido", "arbitro")
