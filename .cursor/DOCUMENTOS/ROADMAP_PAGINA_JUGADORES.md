# 🎯 ROADMAP — PÁGINA DE PERFIL DE JUGADOR

## 📋 RESUMEN EJECUTIVO

Implementar la página de perfil de jugador, el "corazón de la marca" según PROJECT_VISION.md. Esta página mostrará:
- Media global tipo FIFA
- Atributos detallados (regate, intensidad, ataque, defensa, pase, potencia, visión, regularidad, carisma)
- Historial por temporadas
- Estadísticas actuales
- Distintivos ganados
- Enlaces al club actual
- Botones de acción: "Votar" y "¿Eres tú? Verifica el perfil"

---

## 🔍 ANÁLISIS DE DATOS DISPONIBLES

### ✅ Datos que YA tenemos en el backend:

#### 1. **Modelos de Jugadores** (`jugadores/models.py`):
- `Jugador`: Identidad permanente
  - `nombre`, `apodo`
  - `fecha_nacimiento`, `edad_estimacion`
  - `posicion_principal` (portero, cierre, ala, pivot, universal)
  - `foto_url`
  - `informe_scout` (texto descriptivo)
  - `identificador_federacion` (ID único del scraping)
  - `activo`

- `JugadorEnClubTemporada`: Estadísticas por temporada
  - `jugador` (FK)
  - `club` (FK)
  - `temporada` (FK)
  - `dorsal`
  - `partidos_jugados`, `goles`
  - `tarjetas_amarillas`, `tarjetas_rojas`
  - `convocados`, `titular`, `suplente`

- `HistorialJugadorScraped`: Historial bruto del scraping
  - `temporada_texto`, `competicion_texto`, `equipo_texto`

#### 2. **Valoraciones FIFA** (`valoraciones/models.py`):
- `ValoracionJugador`: Nota oficial agregada por temporada
  - `jugador` (FK)
  - `temporada` (FK)
  - Atributos: `ataque`, `defensa`, `pase`, `regate`, `potencia`, `intensidad`, `vision`, `regularidad`, `carisma`
  - `media_global` (calculada)

- `VotoValoracionJugador`: Votos individuales
  - `jugador`, `usuario`, `temporada`
  - `atributo`, `valor` (0-100)
  - `peso_aplicado`

#### 3. **Datos del Scraping** (`data_clean/jugadores/`):
Estructura JSON scrapeada:
```json
{
  "jugador_id": 100738,
  "id_temp": 18,
  "datos_generales": {
    "nombre_completo": "VIDAL VIDAL SOLA, JAVIER",
    "edad": 21,
    "equipo_actual": "C.F.S. Ribeco Castalla 'A'"
  },
  "estadisticas": {
    "convocados": 0,
    "titular": 0,
    "suplente": 0,
    "jugados": 0,
    "total_goles": 0,
    "media_goles": 0.0,
    "amarillas": 0,
    "rojas": 0
  },
  "historico": [
    {
      "temporada": "2024-2025",
      "competicion": "1ª. Regional Futsal",
      "equipo": "C.F.S. Ribeco Castalla"
    }
  ],
  "header": {
    "nombre_header": "...",
    "competicion_header": "...",
    "dorsal_header": null,
    "escudo_equipo_url": "..."
  },
  "foto": {
    "source": "data:image/png;base64,...",
    "is_base64": true
  }
}
```

#### 4. **Datos en Rankings Actuales**:
Los endpoints de valoraciones ya devuelven información de jugadores:
- `jugador_id`, `nombre`, `apodo`
- `foto`
- `club_id`, `club_nombre`, `club_escudo`
- `puntos_acumulados`, `puntos_jornada`
- `posicion` (en ranking)

### ❌ Datos que FALTAN o necesitan endpoints:

1. **Endpoint específico de jugador**: No existe `/api/jugadores/detalle/` o similar
2. **Endpoint de historial completo**: Necesitamos consolidar `HistorialJugadorScraped` + `JugadorEnClubTemporada`
3. **Endpoint de valoraciones del jugador**: Necesitamos obtener `ValoracionJugador` por jugador
4. **Endpoint de partidos del jugador**: Para mostrar estadísticas detalladas
5. **Distintivos**: Modelo no revisado aún (puede existir en `destacados` o similar)

---

## 🎯 FASE 1 — BACKEND: Endpoints de Jugadores

### 1.1 Crear app `jugadores/urls.py` y registrar en `administracion/urls.py`

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/urls.py` (NUEVO)
```python
from django.urls import path
from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
)

urlpatterns = [
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]
```

**Registrar en**: `/home/rubenmaestre/pcfutsal.es/backend/administracion/urls.py`
```python
path("api/jugadores/", include("jugadores.urls")),
```

### 1.2 Crear Serializers

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/serializers.py` (NUEVO)

Serializers necesarios:
- `JugadorSerializer`: Datos básicos del jugador
- `JugadorEnClubTemporadaSerializer`: Ya existe en `clubes/serializers.py`, reutilizar o mover
- `ValoracionJugadorSerializer`: Para mostrar atributos FIFA
- `HistorialJugadorSerializer`: Para historial consolidado

### 1.3 Crear Views

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/views.py` (ACTUALIZAR)

#### 1.3.1 `GET /api/jugadores/detalle/?jugador_id=XX`
**Descripción**: Detalle básico del jugador
**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "escudo_url": "string",
    "slug": "string"
  } | null,
  "temporada_actual": {
    "id": number,
    "nombre": "string"
  } | null,
  "dorsal_actual": "string" | null
}
```

#### 1.3.2 `GET /api/jugadores/full/?jugador_id=XX&temporada_id=YY&include=valoraciones,historial,partidos,stats`
**Descripción**: Ficha completa del jugador (similar a `/api/clubes/full/`)
**Parámetros**:
- `jugador_id` (requerido): ID del jugador
- `temporada_id` (opcional): Para filtrar datos de una temporada específica
- `include` (opcional, CSV): `valoraciones`, `historial`, `partidos`, `stats`, `distintivos`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Distintivos (si `include=distintivos` y existe modelo)

