from django.contrib import admin
from .models import ValoracionJugador, VotoValoracionJugador, CoeficienteClub, CoeficienteDivision


@admin.register(ValoracionJugador)
class ValoracionJugadorAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "temporada",
        "media_global",
        "ataque",
        "defensa",
        "pase",
        "regate",
        "potencia",
        "intensidad",
        "vision",
        "regularidad",
        "carisma",
    )
    list_filter = ("temporada",)
    search_fields = ("jugador__nombre", "jugador__apodo")


@admin.register(VotoValoracionJugador)
class VotoValoracionJugadorAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "usuario",
        "temporada",
        "atributo",
        "valor",
        "peso_aplicado",
        "creado_en",
    )
    list_filter = ("atributo", "temporada")
    search_fields = ("jugador__nombre", "jugador__apodo", "usuario__username")
    readonly_fields = ("creado_en",)



@admin.register(CoeficienteClub)
class CoeficienteClubAdmin(admin.ModelAdmin):
    list_display = ("club", "temporada", "jornada_referencia", "valor")
    list_filter = ("temporada", "jornada_referencia")
    search_fields = ("club__nombre_oficial", "club__nombre_corto")

@admin.register(CoeficienteDivision)
class CoeficienteDivisionAdmin(admin.ModelAdmin):
    """
    Admin ajustado a los campos reales del modelo.
    Si más adelante añades un CharField 'division', podemos mostrarlo/filtrarlo.
    """
    list_display = (
        "id",
        "competicion",
        "temporada",
        "jornada_referencia",
        "valor",
        "comentario",
        "actualizado_en",
    )
    list_filter = ("competicion", "temporada", "jornada_referencia")
    search_fields = ("competicion__nombre", "temporada__nombre", "comentario")
    ordering = ("competicion", "temporada", "jornada_referencia", "id")
    # el primero de list_display no puede ser editable
    list_editable = ("valor", "comentario")