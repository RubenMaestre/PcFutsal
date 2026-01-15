# clubes/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from nucleo.models import Grupo, Temporada


# ——————————————————————————————————————————————
# BLOQUE 1. IDENTIDAD DEL CLUB
# ——————————————————————————————————————————————
class Club(models.Model):
    """
    Entidad global del club (independiente de temporada).
    Mantiene los campos usados por tus vistas (escudo_url, nombre_corto, pabellon).
    """
    nombre_oficial   = models.CharField(max_length=160)
    nombre_corto     = models.CharField(max_length=80, blank=True, default="")
    siglas           = models.CharField(max_length=16, blank=True, default="")
    slug             = models.SlugField(max_length=180, unique=True, blank=True, null=True)

    # Identificador oficial para scraping / federación.
    # Este ID permite referenciar un club específico en la web de FFCV
    # y es crucial para el proceso de scraping y normalización de datos.
    # Se permite NULL para evitar problemas de unicidad con "" en MySQL.
    identificador_federacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,         # permite múltiples NULL y evita problemas de unicidad con "" en MySQL
        unique=True,
        help_text="ID del club en la federación (ej. 10176)",
    )

    # Identidad visual
    escudo_url       = models.CharField(max_length=300, blank=True, default="")
    color_primario   = models.CharField(max_length=9, blank=True, default="")   # "#112233"
    color_secundario = models.CharField(max_length=9, blank=True, default="")

    # Sede / pabellón
    pabellon         = models.CharField(max_length=160, blank=True, default="")
    direccion        = models.CharField(max_length=220, blank=True, default="")
    ciudad           = models.CharField(max_length=120, blank=True, default="")
    provincia        = models.CharField(max_length=120, blank=True, default="")
    lat              = models.FloatField(null=True, blank=True)
    lng              = models.FloatField(null=True, blank=True)
    aforo_aprox      = models.PositiveIntegerField(null=True, blank=True)

    # Contacto y redes
    web              = models.URLField(max_length=300, blank=True, default="")
    email_contacto   = models.EmailField(blank=True, default="")
    telefono         = models.CharField(max_length=100, blank=True, default="")
    twitter          = models.URLField(max_length=300, blank=True, default="")
    instagram        = models.URLField(max_length=300, blank=True, default="")
    facebook         = models.URLField(max_length=300, blank=True, default="")
    tiktok           = models.URLField(max_length=300, blank=True, default="")
    youtube          = models.URLField(max_length=300, blank=True, default="")

    # Historia / meta
    fundado_en       = models.PositiveIntegerField(null=True, blank=True)  # año
    historia_resumida= models.TextField(blank=True, default="")
    activo           = models.BooleanField(default=True)

    creado_en        = models.DateTimeField(auto_now_add=True)
    actualizado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["nombre_oficial"]),
            models.Index(fields=["nombre_corto"]),
            models.Index(fields=["siglas"]),
            models.Index(fields=["ciudad", "provincia"]),
            models.Index(fields=["identificador_federacion"]),  # 🔎 búsqueda rápida por ID federación
        ]

    def __str__(self) -> str:
        return self.nombre_corto or self.nombre_oficial

    def save(self, *args, **kwargs):
        # Generación automática de slug para URLs SEO-friendly.
        # Se usa nombre_corto si está disponible, sino nombre_oficial.
        # Si el slug ya existe, se añade un contador numérico para garantizar unicidad.
        if not self.slug:
            base = self.nombre_corto or self.nombre_oficial
            if base:
                slug_base = slugify(base)[:175]
                # Verificar que el slug no esté duplicado y añadir contador si es necesario
                slug_final = slug_base
                contador = 1
                while Club.objects.filter(slug=slug_final).exclude(id=self.id).exists():
                    slug_final = f"{slug_base}-{contador}"[:175]
                    contador += 1
                self.slug = slug_final
        super().save(*args, **kwargs)


class ClubAlias(models.Model):
    """Alias para robustecer scraping/normalización."""
    club  = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=160, unique=True)

    def __str__(self) -> str:
        return f"{self.alias} → {self.club}"


# ——————————————————————————————————————————————
# BLOQUE 2. DIRECTIVA, STAFF Y GESTIÓN
# ——————————————————————————————————————————————
class ClubBoardMember(models.Model):
    """Miembros de directiva (presidente, vicepresidente, etc.)."""
    club     = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="directiva")
    nombre   = models.CharField(max_length=140)
    cargo    = models.CharField(max_length=120)  # "Presidente", "Director deportivo", etc.
    email    = models.EmailField(blank=True, default="")
    telefono = models.CharField(max_length=100, blank=True, default="")
    visible_publico = models.BooleanField(default=True)
    orden    = models.PositiveIntegerField(default=0)

    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "cargo", "nombre"]

    def __str__(self) -> str:
        return f"{self.cargo} - {self.nombre} ({self.club})"


