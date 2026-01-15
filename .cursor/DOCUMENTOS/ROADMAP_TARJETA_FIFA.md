# 🎴 ROADMAP — TARJETAS FIFA DE JUGADORES

## 📋 RESUMEN EJECUTIVO

Crear sistema completo de tarjetas FIFA para jugadores de fútbol sala que muestre:
- Media global tipo FIFA (1-100) calculada como: (media_ataque + media_defensa) / 2
- Media de ataque (1-100) calculada como promedio de los 6 atributos ofensivos
- Media de defensa (1-100) calculada como promedio de los 6 atributos defensivos
- 12 atributos detallados (6 ofensivos + 6 defensivos) con puntuación 1-100 cada uno
- **Valor inicial**: Todos los jugadores empiezan con 50 puntos en todos los atributos
- Foto del jugador y escudo del club
- Posición del jugador
- Diseño reutilizable en múltiples contextos

---

## 🔍 ATRIBUTOS FIFA

### 🟥 6 ATRIBUTOS DE ATAQUE (OFENSIVOS)

1. **Finalización**
   - Capacidad para convertir en gol: definición en área, remate rápido, precisión en acciones decisivas.

2. **Regate / 1x1 Ofensivo**
   - Habilidad para desequilibrar en espacios reducidos, cambios de ritmo y acciones individuales clave.

3. **Pase Creativo**
   - Calidad de pase corto, paredes, asistencias y capacidad de romper líneas con balón.

4. **Visión Ofensiva**
   - Lectura de superioridades, toma de decisiones con presión y generación de ventajas.

5. **Velocidad / Aceleración**
   - Primer paso explosivo, conducción rápida y desborde lateral.

6. **Potencia de Disparo**
   - Fuerza y precisión en tiros exteriores, golpeos en movimiento y doble penalti.

### 🟦 6 ATRIBUTOS DE DEFENSA (DEFENSIVOS)

1. **Colocación Defensiva**
   - Posicionamiento sin balón, lectura táctica, orientación de rival y control de espacios.

2. **Robo / Duelos Defensivos**
   - Capacidad de arrebatar el balón, agresividad controlada y éxito en 1x1 defensivo.

3. **Intensidad / Presión**
   - Constancia presionando, ida y vuelta, esfuerzo físico y disciplina en la presión alta.

4. **Intercepciones**
   - Lectura de líneas de pase, anticipación y capacidad para cortar juego rival.

5. **Repliegue / Transición Defensiva**
   - Velocidad para volver, disciplina táctica y recuperación tras pérdida.

6. **Balón Parado Defensivo**
   - Marcaje, bloqueos, defensas de estrategia, gestión de saques de esquina y faltas.

### 📊 Cálculo de Medias

- **Media de Ataque**: Promedio de los 6 atributos ofensivos (1-100)
- **Media de Defensa**: Promedio de los 6 atributos defensivos (1-100)
- **Media Global**: (Media de Ataque + Media de Defensa) / 2

### ⚙️ Valores Iniciales

- **Valor inicial**: Todos los jugadores empiezan con **50 puntos** en todos los atributos
- **Rango válido**: Los atributos pueden tener valores entre **1 y 100**
- Con valores iniciales de 50, las medias iniciales serán:
  - Media de Ataque: 50
  - Media de Defensa: 50
  - Media Global: 50

---

## 🔍 DATOS DISPONIBLES

✅ **Backend ya tiene**:
- Modelo `Jugador` con nombre, apodo, foto_url, posicion_principal
- Endpoint `/api/jugadores/full/` ✅

⚠️ **Backend NUEVO - A CREAR**:
- Nueva app Django para gestionar las valoraciones FIFA
- Modelo `ValoracionFIFAJugador` con 12 atributos + medias calculadas
- Endpoint `/api/fifa/jugador/{jugador_id}/` o similar

---

## 🎨 DISEÑO

**Inspiración**: Cartas FIFA Ultimate Team
**Colores**: Rojo #A51B3D, Negro #000, Gris #121212, Blanco #FFF
**Tipografías**: Cabin + Orbitron

**Elementos**:
1. Header con escudo del club y posición
2. Foto del jugador (con fallback)
3. Media global destacada (color: 90-100 oro, 80-89 plata, 70-79 bronce, <70 gris)
4. Media de ataque y media de defensa (opcional, según variante)
5. 12 atributos organizados en dos secciones:
   - Sección Ataque (🟥 6 atributos)
   - Sección Defensa (🟦 6 atributos)