#### 1.3.3 `GET /api/jugadores/historial/?jugador_id=XX`
**Descripción**: Historial completo del jugador (consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`)
**Retorna**:
```json
{
  "jugador_id": number,
  "jugador_nombre": "string",
  "historico": [
    {
      "temporada": "string",
      "temporada_id": number | null,
      "competicion": "string",
      "competicion_id": number | null,
      "grupo": "string",
      "grupo_id": number | null,
      "club": "string",
      "club_id": number | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean  // true si viene de HistorialJugadorScraped
    }
  ]
}
```

#### 1.3.4 `GET /api/jugadores/valoraciones/?jugador_id=XX&temporada_id=YY`
**Descripción**: Valoraciones FIFA del jugador
**Retorna**:
```json
{
  "jugador_id": number,
  "temporada": {
    "id": number,
    "nombre": "string"
  } | null,
  "valoracion": {
    "ataque": number,
    "defensa": number,
    "pase": number,
    "regate": number,
    "potencia": number,
    "intensidad": number,
    "vision": number,
    "regularidad": number,
    "carisma": number,
    "media_global": number
  } | null,
  "total_votos": number,
  "ultima_actualizacion": "YYYY-MM-DDTHH:mm:ssZ" | null
}
```

#### 1.3.5 `GET /api/jugadores/partidos/?jugador_id=XX&temporada_id=YY&grupo_id=ZZ&limit=NN`
**Descripción**: Partidos del jugador con estadísticas
**Retorna**:
```json
{
  "jugador_id": number,
  "filtros": {
    "temporada_id": number | null,
    "grupo_id": number | null
  },
  "partidos": [
    {
      "partido_id": number,
      "fecha": "YYYY-MM-DD",
      "jornada": number,
      "local": "string",
      "local_id": number,
      "visitante": "string",
      "visitante_id": number,
      "goles_local": number,
      "goles_visitante": number,
      "goles_jugador": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "titular": boolean,
      "mvp": boolean
    }
  ],
  "totales": {
    "partidos_jugados": number,
    "goles": number,
    "tarjetas_amarillas": number,
    "tarjetas_rojas": number,
    "partidos_titular": number,
    "mvps": number
  }
}
```

### 1.4 Verificar modelo de Distintivos

**Tarea**: Revisar si existe modelo `Distintivo` y `DistintivoAsignado` en alguna app (probablemente `destacados` o `valoraciones`)

Si existe:
- Crear endpoint `GET /api/jugadores/distintivos/?jugador_id=XX`
- Retornar lista de distintivos ganados

Si no existe:
- Documentar como "pendiente de implementación"

---

## 🎯 FASE 2 — FRONTEND: Estructura de Páginas

### 2.1 Crear ruta dinámica

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx` (NUEVO)

**Estructura**:
- Server Component que obtiene `jugador_id` de params
- Fetch del diccionario de idiomas
- Fetch de datos del jugador (`/api/jugadores/full/`)
- Generación de metadata SEO dinámica
- Render del Client Component `JugadorDetailClient`

### 2.2 Crear Client Component principal

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/JugadorDetailClient.tsx` (NUEVO)

**Secciones**:
1. **Header del jugador**: Foto, nombre, apodo, posición, edad, club actual (con enlace)
2. **Tarjeta FIFA**: Media global + atributos visuales (tipo carta FIFA)
3. **Estadísticas actuales**: Partidos, goles, tarjetas, dorsal
4. **Historial**: Timeline de temporadas y clubes
5. **Partidos recientes**: Lista de últimos partidos con estadísticas
6. **Distintivos**: Badges ganados (si existen)
7. **Botones de acción**: "Votar" y "¿Eres tú? Verifica el perfil"

### 2.3 Crear componentes reutilizables

#### 2.3.1 Tarjeta FIFA del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorFIFACard.tsx` (NUEVO)

**Props**:
- `jugador`: Datos básicos
- `valoracion`: Atributos FIFA
- `club`: Club actual (opcional)

**Diseño**: Similar a las tarjetas FIFA existentes en rankings, pero más grande y detallada

#### 2.3.2 Historial del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorHistorial.tsx` (NUEVO)

**Props**:
- `historial`: Array de temporadas
- `lang`: Idioma actual

**Diseño**: Timeline vertical o cards horizontales con:
- Temporada
- Competición/Grupo
- Club (con enlace)
- Estadísticas básicas (goles, partidos)

#### 2.3.3 Estadísticas del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorStats.tsx` (NUEVO)

**Props**:
- `stats`: Estadísticas actuales
- `partidos`: Array de partidos recientes

**Diseño**: Tabla o cards con estadísticas detalladas

### 2.4 Crear Hook personalizado

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/hooks/useJugadorFull.ts` (NUEVO)

**Patrón**: Similar a `useClubFull`
- `use client`
- Manejo de estado: `data`, `loading`, `error`
- `useEffect` con cleanup
- URL relativa en cliente
- Cache: `no-store`

**Uso**:
```typescript
const { data, loading, error, refetch } = useJugadorFull({
  jugadorId: number,
  temporadaId?: number,
  include?: string[]
});
```

---

## 🎯 FASE 3 — Integración y Enlaces

### 3.1 Enlaces desde Rankings

**Archivos a actualizar**:
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/mvp/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/goleadores/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/sanciones/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/tarjetas/page.tsx`
- Componentes de rankings globales

**Cambio**: Hacer clicables los nombres/fotos de jugadores → `/es/jugadores/[id]`

### 3.2 Enlaces desde Plantillas de Clubes

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/clubes/[id]/ClubDetailClient.tsx`

**Cambio**: En la sección de plantilla, hacer clicables los jugadores → `/es/jugadores/[id]`

### 3.3 Enlaces desde Home (Jugador de la Jornada)

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/GlobalMVPCard.tsx` (o similar)

**Cambio**: Hacer clicable el jugador destacado → `/es/jugadores/[id]`

### 3.4 Enlaces desde Partidos

**Tarea**: Si hay componentes que muestran goleadores o eventos de partidos, añadir enlaces a perfiles de jugadores

---

## 🎯 FASE 4 — Traducciones y SEO

### 4.1 Añadir claves JSON

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/i18n/es.json` (y todos los idiomas)

**Nuevas secciones**:
```json
{
  "jugador": {
    "page_title": "Perfil de {nombre}",
    "media_global": "Media Global",
    "atributos": {
      "ataque": "Ataque",
      "defensa": "Defensa",
      "pase": "Pase",
      "regate": "Regate",
      "potencia": "Potencia",
      "intensidad": "Intensidad",
      "vision": "Visión",
      "regularidad": "Regularidad",
      "carisma": "Carisma"
    },
    "estadisticas": {
      "titulo": "Estadísticas",
      "partidos_jugados": "Partidos jugados",
      "goles": "Goles",
      "tarjetas_amarillas": "Tarjetas amarillas",
      "tarjetas_rojas": "Tarjetas rojas",
      "dorsal": "Dorsal"
    },
    "historial": {
      "titulo": "Historial",
      "temporada": "Temporada",
      "competicion": "Competición",
      "club": "Club"
    },
    "partidos": {
      "titulo": "Partidos",
      "recientes": "Partidos recientes"
    },
    "botones": {
      "votar": "Votar",
      "verificar_perfil": "¿Eres tú? Verifica el perfil"
    },
    "sin_datos": "No hay datos disponibles para este jugador"
  }
}
```

### 4.2 SEO Metadata

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx`

**Implementar**:
- `generateMetadata` dinámico con nombre del jugador
- Usar `dict.seo.jugador.title` y `dict.seo.jugador.description` con `replaceTemplate`
- Open Graph con foto del jugador
- Schema.org para `Person` y `SportsPerson`

**Añadir a `es.json`**:
```json
{
  "seo": {
    "jugador": {
      "title": "Perfil de {nombre} - PC FUTSAL",
      "description": "Ficha completa de {nombre} con estadísticas, valoraciones FIFA, historial y más en PC FUTSAL."
    }
  }
}
```

---

## 🎯 FASE 5 — Funcionalidades Adicionales (Opcional)

### 5.1 Sistema de Votación

**Backend**: Endpoint `POST /api/jugadores/votar/`
- Validar usuario autenticado
- Guardar voto en `VotoValoracionJugador`
- Recalcular `ValoracionJugador` agregada

**Frontend**: Modal o página de votación
- Formulario con sliders para cada atributo
- Mostrar peso del voto según rol del usuario
- Confirmación y feedback

### 5.2 Verificación de Perfil

**Backend**: Endpoint `POST /api/jugadores/solicitar-verificacion/`
- Crear `SolicitudVerificacion` (si existe modelo)
- Enviar email de confirmación

**Frontend**: Formulario de solicitud
- Campos: nombre, email, equipo actual, posición, dorsal
- Enlace al perfil actual
- Mensaje de confirmación

### 5.3 Comparación de Jugadores

**Backend**: Endpoint `GET /api/jugadores/compare/?jugador_id_1=XX&jugador_id_2=YY`
- Comparar atributos FIFA
- Comparar estadísticas
- Comparar historial

**Frontend**: Página de comparación
- Side-by-side de dos jugadores
- Gráficos comparativos

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Backend
- [x] Crear `jugadores/urls.py` ✅
- [x] Registrar en `administracion/urls.py` ✅
- [x] Crear `jugadores/serializers.py` ✅
- [x] Implementar `JugadorDetalleView` ✅
- [x] Implementar `JugadorFullView` ✅
- [x] Implementar `JugadorHistorialView` ✅
- [x] Implementar `JugadorValoracionesView` ✅
- [x] Implementar `JugadorPartidosView` ✅
- [ ] Verificar modelo de Distintivos
- [ ] (Opcional) Implementar endpoint de votación
- [ ] (Opcional) Implementar endpoint de verificación

### Frontend
- [x] Crear ruta `/app/[lang]/jugadores/[id]/page.tsx` ✅
- [x] Crear `JugadorDetailClient.tsx` ✅
- [ ] Crear `JugadorFIFACard.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorHistorial.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorStats.tsx` (opcional - funcionalidad integrada)
- [x] Crear hook `useJugadorFull.ts` ✅
- [ ] Añadir enlaces desde rankings
- [ ] Añadir enlaces desde plantillas de clubes
- [ ] Añadir enlaces desde home
- [x] Añadir traducciones en todos los idiomas ✅
- [x] Implementar SEO metadata ✅
- [ ] (Opcional) Implementar modal de votación
- [ ] (Opcional) Implementar formulario de verificación

### Testing
- [ ] Probar endpoints con jugadores existentes
- [ ] Probar con jugadores sin datos completos
- [ ] Probar enlaces desde diferentes páginas
- [ ] Verificar SEO en diferentes idiomas
- [ ] Verificar responsive design

---

## 🚀 ORDEN DE EJECUCIÓN RECOMENDADO

1. **FASE 1** (Backend): Crear endpoints básicos
2. **FASE 2.1-2.2** (Frontend): Crear página básica con datos principales
3. **FASE 2.3** (Frontend): Crear componentes visuales
4. **FASE 3** (Frontend): Añadir enlaces desde otras páginas
5. **FASE 4** (Frontend): Añadir traducciones y SEO
6. **FASE 5** (Opcional): Funcionalidades avanzadas

---

## 📚 REFERENCIAS

- `PROJECT_VISION.md`: Sección "4. Perfil de jugador" (líneas 76-97)
- `DOCUMENTACION/APIS.md`: Estructura de endpoints existentes
- `backend/jugadores/models.py`: Modelos de jugadores
- `backend/valoraciones/models.py`: Modelos de valoraciones
- `backend/clubes/views.py`: Ejemplo de implementación de `/api/clubes/full/`

---

**Última actualización**: 2025-11-25
**Estado**: FASE 1 COMPLETADA ✅ — FASE 2 EN PROGRESO ✅
- Backend: Completo y listo para testing
- Frontend: Página básica funcional, hook creado, traducciones completas, SEO implementado
- Pendiente: FASE 3 (enlaces desde otras páginas) y componentes auxiliares opcionales



## 📋 RESUMEN EJECUTIVO

Implementar la página de perfil de jugador, el "corazón de la marca" según PROJECT_VISION.md. Esta página mostrará:
- Media global tipo FIFA
- Atributos detallados (regate, intensidad, ataque, defensa, pase, potencia, visión, regularidad, carisma)
- Historial por temporadas
- Estadísticas actuales
- Distintivos ganados
- Enlaces al club actual
- Botones de acción: "Votar" y "¿Eres tú? Verifica el perfil"

---

## 🔍 ANÁLISIS DE DATOS DISPONIBLES

### ✅ Datos que YA tenemos en el backend:

#### 1. **Modelos de Jugadores** (`jugadores/models.py`):
- `Jugador`: Identidad permanente
  - `nombre`, `apodo`
  - `fecha_nacimiento`, `edad_estimacion`
  - `posicion_principal` (portero, cierre, ala, pivot, universal)
  - `foto_url`
  - `informe_scout` (texto descriptivo)
  - `identificador_federacion` (ID único del scraping)
  - `activo`

- `JugadorEnClubTemporada`: Estadísticas por temporada
  - `jugador` (FK)
  - `club` (FK)
  - `temporada` (FK)
  - `dorsal`
  - `partidos_jugados`, `goles`
  - `tarjetas_amarillas`, `tarjetas_rojas`
  - `convocados`, `titular`, `suplente`

- `HistorialJugadorScraped`: Historial bruto del scraping
  - `temporada_texto`, `competicion_texto`, `equipo_texto`

#### 2. **Valoraciones FIFA** (`valoraciones/models.py`):
- `ValoracionJugador`: Nota oficial agregada por temporada
  - `jugador` (FK)
  - `temporada` (FK)
  - Atributos: `ataque`, `defensa`, `pase`, `regate`, `potencia`, `intensidad`, `vision`, `regularidad`, `carisma`
  - `media_global` (calculada)

- `VotoValoracionJugador`: Votos individuales
  - `jugador`, `usuario`, `temporada`
  - `atributo`, `valor` (0-100)
  - `peso_aplicado`

#### 3. **Datos del Scraping** (`data_clean/jugadores/`):
Estructura JSON scrapeada:
```json
{
  "jugador_id": 100738,
  "id_temp": 18,
  "datos_generales": {
    "nombre_completo": "VIDAL VIDAL SOLA, JAVIER",
    "edad": 21,
    "equipo_actual": "C.F.S. Ribeco Castalla 'A'"
  },
  "estadisticas": {
    "convocados": 0,
    "titular": 0,
    "suplente": 0,
    "jugados": 0,
    "total_goles": 0,
    "media_goles": 0.0,
    "amarillas": 0,
    "rojas": 0
  },
  "historico": [
    {
      "temporada": "2024-2025",
      "competicion": "1ª. Regional Futsal",
      "equipo": "C.F.S. Ribeco Castalla"
    }
  ],
  "header": {
    "nombre_header": "...",
    "competicion_header": "...",
    "dorsal_header": null,
    "escudo_equipo_url": "..."
  },
  "foto": {
    "source": "data:image/png;base64,...",
    "is_base64": true
  }
}
```

#### 4. **Datos en Rankings Actuales**:
Los endpoints de valoraciones ya devuelven información de jugadores:
- `jugador_id`, `nombre`, `apodo`
- `foto`
- `club_id`, `club_nombre`, `club_escudo`
- `puntos_acumulados`, `puntos_jornada`
- `posicion` (en ranking)

### ❌ Datos que FALTAN o necesitan endpoints:

1. **Endpoint específico de jugador**: No existe `/api/jugadores/detalle/` o similar
2. **Endpoint de historial completo**: Necesitamos consolidar `HistorialJugadorScraped` + `JugadorEnClubTemporada`
3. **Endpoint de valoraciones del jugador**: Necesitamos obtener `ValoracionJugador` por jugador
4. **Endpoint de partidos del jugador**: Para mostrar estadísticas detalladas
5. **Distintivos**: Modelo no revisado aún (puede existir en `destacados` o similar)

---

## 🎯 FASE 1 — BACKEND: Endpoints de Jugadores

### 1.1 Crear app `jugadores/urls.py` y registrar en `administracion/urls.py`

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/urls.py` (NUEVO)
```python
from django.urls import path
from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
)

