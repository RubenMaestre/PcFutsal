# ROADMAP: FICHA DE PARTIDOS — PC FUTSAL

## 📋 RESUMEN EJECUTIVO

Implementación completa de la ficha detallada de partidos con línea del tiempo de eventos, alineaciones, valoraciones, estadísticas y toda la información disponible del partido. Incluye también la página de listado de partidos con selección por competición, grupo y jornada.

---

## 🔍 ANÁLISIS DE DATOS DISPONIBLES

### Modelos Django Existentes

#### 1. **Partido** (`partidos.models.Partido`)
- `id`, `grupo`, `jornada_numero`, `fecha_hora`
- `local`, `visitante` (FK a Club)
- `goles_local`, `goles_visitante`
- `jugado` (boolean)
- `identificador_federacion` (ID único de federación)
- `pabellon` (string)
- `arbitros` (TextField - texto libre con nombres)
- `indice_intensidad` (0-100)

#### 2. **EventoPartido** (`partidos.models.EventoPartido`)
- `partido` (FK)
- `minuto` (IntegerField - minuto del evento)
- `tipo_evento`: `"gol"`, `"gol_pp"`, `"amarilla"`, `"doble_amarilla"`, `"roja"`, `"mvp"`
- `jugador` (FK a Jugador, nullable)
- `club` (FK a Club, nullable)
- `nota` (TextField - descripción del evento)

#### 3. **AlineacionPartidoJugador** (`partidos.models.AlineacionPartidoJugador`)
- `partido` (FK)
- `club` (FK)
- `jugador` (FK, nullable)
- `dorsal` (CharField)
- `titular` (BooleanField)
- `etiqueta` (CharField - "Pt", "Ps", "C", etc.)

#### 4. **ArbitrajePartido** (`arbitros.models.ArbitrajePartido`)
- `partido` (FK)
- `arbitro` (FK a Arbitro)
- `rol` (CharField - "Principal", "Auxiliar", "Mesa", "Cronometrador")

#### 5. **StaffEnPartido** (`staff.models.StaffEnPartido`)
- `partido` (FK)
- `club` (FK)
- `staff` (FK a StaffClub, nullable)
- `nombre` (CharField)
- `rol` (CharField - "Entrenador", "Delegado", etc.)

### Datos del Scraping (`parser_partido_detalle.py`)

El parser extrae:
- **Info partido**: fecha, hora, pabellón, árbitros (lista)
- **Marcador**: goles local/visitante
- **Alineaciones**: 
  - Titulares y suplentes por equipo
  - Dorsal, etiqueta (Pt, Ps, C), nombre
- **Técnicos**: nombre y rol por equipo
- **Eventos timeline**: minuto, tipo, jugador, equipo (local/visitante)

### Endpoints Existentes Relacionados con Partidos

#### Endpoints que podemos REUTILIZAR o EXTENDER:

1. **`/api/estadisticas/resultados-jornada/`** (`estadisticas.views.ResultadosJornadaView`)
   - **Qué devuelve**: Lista de partidos de una jornada con marcador, equipos, árbitros, pabellón
   - **Qué incluye**: `id`, `jornada`, `jugado`, `fecha_hora`, `pabellon`, `arbitros`, `local` (id, nombre, escudo, slug, goles), `visitante` (id, nombre, escudo, slug, goles)
   - **Qué NO incluye**: Eventos, alineaciones, staff técnico, detalle completo
   - **Uso**: Podemos reutilizar la lógica de filtrado por grupo/jornada, pero necesitamos crear endpoints específicos en `partidos/`

2. **`/api/valoraciones/partido-estrella/`** (`valoraciones.views.PartidoEstrellaView`)
   - **Qué devuelve**: Partido más interesante de la jornada según algoritmo
   - **Uso**: Solo para destacar partidos, no para listado general

3. **`/api/valoraciones/partidos-top-global/`** (`valoraciones.views.PartidosTopGlobalView`)
   - **Qué devuelve**: Top partidos globales de la jornada
   - **Uso**: Solo para rankings, no para listado general

4. **`/api/valoraciones/jugadores-jornada/`** (`valoraciones.views.JugadoresJornadaView`)
   - **Qué devuelve**: Puntos de valoración de jugadores en una jornada
   - **Uso**: **REUTILIZAR** para obtener puntos de jugadores en el frontend (ver sección de integración)

