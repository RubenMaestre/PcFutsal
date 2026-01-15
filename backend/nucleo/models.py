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

    # IMPORTANTO: quitamos unique=True por ahora, y permitimos null/blank
    slug = models.SlugField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Slug público tipo 'tercera-division' usado en la URL",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.nombre.lower()
            # ejemplo: "Tercera División Nacional Futsal" -> "tercera-division-nacional-futsal"
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
        if not self.slug:
            base = self.nombre.lower()
            self.slug = slugify(base)  # "Grupo XV" -> "grupo-xv"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.competicion.nombre} · {self.nombre} · {self.temporada.nombre}"

    class Meta:
        # mantenemos el unique_together porque tiene sentido lógico
        unique_together = ("competicion", "temporada", "slug")
