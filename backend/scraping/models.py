from django.db import models


class EstadoScraping(models.Model):
    temporada_texto = models.CharField(max_length=20, unique=True)

    # Jornada que estamos monitorizando "esta semana" (en directo)
    jornada_actual = models.IntegerField(default=1)

    # La jornada más antigua que aún tiene pendientes/aplazados
    # Ej: si la J6 tuvo un aplazado que no se jugó aún, esto sigue en 6 aunque estemos ya en la J8
    jornada_pendiente_minima = models.IntegerField(default=1)

    ultima_actualizacion = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default="ok", db_index=True)

    def __str__(self):
        return f"{self.temporada_texto} -> actual J{self.jornada_actual} / pendiente>=J{self.jornada_pendiente_minima}"