5. **`/api/valoraciones/equipo-jornada/`** (`valoraciones.views.EquipoJornadaView`)
   - **Qué devuelve**: Puntos de valoración de equipos en una jornada
   - **Uso**: **REUTILIZAR** para obtener puntos de equipos en el frontend (ver sección de integración)

#### Endpoints que NECESITAMOS CREAR en `backend/partidos/`:

1. **`/api/partidos/lista/`** - Listado de partidos con filtros (GLOBAL/COMPETICIONES)
2. **`/api/partidos/detalle/`** - Detalle completo de un partido individual (eventos, alineaciones, staff, etc.)

**NOTA**: Todo se creará en `backend/partidos/` (views.py, urls.py)

---

## 🎯 FUNCIONALIDADES A IMPLEMENTAR

### 1. PÁGINA DE LISTADO DE PARTIDOS (`/partidos`)

#### 1.1. Comportamiento Inicial
- **Por defecto**: Mostrar partidos aleatorios de la última semana disputada
- **Criterio "última semana"**: Partidos jugados en los últimos 7 días (o última jornada con partidos)
- **Cantidad**: Mostrar 6-12 partidos aleatorios

#### 1.2. Selectores
- **Selector de SCOPE**: `GLOBAL` | `COMPETICIONES` (igual que en otras páginas)
- **Si SCOPE = COMPETICIONES**:
  - Selector de Competición
  - Selector de Grupo (dependiente de competición)
  - Selector de Jornada (dependiente de grupo)
  - Lógica de favorito/aleatorio (igual que en clasificación)

#### 1.3. Componentes Necesarios
- `PartidosShell.tsx` - Componente principal (similar a `ClasificacionShell.tsx`)
- `PartidosList.tsx` - Lista de partidos con cards
- `PartidoCard.tsx` - Card individual de partido (ya existe, reutilizar)
- `CompetitionFilter.tsx` - Reutilizar componente existente

#### 1.4. Endpoint Backend
```
GET /api/partidos/lista/
  ?scope=GLOBAL|COMPETICIONES
  &competicion_id=XX (si scope=COMPETICIONES)
  &grupo_id=YY (si scope=COMPETICIONES)
  &jornada=ZZ (opcional)
  &random=true (si queremos aleatorios de última semana)
  &limit=12
```

**Respuesta**:
```json
{
  "scope": "GLOBAL" | "COMPETICIONES",
  "filtros": {
    "competicion_id": number | null,
    "grupo_id": number | null,
    "jornada": number | null
  },
  "partidos": [
    {
      "id": number,
      "identificador_federacion": string | null,
      "jornada_numero": number,
      "fecha_hora": "ISO string",
      "jugado": boolean,
      "local": {
        "id": number,
        "nombre": string,
        "escudo": string,
        "slug": string | null
      },
      "visitante": {
        "id": number,
        "nombre": string,
        "escudo": string,
        "slug": string | null
      },
      "goles_local": number | null,
      "goles_visitante": number | null,
      "grupo": {
        "id": number,
        "nombre": string,
        "slug": string | null,
        "competicion": {
          "id": number,
          "nombre": string,
          "slug": string | null
        },
        "temporada": {
          "id": number,
          "nombre": string
        }
      }
    }
  ]
}
```

---

### 2. FICHA DETALLADA DE PARTIDO (`/partidos/[id]` o `/partidos/[slug]`)

#### 2.1. Estructura de la Página

**Header del Partido**
- Escudos y nombres de local/visitante (con enlaces a páginas de club)
- Marcador final
- Fecha y hora
- Jornada y grupo (con enlace a página de competición)
- Pabellón (con enlace si hay página de pabellón)
- Árbitros (lista con enlaces si hay páginas de árbitros)
- Índice de intensidad (si existe)

**Línea del Tiempo de Eventos**
- Timeline visual con dos columnas (local izquierda, visitante derecha)
- Separación visual entre primera parte (0-20 min) y segunda parte (20:01-40 min)
- Eventos ordenados por minuto
- Iconos diferenciados por tipo:
  - ⚽ Gol
  - 🟨 Amarilla
  - 🟨🟨 Doble amarilla
  - 🟥 Roja
  - ⭐ MVP
- Al hacer clic en evento → scroll a jugador en alineación o enlace a perfil

