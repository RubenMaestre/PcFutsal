# ESTRATEGIA SEO — PC FUTSAL

**Fecha de creación:** 2025-11-24  
**Última actualización:** 2025-11-25  
**Estado:** ✅ Implementado con soporte multilenguaje

---

## 🌍 SOPORTE MULTILENGUAJE

**Idiomas soportados:** Español (es), Inglés (en), Valenciano (val), Francés (fr), Alemán (de), Italiano (it), Portugués (pt)

**Implementación:**
- ✅ Todos los meta titles y descriptions están traducidos en `/frontend/i18n/[lang].json` bajo la sección `seo`
- ✅ Las páginas usan `generateMetadataWithAlternates()` con traducciones dinámicas según el idioma
- ✅ Open Graph y Twitter Cards se generan automáticamente en el idioma correspondiente
- ✅ Hreflang configurado para todos los idiomas en todas las páginas
- ✅ URLs canónicas específicas por idioma

**Estructura de traducciones SEO:**
```json
{
  "seo": {
    "default": {
      "og_title": "...",
      "og_description": "...",
      "site_name": "PC FUTSAL"
    },
    "home": { "title": "...", "description": "..." },
    "competicion": { "title_template": "...", "description_template": "..." },
    "club": { "title_template": "...", "description_template": "..." },
    "rankings": { ... },
    "mvp": { ... },
    "clasificacion": { ... },
    "clubes": { ... }
  }
}
```

**Archivos modificados:**
- `frontend/lib/seo.ts` - Actualizado para usar traducciones dinámicas
- `frontend/i18n/*.json` - Sección `seo` añadida en todos los idiomas
- Todas las páginas con `generateMetadata` - Actualizadas para usar traducciones

---

## 1. REDEFINICIÓN DEL POSICIONAMIENTO SEO

### ❌ Posicionamiento anterior (obsoleto)
- "Tercera División de Alicante"
- Web local/regional
- Enfoque limitado geográficamente

### ✅ Nuevo posicionamiento SEO

**PC FUTSAL es:**
> **La plataforma de datos del fútbol sala amateur en España**

**Con funcionalidades:**
- ✅ Resultados en tiempo real
- ✅ Clasificaciones completas
- ✅ Perfiles de jugadores
- ✅ Perfiles de clubs
- ✅ Valoraciones tipo FIFA
- ✅ Fantasy semanal
- ✅ Múltiples grupos y categorías
- ✅ Rankings globales
- ✅ Estadísticas avanzadas

### Impacto en SEO

**Antes:**
- Google lo veía como web local
- Búsquedas limitadas a "tercera división alicante"

**Ahora:**
- Google lo verá como plataforma nacional
- Clasificará por miles de búsquedas:
  - `fútbol sala + [zona]` (ej: "fútbol sala valencia", "fútbol sala madrid")
  - `fútbol sala + [categoría]` (ej: "tercera división nacional", "segunda división")
  - `fútbol sala + [equipo]` (ej: "CD Futbol Sala X", "Club Y")
  - `fútbol sala + [jugador]` (ej: "Juan Pérez fútbol sala")
  - `clasificación fútbol sala [categoría]`
  - `ranking jugadores fútbol sala`
  - `fantasy fútbol sala`

---

## 2. ARQUITECTURA SEO — ESTRUCTURA DE URLs

### Mapeo de rutas actuales

**Rutas existentes identificadas:**
```
/[lang]/                          → Home (página principal)
/[lang]/clubes                    → Lista de clubes
/[lang]/clubes/[id]               → Detalle de club
/[lang]/competicion/[slug]/[grupo] → Página de competición/grupo
/[lang]/clasificacion              → Clasificaciones
/[lang]/clasificacion/[slug]/[grupo] → Clasificación específica
/[lang]/competicion/[slug]/[grupo]/clasificacion → Clasificación dentro de competición
/[lang]/mvp                        → MVP general
/[lang]/competicion/[slug]/[grupo]/mvp → MVP de competición
/[lang]/rankings/equipos           → Ranking global de equipos
/[lang]/rankings/mvp               → Ranking global MVP
```

### Arquitectura SEO propuesta

#### A. Página global de ligas/competiciones
**URL:** `/[lang]/ligas` o `/[lang]/competiciones`

**Propósito:**
- Lista todas las competiciones disponibles
- Agrupa por comunidades autónomas
- Agrupa por categorías (Nacional, Regional, etc.)

**Contenido SEO:**
- Título: "Competiciones de Fútbol Sala en España | PC FUTSAL"
- Descripción: "Descubre todas las competiciones de fútbol sala amateur en España. Clasificaciones, resultados, estadísticas y más."
- Keywords: competiciones fútbol sala, ligas fútbol sala españa, categorías fútbol sala

**Estado:** ⚠️ **NO EXISTE** — Necesita creación

---

#### B. Página de una competición
**URL actual:** `/[lang]/competicion/[competicionSlug]/[grupoSlug]`

**Ejemplo:** `/es/competicion/tercera-division-nacional/grupo-xv-2024-2025`

**Propósito:**
- Página dedicada a una competición específica
- Muestra información del grupo, clasificación, partidos, estadísticas

**Contenido SEO:**
- Título dinámico: "[Nombre Competición] - [Grupo] | PC FUTSAL"
- Descripción: "Clasificación, resultados y estadísticas de [Nombre Competición] - Grupo [X]. Sigue la temporada en tiempo real."
- Keywords: [nombre competición], [grupo], clasificación [competición]

