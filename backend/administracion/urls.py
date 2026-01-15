from django.contrib import admin
from django.urls import path, include


from status.views import LastUpdateView


urlpatterns = [
    path("admin/", admin.site.urls),

    #APIS
    path("api/status/last_update/", LastUpdateView.as_view(), name="last_update"),
    path("api/nucleo/", include("nucleo.urls")),
    path("api/estadisticas/", include("estadisticas.urls")),
    path("api/clubes/", include("clubes.urls")),
    path("api/valoraciones/", include("valoraciones.urls")),
    path("api/jugadores/", include("jugadores.urls")),
    path("api/partidos/", include("partidos.urls")),
    path("api/fantasy/", include("fantasy.urls")),  # Reconocimientos MVP y Fantasy
]
