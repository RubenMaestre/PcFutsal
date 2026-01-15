# DOCUMENTACIÓN DE APIs — PC FUTSAL

Este archivo contiene la documentación completa de todas las APIs del backend de PC FUTSAL.

**IMPORTANTE**: Cada vez que se cree una nueva API, debe documentarse aquí inmediatamente.

---

## STATUS

### GET /api/status/last_update/

**App**: `status`

**Descripción**: Proporciona información sobre la última actualización del scraping sincronizado.

**Parámetros**:
- `Accept-Language` (header, opcional): Idioma para la respuesta

**Retorna**:
```json
{
  "last_update_display": "string",
  "detalle": "string"
}
```

**Uso**: Se utiliza para mostrar cuándo fue la última vez que se actualizaron los datos desde el scraping.

---

## NUCLEO (Configuración y filtros)

### GET /api/nucleo/filter-context/

**App**: `nucleo`

**Descripción**: Devuelve el contexto de filtros para temporadas, competiciones y grupos. Esencial para inicializar los selectores y filtros en el frontend.

**Parámetros**: Ninguno

**Retorna**:
```json
{
  "temporada_activa": {
    "id": number,
    "nombre": "string"
  },
  "competiciones": [
    {
      "id": number,
      "nombre": "string",
      "grupos": [
        {
          "id": number,
          "nombre": "string"
        }
      ]
    }
  ]
}
```

**Uso**: Se utiliza al cargar la aplicación para poblar los filtros de temporada, competición y grupo.

---

## ESTADISTICAS (14 endpoints principales)

### GET /api/estadisticas/grupo-info/

**App**: `estadisticas`

**Descripción**: Endpoint completo que devuelve TODO el paquete de datos del grupo en una sola llamada. Es un endpoint agregado que incluye múltiples datos para optimizar las peticiones.

**Parámetros**:
- `competicion_slug` (query, requerido): Slug de la competición
- `grupo_slug` (query, requerido): Slug del grupo
- `temporada` (query, requerido): Temporada
- `jornada` (query, opcional): Número de jornada

**Retorna**: Objeto complejo que incluye clasificación, resultados, KPIs, goleadores, pichichi, sanciones, fair play, etc.

**Uso**: Ideal para pantallas públicas donde se necesitan múltiples datos del grupo sin hacer múltiples peticiones.

---

### GET /api/estadisticas/clasificacion-mini/

**App**: `estadisticas`

**Descripción**: Clasificación compacta del grupo con información mínima pero esencial.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo

**Retorna**:
```json
{
  "grupo": {
    "id": number,
    "nombre": "string",
    "competicion": "string"
  },
  "tabla": [
    {
      "pos": number | null,
      "club_id": number,
      "nombre": "string",
      "escudo": "string",
      "pj": number,
      "puntos": number
    }
  ]
}
```

**Uso**: Para widgets compactos, headers o listas rápidas de clasificación.

---

### GET /api/estadisticas/clasificacion-completa/

**App**: `estadisticas`

**Descripción**: Clasificación completa con todos los detalles estadísticos (PJ, PG, PE, PP, GF, GC, DG).

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `scope` (query, requerido): `"overall"` | `"home"` | `"away"`
- `jornada` (query, opcional): Número de jornada para ver la clasificación hasta esa jornada

**Retorna**:
```json
{
  "grupo": {
    "id": number,
    "nombre": "string",
    "competicion": "string",
    "temporada": "string"
  },
  "scope": "overall" | "home" | "away",
  "jornadas_disponibles": number[],
  "jornada_aplicada": number | null,
  "tabla": [
    {
      "club_id": number,
      "nombre": "string",
      "escudo": "string",
      "puntos": number,
      "pj": number,
      "pg": number,
      "pe": number,
      "pp": number,
      "gf": number,
      "gc": number,
      "dg": number
    }
  ]
}
```

**Uso**: Para pantallas completas de clasificación con todos los detalles estadísticos.

---

### GET /api/estadisticas/clasificacion-evolucion/

**App**: `estadisticas`

**Descripción**: Evolución jornada a jornada de la clasificación para generar gráficos de líneas.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `scope` (query, requerido): `"overall"` | `"home"` | `"away"`
- `parameter` (query, requerido): `"pts"` | `"gf"` | `"gc"` | otro parámetro