**Estado:** ✅ **EXISTE** — Necesita optimización de metadata

---

#### C. Página de un grupo
**URL actual:** `/[lang]/competicion/[competicionSlug]/[grupoSlug]`

**Nota:** Actualmente está integrado con la página de competición. Podría separarse si es necesario.

**Estado:** ✅ **EXISTE** (integrado) — Evaluar si necesita separación

---

#### D. Página de un club
**URL actual:** `/[lang]/clubes/[id]`

**Ejemplo:** `/es/clubes/123` o idealmente `/es/clubes/cd-futbol-sala-x`

**Propósito:**
- Perfil completo del club
- Historial, jugadores, estadísticas, partidos

**Contenido SEO:**
- Título dinámico: "[Nombre Club] - Perfil y Estadísticas | PC FUTSAL"
- Descripción: "Perfil completo de [Nombre Club]. Jugadores, partidos, clasificación y estadísticas en PC FUTSAL."
- Keywords: [nombre club], [club] fútbol sala, jugadores [club]

**Mejora propuesta:**
- ⚠️ Cambiar de `/clubes/[id]` a `/clubes/[slug]` para mejor SEO
- Slug basado en nombre del club (ej: `cd-futbol-sala-x`)

**Estado:** ✅ **EXISTE** — Necesita optimización y posible cambio a slug

---

#### E. Página de un jugador
**URL actual:** ⚠️ **NO EXISTE**

**URL propuesta:** `/[lang]/jugador/[slug-jugador]`

**Ejemplo:** `/es/jugador/juan-perez-garcia`

**Propósito:**
- Perfil completo del jugador
- Estadísticas, valoraciones, partidos, goles, asistencias
- Historial de equipos

**Contenido SEO:**
- Título dinámico: "[Nombre Jugador] - Perfil y Estadísticas | PC FUTSAL"
- Descripción: "Perfil completo de [Nombre Jugador]. Estadísticas, goles, asistencias y valoraciones en PC FUTSAL."
- Keywords: [nombre jugador], [jugador] fútbol sala, estadísticas [jugador]

**Estado:** ⚠️ **NO EXISTE** — Necesita creación

---

#### F. Página de un partido
**URL actual:** ⚠️ **NO EXISTE** (probablemente solo en listados)

**URL propuesta:** `/[lang]/partido/[id]` o `/[lang]/partido/[slug]`

**Ejemplo:** `/es/partido/12345` o `/es/partido/cd-x-vs-cd-y-2024-11-24`

**Propósito:**
- Detalle completo del partido
- Resultado, estadísticas, jugadores destacados, MVP del partido

**Contenido SEO:**
- Título dinámico: "[Equipo A] vs [Equipo B] - [Fecha] | PC FUTSAL"
- Descripción: "Resultado y estadísticas del partido [Equipo A] vs [Equipo B] del [Fecha]. Goles, asistencias y más."
- Keywords: [equipo a] vs [equipo b], partido [fecha], resultado [equipo]

**Estado:** ⚠️ **NO EXISTE** — Necesita creación

---

#### G. Rankings globales
**URL actual:** 
- `/[lang]/rankings/equipos` ✅
- `/[lang]/rankings/mvp` ✅

**Propósito:**
- Rankings globales de equipos y jugadores
- Comparativas entre competiciones

**Contenido SEO:**
- Título: "Ranking Global de Equipos de Fútbol Sala | PC FUTSAL"
- Descripción: "Ranking global de los mejores equipos de fútbol sala amateur en España. Compara equipos de todas las competiciones."
- Keywords: ranking equipos fútbol sala, mejores equipos fútbol sala, clasificación global

**Estado:** ✅ **EXISTE** — Necesita optimización de metadata

---

## 3. PRIORIZACIÓN DE TRABAJO

### Fase 1: Fundamentos (Alta prioridad)
1. ✅ Redefinir posicionamiento SEO (este documento)
2. ✅ Mapear arquitectura actual (este documento)
3. ⏳ Crear documento de keywords y meta descriptions
4. ⏳ Implementar metadata dinámica en páginas existentes
5. ⏳ Crear sitemap.xml
6. ⏳ Optimizar robots.txt

### Fase 2: Contenido faltante (Media prioridad)
1. ⏳ Crear página `/ligas` o `/competiciones`
2. ⏳ Crear páginas de jugadores `/jugador/[slug]`
3. ⏳ Crear páginas de partidos `/partido/[id]`
4. ⏳ Migrar `/clubes/[id]` a `/clubes/[slug]`

### Fase 3: Optimización avanzada (Baja prioridad)
1. ⏳ Implementar schema.org markup
2. ⏳ Breadcrumbs estructurados
3. ⏳ Open Graph y Twitter Cards
4. ⏳ Canonical URLs
5. ⏳ Hreflang para multilenguaje

---

## 4. KEYWORDS PRINCIPALES

### Keywords primarias (alto volumen)
- fútbol sala españa
- fútbol sala amateur
- clasificación fútbol sala
- resultados fútbol sala
- ranking jugadores fútbol sala
- fantasy fútbol sala

### Keywords secundarias (medio volumen)
- tercera división nacional fútbol sala
- segunda división fútbol sala
- fútbol sala [comunidad autónoma]
- [nombre equipo] fútbol sala
- [nombre jugador] fútbol sala
- estadísticas fútbol sala

