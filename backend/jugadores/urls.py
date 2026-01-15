# jugadores/urls.py
from django.urls import path
from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
    JugadoresListaView,
)

urlpatterns = [
    path("lista/", JugadoresListaView.as_view(), name="jugadores-lista"),
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]



from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
    JugadoresListaView,
)

urlpatterns = [
    path("lista/", JugadoresListaView.as_view(), name="jugadores-lista"),
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]



from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
    JugadoresListaView,
)

urlpatterns = [
    path("lista/", JugadoresListaView.as_view(), name="jugadores-lista"),
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]



from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
    JugadoresListaView,
)

urlpatterns = [
    path("lista/", JugadoresListaView.as_view(), name="jugadores-lista"),
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]