urlpatterns = [
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]
```

**Registrar en**: `/home/rubenmaestre/pcfutsal.es/backend/administracion/urls.py`
```python
path("api/jugadores/", include("jugadores.urls")),
```

### 1.2 Crear Serializers

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/serializers.py` (NUEVO)

Serializers necesarios:
- `JugadorSerializer`: Datos básicos del jugador
- `JugadorEnClubTemporadaSerializer`: Ya existe en `clubes/serializers.py`, reutilizar o mover
- `ValoracionJugadorSerializer`: Para mostrar atributos FIFA
- `HistorialJugadorSerializer`: Para historial consolidado

### 1.3 Crear Views

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/views.py` (ACTUALIZAR)

#### 1.3.1 `GET /api/jugadores/detalle/?jugador_id=XX`
**Descripción**: Detalle básico del jugador
**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "escudo_url": "string",
    "slug": "string"
  } | null,
  "temporada_actual": {
    "id": number,
    "nombre": "string"
  } | null,
  "dorsal_actual": "string" | null
}
```

#### 1.3.2 `GET /api/jugadores/full/?jugador_id=XX&temporada_id=YY&include=valoraciones,historial,partidos,stats`
**Descripción**: Ficha completa del jugador (similar a `/api/clubes/full/`)
**Parámetros**:
- `jugador_id` (requerido): ID del jugador
- `temporada_id` (opcional): Para filtrar datos de una temporada específica
- `include` (opcional, CSV): `valoraciones`, `historial`, `partidos`, `stats`, `distintivos`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Distintivos (si `include=distintivos` y existe modelo)

