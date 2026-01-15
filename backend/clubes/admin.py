# clubes/admin.py
from django.contrib import admin
from .models import (
    Club, ClubAlias,
    ClubBoardMember, ClubStaffMember, ClubManager,
    ClubEnGrupo, ClubSeasonProgress, ClubSeasonHistory,
    ClubAward, ClubTrip, ClubTravelStat,
    ClubMedia, ClubNota,
)

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre_corto", "nombre_oficial", "ciudad", "provincia", "web", "activo")
    list_filter  = ("activo", "provincia")
    search_fields = ("nombre_oficial", "nombre_corto", "siglas", "ciudad", "provincia")
    prepopulated_fields = {"slug": ("nombre_corto",)}
    readonly_fields = ("creado_en", "actualizado_en")

@admin.register(ClubAlias)
class ClubAliasAdmin(admin.ModelAdmin):
    list_display = ("alias", "club")
    search_fields = ("alias", "club__nombre_oficial", "club__nombre_corto")

@admin.register(ClubBoardMember)
class ClubBoardMemberAdmin(admin.ModelAdmin):
    list_display = ("club", "cargo", "nombre", "visible_publico", "orden")
    list_filter  = ("visible_publico", "cargo")
    search_fields = ("nombre", "cargo", "club__nombre_corto", "club__nombre_oficial")
    ordering = ("club", "orden", "cargo")

@admin.register(ClubStaffMember)
class ClubStaffMemberAdmin(admin.ModelAdmin):
    list_display = ("club", "temporada", "rol", "nombre", "visible_publico", "orden")
    list_filter  = ("temporada", "rol", "visible_publico")
    search_fields = ("nombre", "rol", "club__nombre_corto", "club__nombre_oficial")
    ordering = ("temporada__nombre", "club__nombre_corto", "orden")

@admin.register(ClubManager)
class ClubManagerAdmin(admin.ModelAdmin):
    list_display = ("club", "usuario", "puede_editar_identidad", "puede_editar_staff",
                    "puede_editar_multimedia", "puede_editar_logistica")
    list_filter  = ("puede_editar_identidad", "puede_editar_staff",
                    "puede_editar_multimedia", "puede_editar_logistica")
    search_fields = ("club__nombre_corto", "club__nombre_oficial", "usuario__username", "usuario__email")

@admin.register(ClubEnGrupo)
class ClubEnGrupoAdmin(admin.ModelAdmin):
    list_display = ("club", "grupo", "posicion_actual", "puntos", "partidos_jugados",
                    "victorias", "empates", "derrotas", "goles_favor", "goles_contra", "diferencia_goles", "racha")
    list_filter  = ("grupo",)
    search_fields = ("club__nombre_corto", "club__nombre_oficial", "grupo__nombre")
    readonly_fields = ("creado_en", "actualizado_en")

@admin.register(ClubSeasonProgress)
class ClubSeasonProgressAdmin(admin.ModelAdmin):
    list_display = ("club", "grupo", "jornada", "puntos_acum", "gf_acum", "gc_acum", "pos_clasif")
    list_filter  = ("grupo",)
    search_fields = ("club__nombre_corto", "club__nombre_oficial", "grupo__nombre")
    ordering = ("grupo", "jornada")

@admin.register(ClubSeasonHistory)
class ClubSeasonHistoryAdmin(admin.ModelAdmin):
    list_display = ("club", "temporada", "competicion", "grupo_text", "pos_final", "puntos", "pj", "v", "e", "d", "gf", "gc")
    list_filter  = ("temporada", "competicion")
    search_fields = ("club__nombre_corto", "club__nombre_oficial", "competicion", "grupo_text")
    ordering = ("-temporada__nombre", "club__nombre_corto")

@admin.register(ClubAward)
class ClubAwardAdmin(admin.ModelAdmin):
    list_display = ("club", "grupo", "jornada", "tipo", "notas", "creado_en")
    list_filter  = ("tipo", "grupo")
    search_fields = ("club__nombre_corto", "club__nombre_oficial", "grupo__nombre")
    ordering = ("-creado_en",)

@admin.register(ClubTrip)
class ClubTripAdmin(admin.ModelAdmin):
    list_display = ("club_origen", "club_destino", "temporada", "grupo", "distancia_km", "duracion_min")
    list_filter  = ("temporada", "grupo")
    search_fields = ("club_origen__nombre_corto", "club_destino__nombre_corto",
                     "club_origen__nombre_oficial", "club_destino__nombre_oficial")

@admin.register(ClubTravelStat)
class ClubTravelStatAdmin(admin.ModelAdmin):
    list_display = ("club", "temporada", "grupo", "total_km", "avg_km", "min_km", "max_km", "min_km_rival", "max_km_rival", "actualizado_en")
    list_filter  = ("temporada", "grupo")
    search_fields = ("club__nombre_corto", "club__nombre_oficial")

@admin.register(ClubMedia)
class ClubMediaAdmin(admin.ModelAdmin):
    list_display = ("club", "tipo", "titulo", "visible_publico", "creado_en")
    list_filter  = ("tipo", "visible_publico")
    search_fields = ("titulo", "club__nombre_corto", "club__nombre_oficial")

@admin.register(ClubNota)
class ClubNotaAdmin(admin.ModelAdmin):
    list_display = ("club", "grupo", "titulo", "creado_en", "actualizado_en")
    list_filter  = ("grupo",)
    search_fields = ("titulo", "texto", "club__nombre_corto", "club__nombre_oficial")
