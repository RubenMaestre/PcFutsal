# jugadores/management/commands/generate_jugador_slugs.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jugadores.models import Jugador


class Command(BaseCommand):
    help = 'Genera slugs para todos los jugadores que no tienen slug'

    def handle(self, *args, **options):
        jugadores_sin_slug = Jugador.objects.filter(slug__isnull=True) | Jugador.objects.filter(slug="")
        total = jugadores_sin_slug.count()
        
        self.stdout.write(f'Generando slugs para {total} jugadores...')
        
        actualizados = 0
        for jugador in jugadores_sin_slug:
            if jugador.nombre:
                base = jugador.nombre.strip()
                slug_candidato = slugify(base)[:195]
                
                # Verificar si el slug ya existe
                slug_final = slug_candidato
                contador = 1
                while Jugador.objects.filter(slug=slug_final).exclude(id=jugador.id).exists():
                    slug_final = f"{slug_candidato}-{contador}"[:195]
                    contador += 1
                
                jugador.slug = slug_final
                jugador.save(update_fields=['slug'])
                actualizados += 1
                
                if actualizados % 100 == 0:
                    self.stdout.write(f'  Procesados {actualizados}/{total}...')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generados {actualizados} slugs correctamente.'))


from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jugadores.models import Jugador


class Command(BaseCommand):
    help = 'Genera slugs para todos los jugadores que no tienen slug'

    def handle(self, *args, **options):
        jugadores_sin_slug = Jugador.objects.filter(slug__isnull=True) | Jugador.objects.filter(slug="")
        total = jugadores_sin_slug.count()
        
        self.stdout.write(f'Generando slugs para {total} jugadores...')
        
        actualizados = 0
        for jugador in jugadores_sin_slug:
            if jugador.nombre:
                base = jugador.nombre.strip()
                slug_candidato = slugify(base)[:195]
                
                # Verificar si el slug ya existe
                slug_final = slug_candidato
                contador = 1
                while Jugador.objects.filter(slug=slug_final).exclude(id=jugador.id).exists():
                    slug_final = f"{slug_candidato}-{contador}"[:195]
                    contador += 1
                
                jugador.slug = slug_final
                jugador.save(update_fields=['slug'])
                actualizados += 1
                
                if actualizados % 100 == 0:
                    self.stdout.write(f'  Procesados {actualizados}/{total}...')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generados {actualizados} slugs correctamente.'))


from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jugadores.models import Jugador


class Command(BaseCommand):
    help = 'Genera slugs para todos los jugadores que no tienen slug'

    def handle(self, *args, **options):
        jugadores_sin_slug = Jugador.objects.filter(slug__isnull=True) | Jugador.objects.filter(slug="")
        total = jugadores_sin_slug.count()
        
        self.stdout.write(f'Generando slugs para {total} jugadores...')
        
        actualizados = 0
        for jugador in jugadores_sin_slug:
            if jugador.nombre:
                base = jugador.nombre.strip()
                slug_candidato = slugify(base)[:195]
                
                # Verificar si el slug ya existe
                slug_final = slug_candidato
                contador = 1
                while Jugador.objects.filter(slug=slug_final).exclude(id=jugador.id).exists():
                    slug_final = f"{slug_candidato}-{contador}"[:195]
                    contador += 1
                
                jugador.slug = slug_final
                jugador.save(update_fields=['slug'])
                actualizados += 1
                
                if actualizados % 100 == 0:
                    self.stdout.write(f'  Procesados {actualizados}/{total}...')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generados {actualizados} slugs correctamente.'))


from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jugadores.models import Jugador


class Command(BaseCommand):
    help = 'Genera slugs para todos los jugadores que no tienen slug'

    def handle(self, *args, **options):
        jugadores_sin_slug = Jugador.objects.filter(slug__isnull=True) | Jugador.objects.filter(slug="")
        total = jugadores_sin_slug.count()
        
        self.stdout.write(f'Generando slugs para {total} jugadores...')
        
        actualizados = 0
        for jugador in jugadores_sin_slug:
            if jugador.nombre:
                base = jugador.nombre.strip()
                slug_candidato = slugify(base)[:195]
                
                # Verificar si el slug ya existe
                slug_final = slug_candidato
                contador = 1
                while Jugador.objects.filter(slug=slug_final).exclude(id=jugador.id).exists():
                    slug_final = f"{slug_candidato}-{contador}"[:195]
                    contador += 1
                
                jugador.slug = slug_final
                jugador.save(update_fields=['slug'])
                actualizados += 1
                
                if actualizados % 100 == 0:
                    self.stdout.write(f'  Procesados {actualizados}/{total}...')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generados {actualizados} slugs correctamente.'))














