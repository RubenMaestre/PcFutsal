from django.db import models


class Distintivo(models.Model):
    TIPOS_OBJETIVO = [
        ("jugador", "Jugador"),
        ("club", "Club"),
        ("usuario_manager", "Usuario / Manager Fantasy"),
    ]

    nombre = models.CharField(max_length=200)      # "Jugador de la Jornada"
    descripcion = models.TextField(blank=True)
    tipo_aplicable = models.CharField(max_length=20, choices=TIPOS_OBJETIVO)

    def __str__(self):
        return self.nombre


class DistintivoAsignado(models.Model):
    distintivo = models.ForeignKey(
        Distintivo,
        on_delete=models.CASCADE,
        related_name="asignaciones",
    )

    jugador = models.ForeignKey(
        "jugadores.Jugador",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="distintivos",
    )

    club = models.ForeignKey(
        "clubes.Club",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="distintivos",
    )

    usuario_manager = models.ForeignKey(
        "usuarios.Usuario",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="distintivos_ganados_como_manager",
    )

    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="distintivos_asignados",
    )

    jornada = models.IntegerField(
        null=True, blank=True,
        help_text="Jornada concreta si aplica (Jugador de la Jornada 7, etc.)",
    )

    comentario_publico = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        objetivo = self.jugador or self.club or self.usuario_manager
        return f"{self.distintivo} -> {objetivo}"
