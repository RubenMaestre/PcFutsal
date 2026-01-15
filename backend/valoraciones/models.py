from django.db import models


class ValoracionJugador(models.Model):
    """
    Nota 'oficial' agregada de cada jugador por temporada.
    Esto es lo que enseñamos en la ficha (ataque, defensa, regate, etc.).
    """
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="valoraciones",
    )

    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="valoraciones_jugadores",
    )

    ataque = models.IntegerField(default=0)
    defensa = models.IntegerField(default=0)
    pase = models.IntegerField(default=0)
    regate = models.IntegerField(default=0)
    potencia = models.IntegerField(default=0)       # físico / disparo
    intensidad = models.IntegerField(default=0)     # ganas / carácter
    vision = models.IntegerField(default=0)         # lectura táctica
    regularidad = models.IntegerField(default=0)    # fiabilidad
    carisma = models.IntegerField(default=0)        # presencia / liderazgo

    media_global = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("jugador", "temporada")

    def __str__(self):
        return f"{self.jugador} {self.temporada} -> {self.media_global}"


class VotoValoracionJugador(models.Model):
    """
    Cada voto individual emitido por un usuario sobre un atributo concreto
    de un jugador en una temporada.
    """
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="votos_valoracion",
    )

    usuario = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="votos_emitidos",
    )

    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="votos_valoracion",
    )

    atributo = models.CharField(max_length=50)  # "intensidad", "ataque", etc.
    valor = models.IntegerField()               # 0-100 que ha votado
    peso_aplicado = models.IntegerField(default=1)  # cuánto valía su voto en ese momento

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} -> {self.jugador} [{self.atributo}={self.valor}]"


class CoeficienteClub(models.Model):
    """
    Coeficiente de fuerza/dificultad de un club en una temporada.
    
    Este coeficiente se usa para calcular el "interés" de los partidos (partido estrella)
    y para ajustar los puntos MVP según la división. Un club con coeficiente alto
    indica que juega en una división más competitiva.
    
    Podemos guardarlo por jornada de referencia (ej. el de la jornada 6) para tener
    un snapshot del coeficiente en un momento específico de la temporada.
    """
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="coeficientes_temporada",
    )
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="coeficientes_clubes",
    )

    # Jornada de referencia sobre la que se calculó este coeficiente.
    # Ejemplo: 6 → "coef calculado con la foto de la jornada 6"
    # Esto permite tener diferentes coeficientes para la misma temporada si se recalcula.
    jornada_referencia = models.IntegerField(
        null=True, blank=True,
        help_text="Jornada sobre la que se calculó este coeficiente.",
    )

    # Valor del coeficiente (0.1 ... 1.0).
    # 1.0 = máxima dificultad/competitividad, 0.1 = mínima.
    valor = models.FloatField(default=1.0)

    comentario = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("club", "temporada", "jornada_referencia")
        ordering = ["-actualizado_en"]

    def __str__(self):
        jr = f"J{self.jornada_referencia}" if self.jornada_referencia else "sin-jornada"
        return f"{self.club} · {self.temporada} · {jr} → {self.valor}"
    
class CoeficienteDivision(models.Model):
    """
    Coeficiente de fuerza/dificultad de una división (Competición) en una temporada.
    Opcionalmente ligado a una jornada de referencia.
    """
    competicion = models.ForeignKey(
        "nucleo.Competicion",
        on_delete=models.CASCADE,
        related_name="coeficientes_division",
    )
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="coeficientes_division",
    )

    jornada_referencia = models.IntegerField(
        null=True, blank=True,
        help_text="Jornada sobre la que se calculó este coeficiente (opcional).",
    )

    # Escala recomendada 0.6 .. 1.0 (configurable en el comando)
    valor = models.FloatField(default=1.0)

    comentario = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("competicion", "temporada", "jornada_referencia")
        ordering = ["-actualizado_en"]

    def __str__(self):
        jr = f"J{self.jornada_referencia}" if self.jornada_referencia else "sin-jornada"
        return f"{self.competicion} · {self.temporada} · {jr} → {self.valor}"