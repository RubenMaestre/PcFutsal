# IMPLEMENTACIÓN: Clasificaciones Históricas - Gráfica de Evolución

## Estado: ✅ COMPLETADO (30 de noviembre de 2025)

---

## 📋 Resumen

Sistema completo implementado para almacenar y visualizar la evolución histórica de las posiciones de equipos en la clasificación jornada a jornada. Incluye backend (nueva app Django, modelos, comandos, endpoints) y frontend (hook, componente de gráfica interactiva).

---

## 🔧 Backend

### Nueva App Django: `clasificaciones`

**Ubicación:** `backend/clasificaciones/`

**Registro en settings.py:**
```python
INSTALLED_APPS = [
    # ...
    "clasificaciones",  # Histórico de posiciones por jornada
]
```

### Modelos

#### `ClasificacionJornada`
Snapshot completo de la clasificación de un grupo en una jornada específica.

**Ubicación:** `backend/clasificaciones/models.py`

**Campos:**
- `grupo` (ForeignKey → Grupo)
- `jornada` (PositiveIntegerField)
- `fecha_calculo` (DateTimeField, auto_now_add)
- `partidos_jugados_total` (PositiveIntegerField)
- `equipos_participantes` (PositiveIntegerField)

**Unique constraint:** `(grupo, jornada)`

**Índices:**
- `["grupo", "jornada"]`
- `["grupo", "-jornada"]` (para obtener la última jornada)

#### `PosicionJornada`
Posición de un equipo en una jornada específica.

**Campos:**
- `clasificacion_jornada` (ForeignKey → ClasificacionJornada)
- `club` (ForeignKey → Club)
- `posicion` (PositiveIntegerField)
- `puntos` (IntegerField)
- `partidos_jugados` (PositiveIntegerField)
- `partidos_ganados` (PositiveIntegerField)
- `partidos_empatados` (PositiveIntegerField)
- `partidos_perdidos` (PositiveIntegerField)
- `goles_favor` (IntegerField)
- `goles_contra` (IntegerField)
- `diferencia_goles` (IntegerField)
- `racha` (CharField, max_length=10)
- `enfrentamientos_directos` (JSONField, nullable)

**Unique constraint:** `(clasificacion_jornada, club)`

**Índices:**
- `["clasificacion_jornada", "posicion"]`
- `["club", "clasificacion_jornada"]`

### Endpoints API

#### GET `/api/clubes/clasificacion-evolucion/`

**Ubicación:** `backend/clubes/views.py` - `ClasificacionEvolucionView`

**Query Parameters:**
- `grupo_id` (required): ID del grupo

**Respuesta:**
```json
{
  "grupo": {
    "id": 1,
    "nombre": "Grupo XV",
    "competicion": "Tercera División",
    "temporada": "2025/2026"
  },
  "jornadas": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
  "equipos": [
    {
      "club_id": 11,
      "nombre": "Crevillent Futsal Starts 'A'",
      "escudo": "http://appffcv.filesnovanet.es/pnfg/pimg/Clubes/...",
      "slug": "crevillent-futsal-starts-a",
      "posicion_actual": 1,
      "evolucion": [
        {
          "jornada": 1,
          "posicion": 2,
          "puntos": 3,
          "goles_favor": 5,
          "goles_contra": 2
        },
        {
          "jornada": 2,
          "posicion": 1,
          "puntos": 6,
          "goles_favor": 10,
          "goles_contra": 4
        }
        // ... más jornadas
      ]
    }
    // ... más equipos
  ]
}
```

**Características:**
- Devuelve todas las jornadas disponibles para el grupo
- Incluye evolución completa de cada equipo jornada a jornada
- Optimizado con `prefetch_related` para reducir queries
- Incluye escudo URL para visualización

### Management Commands

#### `recalcular_clasificacion`

**Ubicación:** `backend/estadisticas/management/commands/recalcular_clasificacion.py`

