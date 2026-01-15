from django.db import models
from django.utils.text import slugify


class Jugador(models.Model):
    POSICIONES = [
        ("portero", "Portero"),
        ("cierre", "Cierre"),
        ("ala", "Ala"),
        ("pivot", "Pívot"),
        ("universal", "Universal"),
    ]

    nombre = models.CharField(max_length=200)
    apodo = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)

    # Fecha real de nacimiento si la sabemos (aportada por el propio jugador o scraping futuro)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    posicion_principal = models.CharField(
        max_length=20,
        choices=POSICIONES,
        blank=True,
    )

    # Ruta local donde guardamos la imagen del jugador (media/jugadores/xxx.png)
    foto_url = models.TextField(blank=True)

    # Texto tipo scouting / descripción estilo prensa
    informe_scout = models.TextField(blank=True)

    # ID único federación / scraping
    identificador_federacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text="ID del jugador en federación / scraping",
    )

    # =============== GESTIÓN DE EDAD ==================
    # Edad que tenemos ahora mismo para mostrar públicamente
    # cuando NO conocemos fecha_nacimiento exacta.
    # Ej: "29" tal cual aparece en la ficha federativa.
    edad_estimacion = models.IntegerField(
        null=True,
        blank=True,
        help_text="Edad conocida/scrapeada si no tenemos fecha_nacimiento exacta.",
    )

    # Año natural en el que guardamos por primera vez esa edad estimada.
    # Ej: si en la temporada 2025-2026 la ficha dice que tiene 29,
    # guardamos edad_estimacion=29 y edad_estimacion_base_year=2025.
    # Esto nos permite luego incrementarla +1 cada 1 de enero.
    edad_estimacion_base_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Año natural en el que se obtuvo la edad_estimacion desde federación.",
    )

    # Si el jugador entra en el futuro y corrige su edad manualmente
    # (o nos da la fecha_nacimiento real),
    # marcamos esto a True para que dejemos de tocar automáticamente su edad.
    edad_estimacion_bloqueada = models.BooleanField(
        default=False,
        help_text="Si True, NO autoincrementar edad_estimacion en enero.",
    )
    # ==================================================

    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.nombre:
            # Generar slug desde nombre (ej: "Daniel Domene Garcia" -> "daniel-domene-garcia")
            base = self.nombre.strip()
            self.slug = slugify(base)[:195]
            # Si el slug ya existe, añadir el ID
            if Jugador.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{self.slug}-{self.id}" if self.id else slugify(base)[:190]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.apodo or self.nombre


class JugadorEnClubTemporada(models.Model):
    """
    Estadísticas del jugador en un club concreto en una temporada concreta.
    Scrap + consolidado de actas.
    """
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="participaciones_temporada",
    )

    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="plantillas_temporada",
    )

    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="jugadores_temporada",
    )

    dorsal = models.CharField(max_length=10, blank=True)

    partidos_jugados = models.IntegerField(default=0)
    goles = models.IntegerField(default=0)
    tarjetas_amarillas = models.IntegerField(default=0)
    tarjetas_rojas = models.IntegerField(default=0)

    convocados = models.IntegerField(default=0)
    titular = models.IntegerField(default=0)
    suplente = models.IntegerField(default=0)

    class Meta:
        unique_together = ("jugador", "club", "temporada")

    def __str__(self):
        return f"{self.jugador} / {self.club} / {self.temporada}"


class HistorialJugadorScraped(models.Model):
    """
    Línea histórica tal y como la da la federación en la ficha del jugador.
    Esto nos permite mostrar trayectoria en la web aunque no tengamos
    aún enlazadas esas temporadas/equipos a nuestras FK reales.
    """
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="historial_scraped",
    )

    temporada_texto = models.CharField(max_length=50, blank=True)
    competicion_texto = models.CharField(max_length=200, blank=True)
    equipo_texto = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Historial bruto de jugador (scraping)"
        verbose_name_plural = "Historial bruto de jugador (scraping)"

    def __str__(self):
        return f"{self.jugador} / {self.temporada_texto} / {self.equipo_texto}"


    temporada_texto = models.CharField(max_length=50, blank=True)
    competicion_texto = models.CharField(max_length=200, blank=True)
    equipo_texto = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Historial bruto de jugador (scraping)"
        verbose_name_plural = "Historial bruto de jugador (scraping)"

    def __str__(self):
        return f"{self.jugador} / {self.temporada_texto} / {self.equipo_texto}"


    temporada_texto = models.CharField(max_length=50, blank=True)
    competicion_texto = models.CharField(max_length=200, blank=True)
    equipo_texto = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Historial bruto de jugador (scraping)"
        verbose_name_plural = "Historial bruto de jugador (scraping)"

    def __str__(self):
        return f"{self.jugador} / {self.temporada_texto} / {self.equipo_texto}"


    temporada_texto = models.CharField(max_length=50, blank=True)
    competicion_texto = models.CharField(max_length=200, blank=True)
    equipo_texto = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Historial bruto de jugador (scraping)"
        verbose_name_plural = "Historial bruto de jugador (scraping)"

    def __str__(self):
        return f"{self.jugador} / {self.temporada_texto} / {self.equipo_texto}"
