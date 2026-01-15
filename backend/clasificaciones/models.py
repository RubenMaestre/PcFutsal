# clasificaciones/models.py
from django.db import models
from nucleo.models import Grupo
from clubes.models import Club


class ClasificacionJornada(models.Model):
    """
    Almacena la clasificación completa de un grupo en una jornada específica.
    Snapshot completo de la tabla en ese momento.
    """
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name="clasificaciones_jornada"
    )
    jornada = models.PositiveIntegerField()
    fecha_calculo = models.DateTimeField(auto_now_add=True)

    # Metadata
    partidos_jugados_total = models.PositiveIntegerField(
        default=0,
        help_text="Total de partidos jugados hasta esa jornada"
    )
    equipos_participantes = models.PositiveIntegerField(
        default=0,
        help_text="Número de equipos en la clasificación"
    )

    class Meta:
        # Un grupo solo puede tener una clasificación por jornada
        unique_together = (("grupo", "jornada"),)
        indexes = [
            # Índice para búsquedas por grupo y jornada (consulta más común)
            models.Index(fields=["grupo", "jornada"]),
            # Índice para obtener la última jornada de un grupo (orden descendente)
            models.Index(fields=["grupo", "-jornada"]),
        ]
        ordering = ["grupo", "jornada"]
        verbose_name = "Clasificación por Jornada"
        verbose_name_plural = "Clasificaciones por Jornada"

    def __str__(self):
        return f"{self.grupo.nombre} - Jornada {self.jornada}"


class PosicionJornada(models.Model):
    """
    Almacena la posición de un equipo en una jornada específica.
    Relación 1:N con ClasificacionJornada (un equipo por jornada).
    """
    clasificacion_jornada = models.ForeignKey(
        ClasificacionJornada,
        on_delete=models.CASCADE,
        related_name="posiciones"
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="posiciones_jornada"
    )

    # Datos de la clasificación en esa jornada
    posicion = models.PositiveIntegerField(help_text="Posición en la clasificación (1, 2, 3...)")
    puntos = models.IntegerField(default=0)
    partidos_jugados = models.PositiveIntegerField(default=0)
    partidos_ganados = models.PositiveIntegerField(default=0)
    partidos_empatados = models.PositiveIntegerField(default=0)
    partidos_perdidos = models.PositiveIntegerField(default=0)
    goles_favor = models.IntegerField(default=0)
    goles_contra = models.IntegerField(default=0)
    diferencia_goles = models.IntegerField(default=0)
    racha = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="Últimos 5 resultados: 'VVEDV' (Victoria, Victoria, Empate, Derrota, Victoria)"
    )

    # Para cálculos de desempate (si los necesitamos en el futuro)
    enfrentamientos_directos = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos de enfrentamientos directos para desempate"
    )

    class Meta:
        # Un club solo puede aparecer una vez por clasificación (snapshot único)
        unique_together = (("clasificacion_jornada", "club"),)
        indexes = [
            # Índice para ordenar por posición dentro de una jornada (gráficas de evolución)
            models.Index(fields=["clasificacion_jornada", "posicion"]),
            # Índice para buscar todas las posiciones de un club a lo largo del tiempo
            models.Index(fields=["club", "clasificacion_jornada"]),
        ]
        ordering = ["clasificacion_jornada", "posicion"]
        verbose_name = "Posición por Jornada"
        verbose_name_plural = "Posiciones por Jornada"

    def __str__(self):
        return f"{self.club} - {self.clasificacion_jornada} - Pos {self.posicion}"