**Alineaciones**
- Dos columnas: Local | Visitante
- Sección "Titulares" y "Suplentes"
- Por cada jugador:
  - Foto (o iniciales)
  - Dorsal
  - Nombre (con enlace a perfil)
  - Etiquetas: Pt (portero), C (capitán), etc.
  - **Puntos de valoración** del partido (si existen)
  - **Goles** marcados en ese partido
  - **Tarjetas** recibidas en ese partido
  - Minutos jugados (si está disponible)

**Staff Técnico**
- Dos columnas: Local | Visitante
- Lista de técnicos con nombre y rol
- Enlaces a perfiles si existen

**Estadísticas del Partido**
- Resumen de eventos:
  - Goles totales
  - Tarjetas (amarillas, dobles, rojas)
  - MVPs
- Distribución de goles por parte (1ª parte / 2ª parte)
- Gráfico de posesión (si está disponible)
- Otros KPIs relevantes

#### 2.2. Endpoint Backend Principal

```
GET /api/partidos/detalle/?partido_id=XX
GET /api/partidos/detalle/?identificador_federacion=YY
```

**Respuesta Completa**:
```json
{
  "partido": {
    "id": number,
    "identificador_federacion": string | null,
    "jornada_numero": number,
    "fecha_hora": "ISO string",
    "jugado": boolean,
    "pabellon": string,
    "indice_intensidad": number | null,
    "grupo": {
      "id": number,
      "nombre": string,
      "slug": string | null,
      "competicion": {
        "id": number,
        "nombre": string,
        "slug": string | null
      },
      "temporada": {
        "id": number,
        "nombre": string
      }
    },
    "jornada_numero": number,
    "local": {
      "id": number,
      "nombre": string,
      "escudo": string,
      "slug": string | null
    },
    "visitante": {
      "id": number,
      "nombre": string,
      "escudo": string,
      "slug": string | null
    },
    "goles_local": number | null,
    "goles_visitante": number | null
  },
  "arbitros": [
    {
      "id": number | null,
      "nombre": string,
      "rol": string,
      "slug": string | null
    }
  ],
  "eventos": [
    {
      "id": number,
      "minuto": number,
      "tipo_evento": "gol" | "amarilla" | "doble_amarilla" | "roja" | "mvp" | "gol_pp",
      "parte": "primera" | "segunda" | "prorroga",
      "jugador": {
        "id": number,
        "nombre": string,
        "slug": string | null,
        "foto": string
      } | null,
      "club": {
        "id": number,
        "nombre": string,
        "slug": string | null,
        "lado": "local" | "visitante"
      } | null,
      "nota": string
    }
  ],
  "alineaciones": {
    "local": {
      "club_id": number,
      "titulares": [
        {
          "jugador_id": number,
          "nombre": string,
          "slug": string | null,
          "foto": string,
          "dorsal": string,
          "etiqueta": string,
          "titular": true,
          "goles": number,
          "tarjetas_amarillas": number,
          "tarjetas_dobles_amarillas": number,
          "tarjetas_rojas": number,
          "mvp": boolean
        }
      ],
      "suplentes": [...],
      "staff": [
        {
          "nombre": string,
          "rol": string,
          "staff_id": number | null
        }
      ]
    },
    "visitante": {
      "club_id": number,
      "titulares": [...],
      "suplentes": [...],
      "staff": [...]
    }
  },
  "estadisticas": {
    "goles_total": number,
    "goles_local": number,
    "goles_visitante": number,
    "goles_primera_parte": number,
    "goles_segunda_parte": number,
    "amarillas_total": number,
    "dobles_amarillas_total": number,
    "rojas_total": number,
    "mvps": number
  }
}
```

#### 2.3. Componentes Frontend

- `PartidoDetailPage.tsx` - Página principal
- `PartidoHeader.tsx` - Header con marcador, equipos, info básica
- `PartidoTimeline.tsx` - Línea del tiempo de eventos
- `PartidoAlineaciones.tsx` - Alineaciones con valoraciones
- `PartidoStaff.tsx` - Staff técnico
- `PartidoEstadisticas.tsx` - Estadísticas resumen

---

## 🔗 INTEGRACIÓN CON ENDPOINTS DE VALORACIONES EXISTENTES

### Endpoints a Utilizar

#### 1. Puntos de Jugadores
**Endpoint**: `GET /api/valoraciones/jugadores-jornada/?grupo_id=XX&jornada=YY`