6. Cada atributo con barra de progreso (1-100)
7. Nombre, apodo, club, edad

**Variantes**:
- `full`: 400x600px - Perfil de jugador
- `compact`: 250x350px - Rankings, listas
- `mini`: 150x200px - Widgets, comparaciones

---

## 🎯 FASE 1 — BACKEND

### 1.1 Crear nueva app Django

**Pasos**:
1. Crear app: `python manage.py startapp fifa`
2. Mover carpeta `fifa/` al directorio `backend/fifa/`
3. Registrar en `backend/settings.py`:
   ```python
   INSTALLED_APPS = [
       # ... otras apps ...
       'fifa',
   ]
   ```

**Estructura de archivos**:
```
backend/fifa/
├── __init__.py
├── models.py          # ValoracionFIFAJugador
├── admin.py           # Registro en admin
├── views.py           # API views
├── serializers.py     # DRF serializers
├── urls.py            # URLs de la app
└── migrations/        # Migraciones Django
```

**Integración con URLs principales**:
En `backend/administracion/urls.py`:
```python
path("api/fifa/", include("fifa.urls")),
```

### 1.2 Modelo de Datos

**Modelo `ValoracionFIFAJugador`**:
```python
from django.core.validators import MinValueValidator, MaxValueValidator

class ValoracionFIFAJugador(models.Model):
    jugador = models.OneToOneField(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="valoracion_fifa"
    )
    
    # Atributos de Ataque (1-100, default: 50)
    finalizacion = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    regate = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    pase_creativo = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    vision_ofensiva = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    velocidad = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    potencia_disparo = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    # Atributos de Defensa (1-100, default: 50)
    colocacion_defensiva = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    robo = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    intensidad = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    intercepciones = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    repliegue = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    balon_parado_defensivo = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    # Medias calculadas (1-100, default: 50)
    media_ataque = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )  # Promedio de 6 atributos ofensivos
    media_defensa = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )  # Promedio de 6 atributos defensivos
    media_global = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )   # (media_ataque + media_defensa) / 2
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calcular medias antes de guardar
        self.media_ataque = (
            self.finalizacion + self.regate + self.pase_creativo +
            self.vision_ofensiva + self.velocidad + self.potencia_disparo
        ) / 6.0
        
        self.media_defensa = (
            self.colocacion_defensiva + self.robo + self.intensidad +
            self.intercepciones + self.repliegue + self.balon_parado_defensivo
        ) / 6.0
        
        self.media_global = (self.media_ataque + self.media_defensa) / 2.0
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Valoración FIFA Jugador"
        verbose_name_plural = "Valoraciones FIFA Jugadores"
```

### 1.3 Endpoints API

- [ ] Crear endpoint `/api/fifa/jugador/{jugador_id}/` para obtener valoración FIFA
- [ ] Crear endpoint `/api/fifa/jugador/{jugador_id}/card/` (opcional, para datos optimizados)
- [ ] Integrar con endpoint existente `/api/jugadores/full/?include=fifa` (opcional)
- [ ] Endpoint debe validar que los valores estén en rango 1-100

### 1.4 Admin Django

- [ ] Registrar `ValoracionFIFAJugador` en admin
- [ ] Crear interface de edición cómoda para los 12 atributos
- [ ] Validar que las medias se calculan automáticamente

### 1.5 Migraciones y Datos Iniciales

- [ ] Crear migración: `python manage.py makemigrations fifa`
- [ ] Aplicar migración: `python manage.py migrate fifa`

### 1.6 Management Command: Inicializar Valoraciones

**Crear comando**: `backend/fifa/management/commands/init_valoraciones_fifa.py`