**Retorna**: Datos estructurados para gráficos con evolución jornada a jornada.

**Uso**: Para gráficos de evolución de puntos, goles, etc.

---

### GET /api/estadisticas/resultados-jornada/

**App**: `estadisticas`

**Descripción**: Partidos de una jornada específica con marcadores, árbitros, pabellón y fechas.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada. Si no se especifica, devuelve la última jugada.

**Retorna**:
```json
{
  "grupo": {...},
  "jornada": number,
  "partidos": [
    {
      "id": number,
      "local": string,
      "visitante": string,
      "goles_local": number,
      "goles_visitante": number,
      "fecha": "string",
      "arbitro": "string",
      "pabellon": "string"
    }
  ]
}
```

**Uso**: Para mostrar los partidos de una jornada con todos sus detalles.

---

### GET /api/estadisticas/kpis-jornada/

**App**: `estadisticas`

**Descripción**: KPIs agregados de la jornada: goles totales, tarjetas, distribución de resultados.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada

**Retorna**:
```json
{
  "grupo": {...},
  "jornada": number | null,
  "stats": {
    "goles_totales": number,
    "amarillas_totales": number,
    "rojas_totales": number,
    "victorias_local": number,
    "empates": number,
    "victorias_visitante": number
  }
}
```

**Uso**: Para widgets de KPIs o resúmenes estadísticos de la jornada.

---

### GET /api/estadisticas/goleadores-jornada/

**App**: `estadisticas`

**Descripción**: Ranking de goleadores de una jornada específica con porcentaje de contribución.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada

**Retorna**:
```json
{
  "grupo": {...},
  "jornada": number | null,
  "goleadores": [
    {
      "jugador_id": number,
      "nombre": "string",
      "apodo": "string",
      "club_id": number,
      "club_nombre": "string",
      "club_posicion": number | null,
      "goles_jornada": number,
      "foto": "string",
      "club_escudo": "string"
    }
  ]
}
```

**Uso**: Para mostrar los máximos goleadores de una jornada.

---

### GET /api/estadisticas/pichichi-temporada/

**App**: `estadisticas`

**Descripción**: Ranking acumulado de máximos goleadores de la temporada.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo

**Retorna**:
```json
{
  "grupo": {...},
  "goleadores": [
    {
      "jugador_id": number,
      "nombre": "string",
      "apodo": "string",
      "club_id": number,
      "club_nombre": "string",
      "goles_total": number,
      "goles_equipo_total": number,
      "contribucion_pct": number,
      "foto": "string"
    }
  ]
}
```

**Uso**: Para mostrar el ranking acumulado de goleadores de toda la temporada (Pichichi).

---

### GET /api/estadisticas/goles-por-equipo/

**App**: `estadisticas`

**Descripción**: Ranking ofensivo de equipos con estadísticas detalladas de goles.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo

**Retorna**:
```json
{
  "grupo": {...},
  "equipos": [
    {
      "club_id": number,
      "club_nombre": "string",
      "club_escudo": "string",
      "partidos_jugados": number,
      "goles_total": number,
      "goles_por_partido": number,
      "goles_local": number,
      "goles_visitante": number,
      "goles_1parte": number,
      "goles_2parte": number
    }
  ]
}
```

**Uso**: Para mostrar estadísticas ofensivas de los equipos.

---

### GET /api/estadisticas/sanciones-jornada/

**App**: `estadisticas`

**Descripción**: Jugadores sancionados en una jornada específica (amarillas, dobles amarillas, rojas) con severidad.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada

**Retorna**:
```json
{
  "grupo": {...},
  "jornada": number | null,
  "sancionados": [
    {
      "jugador_id": number,
      "nombre": "string",
      "apodo": "string",
      "foto": "string",
      "club_id": number,
      "club_nombre": "string",
      "amarillas": number,
      "dobles_amarillas": number,
      "rojas": number,
      "severidad_puntos": number
    }
  ]
}
```

**Uso**: Para mostrar los jugadores sancionados en una jornada.

---

### GET /api/estadisticas/sanciones-jugadores/