class ClubStaffMember(models.Model):
    """Cuerpo técnico por temporada (entrenador, ayudante, fisio…)."""
    club       = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="staff")
    temporada  = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name="staff_clubes")
    nombre     = models.CharField(max_length=140)
    rol        = models.CharField(max_length=120)  # "Entrenador", "Segundo", "Fisio"…
    email      = models.EmailField(blank=True, default="")
    telefono   = models.CharField(max_length=100, blank=True, default="")
    visible_publico = models.BooleanField(default=True)
    orden      = models.PositiveIntegerField(default=0)

    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("club", "temporada", "nombre", "rol"),)
        ordering = ["temporada__nombre", "orden", "rol", "nombre"]


class ClubManager(models.Model):
    """
    Relación opcional usuario↔club para dar acceso a edición (panel futuro).
    """
    club      = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="managers")
    usuario   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puede_editar_identidad   = models.BooleanField(default=True)
    puede_editar_staff       = models.BooleanField(default=True)
    puede_editar_multimedia  = models.BooleanField(default=True)
    puede_editar_logistica   = models.BooleanField(default=True)

    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("club", "usuario"),)


# ——————————————————————————————————————————————
# BLOQUE 3. PARTICIPACIÓN EN GRUPO / TEMPORADA
# ——————————————————————————————————————————————
class ClubEnGrupo(models.Model):
    """
    Mantiene campos usados por tus endpoints + ampliaciones para métricas y gráficas.
    """
    club  = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="participaciones")
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="clubes")

    # CLASIFICACIÓN ACTUAL
    posicion_actual   = models.PositiveIntegerField(null=True, blank=True)
    puntos            = models.IntegerField(default=0)
    partidos_jugados  = models.IntegerField(default=0)
    victorias         = models.IntegerField(default=0)
    empates           = models.IntegerField(default=0)
    derrotas          = models.IntegerField(default=0)

    goles_favor       = models.IntegerField(default=0)
    goles_contra      = models.IntegerField(default=0)
    diferencia_goles  = models.IntegerField(default=0)

    # Racha (string tipo "VVEDV")
    racha             = models.CharField(max_length=10, blank=True, default="")

    # BREAKDOWN casa/fuera
    puntos_local              = models.IntegerField(default=0)
    puntos_visitante          = models.IntegerField(default=0)
    goles_favor_local         = models.IntegerField(default=0)
    goles_favor_visitante     = models.IntegerField(default=0)
    goles_contra_local        = models.IntegerField(default=0)
    goles_contra_visitante    = models.IntegerField(default=0)

    # CACHES útiles
    ult_5            = models.CharField(max_length=5, blank=True, default="")
    ult_10_puntos    = models.IntegerField(default=0)
    clean_sheets     = models.IntegerField(default=0)   # porterías a 0
    goles_pp         = models.IntegerField(default=0)   # en propia

    # CONTADORES “menciones”
    veces_equipo_de_la_jornada  = models.PositiveIntegerField(default=0)
    veces_partido_estrella      = models.PositiveIntegerField(default=0)
    veces_mvp_jornada           = models.PositiveIntegerField(default=0)

    # Trazabilidad
    creado_en        = models.DateTimeField(auto_now_add=True)
    actualizado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("club", "grupo"),)
        indexes = [
            models.Index(fields=["grupo", "posicion_actual"]),
            models.Index(fields=["grupo", "puntos"]),
            models.Index(fields=["grupo", "diferencia_goles"]),
            models.Index(fields=["grupo", "racha"]),
        ]

    def __str__(self) -> str:
        return f"{self.club} @ {self.grupo} (pos: {self.posicion_actual})"

    def recomputa_derivados(self):
        self.diferencia_goles = (self.goles_favor or 0) - (self.goles_contra or 0)


# ——————————————————————————————————————————————
# BLOQUE 4. HISTÓRICO / PROGRESO POR JORNADA
# ——————————————————————————————————————————————
class ClubSeasonProgress(models.Model):
    """Snapshot jornada a jornada para gráficas de evolución."""
    club      = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="progresos")
    grupo     = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="progresos_club")
    jornada   = models.PositiveIntegerField()
    puntos_acum = models.IntegerField(default=0)
    gf_acum     = models.IntegerField(default=0)
    gc_acum     = models.IntegerField(default=0)
    pos_clasif  = models.PositiveIntegerField(null=True, blank=True)

    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("club", "grupo", "jornada"),)
        ordering = ["grupo", "jornada"]


