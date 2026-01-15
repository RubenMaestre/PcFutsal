from django.db import models


class StaffClub(models.Model):
    """
    Personal técnico de un club (entrenadores, delegados, fisioterapeutas...) por temporada.
    """
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="staff_temporada",
    )

    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="staff_tecnicos",
    )


    nombre = models.CharField(max_length=200)
    rol = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.rol}) - {self.club}"


class StaffEnPartido(models.Model):
    """
    Staff presente en un partido (entrenador, delegado, segundo entrenador...).
    Puede no coincidir exactamente con el StaffClub registrado.
    """
    partido = models.ForeignKey(
        "partidos.Partido",
        on_delete=models.CASCADE,
        related_name="staff_partido",
    )

    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="staff_en_partidos",
    )

    staff = models.ForeignKey(
        "staff.StaffClub",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="apariciones_en_partidos",
    )

    nombre = models.CharField(max_length=200)
    rol = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.rol}) en {self.partido}"