**App**: `estadisticas`

**Descripción**: Ranking acumulado de jugadores más sancionados de la temporada.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo

**Retorna**:
```json
{
  "grupo": {...},
  "jugadores": [
    {
      "jugador_id": number,
      "nombre": "string",
      "apodo": "string",
      "foto": "string",
      "club_id": number,
      "club_nombre": "string",
      "amarillas": number,
      "dobles_amarillas": number,
      "rojas": number,
      "puntos_disciplina": number
    }
  ]
}
```

**Uso**: Para mostrar el ranking acumulado de jugadores más sancionados.

---

### GET /api/estadisticas/fair-play-equipos/

**App**: `estadisticas`

**Descripción**: Ranking de fair play entre equipos (menos puntos = mejor comportamiento).

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo

**Retorna**:
```json
{
  "grupo": {...},
  "equipos": [
    {
      "club_id": number,
      "club_nombre": "string",
      "club_escudo": "string",
      "amarillas": number,
      "dobles_amarillas": number,
      "rojas": number,
      "puntos_fair_play": number
    }
  ]
}
```

**Uso**: Para mostrar el ranking de fair play de los equipos.

---

### GET /api/estadisticas/coeficientes-clubes/

**App**: `estadisticas`

**Descripción**: Coeficientes de valoración FIFA-like de los clubes.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada

**Retorna**: Coeficientes de valoración de los clubes.

**Uso**: Para mostrar la valoración de los clubes según un sistema similar al de FIFA.

---

### POST /api/estadisticas/coeficientes-clubes/

**App**: `estadisticas`

**Descripción**: Crear o actualizar un coeficiente manualmente (solo admin).

**Parámetros** (body):
- Datos del coeficiente a crear/actualizar

**Retorna**: Confirmación de creación/actualización.

**Uso**: Para administradores que necesitan ajustar coeficientes manualmente.

---

## CLUBES (4 endpoints)

### GET /api/clubes/lista/

**App**: `clubes`

**Descripción**: Lista de clubes del grupo o competición con mini-estadísticas.

**Parámetros**:
- `grupo_id` (query, opcional): ID del grupo
- O alternativamente:
  - `competicion_id` (query, opcional): ID de la competición
  - `temporada_id` (query, opcional): ID de la temporada

**Retorna**:
```json
{
  "grupo": {...},
  "count": number,
  "results": [
    {
      "id": number,
      "nombre_oficial": "string",
      "nombre_corto": "string",
      "localidad": "string",
      "pabellon": "string",
      "escudo_url": "string"
    }
  ]
}
```

**Uso**: Para listar los clubes de un grupo o competición.

---

### GET /api/clubes/detalle/

**App**: `clubes`

**Descripción**: Detalle básico del club con participaciones, plantilla y staff (si se proporciona temporada_id).

**Parámetros**:
- `club_id` (query, requerido): ID del club
- `temporada_id` (query, opcional): ID de la temporada

**Retorna**: Detalle del club con información básica, participaciones, plantilla y staff si se especifica temporada.

**Uso**: Para mostrar la ficha básica de un club.

---

### GET /api/clubes/full/

**App**: `clubes`

**Descripción**: Ficha completa del club con todos los bloques opcionales.

**Parámetros**:
- `club_id` (query, requerido): ID del club (o alternativamente `slug`)
- `temporada_id` (query, opcional): ID de la temporada
- `grupo_id` (query, opcional): ID del grupo
- `include` (query, opcional): CSV de bloques a incluir: `progress,history,awards,media,notes,travel,staff,roster`

**Retorna**: Objeto complejo con:
- Información del club
- Contexto (temporada, grupo)
- Clasificación actual
- Participaciones
- Plantilla (si se incluye `roster`)
- Staff (si se incluye `staff`)
- Valoración
- Series (gráficos de progreso, histórico)
- Awards (premios)
- Media (vídeos, imágenes)
- Notas
- Travel (estadísticas de viajes)

**Uso**: Para la ficha completa del club con todos los detalles disponibles.

---

### GET /api/clubes/historico/

**App**: `clubes`

**Descripción**: Obtiene el histórico de temporadas en las que el club ha participado, mostrando la división/grupo de cada temporada.

