# valoraciones/urls.py
from django.urls import path
from .views import (
    PartidoEstrellaView,
    EquipoJornadaView,
    JugadoresJornadaView,
    MVPClasificacionView,
    EquipoJornadaGlobalView,
    JugadoresJornadaGlobalView,
    PartidosTopGlobalView,
    MVPGlobalView,
    CalcularScoreInteresView,
)

urlpatterns = [
    path("partido-estrella/", PartidoEstrellaView.as_view(), name="partido-estrella"),
    path("equipo-jornada/", EquipoJornadaView.as_view(), name="equipo-jornada"),
    path("jugadores-jornada/", JugadoresJornadaView.as_view(), name="jugadores-jornada"),
    path("mvp-clasificacion/", MVPClasificacionView.as_view(), name="mvp-clasificacion"),
    path("equipo-jornada-global/", EquipoJornadaGlobalView.as_view(), name="equipo-jornada-global"),
    path("jugadores-jornada-global/", JugadoresJornadaGlobalView.as_view(), name="jugadores-jornada-global"),
    path("partidos-top-global/", PartidosTopGlobalView.as_view(), name="partidos-top-global"),
    path("partidos-estrella-global/", PartidosTopGlobalView.as_view(), name="partidos-estrella-global"),
    path("mvp-global/", MVPGlobalView.as_view(), name="mvp-global"),
    path("calcular-score-interes/", CalcularScoreInteresView.as_view(), name="calcular-score-interes"),
]