**Modificaciones:**
- Añadido guardado automático de snapshot histórico después de calcular clasificación
- Detecta la última jornada jugada
- Crea/actualiza `ClasificacionJornada`
- Guarda todas las posiciones usando `bulk_create`
- Se ejecuta automáticamente con el scraping semanal

**Uso:**
```bash
python manage.py recalcular_clasificacion --grupo=1
```

#### `generar_historico_clasificaciones`

**Ubicación:** `backend/clasificaciones/management/commands/generar_historico_clasificaciones.py`

**Propósito:** Generar histórico retrospectivo para jornadas pasadas

**Opciones:**
- `--grupo_id=X`: Genera histórico para un grupo específico
- `--temporada_id=X`: Genera histórico para todos los grupos de una temporada
- `--retrospectivo`: Genera histórico para todas las temporadas
- `--force`: Regenera clasificaciones existentes

**Uso:**
```bash
# Generar histórico para un grupo específico
python manage.py generar_historico_clasificaciones --grupo_id=1

# Generar histórico para todos los grupos de una temporada
python manage.py generar_historico_clasificaciones --temporada_id=4

# Generar histórico para todas las temporadas
python manage.py generar_historico_clasificaciones --retrospectivo

# Regenerar histórico existente
python manage.py generar_historico_clasificaciones --grupo_id=1 --force
```

**Funcionalidad:**
- Reutiliza la lógica de cálculo de `recalcular_clasificacion`
- Calcula clasificación progresiva jornada por jornada
- Solo crea snapshots que no existan (a menos que se use `--force`)
- Muestra progreso detallado con emojis

### Admin Django

**Ubicación:** `backend/clasificaciones/admin.py`

**Configuración:**
- `ClasificacionJornadaAdmin`: List display, filtros por temporada/competición/grupo/jornada
- `PosicionJornadaAdmin`: List display, filtros, búsqueda por club
- `PosicionJornadaInline`: Inline dentro de `ClasificacionJornada` para edición fácil

---

## 🎨 Frontend

### Hook: `useClasificacionEvolucion`

**Ubicación:** `frontend/hooks/useClasificacionEvolucion.ts`

**Uso:**
```typescript
const { data, loading, error } = useClasificacionEvolucion(grupoId, enabled);
```

**Propiedades:**
- `grupoId`: number | string | null - ID del grupo
- `enabled`: boolean (default: true) - Si el hook debe hacer fetch

**Retorno:**
- `data`: `ClasificacionEvolucionResponse | null`
- `loading`: boolean
- `error`: string | null

**Tipos TypeScript:**
```typescript
export type EvolucionJornada = {
  jornada: number;
  posicion: number | null;
  puntos: number;
  goles_favor: number;
  goles_contra: number;
};

export type EquipoEvolucion = {
  club_id: number;
  nombre: string;
  escudo: string;
  slug: string | null;
  posicion_actual: number | null;
  evolucion: EvolucionJornada[];
};

export type ClasificacionEvolucionResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornadas: number[];
  equipos: EquipoEvolucion[];
};
```

**Características:**
- Fetch automático cuando cambia `grupoId`
- Manejo de estados de loading y error
- Cancela requests si el componente se desmonta
- Cache: "no-store" para siempre obtener datos frescos

### Componente: `ClasificacionEvolucionChart`

**Ubicación:** `frontend/components/ClasificacionEvolucionChart.tsx`

**Props:**
```typescript
type Props = {
  grupoId: number | string | null;
  dict: any;
  lang?: string;
};
```

**Características:**
- Gráfica de líneas usando Recharts
- Eje X: Jornadas (1, 2, 3, ...)
- Eje Y: Posición (invertido: 1 arriba, 16 abajo)
- Múltiples líneas: Una por cada equipo
- **Escudos de equipos como marcadores** en lugar de círculos
- Selector interactivo de equipos para activar/desactivar líneas
- Tooltip con información detallada
- Leyenda con nombres de equipos
- Colores únicos generados automáticamente para cada equipo