**Parámetros**:
- `club_id` (query, opcional): ID numérico del club (opcional si se usa slug)
- `slug` (query, opcional): Slug del club (opcional si se usa club_id)

**Retorna**:
```json
{
  "club_id": number,
  "club_nombre": "string",
  "historico": [
    {
      "temporada": "string",          // Ej: "2024/2025"
      "division": "string",            // Ej: "Tercera División"
      "grupo": "string",               // Ej: "Grupo XV"
      "grupo_id": number,
      "competicion_id": number,
      "posicion": number | null,       // Posición final en esa temporada
      "puntos": number                 // Puntos totales en esa temporada
    }
  ]
}
```

**Notas**:
- Las participaciones están ordenadas por temporada descendente (más reciente primero)
- El histórico incluye todas las temporadas en las que el club ha participado según `ClubEnGrupo`
- Se obtienen datos directamente de `ClubEnGrupo` con relaciones optimizadas a `Grupo`, `Competicion` y `Temporada`

**Uso**: Para mostrar el histórico de participaciones del club en diferentes temporadas y divisiones.

---

## VALORACIONES (8 endpoints)

### GET /api/valoraciones/partido-estrella/

**App**: `valoraciones`

**Descripción**: Partido más interesante de la jornada según algoritmo de coeficientes.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada

**Retorna**: Información del partido estrella con detalles y razón de su selección.

**Uso**: Para destacar el partido más interesante de la jornada.

---

### GET /api/valoraciones/equipo-jornada/

**App**: `valoraciones`

**Descripción**: Equipo ideal de la jornada (mejor formación tipo FIFA).

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada

**Retorna**: Formación ideal con jugadores y sus posiciones.

**Uso**: Para mostrar el equipo ideal de la jornada según las valoraciones.

---

### GET /api/valoraciones/jugadores-jornada/

**App**: `valoraciones`

**Descripción**: Top jugadores de la jornada con valoraciones.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada
- `only_porteros` (query, opcional): `1` para filtrar solo porteros

**Retorna**:
```json
{
  "grupo": {...},
  "jornada": number | null,
  "jugador_de_la_jornada": {...},
  "ranking_jugadores": [...]
}
```

**Uso**: Para mostrar el ranking de jugadores más valorados de la jornada.

---

### GET /api/valoraciones/mvp-clasificacion/

**App**: `valoraciones`

**Descripción**: Clasificación de MVP acumulada del grupo.

**Parámetros**:
- `grupo_id` (query, requerido): ID del grupo
- `jornada` (query, opcional): Número de jornada hasta la que calcular
- `only_porteros` (query, opcional): `1` para filtrar solo porteros

**Retorna**:
```json
{
  "grupo": {...},
  "jornada_aplicada": number | null,
  "jornadas_disponibles": number[],
  "ranking": [
    {
      "jugador_id": number,
      "nombre": "string",
      "foto": "string",
      "club_id": number,
      "club_nombre": "string",
      "club_escudo": "string",
      "puntos_acumulados": number,
      "puntos_jornada": number,
      "posicion": number
    }
  ]
}
```

**Uso**: Para mostrar la clasificación acumulada de MVP del grupo.

---

### GET /api/valoraciones/equipo-jornada-global/

**App**: `valoraciones`

**Descripción**: Equipo ideal global de la jornada (todos los grupos combinados).

**Parámetros**:
- `temporada_id` (query, requerido): ID de la temporada
- `jornada` (query, opcional): Número de jornada
- `weekend` (query, opcional): Fecha en formato YYYY-MM-DD
- `top` (query, opcional): Número de equipos a devolver (default: 30)
- `strict` (query, opcional): `1` para usar exactamente esa semana

**Retorna**: Equipo ideal global con jugadores de todos los grupos.

**Uso**: Para mostrar el equipo ideal global de la jornada en toda la temporada.

---

### GET /api/valoraciones/jugadores-jornada-global/

**App**: `valoraciones`

**Descripción**: Top jugadores globales de la jornada (todos los grupos combinados).

