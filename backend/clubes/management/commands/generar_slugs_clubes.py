# clubes/management/commands/generar_slugs_clubes.py
"""
Comando de gestión para generar slugs para todos los clubes que no los tengan.

Uso:
    python manage.py generar_slugs_clubes
    python manage.py generar_slugs_clubes --force  # Regenera todos los slugs
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from clubes.models import Club


class Command(BaseCommand):
    help = "Genera slugs para todos los clubes que no los tengan"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenera todos los slugs, incluso si ya existen",
        )

    def handle(self, *args, **options):
        force = options["force"]
        
        clubes = Club.objects.all()
        total = clubes.count()
        generados = 0
        actualizados = 0
        
        self.stdout.write(f"Procesando {total} clubes...")
        
        for club in clubes:
            if not club.slug or force:
                base = club.nombre_corto or club.nombre_oficial
                if base:
                    nuevo_slug = slugify(base)[:175]
                    
                    # Verificar que el slug no esté duplicado
                    slug_base = nuevo_slug
                    contador = 1
                    while Club.objects.filter(slug=nuevo_slug).exclude(id=club.id).exists():
                        nuevo_slug = f"{slug_base}-{contador}"[:175]
                        contador += 1
                    
                    if club.slug != nuevo_slug:
                        club.slug = nuevo_slug
                        club.save(update_fields=["slug"])
                        if club.slug:
                            actualizados += 1
                        else:
                            generados += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ {club.nombre_corto or club.nombre_oficial} → {nuevo_slug}"
                            )
                        )
                    else:
                        generados += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ Club ID {club.id} no tiene nombre_corto ni nombre_oficial"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Proceso completado: {generados + actualizados} slugs generados/actualizados"
            )
        )