**Respuesta**:
```json
{
  "grupo": {...},
  "jornada": number,
  "jugador_de_la_jornada": {...},
  "ranking_jugadores": [
    {
      "jugador_id": number,
      "nombre": string,
      "slug": string | null,
      "foto": string,
      "club_id": number,
      "club_nombre": string,
      "club_escudo": string,
      "club_slug": string | null,
      "puntos": number,
      "detalles": string[],
      "es_portero": boolean
    }
  ]
}
```

**Uso en Frontend**:
- Llamar a este endpoint con el `grupo_id` y `jornada` del partido
- Filtrar `ranking_jugadores` para obtener solo los jugadores que participaron en el partido específico
- Matchear por `jugador_id` con las alineaciones del partido
- Mostrar `puntos` en la alineación junto a cada jugador

#### 2. Puntos de Equipos
**Endpoint**: `GET /api/valoraciones/equipo-jornada/?grupo_id=XX&jornada=YY`

**Respuesta**:
```json
{
  "grupo": {...},
  "jornada": number,
  "equipo_de_la_jornada": {...},
  "ranking_clubes": [
    {
      "club_id": number,
      "nombre": string,
      "escudo": string,
      "slug": string | null,
      "score": number,
      "motivos": string[]
    }
  ]
}
```

**Uso en Frontend**:
- Llamar a este endpoint con el `grupo_id` y `jornada` del partido
- Filtrar `ranking_clubes` para obtener solo los dos equipos del partido (local y visitante)
- Matchear por `club_id` con `partido.local_id` y `partido.visitante_id`
- Mostrar `score` en el header del partido o en una sección de estadísticas

### Implementación en Frontend

En `PartidoDetailClient.tsx` o componente similar:

```typescript
// Hook para obtener puntos de jugadores
const { data: valoracionesJugadores } = useJugadoresJornada({
  grupoId: partido.grupo.id,
  jornada: partido.jornada_numero
});

// Hook para obtener puntos de equipos
const { data: valoracionesEquipos } = useEquipoJornada({
  grupoId: partido.grupo.id,
  jornada: partido.jornada_numero
});

// Crear lookup de puntos por jugador_id
const puntosPorJugador = useMemo(() => {
  if (!valoracionesJugadores?.ranking_jugadores) return {};
  const lookup: Record<number, number> = {};
  valoracionesJugadores.ranking_jugadores.forEach(j => {
    lookup[j.jugador_id] = j.puntos;
  });
  return lookup;
}, [valoracionesJugadores]);

// Crear lookup de puntos por club_id
const puntosPorEquipo = useMemo(() => {
  if (!valoracionesEquipos?.ranking_clubes) return {};
  const lookup: Record<number, number> = {};
  valoracionesEquipos.ranking_clubes.forEach(c => {
    lookup[c.club_id] = c.score;
  });
  return lookup;
}, [valoracionesEquipos]);
```

### Notas Importantes

1. **No calcular puntos en el backend del detalle**: Los puntos ya están calculados en los endpoints de valoraciones. Solo hay que consumirlos.

2. **Matching de datos**: 
   - Los jugadores se matchean por `jugador_id` entre alineaciones y `ranking_jugadores`
   - Los equipos se matchean por `club_id` entre partido y `ranking_clubes`

3. **Slugs incluidos**: Los endpoints ya devuelven `slug` para jugadores y clubes, así que se pueden usar directamente para los enlaces.

4. **Datos adicionales**: Los endpoints también devuelven `detalles` y `motivos` que se pueden mostrar en tooltips o secciones expandibles.

---

## 📐 DISEÑO DE LA LÍNEA DEL TIEMPO

### Estructura Visual

```
┌─────────────────────────────────────────────────────────┐
│  PRIMERA PARTE (0-20 min)                               │
├──────────────┬──────────────────────────────────────────┤
│ LOCAL        │ VISITANTE                                │
│              │                                           │
│  5' ⚽       │                                           │
│  Gol: Juan   │                                           │
│              │                                           │
│              │  12' 🟨                                  │
│              │  Amarilla: Pedro                         │
│              │                                           │
│  18' ⚽      │                                           │
│  Gol: Luis   │                                           │
├──────────────┴──────────────────────────────────────────┤
│  SEGUNDA PARTE (20:01-40 min)                           │
├──────────────┬──────────────────────────────────────────┤
│              │  25' ⚽                                   │
│              │  Gol: Carlos                             │
│              │                                           │
│  30' 🟥      │                                           │
│  Roja: Ana   │                                           │
│              │                                           │
│              │  35' ⚽                                   │
│              │  Gol: Miguel                             │
└──────────────┴──────────────────────────────────────────┘
```

