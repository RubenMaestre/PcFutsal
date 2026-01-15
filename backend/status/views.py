from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DataSyncStatus


def format_datetime(dt, lang_code):
    if not dt:
        return "—"

    dt_local = timezone.localtime(dt)

    # inglés americano → mes/día/año
    if lang_code.startswith("en"):
        return dt_local.strftime("%m/%d/%Y %H:%M")
    else:
        # resto → día/mes/año
        return dt_local.strftime("%d/%m/%Y %H:%M")


class LastUpdateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        lang = request.headers.get("Accept-Language", "es").lower()
        obj = DataSyncStatus.objects.order_by("-last_success").first()

        if obj is None:
            return Response({"last_update_display": "—", "detalle": ""})

        return Response({
            "last_update_display": format_datetime(obj.last_success, lang),
            "detalle": obj.detalle,
        })