```python
from django.core.management.base import BaseCommand
from jugadores.models import Jugador
from fifa.models import ValoracionFIFAJugador

class Command(BaseCommand):
    help = 'Inicializa valoraciones FIFA para todos los jugadores con valores por defecto (50)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Sobrescribir valoraciones existentes',
        )

    def handle(self, *args, **options):
        jugadores = Jugador.objects.all()
        creados = 0
        actualizados = 0
        omitidos = 0

        for jugador in jugadores:
            valoracion, created = ValoracionFIFAJugador.objects.get_or_create(
                jugador=jugador,
                defaults={
                    # Todos los atributos inicializados a 50
                    'finalizacion': 50,
                    'regate': 50,
                    'pase_creativo': 50,
                    'vision_ofensiva': 50,
                    'velocidad': 50,
                    'potencia_disparo': 50,
                    'colocacion_defensiva': 50,
                    'robo': 50,
                    'intensidad': 50,
                    'intercepciones': 50,
                    'repliegue': 50,
                    'balon_parado_defensivo': 50,
                }
            )

            if created:
                creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada valoración para {jugador.nombre}')
                )
            elif options['force']:
                # Si ya existe y --force, actualizar a 50
                for field in ['finalizacion', 'regate', 'pase_creativo', 
                             'vision_ofensiva', 'velocidad', 'potencia_disparo',
                             'colocacion_defensiva', 'robo', 'intensidad',
                             'intercepciones', 'repliegue', 'balon_parado_defensivo']:
                    setattr(valoracion, field, 50)
                valoracion.save()
                actualizados += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Actualizada valoración para {jugador.nombre}')
                )
            else:
                omitidos += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Completado: {creados} creados, {actualizados} actualizados, {omitidos} omitidos'
            )
        )
```

**Ejecución**:
```bash
# Crear valoraciones para todos los jugadores (solo si no existen)
python manage.py init_valoraciones_fifa

# Sobrescribir todas las valoraciones existentes
python manage.py init_valoraciones_fifa --force
```

- [ ] Crear archivo `backend/fifa/management/__init__.py` (si no existe)
- [ ] Crear archivo `backend/fifa/management/commands/__init__.py` (si no existe)
- [ ] Crear comando `init_valoraciones_fifa.py`
- [ ] Ejecutar comando para inicializar todos los jugadores

---

## 🎯 FASE 2 — FRONTEND: Componentes

### 2.1 Componente principal
**Archivo**: `/frontend/components/JugadorFIFACard.tsx`

**Props**:
```typescript
interface JugadorFIFACardProps {
  jugador: { id, nombre, apodo, foto_url, posicion_principal, edad };
  club?: { id, nombre, escudo_url, slug } | null;
  valoracion?: {
    // Medias
    media_global: number;
    media_ataque: number;
    media_defensa: number;
    
    // Atributos de Ataque (1-100)
    finalizacion: number;
    regate: number;
    pase_creativo: number;
    vision_ofensiva: number;
    velocidad: number;
    potencia_disparo: number;
    
    // Atributos de Defensa (1-100)
    colocacion_defensiva: number;
    robo: number;
    intensidad: number;
    intercepciones: number;
    repliegue: number;
    balon_parado_defensivo: number;
  } | null;
  variant?: 'full' | 'compact' | 'mini';
  lang?: string;
  dict?: any;
}
```

### 2.2 Componentes auxiliares
- `AtributoBar.tsx` - Barra de progreso (1-100)
- `MediaGlobalBadge.tsx` - Badge con media global y color (oro/plata/bronce/gris)
- `MediaAtaqueBadge.tsx` - Badge con media de ataque (opcional)
- `MediaDefensaBadge.tsx` - Badge con media de defensa (opcional)
- `PosicionBadge.tsx` - Badge de posición traducida
- `AtributosAtaqueSection.tsx` - Sección con los 6 atributos ofensivos
- `AtributosDefensaSection.tsx` - Sección con los 6 atributos defensivos

### 2.3 Estilos
- Tailwind CSS
- Framer Motion (animaciones)
- Responsive

---

## 🎯 FASE 3 — Integración

- [ ] Perfil de jugador (`JugadorDetailClient.tsx`) - variant `full`
- [ ] Rankings (MVP, goleadores) - variant `compact`
- [ ] Home (`GlobalMVPCard.tsx`) - variant `full` o `compact`
- [ ] Plantillas de clubes - variant `mini`
- [ ] (Opcional) Comparaciones - variant `compact`

---

## 🎯 FASE 4 — Traducciones

Añadir en `/frontend/i18n/es.json` (y todos los idiomas):
```json
{
  "fifa_card": {
    "media_global": "Media Global",
    "media_ataque": "Media Ataque",
    "media_defensa": "Media Defensa",
    "atributos": {
      "ataque": {
        "title": "Ataque",
        "finalizacion": "Finalización",
        "regate": "Regate / 1x1 Ofensivo",
        "pase_creativo": "Pase Creativo",
        "vision_ofensiva": "Visión Ofensiva",
        "velocidad": "Velocidad / Aceleración",
        "potencia_disparo": "Potencia de Disparo"
      },
      "defensa": {
        "title": "Defensa",
        "colocacion_defensiva": "Colocación Defensiva",
        "robo": "Robo / Duelos Defensivos",
        "intensidad": "Intensidad / Presión",
        "intercepciones": "Intercepciones",
        "repliegue": "Repliegue / Transición Defensiva",
        "balon_parado_defensivo": "Balón Parado Defensivo"
      }
    },
    "posiciones": {
      "portero": "Portero",
      "cierre": "Cierre",
      "ala": "Ala",
      "pivot": "Pivot",
      "universal": "Universal"
    }
  }
}
```