### Keywords long-tail (bajo volumen, alta conversión)
- clasificación tercera división nacional fútbol sala
- ranking mvp fútbol sala españa
- mejores jugadores fútbol sala [categoría]
- resultados [equipo] fútbol sala
- perfil [jugador] fútbol sala

---

## 5. META TITLES Y META DESCRIPTIONS

### A. Home (Página Principal)

**URL:** `/[lang]/` o `/[lang]/page`

**Meta Title:**
```
PC FUTSAL — Resultados, Estadísticas y Rankings de Fútbol Sala en España
```

**Meta Description:**
```
Resultados oficiales, clasificaciones, jugadores, clubes y rankings tipo FIFA del fútbol sala amateur en España. Datos actualizados y Fantasy semanal.
```

**Keywords principales:**
- fútbol sala españa
- resultados fútbol sala
- estadísticas fútbol sala
- rankings fútbol sala
- fantasy fútbol sala

---

### B. Página de Competiciones

**URL:** `/[lang]/ligas` o `/[lang]/competiciones` (a crear)

**Meta Title:**
```
Competiciones de Fútbol Sala — Temporadas y Grupos | PC FUTSAL
```

**Meta Description:**
```
Consulta todas las competiciones de fútbol sala amateur: categorías, grupos y temporadas disponibles en PC FUTSAL.
```

**Keywords principales:**
- competiciones fútbol sala
- ligas fútbol sala españa
- categorías fútbol sala
- temporadas fútbol sala

**Estado:** ⚠️ **Página a crear**

---

### C. Página de Grupo

**URL:** `/[lang]/competicion/[competicionSlug]/[grupoSlug]`

**Meta Title (dinámico):**
```
[Competición] · [Grupo] · [Temporada] — Resultados y Clasificación | PC FUTSAL
```

**Ejemplo:**
```
Tercera División Nacional · Grupo XV · 2024-2025 — Resultados y Clasificación | PC FUTSAL
```

**Meta Description (dinámico):**
```
Jornadas, resultados, clasificación, clubs, goleadores y ranking de jugadores del Grupo [X] de [competición] en [temporada].
```

**Ejemplo:**
```
Jornadas, resultados, clasificación, clubs, goleadores y ranking de jugadores del Grupo XV de Tercera División Nacional en 2024-2025.
```

**Keywords principales:**
- [nombre competición] [grupo]
- clasificación [competición] [grupo]
- resultados [competición] [grupo]
- [grupo] fútbol sala

**Estado:** ✅ **Existe** — Necesita implementación de metadata dinámica

---

### D. Ficha de Club

**URL:** `/[lang]/clubes/[id]` (actual) o `/[lang]/clubes/[slug]` (propuesto)

**Meta Title (dinámico):**
```
[Nombre del club] — Resultados, Plantilla y Estadísticas | PC FUTSAL
```

**Ejemplo:**
```
CD Futbol Sala X — Resultados, Plantilla y Estadísticas | PC FUTSAL
```

**Meta Description (dinámico):**
```
Plantilla completa, últimos resultados, clasificación, racha y estadísticas del [club].
```

**Ejemplo:**
```
Plantilla completa, últimos resultados, clasificación, racha y estadísticas del CD Futbol Sala X.
```

**Keywords principales:**
- [nombre club] fútbol sala
- [club] plantilla
- [club] resultados
- [club] estadísticas

**Estado:** ✅ **Existe** — Necesita implementación de metadata dinámica

---

### E. Ficha de Jugador

**URL:** `/[lang]/jugador/[slug-jugador]` (a crear)

**Meta Title (dinámico):**
```
[Jugador] — Estadísticas y Media Tipo FIFA | PC FUTSAL
```

**Ejemplo:**
```
Juan Pérez García — Estadísticas y Media Tipo FIFA | PC FUTSAL
```

**Meta Description (dinámico):**
```
Perfil completo de [nombre], media tipo FIFA, atributos, historial, goles y estadísticas por temporada.
```

**Ejemplo:**
```
Perfil completo de Juan Pérez García, media tipo FIFA, atributos, historial, goles y estadísticas por temporada.
```

**Keywords principales:**
- [nombre jugador] fútbol sala
- [jugador] estadísticas
- [jugador] media fifa
- perfil [jugador]

**Estado:** ⚠️ **Página a crear**

---

### F. Ficha de Partido

**URL:** `/[lang]/partido/[id]` o `/[lang]/partido/[slug]` (a crear)

**Meta Title (dinámico):**
```
[Local] vs [Visitante] — Jornada [X] | PC FUTSAL
```

**Ejemplo:**
```
CD Futbol Sala X vs CD Futbol Sala Y — Jornada 5 | PC FUTSAL
```

**Meta Description (dinámico):**
```
Resultado, goles, tarjetas y eventos del partido entre [local] y [visitante].
```

**Ejemplo:**
```
Resultado, goles, tarjetas y eventos del partido entre CD Futbol Sala X y CD Futbol Sala Y.
```

**Keywords principales:**
- [equipo local] vs [equipo visitante]
- partido [equipo local] [equipo visitante]
- resultado [equipo local] vs [equipo visitante]
- jornada [X] [competición]

**Estado:** ⚠️ **Página a crear**

---

### G. Rankings Globales

**URL:** `/[lang]/rankings/equipos` y `/[lang]/rankings/mvp`

#### Rankings de Equipos

**Meta Title:**
```
Ranking Global de Equipos — Mejores Equipos de Fútbol Sala | PC FUTSAL
```

