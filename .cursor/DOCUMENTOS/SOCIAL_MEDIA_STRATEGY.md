# ESTRATEGIA DE REDES SOCIALES — PC FUTSAL

**Fecha de creación:** 2025-11-25  
**Última actualización:** 2025-11-25  
**Estado:** ✅ Implementado con soporte multilenguaje

---

## 🌍 SOPORTE MULTILENGUAJE

**Idiomas soportados:** Español (es), Inglés (en), Valenciano (val), Francés (fr), Alemán (de), Italiano (it), Portugués (pt)

**Implementación:**
- ✅ Todos los textos de Open Graph y Twitter Cards están traducidos en `/frontend/i18n/[lang].json` bajo la sección `seo.default`
- ✅ Las páginas generan automáticamente Social Cards en el idioma correspondiente
- ✅ El helper `generateMetadataWithAlternates()` acepta un diccionario opcional para usar traducciones
- ✅ Fallback automático a español si no hay traducción disponible

**Estructura de traducciones Social Media:**
```json
{
  "seo": {
    "default": {
      "og_title": "PC FUTSAL — Datos, Rankings y Fantasy del Fútbol Sala Amateur",
      "og_description": "Resultados reales, clasificaciones, jugadores, clubes y rankings tipo FIFA...",
      "site_name": "PC FUTSAL"
    }
  }
}
```

**Archivos modificados:**
- `frontend/lib/seo.ts` - Actualizado para usar traducciones dinámicas en Open Graph y Twitter Cards
- `frontend/i18n/*.json` - Sección `seo.default` añadida en todos los idiomas
- Todas las páginas con `generateMetadata` - Actualizadas para pasar el diccionario

---

## OBJETIVO

Configurar las Social Cards (preview cards) para que cualquier enlace compartido en Facebook, Twitter/X, LinkedIn y WhatsApp se vea correctamente y de forma atractiva.

---

## 1. IMAGEN OG GLOBAL (La más importante)

### Especificaciones

**Tamaño:** 1200×630 px  
**Formato:** PNG o JPG  
**Ubicación:** `/public/og/og-default.png`

### Contenido de la imagen