class ClubSeasonHistory(models.Model):
    """Mini resumen por temporada: cómo acabó el club."""
    club       = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="historial")
    temporada  = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name="historial_clubes")
    competicion= models.CharField(max_length=140)
    grupo_text = models.CharField(max_length=140, blank=True, default="")
    pos_final  = models.PositiveIntegerField(null=True, blank=True)
    pj         = models.PositiveIntegerField(default=0)
    v          = models.PositiveIntegerField(default=0)
    e          = models.PositiveIntegerField(default=0)
    d          = models.PositiveIntegerField(default=0)
    gf         = models.PositiveIntegerField(default=0)
    gc         = models.PositiveIntegerField(default=0)
    puntos     = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("club", "temporada", "competicion", "grupo_text"),)
        ordering = ["-temporada__nombre"]


# ——————————————————————————————————————————————
# BLOQUE 5. PREMIOS / MENCIONES
# ——————————————————————————————————————————————
class ClubAward(models.Model):
    """
    Registro de 'menciones' por jornada (para listados y conteo):
      - equipo_de_la_jornada
      - partido_estrella
      - mvp_jornada (si aplica club via jugador)
    """
    TIPO = (
        ("equipo_jornada", "Equipo de la jornada"),
        ("partido_estrella", "Partido estrella"),
        ("mvp_jornada", "MVP de la jornada (club)"),
    )
    club     = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="awards")
    grupo    = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="awards_club")
    jornada  = models.PositiveIntegerField()
    tipo     = models.CharField(max_length=32, choices=TIPO)
    notas    = models.CharField(max_length=240, blank=True, default="")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("club", "grupo", "jornada", "tipo"),)
        indexes = [models.Index(fields=["grupo", "tipo", "jornada"])]


# ——————————————————————————————————————————————
# BLOQUE 6. LOGÍSTICA / DESPLAZAMIENTOS
# ——————————————————————————————————————————————
class ClubTrip(models.Model):
    """Distancia/tiempo estimado club→rival (por temporada/grupo)."""
    club_origen   = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="viajes_saliendo")
    club_destino  = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="viajes_recibiendo")
    temporada     = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    grupo         = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    distancia_km  = models.FloatField(default=0.0)
    duracion_min  = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("club_origen", "club_destino", "temporada", "grupo"),)
        indexes = [
            models.Index(fields=["grupo", "temporada"]),
            models.Index(fields=["club_origen", "grupo"]),
        ]


class ClubTravelStat(models.Model):
    """Resumen de kilometraje por club/temporada (cache de vista curiosa)."""
    club          = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="travel_stats")
    temporada     = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name="travel_stats")
    grupo         = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="travel_stats")
    total_km      = models.FloatField(default=0.0)
    avg_km        = models.FloatField(default=0.0)
    max_km        = models.FloatField(default=0.0)
    min_km        = models.FloatField(default=0.0)
    max_km_rival  = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    min_km_rival  = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")

    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("club", "temporada", "grupo"),)


# ——————————————————————————————————————————————
# BLOQUE 7. MULTIMEDIA / NOTAS
# ——————————————————————————————————————————————
class ClubMedia(models.Model):
    """Fotos variadas para la ficha: pabellón, equipo, escudos HD, etc."""
    TIPO = (
        ("pabellon", "Pabellón"),
        ("equipo", "Equipo"),
        ("escudo", "Escudo"),
        ("otro", "Otro"),
    )
    club    = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="media")
    tipo    = models.CharField(max_length=24, choices=TIPO, default="otro")
    titulo  = models.CharField(max_length=140, blank=True, default="")
    url     = models.CharField(max_length=400)
    visible_publico = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["club", "tipo"])]


class ClubNota(models.Model):
    """Notas internas por club y grupo (scouting, incidencias, enlaces)."""
    club  = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="notas")
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="notas_club")
    titulo = models.CharField(max_length=140)
    texto  = models.TextField(blank=True, default="")
    enlace = models.URLField(max_length=400, blank=True, default="")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["club", "grupo"])]

    def __str__(self):
        return f"{self.titulo} ({self.club})"


# ——————————————————————————————————————————————
# BLOQUE EXTRA. VALORACIÓN CLUB (compatibilidad con vistas antiguas)
# ——————————————————————————————————————————————
class ValoracionClub(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="valoraciones_club",
    )
    temporada = models.ForeignKey(
        Temporada,
        on_delete=models.CASCADE,
        related_name="valoraciones_club",
    )
    historia_tradicion = models.IntegerField(default=0)
    cantera_talento = models.IntegerField(default=0)
    intensidad_competitiva = models.IntegerField(default=0)
    solidez_tactica = models.IntegerField(default=0)
    proyecto_seriedad = models.IntegerField(default=0)
    reputacion_respecto = models.IntegerField(default=0)
    media_global = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("club", "temporada")

    def __str__(self):
        return f"{self.club} {self.temporada} -> {self.media_global}"