**Meta Description:**
```
Ranking global de los mejores equipos de fútbol sala amateur en España. Compara equipos de todas las competiciones y categorías.
```

#### Rankings MVP

**Meta Title:**
```
Ranking Global MVP — Mejores Jugadores de Fútbol Sala | PC FUTSAL
```

**Meta Description:**
```
Ranking global de los mejores jugadores de fútbol sala amateur. Valoraciones tipo FIFA, goles, asistencias y estadísticas completas.
```

**Estado:** ✅ **Existe** — Necesita implementación de metadata

---

### H. Página MVP

**URL:** `/[lang]/mvp`

**Meta Title:**
```
Clasificación MVP — Mejores Jugadores por Jornada | PC FUTSAL
```

**Meta Description:**
```
Sistema de valoración tipo FIFA para jugadores de fútbol sala. Descubre los mejores jugadores de cada jornada y competición.
```

**Estado:** ✅ **Existe** — Necesita implementación de metadata

---

## 6. IMPLEMENTACIÓN TÉCNICA

### Variables dinámicas necesarias

Para implementar los meta titles y descriptions dinámicos, necesitaremos:

1. **Página de Grupo:**
   - `competicion.nombre`
   - `grupo.nombre` o `grupo.codigo`
   - `temporada.nombre` o `temporada.anio`

2. **Ficha de Club:**
   - `club.nombre`
   - `club.slug` (si se implementa)

3. **Ficha de Jugador:**
   - `jugador.nombre_completo`
   - `jugador.slug` (a crear)

4. **Ficha de Partido:**
   - `partido.equipo_local.nombre`
   - `partido.equipo_visitante.nombre`
   - `partido.jornada.numero`

### Formato de implementación (Next.js 15)

```typescript
// Ejemplo para página de grupo
export async function generateMetadata({ params }): Promise<Metadata> {
  const competicion = await getCompeticion(params.competicionSlug);
  const grupo = await getGrupo(params.grupoSlug);
  
  return {
    title: `${competicion.nombre} · ${grupo.nombre} · ${temporada.nombre} — Resultados y Clasificación | PC FUTSAL`,
    description: `Jornadas, resultados, clasificación, clubs, goleadores y ranking de jugadores del ${grupo.nombre} de ${competicion.nombre} en ${temporada.nombre}.`,
  };
}
```

---

## 7. ELEMENTOS TÉCNICOS OBLIGATORIOS

### A. Sitemap XML Jerárquico

**Estructura propuesta:**

```
sitemap-index.xml (principal)
├── sitemap-grupos.xml
├── sitemap-clubs.xml
├── sitemap-jugadores.xml
├── sitemap-partidos.xml
├── sitemap-estaticas.xml
└── sitemap-apis-publicas.xml (opcional, solo si sirven contenido estable)
```

#### sitemap-index.xml

**Ubicación:** `/sitemap.xml` o `/sitemap-index.xml`

**Contenido:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://pcfutsal.es/sitemap-grupos.xml</loc>
    <lastmod>2025-11-25</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://pcfutsal.es/sitemap-clubs.xml</loc>
    <lastmod>2025-11-25</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://pcfutsal.es/sitemap-jugadores.xml</loc>
    <lastmod>2025-11-25</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://pcfutsal.es/sitemap-partidos.xml</loc>
    <lastmod>2025-11-25</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://pcfutsal.es/sitemap-estaticas.xml</loc>
    <lastmod>2025-11-25</lastmod>
  </sitemap>
</sitemapindex>
```

#### sitemap-grupos.xml

**Contenido dinámico:**
- Todas las URLs de grupos: `/[lang]/competicion/[competicionSlug]/[grupoSlug]`
- Para cada idioma (7 idiomas: es, en, de, fr, it, pt, val)
- Prioridad: 0.8
- Frecuencia de actualización: semanal

**Ejemplo de entrada:**
```xml
<url>
  <loc>https://pcfutsal.es/es/competicion/tercera-division-nacional/grupo-xv-2024-2025</loc>
  <lastmod>2025-11-25</lastmod>
  <changefreq>weekly</changefreq>
  <priority>0.8</priority>
</url>
```

**Actualización automática:**
- Se actualiza cada vez que se añade un grupo o temporada
- Se regenera automáticamente en el build o mediante endpoint dinámico

#### sitemap-clubs.xml

**Contenido dinámico:**
- Todas las URLs de clubs: `/[lang]/clubes/[id]` (actual) o `/[lang]/clubes/[slug]` (futuro)
- Para cada idioma
- Prioridad: 0.7
- Frecuencia de actualización: semanal

**Ejemplo de entrada:**
```xml
<url>
  <loc>https://pcfutsal.es/es/clubes/123</loc>
  <lastmod>2025-11-25</lastmod>
  <changefreq>weekly</changefreq>
  <priority>0.7</priority>
