from django.db import models


class JornadaFantasy(models.Model):
    ESTADOS = [
        ("abierta", "Abierta para elegir equipo"),
        ("cerrada", "Cerrada / en juego"),
        ("finalizada", "Finalizada"),
    ]

    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="jornadas_fantasy",
    )

    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="jornadas_fantasy",
    )

    numero_jornada = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="abierta")

    class Meta:
        unique_together = ("grupo", "temporada", "numero_jornada")

    def __str__(self):
        return f"Fantasy {self.grupo} J{self.numero_jornada} {self.temporada}"


class EquipoFantasyUsuario(models.Model):
    jornada_fantasy = models.ForeignKey(
        JornadaFantasy,
        on_delete=models.CASCADE,
        related_name="equipos_usuario",
    )

    usuario = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="equipos_fantasy",
    )

    jugador_portero = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="alineaciones_fantasy_portero",
    )

    jugador_cierre = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="alineaciones_fantasy_cierre",
    )

    jugador_ala = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="alineaciones_fantasy_ala",
    )

    jugador_pivot = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="alineaciones_fantasy_pivot",
    )

    jugador_extra = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="alineaciones_fantasy_extra",
    )

    puntos_totales_semana = models.IntegerField(default=0)
    posicion_en_ranking_semana = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("jornada_fantasy", "usuario")

    def __str__(self):
        return f"{self.usuario} @ {self.jornada_fantasy}"


class PuntosFantasyJugador(models.Model):
    jornada_fantasy = models.ForeignKey(
        JornadaFantasy,
        on_delete=models.CASCADE,
        related_name="puntos_jugadores",
    )

    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="puntos_fantasy",
    )

    goles = models.IntegerField(default=0)
    tarjetas = models.IntegerField(default=0)  # total tarjetas (ya refinaremos amarilla/roja por separado si queremos)
    mvp = models.BooleanField(default=False)
    victoria_equipo = models.BooleanField(default=False)

    puntos_resultado_final_calculado = models.IntegerField(default=0)

    class Meta:
        unique_together = ("jornada_fantasy", "jugador")

    def __str__(self):
        return f"{self.jugador} -> {self.puntos_resultado_final_calculado} pts ({self.jornada_fantasy})"


class PuntosMVPJornada(models.Model):
    """
    Almacena los puntos MVP de un jugador en una jornada/semana específica.
    
    Estos puntos se calculan desde valoraciones y se almacenan aquí para optimizar
    el ranking MVP global. Esto evita tener que recalcular los puntos cada vez
    que se consulta el ranking, mejorando significativamente el rendimiento.
    
    Se crea/actualiza cuando termina una jornada o semana mediante un management command.
    """
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="puntos_mvp_jornada",
    )
    
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="puntos_mvp_jornada",
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="puntos_mvp_jornada",
    )
    
    # Número de jornada (del grupo)
    jornada = models.IntegerField()
    
    # Puntos calculados (sin coeficiente división)
    puntos_base = models.FloatField(default=0.0)
    
    # Puntos con coeficiente división aplicado
    puntos_con_coef = models.FloatField(default=0.0)
    
    # Coeficiente de división usado en el momento del cálculo
    coef_division = models.FloatField(default=1.0)
    
    # Metadatos de la jornada
    partidos_jugados = models.IntegerField(default=0)  # Partidos jugados en esa jornada
    goles = models.IntegerField(default=0)  # Goles en esa jornada
    
    # Fecha de cálculo (última vez que se actualizaron)
    fecha_calculo = models.DateTimeField(auto_now=True)
    
    # Fecha de creación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("jugador", "temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["jugador", "temporada"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
            models.Index(fields=["temporada", "jornada"]),
        ]
        ordering = ["-temporada", "-jornada", "-puntos_con_coef"]
    
    def __str__(self):
        return f"{self.jugador} - {self.grupo} J{self.jornada} -> {self.puntos_con_coef} pts"


