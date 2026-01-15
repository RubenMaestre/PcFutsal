# ROADMAP: Implementación de Tema WHITE (Modo Claro) — PC FUTSAL

**Fecha:** 2025-12-01  
**Objetivo:** Crear versión WHITE (clara) de la web manteniendo rojo y azul navy como colores principales

---

## 🎯 OBJETIVOS

1. Implementar sistema de temas (WHITE/DARK) con selector en el header
2. Cambiar backgrounds negros a blancos (blanco roto)
3. Adaptar textos y colores manteniendo rojo (#A51B3D) y azul navy (#0B1C2E)
4. Por defecto mostrar tema WHITE
5. Persistir preferencia del usuario (localStorage)

---

## 📋 ANÁLISIS ACTUAL

### Estructura de Colores Actual (DARK)

**Variables CSS (`globals.css`):**
- `--color-bg: #000000` (negro)
- `--color-card: #121212` (gris muy oscuro)
- `--color-accent: #A51B3D` (rojo - mantener)
- `--color-navy: #0B1C2E` (azul navy - mantener)
- `--color-text: #FFFFFF` (blanco)
- `--color-text-secondary: #B3B3B3` (gris claro)

**Tailwind Config (`tailwind.config.js`):**
- `brand.bg: "#000000"`
- `brand.card: "#121212"`
- `brand.text: "#FFFFFF"`
- `brand.textSecondary: "#B3B3B3"`

**Patrones encontrados:**
1. Variables CSS: `var(--color-bg)`, `var(--color-text)`, etc.
2. Clases Tailwind: `bg-brand-bg`, `text-brand-text`, `border-brand-card`
3. Colores hardcodeados: `bg-[#111]`, `bg-black`, `text-white`, `bg-[#0D0D0D]`
4. Opacidades: `bg-white/10`, `text-white/80`, `border-white/20`

---

## 🎨 PROPUESTA DE COLORES WHITE

### Variables CSS para Tema WHITE

```css
--color-bg: #FAFAFA;              /* Blanco roto (fondo principal) */
--color-card: #FFFFFF;            /* Blanco puro (tarjetas) */
--color-accent: #A51B3D;          /* Rojo (mantener) */
--color-navy: #0B1C2E;            /* Azul navy (mantener) */
--color-text: #1A1A1A;           /* Negro suave (texto principal) */
--color-text-secondary: #666666;  /* Gris medio (texto secundario) */
--color-border: #E5E5E5;          /* Gris muy claro (bordes) */
```

### Mapeo de Colores

| DARK (actual) | WHITE (nuevo) | Uso |
|---------------|---------------|-----|
| `#000000` (bg) | `#FAFAFA` (bg) | Fondo principal |
| `#121212` (card) | `#FFFFFF` (card) | Tarjetas/módulos |
| `#FFFFFF` (text) | `#1A1A1A` (text) | Texto principal |
| `#B3B3B3` (text-secondary) | `#666666` (text-secondary) | Texto secundario |
| `#111` (hardcoded) | `#F5F5F5` | Fondos alternativos |
| `#0D0D0D` (hardcoded) | `#FFFFFF` | Dropdowns/menús |
| `white/10` (opacity) | `black/5` (opacity) | Overlays sutiles |
| `white/80` (opacity) | `black/80` (opacity) | Textos con opacidad |
| `white/20` (opacity) | `black/10` (opacity) | Bordes con opacidad |

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### FASE 1: Sistema de Temas (Context + Provider)

**1.1 Crear Context de Tema**
- Archivo: `frontend/lib/ThemeContext.tsx`
- Funcionalidad:
  - Context para manejar tema actual (WHITE/DARK)
  - Provider que envuelve la app
  - Hook `useTheme()` para acceder al tema
  - Persistencia en localStorage
  - Por defecto: WHITE

**1.2 Integrar Provider en Layout**
- Modificar: `frontend/app/[lang]/layout.tsx`
- Envolver children con `<ThemeProvider>`

**1.3 Variables CSS Dinámicas**
- Modificar: `frontend/app/globals.css`
- Añadir clases `.theme-white` y `.theme-dark`
- Definir variables CSS para ambos temas
- Aplicar clase al `<html>` según tema activo

---

### FASE 2: Selector de Tema en Header

**2.1 Crear Componente ThemeSwitcher**
- Archivo: `frontend/components/ThemeSwitcher.tsx`
- Similar a `LanguageSwitcher.tsx`
- Botones/selector para cambiar entre WHITE y DARK
- Iconos: ☀️ (WHITE) y 🌙 (DARK)

**2.2 Integrar en Header**
- Modificar: `frontend/components/Header.tsx`
- Añadir junto a `LanguageSwitcher` (desktop y móvil)
- Posición: derecha del header, junto al selector de idioma

---

### FASE 3: Actualizar Variables CSS y Tailwind

**3.1 Actualizar globals.css**
- Añadir variables para tema WHITE
- Mantener variables para tema DARK
- Usar clases CSS para aplicar según tema

**3.2 Actualizar tailwind.config.js**
- Añadir colores para tema WHITE
- Mantener compatibilidad con clases `brand-*`
- Considerar usar CSS variables en Tailwind

---

### FASE 4: Actualizar Componentes (Sistema de Clases)

**4.1 Componentes que usan Variables CSS**
- ✅ Ya funcionarán automáticamente si usan `var(--color-*)`
- Verificar: `ClasificacionEvolucionChart.tsx`, `ClasificacionShell.tsx`, etc.

**4.2 Componentes que usan Clases Tailwind `brand-*`**
- ✅ Ya funcionarán si Tailwind está configurado correctamente
- Verificar: `Header.tsx`, `Footer.tsx`, etc.

**4.3 Componentes con Colores Hardcodeados**
- ⚠️ Requieren cambios manuales
- Buscar y reemplazar:
  - `bg-[#111]` → `bg-[var(--color-card)]` o clase dinámica
  - `bg-[#0D0D0D]` → `bg-[var(--color-card)]`
  - `bg-black` → `bg-[var(--color-bg)]`
  - `text-white` → `text-[var(--color-text)]`
  - `bg-white/10` → `bg-[var(--color-text)]/5` (en WHITE)
  - `text-white/80` → `text-[var(--color-text)]/80`
  - `border-white/20` → `border-[var(--color-text)]/10`

**Archivos a revisar:**
- `components/Header.tsx` (línea 238: `bg-[#0D0D0D]`)
- `app/[lang]/clubes/ClubsPageClient.tsx` (línea 304: `bg-[#111]`)
- `components/MatchCard.tsx` (varios `bg-black/10`)
- `home_components/GlobalTopMatches.tsx` (`bg-black/10`)
- `home_components/GlobalTeamCard.tsx` (`bg-black/10`)
- `home_components/GlobalMVPCard.tsx` (`bg-black/10`, `bg-black/20`)
- `components/TopScorerOfMatchday.tsx` (`bg-black/10`)
- `components/GoalkeeperOfMatchday.tsx` (`bg-black/20`, `bg-black/30`)
- `components/MVPOfMatchday.tsx` (`bg-black/10`, `bg-black/20`)
- `components/JugadorReconocimientosCard.tsx` (`text-white`)
- `components/EquipoReconocimientosCard.tsx` (`text-white`)

---

### FASE 5: Componentes Específicos

**5.1 Tablas**
- `FullClassificationTable.tsx`
- `MVPClassificationTable.tsx`
- `MiniClassificationTable.tsx`
- `TeamGoalsTable.tsx`
- Ajustar colores de fondo, texto y bordes

**5.2 Cards y Tarjetas**
- `MatchCard.tsx`
- `MVPPartidoCard.tsx`
- `HomeSectionCard.tsx`
- Ajustar backgrounds y textos

**5.3 Gráficas**
- `ClasificacionEvolucionChart.tsx`
- Ajustar colores de líneas, ejes y tooltips

**5.4 Formularios y Inputs**
- Inputs de búsqueda
- Selectores
- Botones
- Ajustar backgrounds y bordes

---

### FASE 6: Páginas Específicas

**6.1 Páginas Principales**
- `app/[lang]/page.tsx` (Home)
- `app/[lang]/clasificacion/...`
- `app/[lang]/clubes/...`
- `app/[lang]/jugadores/...`
- `app/[lang]/partidos/...`
- `app/[lang]/rankings/...`

**6.2 Verificar Contraste**
- Asegurar que textos sean legibles en fondo blanco
- Ajustar opacidades y colores según necesidad

---

### FASE 7: Testing y Ajustes

**7.1 Testing Visual**
- Revisar todas las páginas en modo WHITE
- Verificar contraste y legibilidad
- Ajustar colores que no funcionen bien

**7.2 Testing Funcional**
- Verificar que el selector de tema funciona
- Verificar persistencia en localStorage
- Verificar que el tema se aplica correctamente

**7.3 Ajustes Finales**
- Refinar colores según feedback
- Ajustar opacidades y sombras
- Optimizar para mejor UX

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Backend
- [ ] No requiere cambios en backend

### Frontend - Sistema Base
- [ ] Crear `lib/ThemeContext.tsx`
- [ ] Crear `components/ThemeSwitcher.tsx`
- [ ] Modificar `app/globals.css` con variables de ambos temas
- [ ] Modificar `tailwind.config.js` (si es necesario)
- [ ] Integrar ThemeProvider en `app/[lang]/layout.tsx`
- [ ] Añadir ThemeSwitcher en `components/Header.tsx`

### Frontend - Componentes
- [ ] Actualizar `components/Header.tsx` (colores hardcodeados)
- [ ] Actualizar `components/Footer.tsx`
- [ ] Actualizar `app/[lang]/clubes/ClubsPageClient.tsx`
- [ ] Actualizar `components/MatchCard.tsx`
- [ ] Actualizar `home_components/GlobalTopMatches.tsx`
- [ ] Actualizar `home_components/GlobalTeamCard.tsx`
- [ ] Actualizar `home_components/GlobalMVPCard.tsx`
- [ ] Actualizar `components/TopScorerOfMatchday.tsx`
- [ ] Actualizar `components/GoalkeeperOfMatchday.tsx`
- [ ] Actualizar `components/MVPOfMatchday.tsx`
- [ ] Actualizar `components/JugadorReconocimientosCard.tsx`
- [ ] Actualizar `components/EquipoReconocimientosCard.tsx`
- [ ] Actualizar `components/FullClassificationTable.tsx`
- [ ] Actualizar `components/MVPClassificationTable.tsx`
- [ ] Actualizar `components/MiniClassificationTable.tsx`
- [ ] Actualizar `components/ClasificacionEvolucionChart.tsx`
- [ ] Revisar y actualizar resto de componentes

### Frontend - Páginas
- [ ] Verificar `app/[lang]/page.tsx` (Home)
- [ ] Verificar páginas de clasificación
- [ ] Verificar páginas de clubes
- [ ] Verificar páginas de jugadores
- [ ] Verificar páginas de partidos
- [ ] Verificar páginas de rankings

### Testing
- [ ] Testing visual en modo WHITE
- [ ] Testing visual en modo DARK (verificar que sigue funcionando)
- [ ] Testing del selector de tema
- [ ] Testing de persistencia
- [ ] Verificar contraste y accesibilidad

---

## 🔧 DETALLES TÉCNICOS

### Implementación de Variables CSS

```css
/* globals.css */
:root {
  /* Tema DARK (actual) */
  --color-bg: #000000;
  --color-card: #121212;
  --color-text: #FFFFFF;
  --color-text-secondary: #B3B3B3;
  /* ... */
}

.theme-white {
  /* Tema WHITE (nuevo) */
  --color-bg: #FAFAFA;
  --color-card: #FFFFFF;
  --color-text: #1A1A1A;
  --color-text-secondary: #666666;
  --color-border: #E5E5E5;
  /* ... */
}

.theme-dark {
  /* Tema DARK (explícito) */
  --color-bg: #000000;
  --color-card: #121212;
  --color-text: #FFFFFF;
  --color-text-secondary: #B3B3B3;
  /* ... */
}
```

### Implementación del Context

```typescript
// lib/ThemeContext.tsx
type Theme = 'white' | 'dark';

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}>(...);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState<Theme>('white'); // Por defecto WHITE
  
  useEffect(() => {
    // Cargar de localStorage
    const saved = localStorage.getItem('theme') as Theme;
    if (saved) setTheme(saved);
  }, []);
  
  useEffect(() => {
    // Aplicar clase al html
    document.documentElement.className = `theme-${theme}`;
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  // ...
}
```

### Selector de Tema

```typescript
// components/ThemeSwitcher.tsx
export default function ThemeSwitcher() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      {theme === 'white' ? '🌙' : '☀️'}
    </button>
  );
}
```

---

## ⚠️ CONSIDERACIONES

1. **Contraste:** Asegurar que textos sean legibles en fondo blanco
2. **Consistencia:** Mantener rojo y azul navy como colores principales
3. **Opacidades:** Invertir opacidades (white/10 → black/5 en WHITE)
4. **Bordes:** Ajustar bordes para que sean visibles en fondo claro
5. **Sombras:** Ajustar sombras para mejor efecto en fondo claro
6. **Imágenes:** Verificar que logos y escudos se vean bien en ambos temas

---

## 📊 ESTIMACIÓN

- **Fase 1 (Sistema de temas):** 2-3 horas
- **Fase 2 (Selector):** 1 hora
- **Fase 3 (CSS/Tailwind):** 1-2 horas
- **Fase 4-5 (Componentes):** 4-6 horas
- **Fase 6 (Páginas):** 2-3 horas
- **Fase 7 (Testing):** 2-3 horas

**Total estimado:** 12-18 horas

---

**Última actualización:** 2025-12-01