</url>
```

#### sitemap-jugadores.xml

**Contenido dinámico:**
- Todas las URLs de jugadores: `/[lang]/jugador/[slug-jugador]`
- Para cada idioma
- Prioridad: 0.6
- Frecuencia de actualización: semanal

**Nota:** Solo incluir cuando se implementen las páginas de jugadores.

#### sitemap-partidos.xml

**Contenido dinámico:**
- URLs de partidos: `/[lang]/partido/[id]` o `/[lang]/partido/[slug]`
- Solo partidos de la temporada actual
- Prioridad: 0.5
- Frecuencia de actualización: diaria

**Nota:** Solo incluir cuando se implementen las páginas de partidos.

#### sitemap-estaticas.xml

**Contenido estático:**
- Home: `/[lang]/`
- Rankings: `/[lang]/rankings/equipos`, `/[lang]/rankings/mvp`
- MVP: `/[lang]/mvp`
- Competiciones: `/[lang]/ligas` o `/[lang]/competiciones` (cuando se cree)
- Clasificaciones: `/[lang]/clasificacion`
- Clubes (lista): `/[lang]/clubes`

**Prioridad:** 0.9 (páginas principales)
**Frecuencia de actualización:** diaria

**Ejemplo:**
```xml
<url>
  <loc>https://pcfutsal.es/es/</loc>
  <lastmod>2025-11-25</lastmod>
  <changefreq>daily</changefreq>
  <priority>1.0</priority>
</url>
<url>
  <loc>https://pcfutsal.es/es/rankings/equipos</loc>
  <lastmod>2025-11-25</lastmod>
  <changefreq>daily</changefreq>
  <priority>0.9</priority>
</url>
```

#### sitemap-apis-publicas.xml (Opcional)

**Solo si las APIs sirven contenido estable y indexable:**
- Endpoints públicos que devuelven HTML o contenido indexable
- No incluir endpoints JSON puros

**Estado:** ⚠️ **Evaluar necesidad** — Probablemente no necesario si solo hay APIs JSON

---

### B. robots.txt

**Ubicación:** `/robots.txt` (en `/frontend/public/robots.txt` o como ruta dinámica)

**Contenido propuesto:**
```
# Robots.txt para PC FUTSAL
# Permitir indexación de todo el contenido deportivo público
# Bloquear backend, APIs privadas y admin

User-agent: *
Allow: /
Allow: /es/
Allow: /en/
Allow: /de/
Allow: /fr/
Allow: /it/
Allow: /pt/
Allow: /val/

# Bloquear backend y APIs privadas
Disallow: /api/
Disallow: /admin/
Disallow: /backend/
Disallow: /_next/
Disallow: /static/

