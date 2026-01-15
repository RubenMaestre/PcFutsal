from django.db import models
from django.utils.text import slugify


class Temporada(models.Model):
    nombre = models.CharField(max_length=20)  # "2024/2025"
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Competicion(models.Model):
    nombre = models.CharField(max_length=100)
    ambito = models.CharField(max_length=100, blank=True)
    categoria = models.CharField(max_length=100, blank=True)

    # Slug para URLs SEO-friendly. No es único porque puede haber competiciones
    # con el mismo nombre en diferentes contextos (aunque es raro).
    # Permitimos null/blank para competiciones que aún no tienen slug asignado.
    slug = models.SlugField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Slug público tipo 'tercera-division' usado en la URL",
    )

    def save(self, *args, **kwargs):
        # Generación automática de slug desde el nombre si no existe.
        # Ejemplo: "Tercera División Nacional Futsal" -> "tercera-division-nacional-futsal"
        if not self.slug:
            base = self.nombre.lower()
            self.slug = slugify(base)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Grupo(models.Model):
    nombre = models.CharField(max_length=100)  # "Grupo XV"
    provincia = models.CharField(max_length=100, blank=True)

    competicion = models.ForeignKey(
        Competicion,
        on_delete=models.CASCADE,
        related_name="grupos",
    )

    temporada = models.ForeignKey(
        Temporada,
        on_delete=models.CASCADE,
        related_name="grupos",
    )

    slug = models.SlugField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Slug público tipo 'grupo-xv' usado en la URL dentro de cada competición",
    )

    def save(self, *args, **kwargs):
        # Generación automática de slug desde el nombre si no existe.
        # Ejemplo: "Grupo XV" -> "grupo-xv"
        if not self.slug:
            base = self.nombre.lower()
            self.slug = slugify(base)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.competicion.nombre} · {self.nombre} · {self.temporada.nombre}"

    class Meta:
        # El unique_together asegura que no haya grupos duplicados con el mismo slug
        # dentro de la misma competición y temporada. Esto es crucial para las URLs.
        unique_together = ("competicion", "temporada", "slug")