---

## 📝 CHECKLIST

### Backend
- [ ] Crear nueva app `fifa` en Django
- [ ] Registrar app en `INSTALLED_APPS`
- [ ] Crear modelo `ValoracionFIFAJugador` con 12 atributos
- [ ] Configurar defaults a 50 para todos los atributos
- [ ] Añadir validadores MinValueValidator(1) y MaxValueValidator(100)
- [ ] Implementar cálculo automático de medias en `save()`
- [ ] Crear migraciones y aplicarlas
- [ ] Crear management command `init_valoraciones_fifa` para inicializar todos los jugadores
- [ ] Ejecutar comando para crear valoraciones iniciales (50 en todos los atributos)
- [ ] Registrar modelo en admin Django
- [ ] Crear endpoints API
- [ ] Verificar fotos/escudos (del modelo Jugador existente)
- [ ] (Opcional) Endpoint optimizado `/api/fifa/jugador/{id}/card/`

### Frontend
- [ ] `JugadorFIFACard.tsx` (componente principal)
- [ ] `AtributoBar.tsx` (barra de progreso)
- [ ] `MediaGlobalBadge.tsx` (badge media global)
- [ ] `MediaAtaqueBadge.tsx` (badge media ataque, opcional)
- [ ] `MediaDefensaBadge.tsx` (badge media defensa, opcional)
- [ ] `AtributosAtaqueSection.tsx` (sección atributos ofensivos)
- [ ] `AtributosDefensaSection.tsx` (sección atributos defensivos)
- [ ] `PosicionBadge.tsx` (badge posición)
- [ ] Hook `useValoracionFIFA.ts` para obtener datos
- [ ] Integrar en perfil de jugador
- [ ] Integrar en rankings
- [ ] Integrar en home
- [ ] Integrar en plantillas

### Traducciones
- [ ] Claves en todos los idiomas
- [ ] Traducir posiciones

### Testing
- [ ] Datos completos
- [ ] Sin foto
- [ ] Sin valoración
- [ ] Responsive
- [ ] Todos los idiomas

---

## 🚀 ORDEN DE EJECUCIÓN

1. **FASE 1 - BACKEND COMPLETO**:
   - Crear nueva app `fifa` en Django
   - Crear modelo `ValoracionFIFAJugador` con 12 atributos
   - Implementar cálculo automático de medias
   - Crear migraciones y aplicarlas
   - Registrar en admin
   - Crear endpoints API
   - Verificar que todo funciona

2. **FASE 4 - TRADUCCIONES**:
   - Añadir todas las claves de traducción en todos los idiomas

3. **FASE 2 - COMPONENTES BASE**:
   - Crear componentes base (card, badges, barras, secciones)
   - Crear hook `useValoracionFIFA`

4. **FASE 3 - INTEGRACIÓN**:
   - Integrar en perfil de jugador (empezar por aquí)
   - Integrar en rankings
   - Integrar en home
   - Integrar en plantillas

5. **OPTIMIZACIONES**:
   - Mejoras de performance
   - Cacheo de datos
   - Animaciones y transiciones

---

## 📚 REFERENCIAS

- `PROJECT_VISION.md`: Sección "4. Perfil de jugador"
- `ROADMAP_PAGINA_JUGADORES.md`: Sección "2.3.1 Tarjeta FIFA"
- `DOCUMENTACION/APIS.md`: Endpoint `/api/jugadores/full/`

---

**Última actualización**: 2025-11-29
**Estado**: ROADMAP ACTUALIZADO — Pendiente de implementación

**Cambios importantes**:
- Actualizado sistema de atributos: 12 atributos (6 ataque + 6 defensa) en lugar de 9 genéricos
- Sistema de medias: media_ataque, media_defensa, media_global
- Nueva app Django `fifa` necesaria para gestionar valoraciones FIFA
- Modelo `ValoracionFIFAJugador` con cálculo automático de medias
