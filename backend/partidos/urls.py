from django.urls import path
from . import views

urlpatterns = [
    path("lista/", views.PartidosListView.as_view(), name="partidos-lista"),
    path("detalle/", views.PartidoDetalleView.as_view(), name="partidos-detalle"),
]













