# VERIFICACIÓN DE REDES SOCIALES — PC FUTSAL

**Fecha:** 2025-11-25  
**Estado:** ✅ Implementación completa

---

## ✅ VERIFICACIONES REALIZADAS

### 1. Imagen OG Global

- ✅ **Archivo:** `og-default.png`
- ✅ **Tamaño:** 1200×630 px (verificado)
- ✅ **Formato:** PNG (verificado)
- ✅ **Ubicación:** `/frontend/public/og/og-default.png`
- ✅ **URL pública:** `https://pcfutsal.es/og/og-default.png`
- ✅ **Tamaño archivo:** 454 KB

---

## 🔗 ENLACES PARA PROBAR

### URLs de prueba

1. **Home:**
   - https://pcfutsal.es/es/

2. **Página de grupo:**
   - https://pcfutsal.es/es/competicion/[slug]/[grupo]

3. **Ficha de club:**
   - https://pcfutsal.es/es/clubes/[id]

4. **Rankings:**
   - https://pcfutsal.es/es/rankings/equipos
   - https://pcfutsal.es/es/rankings/mvp

---

## 🧪 VALIDADORES OFICIALES

### Facebook Debugger
**URL:** https://developers.facebook.com/tools/debug/

**Instrucciones:**
1. Ve a la URL del validador
2. Pega cualquier URL de pcfutsal.es (ej: https://pcfutsal.es/es/)
3. Haz clic en "Debug"
4. Verifica que:
   - ✅ Aparece la imagen OG (og-default.png)
   - ✅ Aparece el título correcto
   - ✅ Aparece la descripción correcta
   - ✅ La preview se ve bien

### Twitter Card Validator
**URL:** https://cards-dev.twitter.com/validator

**Instrucciones:**
1. Ve a la URL del validador
2. Pega cualquier URL de pcfutsal.es
3. Haz clic en "Preview card"
4. Verifica que:
   - ✅ Aparece la imagen grande (summary_large_image)
   - ✅ Aparece el título
   - ✅ Aparece la descripción
   - ✅ La tarjeta se ve correctamente

### LinkedIn Post Inspector
**URL:** https://www.linkedin.com/post-inspector/

**Instrucciones:**
1. Ve a la URL del inspector
2. Pega cualquier URL de pcfutsal.es
3. Haz clic en "Inspect"
4. Verifica que:
   - ✅ Aparece la imagen OG
   - ✅ Aparece el título
   - ✅ Aparece la descripción

### WhatsApp Test
**Instrucciones:**
1. Abre WhatsApp (Web o móvil)
2. Comparte cualquier URL de pcfutsal.es contigo mismo o en un grupo de prueba
3. Verifica que:
   - ✅ Aparece la preview con imagen
   - ✅ Aparece el título
   - ✅ Aparece la descripción

---

## 📋 META TAGS ESPERADOS

### Open Graph (Facebook, LinkedIn)
```html
<meta property="og:title" content="[Título de la página] | PC FUTSAL" />
<meta property="og:description" content="[Descripción de la página]" />
<meta property="og:image" content="https://pcfutsal.es/og/og-default.png" />
<meta property="og:url" content="https://pcfutsal.es/[lang]/[path]" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="PC FUTSAL" />
<meta property="og:locale" content="[es|en|de|fr|it|pt]" />
```

### Twitter Cards
```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="[Título de la página] | PC FUTSAL" />
<meta name="twitter:description" content="[Descripción de la página]" />
<meta name="twitter:image" content="https://pcfutsal.es/og/og-default.png" />
```

---

## ✅ ESTADO FINAL

- ✅ Imagen OG subida y accesible
- ✅ Código implementado y deployado
- ✅ Todas las páginas tienen Open Graph
- ✅ Todas las páginas tienen Twitter Cards
- ⏳ Pendiente: Probar en validadores oficiales

---

## 📝 NOTAS

- La imagen se usará automáticamente en todas las páginas
- Si una página tiene imagen específica, puede pasarla como parámetro a `generateMetadataWithAlternates`
- La imagen actual se servirá desde: `https://pcfutsal.es/og/og-default.png`

---

**Última actualización:** 2025-11-25