#### 1.3.3 `GET /api/jugadores/historial/?jugador_id=XX`
**Descripción**: Historial completo del jugador (consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`)
**Retorna**:
```json
{
  "jugador_id": number,
  "jugador_nombre": "string",
  "historico": [
    {
      "temporada": "string",
      "temporada_id": number | null,
      "competicion": "string",
      "competicion_id": number | null,
      "grupo": "string",
      "grupo_id": number | null,
      "club": "string",
      "club_id": number | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean  // true si viene de HistorialJugadorScraped
    }
  ]
}
```

#### 1.3.4 `GET /api/jugadores/valoraciones/?jugador_id=XX&temporada_id=YY`
**Descripción**: Valoraciones FIFA del jugador
**Retorna**:
```json
{
  "jugador_id": number,
  "temporada": {
    "id": number,
    "nombre": "string"
  } | null,
  "valoracion": {
    "ataque": number,
    "defensa": number,
    "pase": number,
    "regate": number,
    "potencia": number,
    "intensidad": number,
    "vision": number,
    "regularidad": number,
    "carisma": number,
    "media_global": number
  } | null,
  "total_votos": number,
  "ultima_actualizacion": "YYYY-MM-DDTHH:mm:ssZ" | null
}
```

#### 1.3.5 `GET /api/jugadores/partidos/?jugador_id=XX&temporada_id=YY&grupo_id=ZZ&limit=NN`
**Descripción**: Partidos del jugador con estadísticas
**Retorna**:
```json
{
  "jugador_id": number,
  "filtros": {
    "temporada_id": number | null,
    "grupo_id": number | null
  },
  "partidos": [
    {
      "partido_id": number,
      "fecha": "YYYY-MM-DD",
      "jornada": number,
      "local": "string",
      "local_id": number,
      "visitante": "string",
      "visitante_id": number,
      "goles_local": number,
      "goles_visitante": number,
      "goles_jugador": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "titular": boolean,
      "mvp": boolean
    }
  ],
  "totales": {
    "partidos_jugados": number,
    "goles": number,
    "tarjetas_amarillas": number,
    "tarjetas_rojas": number,
    "partidos_titular": number,
    "mvps": number
  }
}
```

### 1.4 Verificar modelo de Distintivos

**Tarea**: Revisar si existe modelo `Distintivo` y `DistintivoAsignado` en alguna app (probablemente `destacados` o `valoraciones`)

Si existe:
- Crear endpoint `GET /api/jugadores/distintivos/?jugador_id=XX`
- Retornar lista de distintivos ganados

Si no existe:
- Documentar como "pendiente de implementación"

---

## 🎯 FASE 2 — FRONTEND: Estructura de Páginas

### 2.1 Crear ruta dinámica

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx` (NUEVO)

**Estructura**:
- Server Component que obtiene `jugador_id` de params
- Fetch del diccionario de idiomas
- Fetch de datos del jugador (`/api/jugadores/full/`)
- Generación de metadata SEO dinámica
- Render del Client Component `JugadorDetailClient`

### 2.2 Crear Client Component principal

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/JugadorDetailClient.tsx` (NUEVO)

**Secciones**:
1. **Header del jugador**: Foto, nombre, apodo, posición, edad, club actual (con enlace)
2. **Tarjeta FIFA**: Media global + atributos visuales (tipo carta FIFA)
3. **Estadísticas actuales**: Partidos, goles, tarjetas, dorsal
4. **Historial**: Timeline de temporadas y clubes
5. **Partidos recientes**: Lista de últimos partidos con estadísticas
6. **Distintivos**: Badges ganados (si existen)
7. **Botones de acción**: "Votar" y "¿Eres tú? Verifica el perfil"

### 2.3 Crear componentes reutilizables

#### 2.3.1 Tarjeta FIFA del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorFIFACard.tsx` (NUEVO)

**Props**:
- `jugador`: Datos básicos
- `valoracion`: Atributos FIFA
- `club`: Club actual (opcional)

**Diseño**: Similar a las tarjetas FIFA existentes en rankings, pero más grande y detallada

#### 2.3.2 Historial del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorHistorial.tsx` (NUEVO)

**Props**:
- `historial`: Array de temporadas
- `lang`: Idioma actual

**Diseño**: Timeline vertical o cards horizontales con:
- Temporada
- Competición/Grupo
- Club (con enlace)
- Estadísticas básicas (goles, partidos)

#### 2.3.3 Estadísticas del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorStats.tsx` (NUEVO)

**Props**:
- `stats`: Estadísticas actuales
- `partidos`: Array de partidos recientes

**Diseño**: Tabla o cards con estadísticas detalladas

### 2.4 Crear Hook personalizado

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/hooks/useJugadorFull.ts` (NUEVO)

**Patrón**: Similar a `useClubFull`
- `use client`
- Manejo de estado: `data`, `loading`, `error`
- `useEffect` con cleanup
- URL relativa en cliente
- Cache: `no-store`

**Uso**:
```typescript
const { data, loading, error, refetch } = useJugadorFull({
  jugadorId: number,
  temporadaId?: number,
  include?: string[]
});
```

---

## 🎯 FASE 3 — Integración y Enlaces

### 3.1 Enlaces desde Rankings

**Archivos a actualizar**:
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/mvp/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/goleadores/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/sanciones/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/tarjetas/page.tsx`
- Componentes de rankings globales

**Cambio**: Hacer clicables los nombres/fotos de jugadores → `/es/jugadores/[id]`

### 3.2 Enlaces desde Plantillas de Clubes

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/clubes/[id]/ClubDetailClient.tsx`

**Cambio**: En la sección de plantilla, hacer clicables los jugadores → `/es/jugadores/[id]`

### 3.3 Enlaces desde Home (Jugador de la Jornada)

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/GlobalMVPCard.tsx` (o similar)

**Cambio**: Hacer clicable el jugador destacado → `/es/jugadores/[id]`

### 3.4 Enlaces desde Partidos

**Tarea**: Si hay componentes que muestran goleadores o eventos de partidos, añadir enlaces a perfiles de jugadores

---

## 🎯 FASE 4 — Traducciones y SEO

### 4.1 Añadir claves JSON

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/i18n/es.json` (y todos los idiomas)

**Nuevas secciones**:
```json
{
  "jugador": {
    "page_title": "Perfil de {nombre}",
    "media_global": "Media Global",
    "atributos": {
      "ataque": "Ataque",
      "defensa": "Defensa",
      "pase": "Pase",
      "regate": "Regate",
      "potencia": "Potencia",
      "intensidad": "Intensidad",
      "vision": "Visión",
      "regularidad": "Regularidad",
      "carisma": "Carisma"
    },
    "estadisticas": {
      "titulo": "Estadísticas",
      "partidos_jugados": "Partidos jugados",
      "goles": "Goles",
      "tarjetas_amarillas": "Tarjetas amarillas",
      "tarjetas_rojas": "Tarjetas rojas",
      "dorsal": "Dorsal"
    },
    "historial": {
      "titulo": "Historial",
      "temporada": "Temporada",
      "competicion": "Competición",
      "club": "Club"
    },
    "partidos": {
      "titulo": "Partidos",
      "recientes": "Partidos recientes"
    },
    "botones": {
      "votar": "Votar",
      "verificar_perfil": "¿Eres tú? Verifica el perfil"
    },
    "sin_datos": "No hay datos disponibles para este jugador"
  }
}
```

### 4.2 SEO Metadata

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx`

**Implementar**:
- `generateMetadata` dinámico con nombre del jugador
- Usar `dict.seo.jugador.title` y `dict.seo.jugador.description` con `replaceTemplate`
- Open Graph con foto del jugador
- Schema.org para `Person` y `SportsPerson`

**Añadir a `es.json`**:
```json
{
  "seo": {
    "jugador": {
      "title": "Perfil de {nombre} - PC FUTSAL",
      "description": "Ficha completa de {nombre} con estadísticas, valoraciones FIFA, historial y más en PC FUTSAL."
    }
  }
}
```

---

## 🎯 FASE 5 — Funcionalidades Adicionales (Opcional)

### 5.1 Sistema de Votación

**Backend**: Endpoint `POST /api/jugadores/votar/`
- Validar usuario autenticado
- Guardar voto en `VotoValoracionJugador`
- Recalcular `ValoracionJugador` agregada

**Frontend**: Modal o página de votación
- Formulario con sliders para cada atributo
- Mostrar peso del voto según rol del usuario
- Confirmación y feedback

### 5.2 Verificación de Perfil

**Backend**: Endpoint `POST /api/jugadores/solicitar-verificacion/`
- Crear `SolicitudVerificacion` (si existe modelo)
- Enviar email de confirmación

**Frontend**: Formulario de solicitud
- Campos: nombre, email, equipo actual, posición, dorsal
- Enlace al perfil actual
- Mensaje de confirmación

### 5.3 Comparación de Jugadores

**Backend**: Endpoint `GET /api/jugadores/compare/?jugador_id_1=XX&jugador_id_2=YY`
- Comparar atributos FIFA
- Comparar estadísticas
- Comparar historial

**Frontend**: Página de comparación
- Side-by-side de dos jugadores
- Gráficos comparativos

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Backend
- [x] Crear `jugadores/urls.py` ✅
- [x] Registrar en `administracion/urls.py` ✅
- [x] Crear `jugadores/serializers.py` ✅
- [x] Implementar `JugadorDetalleView` ✅
- [x] Implementar `JugadorFullView` ✅
- [x] Implementar `JugadorHistorialView` ✅
- [x] Implementar `JugadorValoracionesView` ✅
- [x] Implementar `JugadorPartidosView` ✅
- [ ] Verificar modelo de Distintivos
- [ ] (Opcional) Implementar endpoint de votación
- [ ] (Opcional) Implementar endpoint de verificación

### Frontend
- [x] Crear ruta `/app/[lang]/jugadores/[id]/page.tsx` ✅
- [x] Crear `JugadorDetailClient.tsx` ✅
- [ ] Crear `JugadorFIFACard.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorHistorial.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorStats.tsx` (opcional - funcionalidad integrada)
- [x] Crear hook `useJugadorFull.ts` ✅
- [ ] Añadir enlaces desde rankings
- [ ] Añadir enlaces desde plantillas de clubes
- [ ] Añadir enlaces desde home
- [x] Añadir traducciones en todos los idiomas ✅
- [x] Implementar SEO metadata ✅
- [ ] (Opcional) Implementar modal de votación
- [ ] (Opcional) Implementar formulario de verificación

### Testing
- [ ] Probar endpoints con jugadores existentes
- [ ] Probar con jugadores sin datos completos
- [ ] Probar enlaces desde diferentes páginas
- [ ] Verificar SEO en diferentes idiomas
- [ ] Verificar responsive design

---

## 🚀 ORDEN DE EJECUCIÓN RECOMENDADO

1. **FASE 1** (Backend): Crear endpoints básicos
2. **FASE 2.1-2.2** (Frontend): Crear página básica con datos principales
3. **FASE 2.3** (Frontend): Crear componentes visuales
4. **FASE 3** (Frontend): Añadir enlaces desde otras páginas
5. **FASE 4** (Frontend): Añadir traducciones y SEO
6. **FASE 5** (Opcional): Funcionalidades avanzadas

---

## 📚 REFERENCIAS

- `PROJECT_VISION.md`: Sección "4. Perfil de jugador" (líneas 76-97)
- `DOCUMENTACION/APIS.md`: Estructura de endpoints existentes
- `backend/jugadores/models.py`: Modelos de jugadores
- `backend/valoraciones/models.py`: Modelos de valoraciones
- `backend/clubes/views.py`: Ejemplo de implementación de `/api/clubes/full/`

---

**Última actualización**: 2025-11-25
**Estado**: FASE 1 COMPLETADA ✅ — FASE 2 EN PROGRESO ✅
- Backend: Completo y listo para testing
- Frontend: Página básica funcional, hook creado, traducciones completas, SEO implementado
- Pendiente: FASE 3 (enlaces desde otras páginas) y componentes auxiliares opcionales



## 📋 RESUMEN EJECUTIVO

Implementar la página de perfil de jugador, el "corazón de la marca" según PROJECT_VISION.md. Esta página mostrará:
- Media global tipo FIFA
- Atributos detallados (regate, intensidad, ataque, defensa, pase, potencia, visión, regularidad, carisma)
- Historial por temporadas
- Estadísticas actuales
- Distintivos ganados
- Enlaces al club actual
- Botones de acción: "Votar" y "¿Eres tú? Verifica el perfil"

---

## 🔍 ANÁLISIS DE DATOS DISPONIBLES

### ✅ Datos que YA tenemos en el backend:

#### 1. **Modelos de Jugadores** (`jugadores/models.py`):
- `Jugador`: Identidad permanente
  - `nombre`, `apodo`
  - `fecha_nacimiento`, `edad_estimacion`
  - `posicion_principal` (portero, cierre, ala, pivot, universal)
  - `foto_url`
  - `informe_scout` (texto descriptivo)
  - `identificador_federacion` (ID único del scraping)
  - `activo`

- `JugadorEnClubTemporada`: Estadísticas por temporada
  - `jugador` (FK)
  - `club` (FK)
  - `temporada` (FK)
  - `dorsal`
  - `partidos_jugados`, `goles`
  - `tarjetas_amarillas`, `tarjetas_rojas`
  - `convocados`, `titular`, `suplente`

- `HistorialJugadorScraped`: Historial bruto del scraping
  - `temporada_texto`, `competicion_texto`, `equipo_texto`

#### 2. **Valoraciones FIFA** (`valoraciones/models.py`):
- `ValoracionJugador`: Nota oficial agregada por temporada
  - `jugador` (FK)
  - `temporada` (FK)
  - Atributos: `ataque`, `defensa`, `pase`, `regate`, `potencia`, `intensidad`, `vision`, `regularidad`, `carisma`
  - `media_global` (calculada)

- `VotoValoracionJugador`: Votos individuales
  - `jugador`, `usuario`, `temporada`
  - `atributo`, `valor` (0-100)
  - `peso_aplicado`

#### 3. **Datos del Scraping** (`data_clean/jugadores/`):
Estructura JSON scrapeada:
```json
{
  "jugador_id": 100738,
  "id_temp": 18,
  "datos_generales": {
    "nombre_completo": "VIDAL VIDAL SOLA, JAVIER",
    "edad": 21,
    "equipo_actual": "C.F.S. Ribeco Castalla 'A'"
  },
  "estadisticas": {
    "convocados": 0,
    "titular": 0,
    "suplente": 0,
    "jugados": 0,
    "total_goles": 0,
    "media_goles": 0.0,
    "amarillas": 0,
    "rojas": 0
  },
  "historico": [
    {
      "temporada": "2024-2025",
      "competicion": "1ª. Regional Futsal",
      "equipo": "C.F.S. Ribeco Castalla"
    }
  ],
  "header": {
    "nombre_header": "...",
    "competicion_header": "...",
    "dorsal_header": null,
    "escudo_equipo_url": "..."
  },
  "foto": {
    "source": "data:image/png;base64,...",
    "is_base64": true
  }
}
```

#### 4. **Datos en Rankings Actuales**:
Los endpoints de valoraciones ya devuelven información de jugadores:
- `jugador_id`, `nombre`, `apodo`
- `foto`
- `club_id`, `club_nombre`, `club_escudo`
- `puntos_acumulados`, `puntos_jornada`
- `posicion` (en ranking)

### ❌ Datos que FALTAN o necesitan endpoints:

1. **Endpoint específico de jugador**: No existe `/api/jugadores/detalle/` o similar
2. **Endpoint de historial completo**: Necesitamos consolidar `HistorialJugadorScraped` + `JugadorEnClubTemporada`
3. **Endpoint de valoraciones del jugador**: Necesitamos obtener `ValoracionJugador` por jugador
4. **Endpoint de partidos del jugador**: Para mostrar estadísticas detalladas
5. **Distintivos**: Modelo no revisado aún (puede existir en `destacados` o similar)

---

## 🎯 FASE 1 — BACKEND: Endpoints de Jugadores

### 1.1 Crear app `jugadores/urls.py` y registrar en `administracion/urls.py`

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/urls.py` (NUEVO)
```python
from django.urls import path
from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
)