class PuntosMVPTotalJugador(models.Model):
    """
    Almacena el SUMATORIO TOTAL de puntos MVP de un jugador en una temporada.
    Esta tabla se actualiza cada vez que se calculan puntos de una jornada,
    sumando los nuevos puntos al total acumulado.
    
    Permite cargar el ranking global de forma muy rápida sin tener que hacer
    SUM() sobre todas las jornadas cada vez.
    """
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="puntos_mvp_total",
    )
    
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="puntos_mvp_total",
    )
    
    # Sumatorio de puntos base (sin coeficiente)
    puntos_base_total = models.FloatField(default=0.0)
    
    # Sumatorio de puntos con coeficiente aplicado (este es el que se usa para ranking)
    puntos_con_coef_total = models.FloatField(default=0.0)
    
    # Metadatos acumulados
    goles_total = models.IntegerField(default=0)
    partidos_total = models.IntegerField(default=0)
    
    # Última jornada procesada (para saber si hay que actualizar)
    ultima_jornada_procesada = models.IntegerField(default=0)
    
    # Fecha de última actualización
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Fecha de creación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("jugador", "temporada")
        indexes = [
            models.Index(fields=["temporada", "-puntos_con_coef_total"]),  # Para ranking rápido
            models.Index(fields=["jugador", "temporada"]),
        ]
        ordering = ["-temporada", "-puntos_con_coef_total"]
    
    def __str__(self):
        return f"{self.jugador} ({self.temporada}): {self.puntos_con_coef_total:.0f} pts totales"


class PuntosEquipoJornada(models.Model):
    """
    Almacena los puntos fantasy de un equipo/club en una jornada específica.
    Estos puntos se calculan desde valoraciones y se almacenan aquí para optimizar
    el ranking global de equipos (evitar recalcular cada vez).
    
    Se crea/actualiza cuando termina una jornada o semana.
    """
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="puntos_equipo_jornada",
    )
    
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="puntos_equipo_jornada",
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="puntos_equipo_jornada",
    )
    
    # Número de jornada (del grupo)
    jornada = models.IntegerField()
    
    # Puntos calculados para esta jornada
    puntos = models.FloatField(default=0.0)
    
    # Metadatos de la jornada
    partidos_jugados = models.IntegerField(default=0)  # Partidos jugados en esa jornada
    victorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    goles_favor = models.IntegerField(default=0)
    goles_contra = models.IntegerField(default=0)
    
    # Fecha de cálculo (última vez que se actualizaron)
    fecha_calculo = models.DateTimeField(auto_now=True)
    
    # Fecha de creación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("club", "temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["club", "temporada"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
            models.Index(fields=["temporada", "jornada"]),
        ]
        ordering = ["-temporada", "-jornada", "-puntos"]
    
    def __str__(self):
        return f"{self.club} - {self.grupo} J{self.jornada} -> {self.puntos:.2f} pts"


class PuntosEquipoTotal(models.Model):
    """
    Almacena el SUMATORIO TOTAL de puntos fantasy de un equipo/club en una temporada.
    Esta tabla se actualiza cada vez que se calculan puntos de una jornada,
    sumando los nuevos puntos al total acumulado.
    
    Permite cargar el ranking global de equipos de forma muy rápida sin tener que hacer
    SUM() sobre todas las jornadas cada vez.
    """
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="puntos_equipo_total",
    )
    
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="puntos_equipo_total",
    )
    
    # Sumatorio de puntos totales
    puntos_total = models.FloatField(default=0.0)
    
    # Metadatos acumulados
    partidos_total = models.IntegerField(default=0)
    victorias_total = models.IntegerField(default=0)
    empates_total = models.IntegerField(default=0)
    derrotas_total = models.IntegerField(default=0)
    goles_favor_total = models.IntegerField(default=0)
    goles_contra_total = models.IntegerField(default=0)
    
    # Última jornada procesada
    ultima_jornada_procesada = models.IntegerField(default=0)
    
    # Fecha de última actualización
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Fecha de creación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("club", "temporada")
        indexes = [
            models.Index(fields=["temporada", "-puntos_total"]),  # Para ranking rápido
            models.Index(fields=["club", "temporada"]),
        ]
        ordering = ["-temporada", "-puntos_total"]
    
    def __str__(self):
        return f"{self.club} ({self.temporada}): {self.puntos_total:.2f} pts totales"


# ============================================================================
# MODELOS DE RECONOCIMIENTOS MVP Y FANTASY
# ============================================================================

class MVPPartido(models.Model):
    """
    Almacena el MVP de cada partido.
    Se calcula seleccionando al jugador con más puntos en ese partido.
    
    Criterios de desempate (en caso de empate a puntos):
    1. Jugador del equipo que ganó el partido
    2. Jugador que marcó más goles
    3. Jugador que recibió menos tarjetas
    4. Jugador con más puntos MVP acumulados en la temporada
    """
    partido = models.OneToOneField(
        "partidos.Partido",
        on_delete=models.CASCADE,
        related_name="mvp_partido"
    )
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="mvp_partidos"
    )
    
    puntos = models.FloatField()  # Puntos obtenidos en ese partido
    
    # Metadatos
    goles = models.IntegerField(default=0)
    tarjetas_amarillas = models.IntegerField(default=0)
    tarjetas_rojas = models.IntegerField(default=0)
    mvp_evento = models.BooleanField(default=False)  # Si tuvo evento MVP
    
    # Para desempate
    equipo_ganador = models.BooleanField(default=False)  # Si su equipo ganó el partido
    puntos_mvp_acumulados = models.FloatField(default=0)  # Puntos MVP acumulados en temporada (al momento del cálculo)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["partido"]),
        ]
    
    def __str__(self):
        return f"MVP {self.partido}: {self.jugador} ({self.puntos} pts)"