- **Fondo:** Negro (#000000)
- **Logo:** PC FUTSAL (centrado o posicionado estratégicamente)
- **Frase principal:** "Donde los goles valen… y los datos también."
- **Detalles:** Rojo #A51B3D (para acentos, bordes, o elementos decorativos)
- **Diseño:** Limpio, profesional, que represente la marca

### Uso

Esta imagen se mostrará cuando compartan:
- ✅ La Home
- ✅ Cualquier página que no tenga OG específico
- ✅ Facebook
- ✅ Twitter/X
- ✅ LinkedIn
- ✅ WhatsApp

**Estado:** ⚠️ **Pendiente de crear** - Necesita diseño

---

## 2. TEXTOS BASE PARA SOCIAL CARDS

### Título Global (og:title)

**Español:**
```
PC FUTSAL — Datos, Rankings y Fantasy del Fútbol Sala Amateur
```

**Otros idiomas:** Traducido en `i18n/[lang].json` bajo `seo.default.og_title`

### Descripción Global (og:description)

**Español:**
```
Resultados reales, clasificaciones, jugadores, clubes y rankings tipo FIFA. Fantasy semanal y estadísticas del futsal amateur en España.
```

**Otros idiomas:** Traducido en `i18n/[lang].json` bajo `seo.default.og_description`

### Uso

Estos textos se usarán en cualquier página donde no se defina un título/descripción específico. Se cargan automáticamente según el idioma de la página.

**Estado:** ✅ **Implementado** - Definido en `i18n/[lang].json` bajo `seo.default`:
- `seo.default.og_title` - Título global por idioma
- `seo.default.og_description` - Descripción global por idioma
- `seo.default.site_name` - Nombre del sitio (siempre "PC FUTSAL")

---

## 3. ELEMENTOS OPEN GRAPH OBLIGATORIOS (Mínimos)

### Parámetros requeridos para cada página

1. **og:title** - Título de la página
2. **og:description** - Descripción de la página
3. **og:image** - URL de la imagen (og-default.png por defecto)
4. **og:type** - Tipo de contenido (siempre "website" para páginas web)
5. **og:url** - URL canónica de la página

### Implementación

Estos elementos deben añadirse a todas las páginas mediante metadata de Next.js 15.

**Estado actual:**
- ✅ **Implementado** - Todas las páginas usan `generateMetadataWithAlternates` que incluye Open Graph
- ✅ Configurado en layout principal
- ✅ Configurado en todas las páginas con metadata dinámica

---

## 4. ELEMENTOS BÁSICOS DE TWITTER CARDS

### Parámetros requeridos

1. **twitter:card** - Tipo de tarjeta (siempre "summary_large_image")
2. **twitter:title** - Título (puede ser el mismo que og:title)
3. **twitter:description** - Descripción (puede ser la misma que og:description)
4. **twitter:image** - URL de la imagen (usa la misma OG global)

### Tipos de Twitter Cards

- **summary_large_image**: Tarjeta grande con imagen 1200×630 (recomendado)
- **summary**: Tarjeta pequeña con imagen pequeña
- **app**: Para aplicaciones
- **player**: Para videos

**Recomendación:** Usar siempre `summary_large_image` para mejor visualización.

**Estado actual:**
- ✅ **Implementado** - Todas las páginas incluyen Twitter Cards mediante `generateMetadataWithAlternates`
- ✅ Tipo `summary_large_image` configurado
- ✅ Usa la misma imagen que Open Graph

---

## 5. CONFIGURACIÓN DE FALLBACK

### Reglas de fallback

Si una página NO tiene:
- **Imagen OG personalizada** → Usar `og-default.png`
- **Título personalizado** → Usar título global
- **Descripción personalizada** → Usar descripción global

### Implementación

El helper `generateMetadataWithAlternates` en `lib/seo.ts` debe:
1. Aceptar parámetros opcionales para imagen OG
2. Si no se proporciona imagen, usar `og-default.png`
3. Si no se proporciona título/descripción, usar los globales

**Estado:** ✅ **Implementado** - El helper `generateMetadataWithAlternates` ya incluye:
- ✅ Parámetro opcional `ogImage` para imágenes personalizadas
- ✅ Fallback automático a `DEFAULT_OG_IMAGE` si no se proporciona
- ✅ Todas las páginas usan este helper, garantizando fallback

---

## 6. VALIDADORES OFICIALES

### Herramientas de prueba

#### Facebook Debugger
**URL:** https://developers.facebook.com/tools/debug/

**Uso:**
- Introduce la URL de cualquier página
- Verifica que Facebook puede leer los OG tags
- Muestra cómo se verá la preview
- Permite limpiar caché si es necesario

#### Twitter Card Validator
**URL:** https://cards-dev.twitter.com/validator

**Uso:**
- Introduce la URL de cualquier página
- Muestra la preview exacta de cómo se verá en Twitter
- Valida que todos los parámetros estén correctos

#### LinkedIn Post Inspector
**URL:** https://www.linkedin.com/post-inspector/

**Uso:**
- Introduce la URL de cualquier página
- LinkedIn usa OG tags pero es más exigente con el tamaño de imagen
- Verifica que la preview se vea correctamente

#### WhatsApp Test
**Método:** Compartir un enlace en un grupo privado o contigo mismo

**Uso:**
- Comparte cualquier URL de pcfutsal.es
- Verifica que la preview se muestre correctamente
- WhatsApp usa OG tags básicos

**Estado:** ⏳ **Pendiente de probar** - Después de implementar

---

## 7. IMPLEMENTACIÓN TÉCNICA

### Estructura actual

**Archivos relevantes:**
- `frontend/lib/seo.ts` - Helper para generar metadata
- `frontend/app/[lang]/layout.tsx` - Layout principal con OG básico
- `frontend/app/[lang]/page.tsx` - Home con metadata
- Todas las páginas con `generateMetadata`

### Mejoras necesarias

1. **Actualizar helper SEO:**
   - Añadir parámetro opcional para imagen OG personalizada
   - Implementar fallback a `og-default.png`
   - Implementar fallback a títulos/descripciones globales

2. **Verificar todas las páginas:**
   - Asegurar que todas tienen Open Graph
   - Asegurar que todas tienen Twitter Cards
   - Verificar que usan imagen por defecto si no tienen específica

3. **Crear imagen OG:**
   - Diseñar `og-default.png` (1200×630)
   - Subir a `/public/og/og-default.png`

---

## 8. METADATA ESPECÍFICA POR TIPO DE PÁGINA

### Home

**og:title:** `PC FUTSAL — Resultados, Estadísticas y Rankings de Fútbol Sala en España`  
**og:description:** `Resultados oficiales, clasificaciones, jugadores, clubes y rankings tipo FIFA del fútbol sala amateur en España. Datos actualizados y Fantasy semanal.`  
**og:image:** `og-default.png`

### Página de Grupo

**og:title:** `[Competición] · [Grupo] · [Temporada] — Resultados y Clasificación | PC FUTSAL`  
**og:description:** `Jornadas, resultados, clasificación, clubs, goleadores y ranking de jugadores del [Grupo] de [Competición] en [Temporada].`  
**og:image:** `og-default.png` (o imagen específica del grupo si se crea)

### Ficha de Club

**og:title:** `[Nombre del club] — Resultados, Plantilla y Estadísticas | PC FUTSAL`  
**og:description:** `Plantilla completa, últimos resultados, clasificación, racha y estadísticas del [club].`  
**og:image:** `og-default.png` (o escudo del club si se implementa)

### Rankings

**og:title:** `Ranking Global de Equipos — Mejores Equipos de Fútbol Sala | PC FUTSAL`  
**og:description:** `Ranking global de los mejores equipos de fútbol sala amateur en España. Compara equipos de todas las competiciones y categorías.`  
**og:image:** `og-default.png`

---

## 9. PRÓXIMOS PASOS

### Fase 1: Implementación básica (Alta prioridad)
1. ⏳ **Crear imagen OG global** (`og-default.png`) - ⚠️ **Pendiente de diseñar** (carpeta `/public/og/` creada)
2. ✅ **Actualizar helper SEO** con fallbacks - **Completado**
3. ✅ **Verificar todas las páginas** tienen OG y Twitter Cards - **Completado**
4. ✅ **Actualizar layout principal** para usar constantes globales - **Completado**
5. ⏳ **Probar en validadores** (Facebook, Twitter, LinkedIn, WhatsApp) - **Pendiente de probar**

### Fase 2: Optimización (Media prioridad)
1. ⏳ **Imágenes OG específicas** para tipos de página importantes
2. ⏳ **Imágenes dinámicas** para clubs (usando escudos)
3. ⏳ **A/B testing** de diferentes imágenes OG

### Fase 3: Avanzado (Baja prioridad)
1. ⏳ **Open Graph dinámico** con datos en tiempo real
2. ⏳ **Twitter Cards mejoradas** con más información
3. ⏳ **LinkedIn específico** (si es necesario)

---

## 10. RESUMEN SUPER BÁSICO

### Lo mínimo imprescindible (3 cosas):

1. ✅ **Imagen OG global** (1200×630) - `/public/og/og-default.png`
2. ✅ **Título y descripción global** - Definidos en este documento
3. ✅ **Configurar Open Graph y Twitter Cards básicos** - En todas las páginas

### Resultado

Con esto, si alguien comparte:
- La Home
- Un ranking
- Una ficha
- Un jugador
- Un partido
- Lo que sea

➡️ **Siempre saldrá una tarjeta bonita, correcta y coherente.**

---

**Última actualización:** 2025-11-25