**Tamaño y márgenes:**
- Altura: 720px
- Márgenes: `{ top: 30, right: 30, left: 40, bottom: 30 }`

**Componentes personalizados de puntos:**
- `CustomDotWithShield`: Escudo circular de 20px para puntos normales
  - Círculo de fondo con color del equipo (opacidad 0.15)
  - Borde circular con color del equipo
  - Escudo con ClipPath circular
- `CustomActiveDot`: Escudo circular de 28px para hover
  - Mismo diseño pero más grande
  - Círculo de fondo más grande (opacidad 0.25)

**Estados:**
- Loading: Mensaje de carga
- Error: Mensaje de error
- No data: Mensaje informativo si no hay datos históricos
- Datos válidos: Gráfica interactiva completa

**Integración:**
- Integrado en `frontend/components/ClasificacionShell.tsx`
- Se muestra debajo de la tabla de clasificación
- Solo visible cuando hay un grupo seleccionado

### Traducciones

**Ubicación:** `frontend/i18n/es.json`

**Claves añadidas:**
```json
{
  "clasificacion_evolucion": {
    "title": "Evolución de Posiciones",
    "subtitle": "Seguimiento de la posición en la clasificación jornada a jornada",
    "loading": "Cargando evolución de clasificación...",
    "no_data": "No hay datos históricos de evolución disponibles para este grupo. La gráfica aparecerá cuando se generen los datos históricos.",
    "error": "Error al cargar la evolución de clasificación",
    "toggle_teams": "Activar/Desactivar equipos",
    "position": "Posición",
    "jornada": "Jornada",
    "jornada_label": "Jornada",
    "posicion_label": "Posición",
    "note": "Haz clic en los equipos arriba para activar o desactivar sus líneas en la gráfica"
  }
}
```

---

## 📦 Estructura de Archivos

### Backend

```
backend/
├── clasificaciones/
│   ├── __init__.py
│   ├── admin.py                    # Registro de modelos en admin
│   ├── apps.py
│   ├── models.py                   # ClasificacionJornada, PosicionJornada
│   ├── migrations/
│   │   └── 0001_initial.py
│   └── management/
│       └── commands/
│           └── generar_historico_clasificaciones.py
├── estadisticas/
│   └── management/
│       └── commands/
│           └── recalcular_clasificacion.py  # Modificado
└── clubes/
    └── views.py                    # ClasificacionEvolucionView actualizado
```

### Frontend

```
frontend/
├── hooks/
│   └── useClasificacionEvolucion.ts
├── components/
│   ├── ClasificacionEvolucionChart.tsx
│   └── ClasificacionShell.tsx      # Integración del gráfico
└── i18n/
    └── es.json                     # Traducciones añadidas
```

---

## 🚀 Flujo de Datos

### 1. Generación de Histórico

```
Scrape Semanal (Domingo 2 PM)
    ↓
scrape_semana.py
    ↓
recalcular_clasificacion --grupo=X (para cada grupo)
    ↓
Calcula clasificación actual
    ↓
Guarda en ClubEnGrupo
    ↓
Guarda snapshot histórico:
    - ClasificacionJornada (última jornada)
    - PosicionJornada (todas las posiciones)
```

### 2. Visualización en Frontend

```
Usuario navega a /clasificacion/tercera/grupo-xv
    ↓
ClasificacionShell se monta
    ↓
ClasificacionEvolucionChart se monta
    ↓
useClasificacionEvolucion hace fetch a /api/clubes/clasificacion-evolucion/?grupo_id=1
    ↓
Backend consulta ClasificacionJornada y PosicionJornada
    ↓
Construye respuesta con estructura optimizada
    ↓
Frontend recibe datos y renderiza gráfica
    ↓
Gráfica muestra evolución jornada a jornada con escudos
```

