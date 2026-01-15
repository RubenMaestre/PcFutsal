# fantasy/urls.py
"""
URLs para el sistema de reconocimientos MVP y Fantasy.
"""

from django.urls import path
from .views import (
    ReconocimientosJugadorView,
    ReconocimientosEquipoView,
    MVPPartidoView,
    EquipoGlobalOptimizedView,
    MVPGlobalOptimizedView,
    MVPTop3OptimizedView,
)

urlpatterns = [
    path(
        "jugador/<int:jugador_id>/reconocimientos/",
        ReconocimientosJugadorView.as_view(),
        name="reconocimientos-jugador"
    ),
    path(
        "equipo/<int:club_id>/reconocimientos/",
        ReconocimientosEquipoView.as_view(),
        name="reconocimientos-equipo"
    ),
    path(
        "partido/<int:partido_id>/mvp/",
        MVPPartidoView.as_view(),
        name="mvp-partido"
    ),
    path(
        "equipo-global-optimized/",
        EquipoGlobalOptimizedView.as_view(),
        name="equipo-global-optimized"
    ),
    path(
        "mvp-global-optimized/",
        MVPGlobalOptimizedView.as_view(),
        name="mvp-global-optimized"
    ),
    path(
        "mvp-top3-optimized/",
        MVPTop3OptimizedView.as_view(),
        name="mvp-top3-optimized"
    ),
]