# Bloquear parámetros de filtro y búsqueda (evitar duplicados)
Disallow: /*?*
Disallow: /*&*

# Permitir específicamente las APIs públicas si sirven contenido indexable
# (Ajustar según necesidad)

# Sitemap principal
Sitemap: https://pcfutsal.es/sitemap.xml
```

**Notas importantes:**
- Permitir indexación de todas las rutas públicas deportivas
- Bloquear `/api/` para evitar indexación de endpoints JSON
- Bloquear `/admin/` y rutas de backend
- Bloquear `/_next/` (archivos internos de Next.js)
- Declarar el sitemap principal
- Considerar bloquear parámetros de query si generan contenido duplicado

**Implementación en Next.js 15:**
- Crear `/frontend/app/robots.ts` o `/frontend/app/robots.txt`
- Next.js 15 soporta ambos formatos

---

### C. URL Canónica

**Propósito:**
- Evitar contenido duplicado por parámetros (jornada, filtro, etc.)
- Indicar a Google cuál es la versión "oficial" de cada página

**Implementación:**

#### Para páginas con parámetros de query

**Ejemplo: Página de grupo con filtros**
```
URL con filtros: /es/competicion/tercera-division-nacional/grupo-xv-2024-2025?jornada=5&filtro=mvp
URL canónica: /es/competicion/tercera-division-nacional/grupo-xv-2024-2025
```

**En metadata (Next.js 15):**
```typescript
export const metadata: Metadata = {
  alternates: {
    canonical: `https://pcfutsal.es/${lang}/competicion/${competicionSlug}/${grupoSlug}`,
  },
};
```

#### Para páginas multilenguaje

**Ejemplo: Home en diferentes idiomas**
```typescript
export const metadata: Metadata = {
  alternates: {
    canonical: `https://pcfutsal.es/${lang}/`,
    languages: {
      'es': 'https://pcfutsal.es/es/',
      'en': 'https://pcfutsal.es/en/',
      'de': 'https://pcfutsal.es/de/',
      'fr': 'https://pcfutsal.es/fr/',
      'it': 'https://pcfutsal.es/it/',
      'pt': 'https://pcfutsal.es/pt/',
      'val': 'https://pcfutsal.es/val/',
    },
  },
};
```

#### Reglas de canonicalización

1. **Páginas sin parámetros:** La URL canónica es la misma que la URL actual
2. **Páginas con parámetros de filtro:** La URL canónica es la base sin parámetros
3. **Páginas con parámetros de paginación:** Considerar si se indexan o no (normalmente no se indexan páginas 2+)
4. **Páginas multilenguaje:** Cada idioma tiene su propia URL canónica

---

### D. Declaración de Idioma (Hreflang)

**Propósito:**
- Indicar a Google las versiones en diferentes idiomas de cada página
- Evitar contenido duplicado entre idiomas
- Mejorar el SEO internacional

**Implementación en Next.js 15:**

#### En metadata de cada página

```typescript
export async function generateMetadata({ params }): Promise<Metadata> {
  const { lang } = params;
  
  return {
    alternates: {
      canonical: `https://pcfutsal.es/${lang}/competicion/${competicionSlug}/${grupoSlug}`,
      languages: {
        'es': `https://pcfutsal.es/es/competicion/${competicionSlug}/${grupoSlug}`,
        'en': `https://pcfutsal.es/en/competicion/${competicionSlug}/${grupoSlug}`,
        'de': `https://pcfutsal.es/de/competicion/${competicionSlug}/${grupoSlug}`,
        'fr': `https://pcfutsal.es/fr/competicion/${competicionSlug}/${grupoSlug}`,
        'it': `https://pcfutsal.es/it/competicion/${competicionSlug}/${grupoSlug}`,
        'pt': `https://pcfutsal.es/pt/competicion/${competicionSlug}/${grupoSlug}`,
        'val': `https://pcfutsal.es/val/competicion/${competicionSlug}/${grupoSlug}`,
      },
    },
  };
}
```

#### En el HTML (generado automáticamente por Next.js)

Next.js 15 genera automáticamente los tags `<link rel="alternate" hreflang="...">` basándose en la metadata.

**Ejemplo de HTML generado:**
```html
<link rel="canonical" href="https://pcfutsal.es/es/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="es" href="https://pcfutsal.es/es/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="en" href="https://pcfutsal.es/en/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="de" href="https://pcfutsal.es/de/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="fr" href="https://pcfutsal.es/fr/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="it" href="https://pcfutsal.es/it/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="pt" href="https://pcfutsal.es/pt/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="val" href="https://pcfutsal.es/val/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
<link rel="alternate" hreflang="x-default" href="https://pcfutsal.es/es/competicion/tercera-division-nacional/grupo-xv-2024-2025" />
```

**Nota sobre `x-default`:**
- Indica la versión por defecto cuando el idioma del usuario no está disponible
- Normalmente es español (`es`) para PC FUTSAL

---

## 8. IMPLEMENTACIÓN TÉCNICA DE SITEMAPS

### Opción 1: Sitemaps estáticos (Build time)

**Ventajas:**
- Más rápido en producción
- No requiere llamadas a API en cada request

**Desventajas:**
- Se regenera solo en cada build
- No se actualiza automáticamente cuando se añaden grupos/temporadas

**Implementación:**
- Crear scripts que generen los sitemaps durante el build
- Guardar en `/frontend/public/`

### Opción 2: Sitemaps dinámicos (Runtime)

**Ventajas:**
- Se actualiza automáticamente cuando cambian los datos
- Siempre está actualizado

**Desventajas:**
- Requiere llamadas a API en cada request
- Puede ser más lento

**Implementación en Next.js 15:**
- Crear rutas dinámicas: `/app/sitemap.xml/route.ts`
- Usar `generateSitemaps` o crear manualmente

**Ejemplo de estructura:**
```
/app
  /sitemap.xml
    route.ts (genera sitemap-index.xml)
  /sitemap-grupos.xml
    route.ts (genera sitemap de grupos)
  /sitemap-clubs.xml
    route.ts (genera sitemap de clubs)
  ...
```

### Recomendación

**Híbrido:**
- Sitemaps estáticos para páginas estáticas (home, rankings, etc.)
- Sitemaps dinámicos para contenido que cambia frecuentemente (grupos, clubs, jugadores, partidos)
- Regenerar sitemaps estáticos en cada build
- Sitemaps dinámicos se generan on-demand

---

## 9. DATOS ESTRUCTURADOS (SCHEMA.ORG)

### A. Organization (PC FUTSAL como marca)

**Implementación:** En el layout principal o en la home

**Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "PC FUTSAL",
  "url": "https://pcfutsal.es",
  "logo": "https://pcfutsal.es/logo/logo.png",
  "description": "Plataforma de datos del fútbol sala amateur en España",
  "sameAs": [
    "https://twitter.com/pcfutsal",
    "https://facebook.com/pcfutsal",
    "https://instagram.com/pcfutsal"
  ]
}
```

**Estado:** ✅ **Implementado** - Añadido al layout principal (`app/[lang]/layout.tsx`)

---

### B. SportsOrganization (Competiciones y grupos)

**Implementación:** En páginas de competición/grupo

**Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "SportsOrganization",
  "name": "[Nombre Competición]",
  "sport": "Fútbol Sala",
  "memberOf": {
    "@type": "SportsOrganization",
    "name": "Federación de Fútbol Sala"
  }
}
```

**Estado:** ✅ **Implementado** - Añadido a páginas de grupo (`competicion/[slug]/[grupo]/page.tsx`)

---

### C. SportsTeam (Clubes)

**Implementación:** En páginas de club

**Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "SportsTeam",
  "name": "[Nombre Club]",
  "sport": "Fútbol Sala",
  "url": "https://pcfutsal.es/es/clubes/[id]",
  "logo": "[URL escudo]",
  "location": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "[Ciudad]",
      "addressRegion": "[Provincia]"
    }
  }
}
```

**Estado:** ✅ **Implementado** - Añadido a páginas de club (`clubes/[id]/ClubDetailClient.tsx`)

---

### D. Person (Jugadores)

**Implementación:** En páginas de jugador (cuando se creen)

**Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "[Nombre Jugador]",
  "jobTitle": "Jugador de Fútbol Sala",
  "memberOf": {
    "@type": "SportsTeam",
    "name": "[Nombre Club]"
  },
  "sport": "Fútbol Sala"
}
```

**Estado:** ⏳ **Pendiente de implementación** (páginas de jugador no existen aún)

---

### E. SportsEvent (Partidos)

**Implementación:** En páginas de partido (cuando se creen)

**Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "SportsEvent",
  "name": "[Equipo Local] vs [Equipo Visitante]",
  "sport": "Fútbol Sala",
  "startDate": "[Fecha]",
  "location": {
    "@type": "Place",
    "name": "[Pabellón]"
  },
  "homeTeam": {
    "@type": "SportsTeam",
    "name": "[Equipo Local]"
  },
  "awayTeam": {
    "@type": "SportsTeam",
    "name": "[Equipo Visitante]"
  },
  "result": {
    "@type": "SportsEventResult",
    "homeScore": "[Goles Local]",
    "awayScore": "[Goles Visitante]"
  }
}
```

**Estado:** ⏳ **Pendiente de implementación** (páginas de partido no existen aún)

---

### F. ItemList (Rankings)

**Implementación:** En páginas de rankings

**Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Ranking Global de Equipos de Fútbol Sala",
  "description": "Ranking de los mejores equipos de fútbol sala amateur en España",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "SportsTeam",
        "name": "[Equipo 1]"
      }
    }
  ]
}
```

**Estado:** ⏳ **Pendiente de implementación**

---

## 10. CONTENIDO INDEXABLE (PÁGINAS EVERGREEN)

### A. Página "Acerca de la competición"

**URL propuesta:** `/[lang]/competiciones` o `/[lang]/ligas`

**Contenido:**
- Explicación de cada categoría y grupo
- Estructura de competiciones en España
- Cómo funciona el sistema de grupos
- Temporadas y calendarios

**Keywords objetivo:**
- competiciones fútbol sala españa
- categorías fútbol sala
- ligas fútbol sala amateur

**Estado:** ⚠️ **Página a crear**

---

### B. Página "Cómo funciona el rating FIFA de PC FUTSAL"

**URL propuesta:** `/[lang]/como-funciona/rating-fifa`

**Contenido:**
- Explicación detallada del sistema de valoración tipo FIFA
- Cómo se calculan las medias
- Atributos y estadísticas que se consideran
- Ejemplos prácticos

**Keywords objetivo:**
- rating fifa fútbol sala
- valoración jugadores fútbol sala
- sistema fifa futsal
- media tipo fifa

**Estado:** ⚠️ **Página a crear**

---

### C. Página "Cómo funciona el Fantasy PC FUTSAL"

**URL propuesta:** `/[lang]/como-funciona/fantasy`

**Contenido:**
- Explicación del sistema de Fantasy
- Cómo crear un equipo
- Cómo funcionan las puntuaciones
- Estrategias y consejos

**Keywords objetivo:**
- fantasy fútbol sala
- fantasy futsal
- fantasy pc futsal
- cómo jugar fantasy futsal

**Estado:** ⚠️ **Página a crear**

---

### D. Página "Estadísticas del fútbol sala en España" (Pilar SEO)

**URL propuesta:** `/[lang]/estadisticas` o `/[lang]/estadisticas-espana`

**Contenido:**
- Estadísticas globales del fútbol sala amateur en España
- Número de competiciones, grupos, equipos, jugadores
- Datos históricos y tendencias
- Gráficos y visualizaciones
- Comparativas por comunidades autónomas

**Keywords objetivo:**
- estadísticas fútbol sala españa
- datos fútbol sala amateur
- fútbol sala españa estadísticas
- números fútbol sala

**Estado:** ⚠️ **Página a crear** (alta prioridad)

---

## 11. SISTEMA DE CONTENIDO EVERGREEN + DINÁMICO

### Contenido Evergreen (siempre válido)

**Páginas que no caducan:**
- ✅ Clubs (perfiles completos)
- ⚠️ Jugadores (perfiles completos - pendiente de crear)
- ✅ Competiciones (estructura y reglas)
- ✅ Grupos (información permanente)
- ⚠️ Reglas y metodología (páginas explicativas - pendiente de crear)

**Estrategia:**
- Estas páginas generan autoridad a largo plazo
- Google las indexa y mantiene en su índice
- Generan backlinks naturales

---

### Contenido Dinámico (actualización semanal)

**Páginas que se actualizan frecuentemente:**
- ✅ Jugador de la jornada (ya existe en MVP)
- ✅ Equipo de la jornada (ya existe)
- ✅ Partido estrella (ya existe)
- ✅ Ranking actualizado (ya existe)
- ✅ Fantasy (ya existe)

**Estrategia:**
- Google rastrea estas páginas con más frecuencia
- Mantienen el sitio "fresco" para los motores de búsqueda
- Generan tráfico recurrente

**Mix perfecto para SEO:**
- **Evergreen = Autoridad** (páginas que siempre son relevantes)
- **Dinámico = Frecuencia de rastreo** (Google visita más a menudo)

---

## 12. SEO INTERNO (ON-PAGE)

### A. H1 claro por página

**Regla:** El H1 debe coincidir con el title (o ser muy similar)

**Estado actual:**
- ✅ Home: H1 configurado
- ✅ Grupos: H1 dinámico con competición, grupo y temporada
- ✅ Clubs: H1 con nombre del club
- ⚠️ Rankings: H1 configurado pero puede mejorarse
- ⚠️ MVP: H1 configurado pero puede mejorarse

**Mejoras necesarias:**
- Asegurar que todos los H1 coincidan con los meta titles
- H1 único por página
- H1 descriptivo y con keywords principales

**Estado:** ⏳ **Parcialmente implementado** - Necesita revisión

---

### B. Breadcrumbs

**Estructura propuesta:**
```
Home → Competición → Grupo → [Página específica]
Home → Clubes → [Nombre Club]
Home → Rankings → [Tipo de Ranking]
```

**Implementación:**
- Schema.org BreadcrumbList
- Navegación visual en la página
- Enlaces internos mejorados

**Estado:** ⏳ **Pendiente de implementación**

---

### C. Paginación interna correcta

**Para listados grandes:**
- Rankings con muchos equipos/jugadores
- Lista de clubes
- Historial de partidos

**Implementación:**
- Rel="next" y rel="prev" en meta tags
- URLs limpias para paginación
- Canonical correcto en cada página

**Estado:** ⏳ **Pendiente de implementación** (evaluar necesidad)

---

### D. Enlazado interno poderoso

#### Enlaces desde página de jugador (cuando exista):
- ✅ Su club
- ✅ Su grupo/competición
- ⚠️ Sus partidos (pendiente de crear páginas de partido)
- ⚠️ Sus estadísticas

#### Enlaces desde página de club:
- ✅ Su grupo/competición (ya existe)
- ⚠️ Sus jugadores (mejorar enlaces)
- ⚠️ Sus partidos (pendiente de crear páginas de partido)
- ✅ Estadísticas del club (ya existe)

#### Enlaces desde página de grupo:
- ✅ Clubs del grupo (ya existe)
- ⚠️ Jugadores del grupo (mejorar)
- ✅ Partidos del grupo (mejorar enlaces a páginas de partido)
- ✅ Clasificación (ya existe)

**Estrategia:**
- Cada página debe enlazar a páginas relacionadas
- Crear una "red interna" de enlaces
- Google ama estas conexiones temáticas

**Estado:** ⏳ **Parcialmente implementado** - Necesita mejoras

---

## 13. ESTRATEGIA DE PALABRAS CLAVE

### A. Fútbol sala + Localización

**Keywords principales:**
- fútbol sala Alicante
- fútbol sala Valencia
- fútbol sala Cataluña
- fútbol sala Madrid
- fútbol sala Andalucía
- tercera división futsal
- preferente futsal
- segunda división futsal

**Estrategia:**
- Crear contenido específico por comunidad autónoma
- Páginas de competiciones por región
- Metadata específica por zona

**Estado:** ⏳ **Pendiente de implementación**

---

### B. Jugadores / Clubs

**Keywords principales:**
- [nombre jugador] futsal
- [nombre jugador] fútbol sala
- [nombre club] futsal
- [nombre club] fútbol sala
- plantilla [nombre club]
- jugadores [nombre club]

**Estrategia:**
- Metadata dinámica en páginas de jugadores/clubs (ya implementado parcialmente)
- URLs con slugs basados en nombres
- Contenido rico en cada página

**Estado:** ✅ **Parcialmente implementado** - Mejorar con slugs

---

### C. Ranking

**Keywords principales:**
- ranking futsal
- ranking fútbol sala
- mejores jugadores futsal
- mejores equipos futsal
- clasificación futsal
- top jugadores futsal

**Estrategia:**
- Metadata específica en páginas de rankings (ya implementado)
- Contenido explicativo sobre el sistema de ranking
- Schema.org ItemList (pendiente)

**Estado:** ✅ **Parcialmente implementado**

---

### D. Resultados

**Keywords principales:**
- resultados futsal hoy
- resultados fútbol sala
- clasificación futsal [grupo]
- partidos futsal hoy
- jornada [número] futsal

**Estrategia:**
- Metadata dinámica en páginas de partidos (pendiente de crear)
- Actualización frecuente de resultados
- Schema.org SportsEvent (pendiente)

**Estado:** ⏳ **Pendiente de implementación** (páginas de partido no existen)

---

### E. Fantasy

**Keywords principales:**
- fantasy futsal
- fantasy fútbol sala
- fantasy pc futsal
- cómo jugar fantasy futsal
- equipo fantasy futsal

**Estrategia:**
- Página explicativa "Cómo funciona Fantasy" (pendiente de crear)
- Metadata específica en páginas de Fantasy
- Contenido evergreen sobre el sistema

**Estado:** ⏳ **Pendiente de implementación**

---

## 14. PRÓXIMOS PASOS PRIORIZADOS

### Fase 1: Implementación técnica inmediata (Alta prioridad)
1. ✅ **Metadata dinámica** (completado)
2. ✅ **Sitemap y robots.txt** (completado)
3. ⏳ **Schema.org markup** (Organization, SportsTeam, ItemList)
4. ⏳ **Breadcrumbs** (visual + Schema.org)
5. ⏳ **Mejoras en H1** (revisar y alinear con titles)

### Fase 2: Contenido evergreen (Media prioridad)
1. ⏳ **Página "Acerca de competiciones"**
2. ⏳ **Página "Cómo funciona rating FIFA"**
3. ⏳ **Página "Cómo funciona Fantasy"**
4. ⏳ **Página "Estadísticas del fútbol sala en España"** (pilar SEO)

### Fase 3: Páginas faltantes (Media prioridad)
1. ⏳ **Páginas de jugadores** (`/jugador/[slug]`)
2. ⏳ **Páginas de partidos** (`/partido/[id]`)
3. ⏳ **Schema.org para jugadores y partidos**

### Fase 4: Optimización avanzada (Baja prioridad)
1. ⏳ **Enlazado interno mejorado**
2. ⏳ **Paginación interna**
3. ⏳ **Contenido por localización**
4. ⏳ **Migración de IDs a slugs** (clubes, jugadores)

---

**Última actualización:** 2025-11-25