---

## ✅ Checklist de Implementación

### Backend
- [x] Crear app `clasificaciones`
- [x] Registrar en `INSTALLED_APPS`
- [x] Crear modelos `ClasificacionJornada` y `PosicionJornada`
- [x] Crear y aplicar migraciones
- [x] Modificar `recalcular_clasificacion.py` para guardar histórico
- [x] Actualizar endpoint `ClasificacionEvolucionView` para usar nuevos modelos
- [x] Registrar modelos en admin
- [x] Crear comando `generar_historico_clasificaciones`

### Frontend
- [x] Crear hook `useClasificacionEvolucion`
- [x] Crear componente `ClasificacionEvolucionChart`
- [x] Integrar componente en `ClasificacionShell`
- [x] Añadir traducciones
- [x] Implementar escudos como marcadores
- [x] Ajustar tamaño y márgenes de la gráfica

### Testing y Deploy
- [x] Ejecutar comando retrospectivo en grupo de prueba
- [x] Verificar que se generan correctamente las posiciones
- [x] Verificar que el endpoint funciona con nuevos datos
- [x] Verificar que la gráfica se muestra correctamente
- [x] Deploy realizado y funcionando

---

## 📊 Ejemplo de Uso

### Generar histórico para un grupo

```bash
cd /home/rubenmaestre/pcfutsal.es/backend
python manage.py generar_historico_clasificaciones --grupo_id=1
```

**Salida esperada:**
```
🚀 Generando histórico para 1 grupo(s)...

📁 Grupo XV (Tercera División - 2025/2026)
  📊 Procesando 11 jornadas...
    ✅ Jornada 1 guardada
    ✅ Jornada 2 guardada
    ...
    ✅ Jornada 11 guardada

✅ Completado: 11 clasificaciones generadas
```

### Usar el hook en un componente

```typescript
import { useClasificacionEvolucion } from "../hooks/useClasificacionEvolucion";

function MiComponente({ grupoId }: { grupoId: number }) {
  const { data, loading, error } = useClasificacionEvolucion(grupoId);
  
  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return null;
  
  return (
    <div>
      <h2>Evolución de {data.grupo.nombre}</h2>
      <p>Jornadas: {data.jornadas.join(", ")}</p>
      {/* ... */}
    </div>
  );
}
```

---

## 🔮 Mejoras Futuras

1. **Lógica de enfrentamientos directos**: Implementar cálculo de enfrentamientos directos para desempates
2. **Gráficas adicionales**: Añadir gráficas de puntos, goles, diferencia de goles
3. **Filtros avanzados**: Permitir filtrar por rango de jornadas
4. **Exportar datos**: Permitir exportar datos de evolución en CSV/JSON
5. **Comparativa de equipos**: Vista para comparar evolución de múltiples equipos lado a lado
6. **Animaciones**: Añadir animaciones suaves al cargar la gráfica
7. **Modo oscuro**: Ajustar colores para mejor contraste

---

## 📝 Notas Técnicas

### Criterios de Clasificación

1. **Puntos** (descendente): 3 por victoria, 1 por empate
2. **Diferencia de goles** (descendente): GF - GC
3. **Goles a favor** (descendente): Total de goles marcados
4. **Nombre del club** (ascendente): Para estabilidad/consistencia

### Racha (Forma)

- Se calcula con los últimos 5 partidos
- Formato: "VVEDV" (Victoria, Victoria, Empate, Derrota, Victoria)
- Se ordena cronológicamente por jornada y fecha_hora

### Rendimiento

- Usar `select_related` y `prefetch_related` para optimizar queries
- Índices en campos críticos (grupo, jornada, posicion)
- `bulk_create` para insertar múltiples posiciones eficientemente
- Gráfica con animaciones deshabilitadas para mejor rendimiento

---

**Fecha de implementación:** 30 de noviembre de 2025  
**Estado:** ✅ Completado y en producción