**Parámetros**:
- `temporada_id` (query, requerido): ID de la temporada
- `jornada` (query, opcional): Número de jornada
- `weekend` (query, opcional): Fecha en formato YYYY-MM-DD
- `top` (query, opcional): Número de jugadores a devolver (default: 50)
- `only_porteros` (query, opcional): `1` para filtrar solo porteros
- `strict` (query, opcional): `1` para usar exactamente esa semana

**Retorna**:
```json
{
  "temporada_id": number,
  "jornada": number | null,
  "window": {...},
  "jugador_de_la_jornada_global": {...},
  "ranking_global": [...]
}
```

**Uso**: Para mostrar el ranking global de jugadores de la jornada en toda la temporada.

---

### GET /api/valoraciones/partidos-top-global/

**App**: `valoraciones`

**Descripción**: Top partidos globales de la jornada.

**Parámetros**:
- `jornada` (query, opcional): Número de jornada

**Retorna**: Lista de los mejores partidos globales de la jornada.

**Uso**: Para mostrar los mejores partidos globales de la jornada.

---

### GET /api/valoraciones/mvp-global/

**App**: `valoraciones`

**Descripción**: Ranking global de MVP acumulado (todos los grupos combinados).

**Parámetros**:
- `from` (query, opcional): Fecha inicio en formato YYYY-MM-DD
- `to` (query, opcional): Fecha fin en formato YYYY-MM-DD
- `temporada_id` (query, opcional): ID de la temporada
- `only_porteros` (query, opcional): `1` para filtrar solo porteros
- `top` (query, opcional): Número de jugadores a devolver
- `strict` (query, opcional): `1` para modo estricto
- `min_matches` (query, opcional): Número mínimo de partidos requeridos

**Retorna**:
```json
{
  "temporada_id": number,
  "window": {
    "start": "string",
    "end": "string",
    "status": "ok" | "strict" | "fallback_failed" | "no-window",
    "matched_games": number,
    "min_required": number
  },
  "jugador_de_la_jornada_global": {...},
  "ranking_global": [...]
}
```

**Uso**: Para mostrar el ranking global de MVP acumulado de toda la temporada.

---

## JUGADORES (5 endpoints)

**Nota importante**: Todos los endpoints de jugadores aceptan `id_or_slug` como parámetro, que puede ser el ID numérico del jugador o su slug (ej: `daniel-domene-garcia`). El slug se genera automáticamente desde el nombre del jugador y se usa para URLs SEO-friendly.

### GET /api/jugadores/detalle/

**App**: `jugadores`

**Descripción**: Detalle básico del jugador con club actual y temporada.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador

**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "slug": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "edad_display": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "nombre_corto": "string",
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

**Uso**: Para obtener información básica del jugador y su club actual.

---

### GET /api/jugadores/full/

**App**: `jugadores`

**Descripción**: Ficha completa del jugador con todos los bloques opcionales (similar a `/api/clubes/full/`).

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar datos
- `include` (query, opcional, CSV): Bloques a incluir: `valoraciones`, `historial`, `partidos`, `stats`, `fantasy`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Puntos Fantasy MVP (si `include=fantasy`)

**Retorna (bloque fantasy)**:
```json
{
  "fantasy": {
    "temporada_id": number,
    "temporada_nombre": "string",
    "puntos_base_total": number,
    "puntos_con_coef_total": number,
    "goles_total": number,
    "partidos_total": number,
    "puntos_por_jornada": [
      {
        "jornada": number,
        "grupo_id": number,
        "grupo_nombre": "string",
        "puntos_base": number,
        "puntos_con_coef": number,
        "coef_division": number,
        "goles": number,
        "partidos_jugados": number,
        "fecha_calculo": "YYYY-MM-DDTHH:mm:ssZ" | null
      }
    ]
  }
}
```

**Notas sobre puntos Fantasy MVP**:
- `puntos_base_total`: Sumatorio de puntos sin coeficiente división
- `puntos_con_coef_total`: Sumatorio de puntos con coeficiente división aplicado (usado para ranking)
- `puntos_por_jornada`: Array con puntos desglosados por jornada
- Los puntos se calculan según: presencia (titular: 3.0, suplente: 1.0), eventos (gol: 3.0, tarjetas: negativas, MVP: 3.0), bonus resultado, bonus rival fuerte, bonus duelo fuertes, bonus intensidad, gol decisivo

