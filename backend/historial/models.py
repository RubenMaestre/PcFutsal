from django.db import models


class PropuestaHistorialJugador(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    usuario = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="propuestas_historial",
    )

    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="propuestas_historial",
    )

    temporada_texto = models.CharField(
        max_length=50,
        help_text="Texto libre tipo '2020/2021' por si esa temporada no está creada en BD",
    )

    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="propuestas_historial",
    )

    goles_reportados = models.IntegerField(null=True, blank=True)
    partidos_reportados = models.IntegerField(null=True, blank=True)

    comentario = models.TextField(blank=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    moderador = models.ForeignKey(
        "usuarios.Usuario",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="propuestas_historial_moderadas",
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.jugador} ({self.temporada_texto}) -> {self.estado}"
