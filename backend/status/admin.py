from django.contrib import admin
from .models import DataSyncStatus


@admin.register(DataSyncStatus)
class DataSyncStatusAdmin(admin.ModelAdmin):
    list_display = ("fuente", "last_success", "detalle")
    list_filter = ("fuente",)
    search_fields = ("fuente", "detalle")
    ordering = ("-last_success",)