**Uso**: Para la ficha completa del jugador con todos los detalles disponibles, incluyendo puntuaciones de fantasy MVP.

---

### GET /api/jugadores/historial/

**App**: `jugadores`

**Descripción**: Historial completo del jugador consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador

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
      "club_nombre": "string" | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean
    }
  ]
}
```

**Uso**: Para mostrar el historial completo del jugador a lo largo de todas las temporadas.

---

### GET /api/jugadores/valoraciones/

**App**: `jugadores`

**Descripción**: Valoraciones FIFA del jugador con todos los atributos.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar

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

**Uso**: Para mostrar los atributos FIFA del jugador y su media global.

---

### GET /api/jugadores/partidos/

**App**: `jugadores`

**Descripción**: Partidos del jugador con estadísticas detalladas.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar
- `grupo_id` (query, opcional): ID del grupo para filtrar
- `limit` (query, opcional): Número máximo de partidos a devolver

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

**Uso**: Para mostrar los partidos del jugador con estadísticas detalladas y totales agregados.

---

## NOTAS FINALES

- Todas las APIs devuelven JSON
- La mayoría de endpoints requieren `grupo_id` o `temporada_id` para filtrar
- Los endpoints globales combinan datos de todos los grupos
- Las fechas se manejan en formato ISO (YYYY-MM-DD)
- Los parámetros opcionales permiten flexibilidad en las consultas

**Última actualización**: 2025-11-25 (añadidos endpoints de jugadores)




**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "slug": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "edad_display": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "nombre_corto": "string",
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

**Uso**: Para obtener información básica del jugador y su club actual.

---

### GET /api/jugadores/full/

**App**: `jugadores`

**Descripción**: Ficha completa del jugador con todos los bloques opcionales (similar a `/api/clubes/full/`).

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar datos
- `include` (query, opcional, CSV): Bloques a incluir: `valoraciones`, `historial`, `partidos`, `stats`, `fantasy`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Puntos Fantasy MVP (si `include=fantasy`)

**Retorna (bloque fantasy)**:
```json
{
  "fantasy": {
    "temporada_id": number,
    "temporada_nombre": "string",
    "puntos_base_total": number,
    "puntos_con_coef_total": number,
    "goles_total": number,
    "partidos_total": number,
    "puntos_por_jornada": [
      {
        "jornada": number,
        "grupo_id": number,
        "grupo_nombre": "string",
        "puntos_base": number,
        "puntos_con_coef": number,
        "coef_division": number,
        "goles": number,
        "partidos_jugados": number,
        "fecha_calculo": "YYYY-MM-DDTHH:mm:ssZ" | null
      }
    ]
  }
}
```

**Notas sobre puntos Fantasy MVP**:
- `puntos_base_total`: Sumatorio de puntos sin coeficiente división
- `puntos_con_coef_total`: Sumatorio de puntos con coeficiente división aplicado (usado para ranking)
- `puntos_por_jornada`: Array con puntos desglosados por jornada
- Los puntos se calculan según: presencia (titular: 3.0, suplente: 1.0), eventos (gol: 3.0, tarjetas: negativas, MVP: 3.0), bonus resultado, bonus rival fuerte, bonus duelo fuertes, bonus intensidad, gol decisivo

**Uso**: Para la ficha completa del jugador con todos los detalles disponibles, incluyendo puntuaciones de fantasy MVP.

---

### GET /api/jugadores/historial/

**App**: `jugadores`

**Descripción**: Historial completo del jugador consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador

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
      "club_nombre": "string" | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean
    }
  ]
}
```

**Uso**: Para mostrar el historial completo del jugador a lo largo de todas las temporadas.

---

### GET /api/jugadores/valoraciones/

**App**: `jugadores`

**Descripción**: Valoraciones FIFA del jugador con todos los atributos.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar

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

**Uso**: Para mostrar los atributos FIFA del jugador y su media global.

---

### GET /api/jugadores/partidos/

**App**: `jugadores`

