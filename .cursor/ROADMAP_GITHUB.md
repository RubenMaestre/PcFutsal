# Roadmap: Subida de PC FUTSAL a GitHub

Este documento define el plan completo para subir el proyecto PC FUTSAL a GitHub de forma segura y organizada, incluyendo la mejora de comentarios según el estilo definido.

---

## 📋 ÍNDICE

1. [Análisis de Archivos Sensibles](#1-análisis-de-archivos-sensibles)
2. [Análisis de Archivos que Necesitan Comentarios](#2-análisis-de-archivos-que-necesitan-comentarios)
3. [Roadmap: Preparación para GitHub](#3-roadmap-preparación-para-github)
4. [Roadmap: Añadir Comentarios](#4-roadmap-añadir-comentarios)

---

## 1. Análisis de Archivos Sensibles

### 1.1. Archivos que NO deben subirse a GitHub

#### 🔴 CRÍTICOS (Nunca subir)

**Backend:**
- `/backend/.env` - Contiene SECRET_KEY, credenciales DB, etc.
- `/backend/db.sqlite3` - Base de datos local
- `/backend/logs/` - Logs del sistema
- `/backend/media/` - Archivos subidos por usuarios
- `/backend/staticfiles/` - Archivos estáticos compilados
- `/backend/__pycache__/` - Cache de Python

**Raíz del proyecto:**
- `/.env` - Contiene GUNICORN_PASSWORD
- `/venv/` - Entorno virtual completo
- `/node_modules/` - Dependencias Node.js

**Archivos del sistema:**
- `.DS_Store`, `Thumbs.db`, `*.swp`

#### 🟡 CONFIGURACIÓN (Revisar antes de subir)

- `/deploy_pcfutsal.sh` - Crear versión `.example` sin rutas hardcodeadas
- `.cursor/DIARIO/` - Información interna, no subir
- Configuraciones con rutas absolutas

### 1.2. Archivos que SÍ deben subirse

✅ Todo el código fuente (`.py`, `.ts`, `.tsx`)
✅ `requirements.txt`, `package.json`
✅ Archivos de configuración (sin secretos)
✅ Documentación técnica de `.cursor/`
✅ `README.md` (crear)

---

## 2. Análisis de Archivos que Necesitan Comentarios

### 2.1. Prioridad ALTA

**Backend:**
- `scraping/core/*.py` - Parsers y fetchers complejos
- `valoraciones/views.py` - Algoritmos de cálculo
- `estadisticas/views.py` - Cálculos estadísticos
- `clasificaciones/models.py` - Modelos con lógica compleja

**Frontend:**
- `hooks/useMVPGlobal.ts` - Normalización de campos
- `hooks/useClasificacionEvolucion.ts` - Datos históricos
- `components/ClasificacionEvolucionChart.tsx` - Gráfica interactiva
- `components/GroupShell.tsx` - Shell principal

### 2.2. Prioridad MEDIA

- Views y serializers con lógica no obvia
- Componentes con estado complejo
- Utilidades compartidas

---

## 3. Roadmap: Preparación para GitHub

### FASE 1: Preparación Git (Día 1)

1. Inicializar repositorio: `git init`
2. Crear `.gitignore` completo
3. Crear `.env.example` y `deploy_pcfutsal.sh.example`

### FASE 2: Limpieza (Día 1-2)

1. Verificar que no hay secretos hardcodeados
2. Revisar configuraciones
3. Limpiar rutas absolutas

### FASE 3: Documentación (Día 2)

1. Crear `README.md` completo
2. Actualizar documentación existente

### FASE 4: Primer Commit (Día 2-3)

1. Commit inicial
2. Crear repositorio en GitHub
3. Push y configuración

---

## 4. Roadmap: Añadir Comentarios

### FASE 1: Backend Crítico (Día 3-5)

- Scraping: parsers, fetchers, comandos
- Valoraciones: algoritmos de cálculo
- Modelos complejos: relaciones y constraints

### FASE 2: Frontend Crítico (Día 5-7)

- Hooks complejos: normalización, ventanas temporales
- Componentes complejos: gráficas, shells

### FASE 3: Utilidades (Día 7-8)

- Backend utils
- Frontend lib

### FASE 4: Revisión (Día 8-9)

- Revisar estilo de comentarios
- Eliminar comentarios obvios
- Documentar decisiones importantes

---

## 📝 Checklist Final

### Antes de subir
- [ ] `.gitignore` completo
- [ ] `.env.example` creado
- [ ] `README.md` completo
- [ ] No hay secretos hardcodeados
- [ ] No hay rutas absolutas

### Comentarios
- [ ] Backend crítico comentado
- [ ] Frontend crítico comentado
- [ ] Utilidades comentadas
- [ ] Revisión completa

---

**Total estimado: 9 días de trabajo**

