from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    ROLES = [
        ("aficionado", "Aficionado"),
        ("jugador", "Jugador verificado"),
        ("entrenador", "Entrenador verificado"),
        ("admin", "Administrador"),
    ]

    rol_base = models.CharField(max_length=20, choices=ROLES, default="aficionado")
    verificado = models.BooleanField(default=False)

    jugador_asociado = models.ForeignKey(
        "jugadores.Jugador",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="usuarios_relacionados",
        verbose_name="Jugador asociado",
    )

    club_asociado = models.ForeignKey(
        "clubes.Club",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="usuarios_relacionados",
        verbose_name="Club asociado",
    )

    def peso_voto(self):
        """
        Lógica de ponderación:
        - Aficionado normal          -> 1
        - Jugador verificado         -> 2
        - Entrenador verificado      -> 3
        - Admin                      -> 3
        """
        if self.rol_base == "entrenador" and self.verificado:
            return 3
        if self.rol_base == "jugador" and self.verificado:
            return 2
        if self.rol_base == "admin":
            return 3
        return 1

    def __str__(self):
        return self.username


class SolicitudVerificacion(models.Model):
    TIPOS = [
        ("jugador", "Jugador"),
        ("entrenador", "Entrenador / Staff"),
    ]
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="solicitudes_verificacion",
    )

    tipo = models.CharField(max_length=20, choices=TIPOS)

    club_reivindicado = models.ForeignKey(
        "clubes.Club",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="solicitudes_verificacion_entrenador",
        verbose_name="Club que dice representar",
    )

    jugador_reivindicado = models.ForeignKey(
        "jugadores.Jugador",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="solicitudes_verificacion_jugador",
        verbose_name="Jugador que dice ser",
    )

    evidencia_url = models.TextField(blank=True)  # foto, captura, etc.
    comentario = models.TextField(blank=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    creado_en = models.DateTimeField(auto_now_add=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} -> {self.tipo} ({self.estado})"