class MVPJornadaDivision(models.Model):
    """
    Almacena el MVP de la jornada por división/grupo.
    Se calcula los domingos por la noche cuando terminan todos los partidos.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_division"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas"
    )
    
    jornada = models.IntegerField()
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_division"
    )
    
    puntos = models.FloatField()  # Puntos totales en esa jornada
    puntos_con_coef = models.FloatField()  # Puntos con coeficiente división
    coef_division = models.FloatField()  # Coeficiente usado
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    goles = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
        ]
    
    def __str__(self):
        return f"MVP J{self.jornada} {self.grupo}: {self.jugador} ({self.puntos_con_coef} pts)"


class MVPJornadaGlobal(models.Model):
    """
    Almacena el MVP global de la semana (todas las divisiones).
    Se calcula los domingos por la noche.
    
    IMPORTANTE: Los reconocimientos globales se calculan por SEMANAS
    (Miércoles 19:00 - Domingo 21:00), NO por jornadas numéricas.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_global"
    )
    
    # Semana: fecha del martes de esa semana (formato YYYY-MM-DD)
    # Ejemplo: Si la semana es Mi 15/01 - Do 19/01, semana = "2025-01-21" (martes)
    semana = models.DateField()  # Fecha del martes de la semana
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_global"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_globales"
    )
    
    puntos = models.FloatField()  # Puntos totales con coeficiente división aplicado
    puntos_base = models.FloatField()  # Puntos sin coeficiente
    coef_division = models.FloatField()  # Coeficiente de división usado
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    goles = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "semana")
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["temporada", "semana"]),
        ]
    
    def __str__(self):
        return f"MVP Global Semana {self.semana}: {self.jugador} ({self.puntos} pts)"


class GoleadorJornadaDivision(models.Model):
    """
    Almacena el goleador de la jornada por división/grupo.
    Se calcula los domingos por la noche.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="goleadores_jornadas_division"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="goleadores_jornadas"
    )
    
    jornada = models.IntegerField()
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="goleador_jornadas_division"
    )
    
    goles = models.IntegerField()  # Goles en esa jornada
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
        ]
    
    def __str__(self):
        return f"Goleador J{self.jornada} {self.grupo}: {self.jugador} ({self.goles} goles)"


class MejorEquipoJornadaDivision(models.Model):
    """
    Almacena el mejor equipo de la jornada por división/grupo.
    Se calcula los domingos por la noche.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas_division"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas"
    )
    
    jornada = models.IntegerField()
    
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="mejor_equipo_jornadas_division"
    )
    
    puntos = models.FloatField()  # Puntos totales en esa jornada
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    victorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    goles_favor = models.IntegerField(default=0)
    goles_contra = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["club", "-fecha_creacion"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
        ]
    
    def __str__(self):
        return f"Mejor Equipo J{self.jornada} {self.grupo}: {self.club} ({self.puntos} pts)"


class MejorEquipoJornadaGlobal(models.Model):
    """
    Almacena el mejor equipo global de la semana (todas las divisiones).
    Se calcula los domingos por la noche.
    
    IMPORTANTE: Los reconocimientos globales se calculan por SEMANAS
    (Miércoles 19:00 - Domingo 21:00), NO por jornadas numéricas.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas_global"
    )
    
    # Semana: fecha del martes de esa semana (formato YYYY-MM-DD)
    # Ejemplo: Si la semana es Mi 15/01 - Do 19/01, semana = "2025-01-21" (martes)
    semana = models.DateField()  # Fecha del martes de la semana
    
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="mejor_equipo_jornadas_global"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas_globales"
    )
    
    puntos = models.FloatField()  # Puntos totales con coeficiente división aplicado
    puntos_base = models.FloatField()  # Puntos sin coeficiente
    coef_division = models.FloatField()  # Coeficiente de división usado
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    victorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    goles_favor = models.IntegerField(default=0)
    goles_contra = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "semana")
        indexes = [
            models.Index(fields=["club", "-fecha_creacion"]),
            models.Index(fields=["temporada", "semana"]),
        ]
    
    def __str__(self):
        return f"Mejor Equipo Global Semana {self.semana}: {self.club} ({self.puntos} pts)"