urlpatterns = [
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]
```

**Registrar en**: `/home/rubenmaestre/pcfutsal.es/backend/administracion/urls.py`
```python
path("api/jugadores/", include("jugadores.urls")),
```

### 1.2 Crear Serializers

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/serializers.py` (NUEVO)

Serializers necesarios:
- `JugadorSerializer`: Datos básicos del jugador
- `JugadorEnClubTemporadaSerializer`: Ya existe en `clubes/serializers.py`, reutilizar o mover
- `ValoracionJugadorSerializer`: Para mostrar atributos FIFA
- `HistorialJugadorSerializer`: Para historial consolidado

### 1.3 Crear Views

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/views.py` (ACTUALIZAR)

#### 1.3.1 `GET /api/jugadores/detalle/?jugador_id=XX`
**Descripción**: Detalle básico del jugador
**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "escudo_url": "string",
    "slug": "string"
  } | null,
  "temporada_actual": {
    "id": number,
    "nombre": "string"
  } | null,
  "dorsal_actual": "string" | null
}
```

#### 1.3.2 `GET /api/jugadores/full/?jugador_id=XX&temporada_id=YY&include=valoraciones,historial,partidos,stats`
**Descripción**: Ficha completa del jugador (similar a `/api/clubes/full/`)
**Parámetros**:
- `jugador_id` (requerido): ID del jugador
- `temporada_id` (opcional): Para filtrar datos de una temporada específica
- `include` (opcional, CSV): `valoraciones`, `historial`, `partidos`, `stats`, `distintivos`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Distintivos (si `include=distintivos` y existe modelo)

