from django.urls import path
from .views import FilterContextAPIView

urlpatterns = [
    path("filter-context/", FilterContextAPIView.as_view(), name="filter-context"),
]