### Lógica de Separación de Partes

- **Primera parte**: `minuto >= 1 && minuto <= 20`
- **Segunda parte**: `minuto >= 21 && minuto <= 40`
- **Prorroga/Extra**: `minuto > 40` (mostrar como sección adicional si existe)

---

## 🗂️ ESTRUCTURA DE ARCHIVOS

### Backend

```
backend/partidos/
├── models.py (ya existe - Partido, EventoPartido, AlineacionPartidoJugador)
├── views.py (CREAR - PartidoDetalleView, PartidosListView)
├── urls.py (CREAR)
├── admin.py (ya existe)
└── serializers.py (OPCIONAL - solo si necesitamos validación compleja)
```

**IMPORTANTE**: Todo el código nuevo se crea en `backend/partidos/`. No modificamos endpoints existentes en otras apps.

### Frontend

```
frontend/
├── app/[lang]/
│   ├── partidos/
│   │   ├── page.tsx (listado de partidos)
│   │   ├── PartidosPageClient.tsx
│   │   └── [id]/
│   │       └── page.tsx (ficha detallada)
│   │       └── PartidoDetailClient.tsx
├── components/
│   ├── PartidosShell.tsx (nuevo)
│   ├── PartidosList.tsx (nuevo)
│   ├── PartidoHeader.tsx (nuevo)
│   ├── PartidoTimeline.tsx (nuevo)
│   ├── PartidoAlineaciones.tsx (nuevo)
│   ├── PartidoStaff.tsx (nuevo)
│   ├── PartidoEstadisticas.tsx (nuevo)
│   └── PartidoCard.tsx (ya existe, posiblemente reutilizar)
└── hooks/
    ├── usePartidoDetalle.ts (nuevo)
    └── usePartidosList.ts (nuevo)
```

---

## 📝 PLAN DE IMPLEMENTACIÓN

### FASE 1: Backend - Endpoints Base en `backend/partidos/`

#### 1.1. Crear `backend/partidos/urls.py`
```python
from django.urls import path
from . import views

urlpatterns = [
    path("lista/", views.PartidosListView.as_view(), name="partidos-lista"),
    path("detalle/", views.PartidoDetalleView.as_view(), name="partidos-detalle"),
]
```

#### 1.2. Implementar `PartidosListView` en `backend/partidos/views.py`
- Filtrado por scope (GLOBAL/COMPETICIONES)
- Filtrado por competición, grupo, jornada
- Modo aleatorio de última semana (últimos 7 días o última jornada con partidos)
- Incluir slugs de clubes
- **Incluir información completa de grupo, competición y temporada** (con slugs)
- Incluir `jornada_numero` en cada partido
- Incluir información básica: marcador, fecha, pabellón, árbitros
- Orden: fecha_hora DESC
- **Reutilizar lógica similar a `ResultadosJornadaView`** pero con filtros adicionales

#### 1.3. Implementar `PartidoDetalleView` en `backend/partidos/views.py`
- Obtener partido por `partido_id` o `identificador_federacion`
- Cargar eventos ordenados por minuto (con `select_related` para jugador y club)
- Cargar alineaciones (titulares/suplentes) por equipo (con `select_related` para jugador y club)
- **NO calcular puntos de valoración** (se obtienen desde endpoints de valoraciones en frontend)
- Agregar goles y tarjetas por jugador en ese partido (contar eventos del partido)
- Cargar staff técnico (desde `StaffEnPartido`)
- Cargar árbitros (desde `ArbitrajePartido` con `select_related`)
- Calcular estadísticas agregadas (goles totales, tarjetas, etc.)
- **Incluir slugs** de jugadores y clubes en todas las respuestas
- **Incluir información completa de grupo, competición y temporada** (con slugs)
- **Incluir `jornada_numero`** en la respuesta del partido

#### 1.4. Añadir a `backend/administracion/urls.py`
```python
path("api/partidos/", include("partidos.urls")),
```

