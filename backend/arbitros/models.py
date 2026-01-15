from django.db import models


class Arbitro(models.Model):
    nombre = models.CharField(max_length=200)

    identificador_federacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,          # <- NUEVO
        unique=True,
        help_text="ID oficial del árbitro en la federación (si lo tenemos)",
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class ArbitrajePartido(models.Model):
    """
    Relación árbitro ↔ partido (puede haber varios árbitros por partido).
    """
    partido = models.ForeignKey(
        "partidos.Partido",
        on_delete=models.CASCADE,
        related_name="arbitrajes",
    )

    arbitro = models.ForeignKey(
        "arbitros.Arbitro",
        on_delete=models.CASCADE,
        related_name="partidos_dirigidos",
    )

    rol = models.CharField(
        max_length=50,
        blank=True,
        help_text="Principal / Auxiliar / Mesa / Cronometrador...",
    )

    def __str__(self):
        return f"{self.arbitro} en {self.partido} ({self.rol})"
