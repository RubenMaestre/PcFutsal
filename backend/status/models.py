from django.db import models
from django.utils import timezone


class DataSyncStatus(models.Model):
    fuente = models.CharField(
        max_length=100,
        unique=True,
        help_text="Identificador de la fuente de datos (ej: 'scrape_semana')",
    )

    last_success = models.DateTimeField(
        default=timezone.now,
        help_text="Momento de la última actualización correcta.",
    )

    detalle = models.TextField(
        blank=True,
        help_text="Resumen breve de lo que se actualizó.",
    )

    class Meta:
        verbose_name = "Estado de sincronización de datos"
        verbose_name_plural = "Estados de sincronización de datos"
        ordering = ["-last_success"]

    def __str__(self):
        return f"{self.fuente} @ {self.last_success}"