**NOTA**: No modificamos endpoints existentes en `estadisticas` o `valoraciones`. Solo creamos nuevos en `partidos/`.

### FASE 2: Frontend - Página de Listado

#### 2.1. Crear estructura de páginas
- `app/[lang]/partidos/page.tsx`
- `app/[lang]/partidos/PartidosPageClient.tsx`

#### 2.2. Crear componentes
- `PartidosShell.tsx` - Lógica principal (scope, filtros, favorito/aleatorio)
- `PartidosList.tsx` - Grid de partidos
- Reutilizar `PartidoCard.tsx` o crear variante

#### 2.3. Crear hooks
- `usePartidosList.ts` - Fetch de lista de partidos

#### 2.4. Añadir traducciones
- Añadir keys en `i18n/*.json` para:
  - Títulos y descripciones
  - Labels de filtros
  - Mensajes de estado (sin datos, cargando, etc.)

### FASE 3: Frontend - Ficha Detallada

#### 3.1. Crear estructura de página
- `app/[lang]/partidos/[id]/page.tsx`
- `app/[lang]/partidos/[id]/PartidoDetailClient.tsx`

#### 3.2. Crear componentes
- `PartidoHeader.tsx` - Header con marcador, equipos, info básica
- `PartidoTimeline.tsx` - Línea del tiempo con eventos
- `PartidoAlineaciones.tsx` - Alineaciones con valoraciones
- `PartidoStaff.tsx` - Staff técnico
- `PartidoEstadisticas.tsx` - Estadísticas resumen

#### 3.3. Crear hooks
- `usePartidoDetalle.ts` - Fetch de detalle completo

#### 3.4. Añadir traducciones
- Keys para eventos, partes, roles, etc.

### FASE 4: Integración de Valoraciones en Frontend

#### 4.1. Crear hooks para endpoints de valoraciones
- Crear o reutilizar `useJugadoresJornada.ts` para obtener puntos de jugadores
- Crear o reutilizar `useEquipoJornada.ts` para obtener puntos de equipos
- Los hooks deben aceptar `grupoId` y `jornada` como parámetros

#### 4.2. Integrar puntos en componentes
- En `PartidoAlineaciones.tsx`:
  - Llamar a `useJugadoresJornada` con grupo y jornada del partido
  - Crear lookup de puntos por `jugador_id`
  - Mostrar puntos junto a cada jugador en la alineación
  - Mostrar enlaces a perfiles usando `slug` del jugador
- En `PartidoHeader.tsx` o `PartidoEstadisticas.tsx`:
  - Llamar a `useEquipoJornada` con grupo y jornada del partido
  - Crear lookup de puntos por `club_id`
  - Mostrar puntos de cada equipo (local y visitante)
  - Mostrar enlaces a páginas de club usando `slug` del club

#### 4.3. Agregar goles y tarjetas por jugador
- Contar eventos de tipo "gol" por jugador (ya incluido en endpoint de detalle)
- Contar eventos de tipo "amarilla", "doble_amarilla", "roja" por jugador (ya incluido)
- Identificar MVP del partido (ya incluido en eventos)

### FASE 5: Mejoras y Optimizaciones

#### 5.1. SEO
- Metadata dinámica por partido
- Open Graph tags
- Structured data (JSON-LD)

#### 5.2. Performance
- Prefetch de relaciones en queries
- Cache de datos estáticos
- Lazy loading de imágenes

#### 5.3. UX
- Loading states
- Error handling
- Empty states
- Animaciones en timeline

---

## 🔧 DETALLES TÉCNICOS

### Obtención de Puntos de Valoración

**NO se calculan en el backend del detalle del partido**. Se obtienen desde los endpoints existentes:

1. **Puntos de Jugadores**: 
   - Endpoint: `GET /api/valoraciones/jugadores-jornada/?grupo_id=XX&jornada=YY`
   - Los puntos ya están calculados y listos para usar
   - Incluyen todos los bonus y penalizaciones (presencia, eventos, resultado, rival fuerte, duelo fuertes, intensidad, gol decisivo, porteros, etc.)

2. **Puntos de Equipos**:
   - Endpoint: `GET /api/valoraciones/equipo-jornada/?grupo_id=XX&jornada=YY`
   - Los puntos ya están calculados y listos para usar
   - Incluyen bonus por victoria, empate, rival fuerte, diferencia de goles, etc.

