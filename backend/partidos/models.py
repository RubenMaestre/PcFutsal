from django.db import models


class Partido(models.Model):
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partidos",
    )


    jornada_numero = models.IntegerField()

    fecha_hora = models.DateTimeField(null=True, blank=True)

    local = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="partidos_como_local",
    )

    visitante = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="partidos_como_visitante",
    )

    goles_local = models.IntegerField(null=True, blank=True)
    goles_visitante = models.IntegerField(null=True, blank=True)

    jugado = models.BooleanField(default=False)

    # NUEVO: ID oficial para poder hacer rescrape por partido concreto
    identificador_federacion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="ID del partido en federación (ej. 26318901)",
    )

    # NUEVO: pabellón específico del partido (puede diferir del del club si cambian pista)
    pabellon = models.CharField(max_length=200, blank=True)

    # NUEVO: árbitros del partido (lo guardamos como texto libre, ej. 'Fernández Barba, Sergio | ...')
    arbitros = models.TextField(blank=True)

    indice_intensidad = models.IntegerField(
        null=True, blank=True,
        help_text="0-100: partido caliente/loco (muchos goles, muchas tarjetas...)",
    )

    # Score de interés del partido (calculado una vez y fijo)
    score_interes = models.FloatField(
        null=True, blank=True,
        help_text="Score de interés del partido calculado en función de clasificación, racha, goles, etc. Se calcula una vez y no cambia.",
    )

    def __str__(self):
        marcador = ""
        if (
            self.jugado
            and self.goles_local is not None
            and self.goles_visitante is not None
        ):
            marcador = f" ({self.goles_local}-{self.goles_visitante})"
        return f"J{self.jornada_numero}: {self.local} vs {self.visitante}{marcador}"


class EventoPartido(models.Model):
    TIPOS_EVENTO = [
        ("gol", "Gol"),
        ("gol_pp", "Gol en propia puerta"),
        ("amarilla", "Tarjeta amarilla"),
        ("doble_amarilla", "Doble amarilla"),
        ("roja", "Tarjeta roja"),
        ("mvp", "MVP del partido"),
    ]

    partido = models.ForeignKey(
        Partido,
        on_delete=models.CASCADE,
        related_name="eventos",
    )

    minuto = models.IntegerField(null=True, blank=True)

    tipo_evento = models.CharField(max_length=20, choices=TIPOS_EVENTO)

    jugador = models.ForeignKey(
        "jugadores.Jugador",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="eventos_en_partidos",
    )

    club = models.ForeignKey(
        "clubes.Club",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="eventos_en_partidos",
    )

    nota = models.TextField(
        blank=True,
        help_text="Descripción rápida: 'Gol segundo palo en transición 3v2'",
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.partido} -> {self.tipo_evento}"


# NUEVO
class AlineacionPartidoJugador(models.Model):
    """
    Titulares y suplentes de cada equipo en un partido concreto.
    Nos viene del scrape del acta:
    - titular/suplente
    - dorsal
    - etiqueta: 'Pt' (portero), 'Ps' (portero suplente), 'C' (capitán)...
    """
    partido = models.ForeignKey(
        Partido,
        on_delete=models.CASCADE,
        related_name="alineaciones_jugadores",
    )

    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="alineaciones_partido",
    )

    jugador = models.ForeignKey(
        "jugadores.Jugador",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="alineaciones_en_partidos",
    )

    dorsal = models.CharField(max_length=10, blank=True)

    titular = models.BooleanField(default=False)

    etiqueta = models.CharField(
        max_length=10,
        blank=True,
        help_text="Pt=portero, Ps=portero suplente, C=capitán, etc.",
    )

    def __str__(self):
        rol = "Titular" if self.titular else "Suplente"
        return f"{self.partido} / {self.club} / {self.jugador} ({rol} {self.dorsal})"
