# clubes/urls.py
from django.urls import path
from .views import (
    ClubesListaView,
    ClubDetalleView,
    ClubFullView,
    ClubHistoricoView,
    ClasificacionEvolucionView,
)

urlpatterns = [
    path("lista/", ClubesListaView.as_view(), name="clubes-lista"),
    path("detalle/", ClubDetalleView.as_view(), name="clubes-detalle"),
    path("full/", ClubFullView.as_view(), name="clubes-full"),
    path("historico/", ClubHistoricoView.as_view(), name="clubes-historico"),
    path("clasificacion-evolucion/", ClasificacionEvolucionView.as_view(), name="clasificacion-evolucion"),
]