3. **Matching en Frontend**:
   - Filtrar `ranking_jugadores` por los `jugador_id` que aparecen en las alineaciones del partido
   - Filtrar `ranking_clubes` por los `club_id` del partido (local y visitante)
   - Crear lookups para acceso rápido: `puntosPorJugador[jugador_id]` y `puntosPorEquipo[club_id]`

### Identificación de Parte del Partido

```python
def get_parte(minuto: int | None) -> str:
    if minuto is None:
        return "desconocida"
    if 1 <= minuto <= 20:
        return "primera"
    elif 21 <= minuto <= 40:
        return "segunda"
    else:
        return "prorroga"
```

### Orden de Eventos en Timeline

1. Ordenar por `minuto` ASC
2. Si mismo minuto, ordenar por tipo: gol → tarjeta → mvp
3. Si mismo minuto y tipo, ordenar por ID (orden de creación)

---

## 📊 DATOS ADICIONALES A INCLUIR

### Información del Pabellón
- Nombre del pabellón (ya disponible en `Partido.pabellon`)
- Posible enlace a página de pabellón (futuro)

### Información de Árbitros
- Lista de árbitros con nombres (ya disponible en `Partido.arbitros` o `ArbitrajePartido`)
- Roles (Principal, Auxiliar, Mesa, Cronometrador)
- Enlaces a perfiles de árbitros (si existen)

### Staff Técnico
- Entrenador principal
- Segundo entrenador
- Delegado
- Otros roles
- Enlaces a perfiles (si existen)

---

## 🎨 CONSIDERACIONES DE DISEÑO

### Timeline
- Diseño tipo "match timeline" de apps deportivas
- Colores diferenciados por equipo (local/visitante)
- Iconos claros y reconocibles
- Hover effects para mostrar más info
- Scroll suave al hacer clic en evento

### Alineaciones
- Diseño tipo "lineup" de apps deportivas
- Formación visual (portero, defensas, medios, delanteros)
- Destacar jugadores con eventos (goles, tarjetas, MVP)
- Tooltips con estadísticas al hover

### Responsive
- Mobile-first approach
- Timeline adaptativa (vertical en mobile, horizontal en desktop)
- Alineaciones apiladas en mobile, lado a lado en desktop

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Backend (todo en `backend/partidos/`)
- [ ] Crear `backend/partidos/urls.py`
- [ ] Crear `backend/partidos/views.py` con `PartidosListView` y `PartidoDetalleView`
- [ ] Añadir `path("api/partidos/", include("partidos.urls"))` a `backend/administracion/urls.py`
- [ ] Implementar `PartidosListView`:
  - [ ] Filtrado por scope (GLOBAL/COMPETICIONES)
  - [ ] Filtrado por competición, grupo, jornada
  - [ ] Modo aleatorio de última semana
  - [ ] Incluir slugs de clubes
  - [ ] **Incluir información completa de grupo, competición y temporada (con slugs)**
  - [ ] **Incluir `jornada_numero` en cada partido**
- [ ] Implementar `PartidoDetalleView`:
  - [ ] Obtener partido por ID o identificador_federacion
  - [ ] Cargar eventos ordenados por minuto
  - [ ] Cargar alineaciones (titulares/suplentes) por equipo
  - [ ] **NO calcular puntos de valoración** (se obtienen desde endpoints existentes)
  - [ ] Agregar goles y tarjetas por jugador (contar eventos)
  - [ ] Incluir staff técnico
  - [ ] Incluir árbitros
  - [ ] Calcular estadísticas agregadas
  - [ ] **Incluir slugs de jugadores y clubes** en todas las respuestas
  - [ ] **Incluir información completa de grupo, competición y temporada (con slugs)**
  - [ ] **Incluir `jornada_numero` en la respuesta**
- [ ] Tests básicos de endpoints

### Frontend - Listado
- [ ] Crear `app/[lang]/partidos/page.tsx`
- [ ] Crear `PartidosPageClient.tsx`
- [ ] Crear `PartidosShell.tsx`
- [ ] Crear `PartidosList.tsx`
- [ ] Crear `usePartidosList.ts`
- [ ] Implementar lógica de favorito/aleatorio
- [ ] Añadir traducciones
- [ ] SEO metadata