#### 1.3.3 `GET /api/jugadores/historial/?jugador_id=XX`
**Descripción**: Historial completo del jugador (consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`)
**Retorna**:
```json
{
  "jugador_id": number,
  "jugador_nombre": "string",
  "historico": [
    {
      "temporada": "string",
      "temporada_id": number | null,
      "competicion": "string",
      "competicion_id": number | null,
      "grupo": "string",
      "grupo_id": number | null,
      "club": "string",
      "club_id": number | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean  // true si viene de HistorialJugadorScraped
    }
  ]
}
```

#### 1.3.4 `GET /api/jugadores/valoraciones/?jugador_id=XX&temporada_id=YY`
**Descripción**: Valoraciones FIFA del jugador
**Retorna**:
```json
{
  "jugador_id": number,
  "temporada": {
    "id": number,
    "nombre": "string"
  } | null,
  "valoracion": {
    "ataque": number,
    "defensa": number,
    "pase": number,
    "regate": number,
    "potencia": number,
    "intensidad": number,
    "vision": number,
    "regularidad": number,
    "carisma": number,
    "media_global": number
  } | null,
  "total_votos": number,
  "ultima_actualizacion": "YYYY-MM-DDTHH:mm:ssZ" | null
}
```

#### 1.3.5 `GET /api/jugadores/partidos/?jugador_id=XX&temporada_id=YY&grupo_id=ZZ&limit=NN`
**Descripción**: Partidos del jugador con estadísticas
**Retorna**:
```json
{
  "jugador_id": number,
  "filtros": {
    "temporada_id": number | null,
    "grupo_id": number | null
  },
  "partidos": [
    {
      "partido_id": number,
      "fecha": "YYYY-MM-DD",
      "jornada": number,
      "local": "string",
      "local_id": number,
      "visitante": "string",
      "visitante_id": number,
      "goles_local": number,
      "goles_visitante": number,
      "goles_jugador": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "titular": boolean,
      "mvp": boolean
    }
  ],
  "totales": {
    "partidos_jugados": number,
    "goles": number,
    "tarjetas_amarillas": number,
    "tarjetas_rojas": number,
    "partidos_titular": number,
    "mvps": number
  }
}
```

### 1.4 Verificar modelo de Distintivos

**Tarea**: Revisar si existe modelo `Distintivo` y `DistintivoAsignado` en alguna app (probablemente `destacados` o `valoraciones`)

Si existe:
- Crear endpoint `GET /api/jugadores/distintivos/?jugador_id=XX`
- Retornar lista de distintivos ganados

Si no existe:
- Documentar como "pendiente de implementación"

---

## 🎯 FASE 2 — FRONTEND: Estructura de Páginas

### 2.1 Crear ruta dinámica

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx` (NUEVO)

**Estructura**:
- Server Component que obtiene `jugador_id` de params
- Fetch del diccionario de idiomas
- Fetch de datos del jugador (`/api/jugadores/full/`)
- Generación de metadata SEO dinámica
- Render del Client Component `JugadorDetailClient`

### 2.2 Crear Client Component principal

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/JugadorDetailClient.tsx` (NUEVO)

**Secciones**:
1. **Header del jugador**: Foto, nombre, apodo, posición, edad, club actual (con enlace)
2. **Tarjeta FIFA**: Media global + atributos visuales (tipo carta FIFA)
3. **Estadísticas actuales**: Partidos, goles, tarjetas, dorsal
4. **Historial**: Timeline de temporadas y clubes
5. **Partidos recientes**: Lista de últimos partidos con estadísticas
6. **Distintivos**: Badges ganados (si existen)
7. **Botones de acción**: "Votar" y "¿Eres tú? Verifica el perfil"

### 2.3 Crear componentes reutilizables

#### 2.3.1 Tarjeta FIFA del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorFIFACard.tsx` (NUEVO)

**Props**:
- `jugador`: Datos básicos
- `valoracion`: Atributos FIFA
- `club`: Club actual (opcional)

**Diseño**: Similar a las tarjetas FIFA existentes en rankings, pero más grande y detallada

#### 2.3.2 Historial del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorHistorial.tsx` (NUEVO)

**Props**:
- `historial`: Array de temporadas
- `lang`: Idioma actual

**Diseño**: Timeline vertical o cards horizontales con:
- Temporada
- Competición/Grupo
- Club (con enlace)
- Estadísticas básicas (goles, partidos)

#### 2.3.3 Estadísticas del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorStats.tsx` (NUEVO)

**Props**:
- `stats`: Estadísticas actuales
- `partidos`: Array de partidos recientes

**Diseño**: Tabla o cards con estadísticas detalladas

### 2.4 Crear Hook personalizado

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/hooks/useJugadorFull.ts` (NUEVO)

**Patrón**: Similar a `useClubFull`
- `use client`
- Manejo de estado: `data`, `loading`, `error`
- `useEffect` con cleanup
- URL relativa en cliente
- Cache: `no-store`

**Uso**:
```typescript
const { data, loading, error, refetch } = useJugadorFull({
  jugadorId: number,
  temporadaId?: number,
  include?: string[]
});
```

---

## 🎯 FASE 3 — Integración y Enlaces

### 3.1 Enlaces desde Rankings

**Archivos a actualizar**:
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/mvp/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/goleadores/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/sanciones/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/tarjetas/page.tsx`
- Componentes de rankings globales

**Cambio**: Hacer clicables los nombres/fotos de jugadores → `/es/jugadores/[id]`

### 3.2 Enlaces desde Plantillas de Clubes

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/clubes/[id]/ClubDetailClient.tsx`

**Cambio**: En la sección de plantilla, hacer clicables los jugadores → `/es/jugadores/[id]`

### 3.3 Enlaces desde Home (Jugador de la Jornada)

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/GlobalMVPCard.tsx` (o similar)

**Cambio**: Hacer clicable el jugador destacado → `/es/jugadores/[id]`

### 3.4 Enlaces desde Partidos

**Tarea**: Si hay componentes que muestran goleadores o eventos de partidos, añadir enlaces a perfiles de jugadores

---

## 🎯 FASE 4 — Traducciones y SEO

### 4.1 Añadir claves JSON

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/i18n/es.json` (y todos los idiomas)

**Nuevas secciones**:
```json
{
  "jugador": {
    "page_title": "Perfil de {nombre}",
    "media_global": "Media Global",
    "atributos": {
      "ataque": "Ataque",
      "defensa": "Defensa",
      "pase": "Pase",
      "regate": "Regate",
      "potencia": "Potencia",
      "intensidad": "Intensidad",
      "vision": "Visión",
      "regularidad": "Regularidad",
      "carisma": "Carisma"
    },
    "estadisticas": {
      "titulo": "Estadísticas",
      "partidos_jugados": "Partidos jugados",
      "goles": "Goles",
      "tarjetas_amarillas": "Tarjetas amarillas",
      "tarjetas_rojas": "Tarjetas rojas",
      "dorsal": "Dorsal"
    },
    "historial": {
      "titulo": "Historial",
      "temporada": "Temporada",
      "competicion": "Competición",
      "club": "Club"
    },
    "partidos": {
      "titulo": "Partidos",
      "recientes": "Partidos recientes"
    },
    "botones": {
      "votar": "Votar",
      "verificar_perfil": "¿Eres tú? Verifica el perfil"
    },
    "sin_datos": "No hay datos disponibles para este jugador"
  }
}
```

### 4.2 SEO Metadata

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx`

**Implementar**:
- `generateMetadata` dinámico con nombre del jugador
- Usar `dict.seo.jugador.title` y `dict.seo.jugador.description` con `replaceTemplate`
- Open Graph con foto del jugador
- Schema.org para `Person` y `SportsPerson`

**Añadir a `es.json`**:
```json
{
  "seo": {
    "jugador": {
      "title": "Perfil de {nombre} - PC FUTSAL",
      "description": "Ficha completa de {nombre} con estadísticas, valoraciones FIFA, historial y más en PC FUTSAL."
    }
  }
}
```

---

## 🎯 FASE 5 — Funcionalidades Adicionales (Opcional)

### 5.1 Sistema de Votación

**Backend**: Endpoint `POST /api/jugadores/votar/`
- Validar usuario autenticado
- Guardar voto en `VotoValoracionJugador`
- Recalcular `ValoracionJugador` agregada

**Frontend**: Modal o página de votación
- Formulario con sliders para cada atributo
- Mostrar peso del voto según rol del usuario
- Confirmación y feedback

### 5.2 Verificación de Perfil

**Backend**: Endpoint `POST /api/jugadores/solicitar-verificacion/`
- Crear `SolicitudVerificacion` (si existe modelo)
- Enviar email de confirmación

**Frontend**: Formulario de solicitud
- Campos: nombre, email, equipo actual, posición, dorsal
- Enlace al perfil actual
- Mensaje de confirmación

### 5.3 Comparación de Jugadores

**Backend**: Endpoint `GET /api/jugadores/compare/?jugador_id_1=XX&jugador_id_2=YY`
- Comparar atributos FIFA
- Comparar estadísticas
- Comparar historial

**Frontend**: Página de comparación
- Side-by-side de dos jugadores
- Gráficos comparativos

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Backend
- [x] Crear `jugadores/urls.py` ✅
- [x] Registrar en `administracion/urls.py` ✅
- [x] Crear `jugadores/serializers.py` ✅
- [x] Implementar `JugadorDetalleView` ✅
- [x] Implementar `JugadorFullView` ✅
- [x] Implementar `JugadorHistorialView` ✅
- [x] Implementar `JugadorValoracionesView` ✅
- [x] Implementar `JugadorPartidosView` ✅
- [ ] Verificar modelo de Distintivos
- [ ] (Opcional) Implementar endpoint de votación
- [ ] (Opcional) Implementar endpoint de verificación

### Frontend
- [x] Crear ruta `/app/[lang]/jugadores/[id]/page.tsx` ✅
- [x] Crear `JugadorDetailClient.tsx` ✅
- [ ] Crear `JugadorFIFACard.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorHistorial.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorStats.tsx` (opcional - funcionalidad integrada)
- [x] Crear hook `useJugadorFull.ts` ✅
- [ ] Añadir enlaces desde rankings
- [ ] Añadir enlaces desde plantillas de clubes
- [ ] Añadir enlaces desde home
- [x] Añadir traducciones en todos los idiomas ✅
- [x] Implementar SEO metadata ✅
- [ ] (Opcional) Implementar modal de votación
- [ ] (Opcional) Implementar formulario de verificación

### Testing
- [ ] Probar endpoints con jugadores existentes
- [ ] Probar con jugadores sin datos completos
- [ ] Probar enlaces desde diferentes páginas
- [ ] Verificar SEO en diferentes idiomas
- [ ] Verificar responsive design

---

## 🚀 ORDEN DE EJECUCIÓN RECOMENDADO

1. **FASE 1** (Backend): Crear endpoints básicos
2. **FASE 2.1-2.2** (Frontend): Crear página básica con datos principales
3. **FASE 2.3** (Frontend): Crear componentes visuales
4. **FASE 3** (Frontend): Añadir enlaces desde otras páginas
5. **FASE 4** (Frontend): Añadir traducciones y SEO
6. **FASE 5** (Opcional): Funcionalidades avanzadas

---

## 📚 REFERENCIAS

- `PROJECT_VISION.md`: Sección "4. Perfil de jugador" (líneas 76-97)
- `DOCUMENTACION/APIS.md`: Estructura de endpoints existentes
- `backend/jugadores/models.py`: Modelos de jugadores
- `backend/valoraciones/models.py`: Modelos de valoraciones
- `backend/clubes/views.py`: Ejemplo de implementación de `/api/clubes/full/`

---

**Última actualización**: 2025-11-25
**Estado**: FASE 1 COMPLETADA ✅ — FASE 2 EN PROGRESO ✅
- Backend: Completo y listo para testing
- Frontend: Página básica funcional, hook creado, traducciones completas, SEO implementado
- Pendiente: FASE 3 (enlaces desde otras páginas) y componentes auxiliares opcionales



## 📋 RESUMEN EJECUTIVO

Implementar la página de perfil de jugador, el "corazón de la marca" según PROJECT_VISION.md. Esta página mostrará:
- Media global tipo FIFA
- Atributos detallados (regate, intensidad, ataque, defensa, pase, potencia, visión, regularidad, carisma)
- Historial por temporadas
- Estadísticas actuales
- Distintivos ganados
- Enlaces al club actual
- Botones de acción: "Votar" y "¿Eres tú? Verifica el perfil"

---

## 🔍 ANÁLISIS DE DATOS DISPONIBLES

### ✅ Datos que YA tenemos en el backend:

#### 1. **Modelos de Jugadores** (`jugadores/models.py`):
- `Jugador`: Identidad permanente
  - `nombre`, `apodo`
  - `fecha_nacimiento`, `edad_estimacion`
  - `posicion_principal` (portero, cierre, ala, pivot, universal)
  - `foto_url`
  - `informe_scout` (texto descriptivo)
  - `identificador_federacion` (ID único del scraping)
  - `activo`

- `JugadorEnClubTemporada`: Estadísticas por temporada
  - `jugador` (FK)
  - `club` (FK)
  - `temporada` (FK)
  - `dorsal`
  - `partidos_jugados`, `goles`
  - `tarjetas_amarillas`, `tarjetas_rojas`
  - `convocados`, `titular`, `suplente`

- `HistorialJugadorScraped`: Historial bruto del scraping
  - `temporada_texto`, `competicion_texto`, `equipo_texto`

#### 2. **Valoraciones FIFA** (`valoraciones/models.py`):
- `ValoracionJugador`: Nota oficial agregada por temporada
  - `jugador` (FK)
  - `temporada` (FK)
  - Atributos: `ataque`, `defensa`, `pase`, `regate`, `potencia`, `intensidad`, `vision`, `regularidad`, `carisma`
  - `media_global` (calculada)

- `VotoValoracionJugador`: Votos individuales
  - `jugador`, `usuario`, `temporada`
  - `atributo`, `valor` (0-100)
  - `peso_aplicado`

#### 3. **Datos del Scraping** (`data_clean/jugadores/`):
Estructura JSON scrapeada:
```json
{
  "jugador_id": 100738,
  "id_temp": 18,
  "datos_generales": {
    "nombre_completo": "VIDAL VIDAL SOLA, JAVIER",
    "edad": 21,
    "equipo_actual": "C.F.S. Ribeco Castalla 'A'"
  },
  "estadisticas": {
    "convocados": 0,
    "titular": 0,
    "suplente": 0,
    "jugados": 0,
    "total_goles": 0,
    "media_goles": 0.0,
    "amarillas": 0,
    "rojas": 0
  },
  "historico": [
    {
      "temporada": "2024-2025",
      "competicion": "1ª. Regional Futsal",
      "equipo": "C.F.S. Ribeco Castalla"
    }
  ],
  "header": {
    "nombre_header": "...",
    "competicion_header": "...",
    "dorsal_header": null,
    "escudo_equipo_url": "..."
  },
  "foto": {
    "source": "data:image/png;base64,...",
    "is_base64": true
  }
}
```

#### 4. **Datos en Rankings Actuales**:
Los endpoints de valoraciones ya devuelven información de jugadores:
- `jugador_id`, `nombre`, `apodo`
- `foto`
- `club_id`, `club_nombre`, `club_escudo`
- `puntos_acumulados`, `puntos_jornada`
- `posicion` (en ranking)

### ❌ Datos que FALTAN o necesitan endpoints:

1. **Endpoint específico de jugador**: No existe `/api/jugadores/detalle/` o similar
2. **Endpoint de historial completo**: Necesitamos consolidar `HistorialJugadorScraped` + `JugadorEnClubTemporada`
3. **Endpoint de valoraciones del jugador**: Necesitamos obtener `ValoracionJugador` por jugador
4. **Endpoint de partidos del jugador**: Para mostrar estadísticas detalladas
5. **Distintivos**: Modelo no revisado aún (puede existir en `destacados` o similar)

---

## 🎯 FASE 1 — BACKEND: Endpoints de Jugadores

### 1.1 Crear app `jugadores/urls.py` y registrar en `administracion/urls.py`

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/urls.py` (NUEVO)
```python
from django.urls import path
from .views import (
    JugadorDetalleView,
    JugadorFullView,
    JugadorHistorialView,
    JugadorValoracionesView,
    JugadorPartidosView,
)

urlpatterns = [
    path("detalle/", JugadorDetalleView.as_view(), name="jugador-detalle"),
    path("full/", JugadorFullView.as_view(), name="jugador-full"),
    path("historial/", JugadorHistorialView.as_view(), name="jugador-historial"),
    path("valoraciones/", JugadorValoracionesView.as_view(), name="jugador-valoraciones"),
    path("partidos/", JugadorPartidosView.as_view(), name="jugador-partidos"),
]
```

**Registrar en**: `/home/rubenmaestre/pcfutsal.es/backend/administracion/urls.py`
```python
path("api/jugadores/", include("jugadores.urls")),
```

### 1.2 Crear Serializers

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/serializers.py` (NUEVO)

Serializers necesarios:
- `JugadorSerializer`: Datos básicos del jugador
- `JugadorEnClubTemporadaSerializer`: Ya existe en `clubes/serializers.py`, reutilizar o mover
- `ValoracionJugadorSerializer`: Para mostrar atributos FIFA
- `HistorialJugadorSerializer`: Para historial consolidado

### 1.3 Crear Views

**Archivo**: `/home/rubenmaestre/pcfutsal.es/backend/jugadores/views.py` (ACTUALIZAR)

#### 1.3.1 `GET /api/jugadores/detalle/?jugador_id=XX`
**Descripción**: Detalle básico del jugador
**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "escudo_url": "string",
    "slug": "string"
  } | null,
  "temporada_actual": {
    "id": number,
    "nombre": "string"
  } | null,
  "dorsal_actual": "string" | null
}
```

#### 1.3.2 `GET /api/jugadores/full/?jugador_id=XX&temporada_id=YY&include=valoraciones,historial,partidos,stats`
**Descripción**: Ficha completa del jugador (similar a `/api/clubes/full/`)
**Parámetros**:
- `jugador_id` (requerido): ID del jugador
- `temporada_id` (opcional): Para filtrar datos de una temporada específica
- `include` (opcional, CSV): `valoraciones`, `historial`, `partidos`, `stats`, `distintivos`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Distintivos (si `include=distintivos` y existe modelo)

#### 1.3.3 `GET /api/jugadores/historial/?jugador_id=XX`
**Descripción**: Historial completo del jugador (consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`)
**Retorna**:
```json
{
  "jugador_id": number,
  "jugador_nombre": "string",
  "historico": [
    {
      "temporada": "string",
      "temporada_id": number | null,
      "competicion": "string",
      "competicion_id": number | null,
      "grupo": "string",
      "grupo_id": number | null,
      "club": "string",
      "club_id": number | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean  // true si viene de HistorialJugadorScraped
    }
  ]
}
```

