from django.urls import path

from .views_grupo_info import GrupoInfoFullView
from .views_coeficientes import CoeficientesClubesView
from .views import (
    ClasificacionMiniView,
    ClasificacionCompletaView,
    ClasificacionEvolucionView,
    ResultadosJornadaView,
    GoleadoresJornadaView,
    PichichiTemporadaView,
    KPIsJornadaView,
    GolesPorEquipoView,
    SancionesJornadaView,
    SancionesJugadoresAcumuladoView,
    FairPlayEquiposView,
    GoleadoresGlobalOptimizedView,
    SancionesGlobalOptimizedView,
)

urlpatterns = [
    # info general del grupo
    path("grupo-info/", GrupoInfoFullView.as_view(), name="grupo-info"),

    # clasificaciones
    path("clasificacion-mini/", ClasificacionMiniView.as_view(), name="clasificacion-mini"),
    path("clasificacion-completa/", ClasificacionCompletaView.as_view(), name="clasificacion-completa"),
    path("clasificacion-evolucion/", ClasificacionEvolucionView.as_view(), name="clasificacion-evolucion"),

    # jornadas / partidos
    path("resultados-jornada/", ResultadosJornadaView.as_view(), name="resultados-jornada"),
    path("kpis-jornada/", KPIsJornadaView.as_view(), name="kpis-jornada"),

    # rankings ofensivos / goleadores
    path("goleadores-jornada/", GoleadoresJornadaView.as_view(), name="goleadores-jornada"),
    path("pichichi-temporada/", PichichiTemporadaView.as_view(), name="pichichi-temporada"),
    path("goles-por-equipo/", GolesPorEquipoView.as_view(), name="goles-por-equipo"),

    # disciplina
    path("sanciones-jornada/", SancionesJornadaView.as_view(), name="sanciones-jornada"),
    path("sanciones-jugadores/", SancionesJugadoresAcumuladoView.as_view(), name="sanciones-jugadores"),
    path("fair-play-equipos/", FairPlayEquiposView.as_view(), name="fair-play-equipos"),

    # rankings globales optimizados (todas las divisiones)
    path("goleadores-global-optimized/", GoleadoresGlobalOptimizedView.as_view(), name="goleadores-global-optimized"),
    path("sanciones-global-optimized/", SancionesGlobalOptimizedView.as_view(), name="sanciones-global-optimized"),

    #Coeficientes
    path("coeficientes-clubes/", CoeficientesClubesView.as_view(), name="coeficientes-clubes"),
]