### Frontend - Detalle
- [ ] Crear `app/[lang]/partidos/[id]/page.tsx`
- [ ] Crear `PartidoDetailClient.tsx`
- [ ] Crear `PartidoHeader.tsx`
- [ ] Crear `PartidoTimeline.tsx`
- [ ] Crear `PartidoAlineaciones.tsx`
- [ ] Crear `PartidoStaff.tsx`
- [ ] Crear `PartidoEstadisticas.tsx`
- [ ] Crear `usePartidoDetalle.ts`
- [ ] **Integrar `useJugadoresJornada` para obtener puntos de jugadores**
- [ ] **Integrar `useEquipoJornada` para obtener puntos de equipos**
- [ ] **Mostrar puntos en alineaciones y header**
- [ ] Añadir traducciones
- [ ] SEO metadata dinámica
- [ ] **Enlaces a jugadores usando `slug`**
- [ ] **Enlaces a clubes usando `slug`**
- [ ] Enlaces a árbitros (si tienen slug)

### Testing
- [ ] Probar listado con diferentes filtros
- [ ] Probar ficha con partidos con/sin eventos
- [ ] Probar ficha con partidos con/sin alineaciones
- [ ] Probar responsive design
- [ ] Probar enlaces y navegación

---

## 🚀 ORDEN DE EJECUCIÓN RECOMENDADO

1. **Backend - PartidosListView** (FASE 1.2)
2. **Backend - PartidoDetalleView** (FASE 1.3) - **Incluir slugs de jugadores y clubes**
3. **Frontend - Listado básico** (FASE 2)
4. **Frontend - Header y Timeline** (FASE 3.2 - parcial)
5. **Frontend - Alineaciones básicas** (FASE 3.2 - parcial) - **Con enlaces usando slugs**
6. **Frontend - Integración valoraciones** (FASE 4) - **Llamar a endpoints existentes**
7. **Frontend - Alineaciones con puntos** (FASE 4.2) - **Mostrar puntos de jugadores**
8. **Frontend - Header con puntos de equipos** (FASE 4.2) - **Mostrar puntos de equipos**
9. **Frontend - Staff y Estadísticas** (FASE 3.2 - completo)
10. **Frontend - Mejoras UX** (FASE 5)

---

## 📌 NOTAS IMPORTANTES

1. **Slugs de partidos**: Actualmente no existe campo `slug` en modelo `Partido`. Opciones:
   - Usar `id` directamente: `/partidos/123`
   - Crear slug basado en fecha + equipos: `/partidos/2025-11-30-inter-tavernes-vs-castalla`
   - Usar `identificador_federacion`: `/partidos/26318901`

2. **Valoraciones**: Los puntos de valoración **NO se calculan en el endpoint de detalle del partido**. Se obtienen llamando a los endpoints existentes de valoraciones desde el frontend:
   - `/api/valoraciones/jugadores-jornada/` para puntos de jugadores
   - `/api/valoraciones/equipo-jornada/` para puntos de equipos
   - Estos endpoints ya calculan todos los puntos usando la lógica completa de valoraciones.

3. **Minutos jugados**: Actualmente no está disponible en `AlineacionPartidoJugador`. Se podría inferir de eventos o añadir campo futuro.

4. **Formación visual**: La posición exacta de cada jugador en el campo no está disponible. Se puede mostrar lista ordenada por dorsal o por tipo (portero, campo).

5. **Compatibilidad**: Asegurar que funciona con partidos antiguos que pueden no tener todos los datos (alineaciones, eventos, etc.).

---

## 🔗 ENLACES Y NAVEGACIÓN

Desde la ficha de partido, se debe poder navegar a:
- **Página del club local** (usando `slug` del club)
- **Página del club visitante** (usando `slug` del club)
- **Perfil de cada jugador** (usando `slug` del jugador)
- Página de la competición/grupo (usando `competicion_slug` y `grupo_slug`)
- Perfil de árbitros (si existen y tienen `slug`)
- Otros partidos de la misma jornada
- Otros partidos del mismo grupo

---

## 📝 PRÓXIMOS PASOS

Una vez aprobado este roadmap:
1. Crear endpoints backend
2. Crear estructura de páginas frontend
3. Implementar componentes básicos
4. Integrar valoraciones
5. Añadir mejoras UX
6. Testing completo
7. Deploy

---

**Fecha de creación**: 2025-11-29
**Versión**: 1.0
**Estado**: Pendiente de aprobación