#### 1.3.4 `GET /api/jugadores/valoraciones/?jugador_id=XX&temporada_id=YY`
**Descripción**: Valoraciones FIFA del jugador
**Retorna**:
```json
{
  "jugador_id": number,
  "temporada": {
    "id": number,
    "nombre": "string"
  } | null,
  "valoracion": {
    "ataque": number,
    "defensa": number,
    "pase": number,
    "regate": number,
    "potencia": number,
    "intensidad": number,
    "vision": number,
    "regularidad": number,
    "carisma": number,
    "media_global": number
  } | null,
  "total_votos": number,
  "ultima_actualizacion": "YYYY-MM-DDTHH:mm:ssZ" | null
}
```

#### 1.3.5 `GET /api/jugadores/partidos/?jugador_id=XX&temporada_id=YY&grupo_id=ZZ&limit=NN`
**Descripción**: Partidos del jugador con estadísticas
**Retorna**:
```json
{
  "jugador_id": number,
  "filtros": {
    "temporada_id": number | null,
    "grupo_id": number | null
  },
  "partidos": [
    {
      "partido_id": number,
      "fecha": "YYYY-MM-DD",
      "jornada": number,
      "local": "string",
      "local_id": number,
      "visitante": "string",
      "visitante_id": number,
      "goles_local": number,
      "goles_visitante": number,
      "goles_jugador": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "titular": boolean,
      "mvp": boolean
    }
  ],
  "totales": {
    "partidos_jugados": number,
    "goles": number,
    "tarjetas_amarillas": number,
    "tarjetas_rojas": number,
    "partidos_titular": number,
    "mvps": number
  }
}
```

### 1.4 Verificar modelo de Distintivos

**Tarea**: Revisar si existe modelo `Distintivo` y `DistintivoAsignado` en alguna app (probablemente `destacados` o `valoraciones`)

Si existe:
- Crear endpoint `GET /api/jugadores/distintivos/?jugador_id=XX`
- Retornar lista de distintivos ganados

Si no existe:
- Documentar como "pendiente de implementación"

---

## 🎯 FASE 2 — FRONTEND: Estructura de Páginas

### 2.1 Crear ruta dinámica

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx` (NUEVO)

**Estructura**:
- Server Component que obtiene `jugador_id` de params
- Fetch del diccionario de idiomas
- Fetch de datos del jugador (`/api/jugadores/full/`)
- Generación de metadata SEO dinámica
- Render del Client Component `JugadorDetailClient`

### 2.2 Crear Client Component principal

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/JugadorDetailClient.tsx` (NUEVO)