**Descripción**: Partidos del jugador con estadísticas detalladas.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar
- `grupo_id` (query, opcional): ID del grupo para filtrar
- `limit` (query, opcional): Número máximo de partidos a devolver

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

**Uso**: Para mostrar los partidos del jugador con estadísticas detalladas y totales agregados.

---

## NOTAS FINALES

- Todas las APIs devuelven JSON
- La mayoría de endpoints requieren `grupo_id` o `temporada_id` para filtrar
- Los endpoints globales combinan datos de todos los grupos
- Las fechas se manejan en formato ISO (YYYY-MM-DD)
- Los parámetros opcionales permiten flexibilidad en las consultas

**Última actualización**: 2025-11-25 (añadidos endpoints de jugadores)




**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "slug": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "edad_display": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "nombre_corto": "string",
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

**Uso**: Para obtener información básica del jugador y su club actual.

---

### GET /api/jugadores/full/

**App**: `jugadores`

**Descripción**: Ficha completa del jugador con todos los bloques opcionales (similar a `/api/clubes/full/`).

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar datos
- `include` (query, opcional, CSV): Bloques a incluir: `valoraciones`, `historial`, `partidos`, `stats`, `fantasy`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Puntos Fantasy MVP (si `include=fantasy`)

**Retorna (bloque fantasy)**:
```json
{
  "fantasy": {
    "temporada_id": number,
    "temporada_nombre": "string",
    "puntos_base_total": number,
    "puntos_con_coef_total": number,
    "goles_total": number,
    "partidos_total": number,
    "puntos_por_jornada": [
      {
        "jornada": number,
        "grupo_id": number,
        "grupo_nombre": "string",
        "puntos_base": number,
        "puntos_con_coef": number,
        "coef_division": number,
        "goles": number,
        "partidos_jugados": number,
        "fecha_calculo": "YYYY-MM-DDTHH:mm:ssZ" | null
      }
    ]
  }
}
```

**Notas sobre puntos Fantasy MVP**:
- `puntos_base_total`: Sumatorio de puntos sin coeficiente división
- `puntos_con_coef_total`: Sumatorio de puntos con coeficiente división aplicado (usado para ranking)
- `puntos_por_jornada`: Array con puntos desglosados por jornada
- Los puntos se calculan según: presencia (titular: 3.0, suplente: 1.0), eventos (gol: 3.0, tarjetas: negativas, MVP: 3.0), bonus resultado, bonus rival fuerte, bonus duelo fuertes, bonus intensidad, gol decisivo

**Uso**: Para la ficha completa del jugador con todos los detalles disponibles, incluyendo puntuaciones de fantasy MVP.

---

### GET /api/jugadores/historial/

**App**: `jugadores`