**Secciones**:
1. **Header del jugador**: Foto, nombre, apodo, posición, edad, club actual (con enlace)
2. **Tarjeta FIFA**: Media global + atributos visuales (tipo carta FIFA)
3. **Estadísticas actuales**: Partidos, goles, tarjetas, dorsal
4. **Historial**: Timeline de temporadas y clubes
5. **Partidos recientes**: Lista de últimos partidos con estadísticas
6. **Distintivos**: Badges ganados (si existen)
7. **Botones de acción**: "Votar" y "¿Eres tú? Verifica el perfil"

### 2.3 Crear componentes reutilizables

#### 2.3.1 Tarjeta FIFA del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorFIFACard.tsx` (NUEVO)

**Props**:
- `jugador`: Datos básicos
- `valoracion`: Atributos FIFA
- `club`: Club actual (opcional)

**Diseño**: Similar a las tarjetas FIFA existentes en rankings, pero más grande y detallada

#### 2.3.2 Historial del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorHistorial.tsx` (NUEVO)

**Props**:
- `historial`: Array de temporadas
- `lang`: Idioma actual

**Diseño**: Timeline vertical o cards horizontales con:
- Temporada
- Competición/Grupo
- Club (con enlace)
- Estadísticas básicas (goles, partidos)

#### 2.3.3 Estadísticas del Jugador
**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/JugadorStats.tsx` (NUEVO)

**Props**:
- `stats`: Estadísticas actuales
- `partidos`: Array de partidos recientes

**Diseño**: Tabla o cards con estadísticas detalladas

### 2.4 Crear Hook personalizado

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/hooks/useJugadorFull.ts` (NUEVO)

**Patrón**: Similar a `useClubFull`
- `use client`
- Manejo de estado: `data`, `loading`, `error`
- `useEffect` con cleanup
- URL relativa en cliente
- Cache: `no-store`

**Uso**:
```typescript
const { data, loading, error, refetch } = useJugadorFull({
  jugadorId: number,
  temporadaId?: number,
  include?: string[]
});
```

---

## 🎯 FASE 3 — Integración y Enlaces

### 3.1 Enlaces desde Rankings

**Archivos a actualizar**:
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/mvp/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/goleadores/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/sanciones/page.tsx`
- `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/rankings/tarjetas/page.tsx`
- Componentes de rankings globales

**Cambio**: Hacer clicables los nombres/fotos de jugadores → `/es/jugadores/[id]`

### 3.2 Enlaces desde Plantillas de Clubes

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/clubes/[id]/ClubDetailClient.tsx`

**Cambio**: En la sección de plantilla, hacer clicables los jugadores → `/es/jugadores/[id]`

### 3.3 Enlaces desde Home (Jugador de la Jornada)

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/components/GlobalMVPCard.tsx` (o similar)

**Cambio**: Hacer clicable el jugador destacado → `/es/jugadores/[id]`

### 3.4 Enlaces desde Partidos

**Tarea**: Si hay componentes que muestran goleadores o eventos de partidos, añadir enlaces a perfiles de jugadores

---

## 🎯 FASE 4 — Traducciones y SEO

### 4.1 Añadir claves JSON

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/i18n/es.json` (y todos los idiomas)

**Nuevas secciones**:
```json
{
  "jugador": {
    "page_title": "Perfil de {nombre}",
    "media_global": "Media Global",
    "atributos": {
      "ataque": "Ataque",
      "defensa": "Defensa",
      "pase": "Pase",
      "regate": "Regate",
      "potencia": "Potencia",
      "intensidad": "Intensidad",
      "vision": "Visión",
      "regularidad": "Regularidad",
      "carisma": "Carisma"
    },
    "estadisticas": {
      "titulo": "Estadísticas",
      "partidos_jugados": "Partidos jugados",
      "goles": "Goles",
      "tarjetas_amarillas": "Tarjetas amarillas",
      "tarjetas_rojas": "Tarjetas rojas",
      "dorsal": "Dorsal"
    },
    "historial": {
      "titulo": "Historial",
      "temporada": "Temporada",
      "competicion": "Competición",
      "club": "Club"
    },
    "partidos": {
      "titulo": "Partidos",
      "recientes": "Partidos recientes"
    },
    "botones": {
      "votar": "Votar",
      "verificar_perfil": "¿Eres tú? Verifica el perfil"
    },
    "sin_datos": "No hay datos disponibles para este jugador"
  }
}
```

### 4.2 SEO Metadata

**Archivo**: `/home/rubenmaestre/pcfutsal.es/frontend/app/[lang]/jugadores/[id]/page.tsx`

**Implementar**:
- `generateMetadata` dinámico con nombre del jugador
- Usar `dict.seo.jugador.title` y `dict.seo.jugador.description` con `replaceTemplate`
- Open Graph con foto del jugador
- Schema.org para `Person` y `SportsPerson`

**Añadir a `es.json`**:
```json
{
  "seo": {
    "jugador": {
      "title": "Perfil de {nombre} - PC FUTSAL",
      "description": "Ficha completa de {nombre} con estadísticas, valoraciones FIFA, historial y más en PC FUTSAL."
    }
  }
}
```

---

## 🎯 FASE 5 — Funcionalidades Adicionales (Opcional)

### 5.1 Sistema de Votación

**Backend**: Endpoint `POST /api/jugadores/votar/`
- Validar usuario autenticado
- Guardar voto en `VotoValoracionJugador`
- Recalcular `ValoracionJugador` agregada

**Frontend**: Modal o página de votación
- Formulario con sliders para cada atributo
- Mostrar peso del voto según rol del usuario
- Confirmación y feedback

### 5.2 Verificación de Perfil

**Backend**: Endpoint `POST /api/jugadores/solicitar-verificacion/`
- Crear `SolicitudVerificacion` (si existe modelo)
- Enviar email de confirmación

**Frontend**: Formulario de solicitud
- Campos: nombre, email, equipo actual, posición, dorsal
- Enlace al perfil actual
- Mensaje de confirmación

### 5.3 Comparación de Jugadores

**Backend**: Endpoint `GET /api/jugadores/compare/?jugador_id_1=XX&jugador_id_2=YY`
- Comparar atributos FIFA
- Comparar estadísticas
- Comparar historial

**Frontend**: Página de comparación
- Side-by-side de dos jugadores
- Gráficos comparativos

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Backend
- [x] Crear `jugadores/urls.py` ✅
- [x] Registrar en `administracion/urls.py` ✅
- [x] Crear `jugadores/serializers.py` ✅
- [x] Implementar `JugadorDetalleView` ✅
- [x] Implementar `JugadorFullView` ✅
- [x] Implementar `JugadorHistorialView` ✅
- [x] Implementar `JugadorValoracionesView` ✅
- [x] Implementar `JugadorPartidosView` ✅
- [ ] Verificar modelo de Distintivos
- [ ] (Opcional) Implementar endpoint de votación
- [ ] (Opcional) Implementar endpoint de verificación

### Frontend
- [x] Crear ruta `/app/[lang]/jugadores/[id]/page.tsx` ✅
- [x] Crear `JugadorDetailClient.tsx` ✅
- [ ] Crear `JugadorFIFACard.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorHistorial.tsx` (opcional - funcionalidad integrada)
- [ ] Crear `JugadorStats.tsx` (opcional - funcionalidad integrada)
- [x] Crear hook `useJugadorFull.ts` ✅
- [ ] Añadir enlaces desde rankings
- [ ] Añadir enlaces desde plantillas de clubes
- [ ] Añadir enlaces desde home
- [x] Añadir traducciones en todos los idiomas ✅
- [x] Implementar SEO metadata ✅
- [ ] (Opcional) Implementar modal de votación
- [ ] (Opcional) Implementar formulario de verificación

### Testing
- [ ] Probar endpoints con jugadores existentes
- [ ] Probar con jugadores sin datos completos
- [ ] Probar enlaces desde diferentes páginas
- [ ] Verificar SEO en diferentes idiomas
- [ ] Verificar responsive design

---

## 🚀 ORDEN DE EJECUCIÓN RECOMENDADO

1. **FASE 1** (Backend): Crear endpoints básicos
2. **FASE 2.1-2.2** (Frontend): Crear página básica con datos principales
3. **FASE 2.3** (Frontend): Crear componentes visuales
4. **FASE 3** (Frontend): Añadir enlaces desde otras páginas
5. **FASE 4** (Frontend): Añadir traducciones y SEO
6. **FASE 5** (Opcional): Funcionalidades avanzadas

---

## 📚 REFERENCIAS

- `PROJECT_VISION.md`: Sección "4. Perfil de jugador" (líneas 76-97)
- `DOCUMENTACION/APIS.md`: Estructura de endpoints existentes
- `backend/jugadores/models.py`: Modelos de jugadores
- `backend/valoraciones/models.py`: Modelos de valoraciones
- `backend/clubes/views.py`: Ejemplo de implementación de `/api/clubes/full/`

---

**Última actualización**: 2025-11-25
**Estado**: FASE 1 COMPLETADA ✅ — FASE 2 EN PROGRESO ✅
- Backend: Completo y listo para testing
- Frontend: Página básica funcional, hook creado, traducciones completas, SEO implementado
- Pendiente: FASE 3 (enlaces desde otras páginas) y componentes auxiliares opcionales