**Descripción**: Historial completo del jugador consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador

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
      "club_nombre": "string" | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean
    }
  ]
}
```

**Uso**: Para mostrar el historial completo del jugador a lo largo de todas las temporadas.

---

### GET /api/jugadores/valoraciones/

**App**: `jugadores`

**Descripción**: Valoraciones FIFA del jugador con todos los atributos.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar

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

**Uso**: Para mostrar los atributos FIFA del jugador y su media global.

---

### GET /api/jugadores/partidos/

**App**: `jugadores`

**Descripción**: Partidos del jugador con estadísticas detalladas.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar
- `grupo_id` (query, opcional): ID del grupo para filtrar
- `limit` (query, opcional): Número máximo de partidos a devolver

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

**Uso**: Para mostrar los partidos del jugador con estadísticas detalladas y totales agregados.

---

## NOTAS FINALES

- Todas las APIs devuelven JSON
- La mayoría de endpoints requieren `grupo_id` o `temporada_id` para filtrar
- Los endpoints globales combinan datos de todos los grupos
- Las fechas se manejan en formato ISO (YYYY-MM-DD)
- Los parámetros opcionales permiten flexibilidad en las consultas

**Última actualización**: 2025-11-25 (añadidos endpoints de jugadores)




**Retorna**:
```json
{
  "jugador": {
    "id": number,
    "nombre": "string",
    "apodo": "string",
    "slug": "string",
    "foto_url": "string",
    "posicion_principal": "string",
    "fecha_nacimiento": "YYYY-MM-DD" | null,
    "edad_estimacion": number | null,
    "edad_display": number | null,
    "informe_scout": "string",
    "activo": boolean
  },
  "club_actual": {
    "id": number,
    "nombre": "string",
    "nombre_corto": "string",
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

**Uso**: Para obtener información básica del jugador y su club actual.

---

### GET /api/jugadores/full/

**App**: `jugadores`

**Descripción**: Ficha completa del jugador con todos los bloques opcionales (similar a `/api/clubes/full/`).

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar datos
- `include` (query, opcional, CSV): Bloques a incluir: `valoraciones`, `historial`, `partidos`, `stats`, `fantasy`

**Retorna**: Objeto complejo con:
- Información básica del jugador
- Club actual (con enlace)
- Valoraciones FIFA (si `include=valoraciones`)
- Historial consolidado (si `include=historial`)
- Partidos y estadísticas (si `include=partidos,stats`)
- Puntos Fantasy MVP (si `include=fantasy`)

**Retorna (bloque fantasy)**:
```json
{
  "fantasy": {
    "temporada_id": number,
    "temporada_nombre": "string",
    "puntos_base_total": number,
    "puntos_con_coef_total": number,
    "goles_total": number,
    "partidos_total": number,
    "puntos_por_jornada": [
      {
        "jornada": number,
        "grupo_id": number,
        "grupo_nombre": "string",
        "puntos_base": number,
        "puntos_con_coef": number,
        "coef_division": number,
        "goles": number,
        "partidos_jugados": number,
        "fecha_calculo": "YYYY-MM-DDTHH:mm:ssZ" | null
      }
    ]
  }
}
```

**Notas sobre puntos Fantasy MVP**:
- `puntos_base_total`: Sumatorio de puntos sin coeficiente división
- `puntos_con_coef_total`: Sumatorio de puntos con coeficiente división aplicado (usado para ranking)
- `puntos_por_jornada`: Array con puntos desglosados por jornada
- Los puntos se calculan según: presencia (titular: 3.0, suplente: 1.0), eventos (gol: 3.0, tarjetas: negativas, MVP: 3.0), bonus resultado, bonus rival fuerte, bonus duelo fuertes, bonus intensidad, gol decisivo

**Uso**: Para la ficha completa del jugador con todos los detalles disponibles, incluyendo puntuaciones de fantasy MVP.

---

### GET /api/jugadores/historial/

**App**: `jugadores`

**Descripción**: Historial completo del jugador consolidado de `JugadorEnClubTemporada` + `HistorialJugadorScraped`.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador

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
      "club_nombre": "string" | null,
      "club_slug": "string" | null,
      "dorsal": "string" | null,
      "partidos_jugados": number,
      "goles": number,
      "tarjetas_amarillas": number,
      "tarjetas_rojas": number,
      "es_scraped": boolean
    }
  ]
}
```

**Uso**: Para mostrar el historial completo del jugador a lo largo de todas las temporadas.

---

### GET /api/jugadores/valoraciones/

**App**: `jugadores`

**Descripción**: Valoraciones FIFA del jugador con todos los atributos.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar

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

**Uso**: Para mostrar los atributos FIFA del jugador y su media global.

---

### GET /api/jugadores/partidos/

**App**: `jugadores`

**Descripción**: Partidos del jugador con estadísticas detalladas.

**Parámetros**:
- `id_or_slug` (query, requerido): ID numérico o slug del jugador
- `temporada_id` (query, opcional): ID de la temporada para filtrar
- `grupo_id` (query, opcional): ID del grupo para filtrar
- `limit` (query, opcional): Número máximo de partidos a devolver

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

**Uso**: Para mostrar los partidos del jugador con estadísticas detalladas y totales agregados.

---

## NOTAS FINALES

- Todas las APIs devuelven JSON
- La mayoría de endpoints requieren `grupo_id` o `temporada_id` para filtrar
- Los endpoints globales combinan datos de todos los grupos
- Las fechas se manejan en formato ISO (YYYY-MM-DD)
- Los parámetros opcionales permiten flexibilidad en las consultas

**Última actualización**: 2025-11-25 (añadidos endpoints de jugadores)


