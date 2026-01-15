# DOCUMENTACIÓN DE HOOKS — PC FUTSAL

Este archivo contiene la documentación completa de todos los hooks personalizados del frontend de PC FUTSAL.

**IMPORTANTE**: Cada vez que se cree un nuevo hook, debe documentarse aquí inmediatamente.

**Ubicación**: Todos los hooks están en `/frontend/hooks/`

---

## PATRONES COMUNES

Todos los hooks siguen un patrón consistente:

- **React Server Components compatible**: Todos son `"use client"`
- **Estado local**: Manejan `data`, `loading`, `error`
- **Cleanup**: Usan `useEffect` con cleanup (`AbortController` o flags `cancelled`)
- **URLs**:
  - Cliente: URLs relativas (`/api/...`) para evitar CORS/proxy
  - SSR: URLs absolutas usando `NEXT_PUBLIC_API_BASE_URL` (por defecto: `https://pcfutsal.es`)
- **Cache**: `"no-store"` en todas las peticiones `fetch`
- **Validación**: Si `grupoId` es `null/undefined`, limpian estado y no hacen fetch
- **TypeScript**: Todos tienen tipos exportados para los datos que devuelven

---

## CLASIFICACIONES (3 hooks)

### useMiniClasificacion

**Archivo**: `/frontend/hooks/useMiniClasificacion.ts`

**Descripción**: Obtiene una clasificación compacta del grupo con información mínima pero esencial.

**Parámetros**:
- `grupoId` (number | null): ID del grupo

**Endpoint que consume**:
```
GET /api/estadisticas/clasificacion-mini/?grupo_id={grupoId}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
    };
    tabla: Array<{
      pos: number | null;
      club_id: number;
      nombre: string;
      escudo: string;
      pj: number;
      puntos: number;
    }>;
  } | null;
  loading: boolean;
  error: string | null;
}
```

**Uso**: Clasificación compacta para widgets o headers donde se necesita información rápida y concisa.

---

### useClasificacionCompleta

**Archivo**: `/frontend/hooks/useClasificacionCompleta.ts`

**Descripción**: Obtiene la clasificación completa con todos los detalles estadísticos (PJ, PG, PE, PP, GF, GC, DG).

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `scope` ("overall" | "home" | "away", default: "overall"): Ámbito de la clasificación
- `jornada` (number | null, opcional): Número de jornada para ver la clasificación hasta esa jornada

**Endpoint que consume**:
```
GET /api/estadisticas/clasificacion-completa/?grupo_id={grupoId}&scope={scope}&jornada={jornada}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada?: string;
    };
    scope?: "overall" | "home" | "away";
    jornadas_disponibles?: number[];
    jornada_aplicada?: number | null;
    tabla: Array<{
      club_id?: number;
      nombre?: string;
      club_nombre?: string;
      escudo?: string;
      club_escudo?: string;
      puntos?: number;
      pt?: number;
      pj?: number;
      pg?: number;
      pe?: number;
      pp?: number;
      gf?: number;
      gc?: number;
      dg?: number;
    }>;
  } | null;
  loading: boolean;
  error: string | null;
}
```

**Uso**: Clasificación completa con estadísticas detalladas por scope (total, local, visitante).

---

### useClasificacionMultiScope

**Archivo**: `/frontend/hooks/useClasificacionMultiScope.ts`

**Descripción**: Carga las tres clasificaciones (overall, home, away) en paralelo para un mismo grupo. Útil para tabs o vistas que muestran las tres al mismo tiempo.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoints que consume**:
```
GET /api/estadisticas/clasificacion-completa/?grupo_id={grupoId}&scope=overall&jornada={jornada}
GET /api/estadisticas/clasificacion-completa/?grupo_id={grupoId}&scope=home&jornada={jornada}
GET /api/estadisticas/clasificacion-completa/?grupo_id={grupoId}&scope=away&jornada={jornada}
```

**Retorna**:
```typescript
{
  dataByScope: {
    overall: any | null;
    home: any | null;
    away: any | null;
  };
  loadingScope: "overall" | "home" | "away" | null;
  error: string | null;
  fetchScope: (scope: "overall" | "home" | "away", j?: number | null) => Promise<void>;
  fetchSingleScope: (scope: "overall" | "home" | "away", j: number) => Promise<any>;
}
```

**Uso**: Cargar las 3 clasificaciones en paralelo, útil para tabs o vistas que alternan entre las tres clasificaciones.

---

## ESTADÍSTICAS Y KPIs (7 hooks)

### useMatchdayKPIs

**Archivo**: `/frontend/hooks/useMatchdayKPIs.ts`

**Descripción**: Obtiene KPIs agregados de la jornada (goles totales, tarjetas, distribución de resultados).

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoint que consume**:
```
GET /api/estadisticas/kpis-jornada/?grupo_id={grupoId}&jornada={jornada}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    jornada: number | null;
    stats: {
      goles_totales: number;
      amarillas_totales: number;
      rojas_totales: number;
      victorias_local: number;
      empates: number;
      victorias_visitante: number;
    };
  } | null;
  loading: boolean;
  error: string | null;
}
```

**Uso**: KPIs agregados de la jornada para widgets o resúmenes estadísticos.

---

### useTopScorerMatchday

**Archivo**: `/frontend/hooks/useTopScorerMatchday.ts`

**Descripción**: Obtiene el ranking de goleadores de una jornada específica.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoint que consume**:
```
GET /api/estadisticas/goleadores-jornada/?grupo_id={grupoId}&jornada={jornada}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    jornada: number | null;
    goleadores: Array<{
      jugador_id: number;
      nombre: string;
      apodo: string;
      club_id: number;
      club_nombre: string;
      club_posicion: number | null;
      goles_jornada: number;
      foto: string;
      club_escudo?: string;
      pabellon?: string;
      fecha_hora?: string | null;
      partido_id?: number | null;
    }>;
  } | null;
  topScorer: MatchdayScorer | null; // Primer elemento del array goleadores
  loading: boolean;
  error: string | null;
}
```

**Uso**: Ranking de goleadores de la jornada.

---

### useSeasonTopScorers

**Archivo**: `/frontend/hooks/useSeasonTopScorers.ts`

**Descripción**: Obtiene el ranking acumulado de máximos goleadores de la temporada (Pichichi).

**Parámetros**:
- `grupoId` (number | null): ID del grupo

**Endpoint que consume**:
```
GET /api/estadisticas/pichichi-temporada/?grupo_id={grupoId}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    goleadores: Array<{
      jugador_id: number;
      nombre: string;
      apodo: string;
      club_id: number;
      club_nombre: string;
      goles_total: number;
      goles_equipo_total: number;
      contribucion_pct: number; // 0-100 redondeado
      foto: string;
    }>;
  } | null;
  top10: SeasonScorer[]; // Memoizado, top 12
  loading: boolean;
  error: string | null;
}
```

**Uso**: Ranking acumulado de goleadores de la temporada.

---

### useTeamGoals

**Archivo**: `/frontend/hooks/useTeamGoals.ts`

**Descripción**: Obtiene el ranking ofensivo de equipos con estadísticas detalladas de goles.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada (aún no implementado en backend)

**Endpoint que consume**:
```
GET /api/estadisticas/goles-por-equipo/?grupo_id={grupoId}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    equipos: Array<{
      club_id: number;
      club_nombre: string;
      club_escudo: string;
      partidos_jugados: number;
      goles_total: number;
      goles_por_partido: number;
      goles_local: number;
      goles_visitante: number;
      goles_1parte: number;
      goles_2parte: number;
    }>;
  } | null;
  equipos: TeamGoalsRow[]; // Alias del array equipos
  loading: boolean;
  error: string | null;
}
```

**Uso**: Ranking ofensivo de equipos con estadísticas de goles.

---

### useSancionesJornada

**Archivo**: `/frontend/hooks/useSancionesJornada.ts`

**Descripción**: Obtiene los jugadores sancionados en una jornada específica (amarillas, dobles amarillas, rojas).

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoint que consume**:
```
GET /api/estadisticas/sanciones-jornada/?grupo_id={grupoId}&jornada={jornada}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    jornada: number | null;
    sancionados: Array<{
      jugador_id: number;
      nombre: string;
      apodo: string;
      foto: string;
      club_id: number;
      club_nombre: string;
      amarillas: number;
      dobles_amarillas: number;
      rojas: number;
      severidad_puntos: number;
    }>;
  } | null;
  sancionados: SancionJornada[]; // Alias del array sancionados
  loading: boolean;
  error: string | null;
}
```

**Uso**: Sanciones de jugadores en una jornada específica.

---

### useSancionesJugadores

**Archivo**: `/frontend/hooks/useSancionesJugadores.ts`

**Descripción**: Obtiene el ranking acumulado de jugadores más sancionados de la temporada.

**Parámetros**:
- `grupoId` (number | null): ID del grupo

**Endpoint que consume**:
```
GET /api/estadisticas/sanciones-jugadores/?grupo_id={grupoId}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    jugadores: Array<{
      jugador_id: number;
      nombre: string;
      apodo: string;
      foto: string;
      club_id: number;
      club_nombre: string;
      amarillas: number;
      dobles_amarillas: number;
      rojas: number;
      puntos_disciplina: number;
    }>;
  } | null;
  jugadores: SancionJugador[]; // Alias del array jugadores
  loading: boolean;
  error: string | null;
}
```

**Uso**: Ranking acumulado de sanciones de jugadores.

---

### useFairPlayEquipos

**Archivo**: `/frontend/hooks/useFairPlayEquipos.ts`

**Descripción**: Obtiene el ranking de fair play entre equipos (menos puntos = mejor comportamiento).

**Parámetros**:
- `grupoId` (number | null): ID del grupo

**Endpoint que consume**:
```
GET /api/estadisticas/fair-play-equipos/?grupo_id={grupoId}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    equipos: Array<{
      club_id: number;
      club_nombre: string;
      club_escudo: string;
      amarillas: number;
      dobles_amarillas: number;
      rojas: number;
      puntos_fair_play: number;
    }>;
  } | null;
  equipos: FairPlayEquipo[]; // Alias del array equipos
  loading: boolean;
  error: string | null;
}
```

**Uso**: Ranking de fair play de equipos.

---

## VALORACIONES Y MVPs (6 hooks)

### usePartidoEstrella

**Archivo**: `/frontend/hooks/usePartidoEstrella.ts`

**Descripción**: Obtiene el partido más interesante de la jornada según algoritmo de coeficientes.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoint que consume**:
```
GET /api/valoraciones/partido-estrella/?grupo_id={grupoId}&jornada={jornada}
```

**Retorna**:
```typescript
{
  data: any | null; // Partido estrella con detalles
  loading: boolean;
  error: string | null;
}
```

**Uso**: Mostrar el partido estrella de la jornada.

---

### useEquipoJornada

**Archivo**: `/frontend/hooks/useEquipoJornada.ts`

**Descripción**: Obtiene el equipo ideal de la jornada (mejor formación tipo FIFA).

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoint que consume**:
```
GET /api/valoraciones/equipo-jornada/?grupo_id={grupoId}&jornada={jornada}
```

**Retorna**:
```typescript
{
  data: any | null; // Equipo ideal de la jornada
  loading: boolean;
  error: string | null;
}
```

**Uso**: Mostrar el equipo ideal de la jornada (5 ideal).

---

### useJugadoresJornada

**Archivo**: `/frontend/hooks/useJugadoresJornada.ts`

**Descripción**: Obtiene el top de jugadores de la jornada con valoraciones.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoint que consume**:
```
GET /api/valoraciones/jugadores-jornada/?grupo_id={grupoId}&jornada={jornada}
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    jornada: number | null;
    jugador_de_la_jornada: {
      jugador_id: number;
      nombre: string;
      foto: string;
      club_id: number | null;
      club_nombre: string;
      club_escudo: string;
      puntos: number;
      detalles?: string[];
    } | null;
    ranking_jugadores: Array<JugadorJornada>;
  } | null;
  jugadorTop: JugadorJornada | null; // Jugador de la jornada
  loading: boolean;
  error: string | null;
}
```

**Uso**: Top jugadores de la jornada.

---

### useTopJugadoresJornada

**Archivo**: `/frontend/hooks/useTopJugadoresJornada.ts`

**Descripción**: Similar a `useJugadoresJornada` pero con opciones de filtrado y límite.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada
- `opts` (opcional): Opciones adicionales
  - `onlyPorteros` (boolean, opcional): Filtrar solo porteros
  - `limit` (number, opcional): Límite de resultados

**Endpoint que consume**:
```
GET /api/valoraciones/jugadores-jornada/?grupo_id={grupoId}&jornada={jornada}&only_porteros=1 (si aplica)
```

**Retorna**:
```typescript
{
  data: ApiResponse | null; // Misma estructura que useJugadoresJornada
  jugadores: JugadorJornada[]; // Array limitado si se especifica limit
  loading: boolean;
  error: string | null;
}
```

**Uso**: Ranking de jugadores con opciones de filtrado y límite.

---

### usePorteroJornada

**Archivo**: `/frontend/hooks/usePorteroJornada.ts`

**Descripción**: Especializado para obtener el portero de la jornada. Es básicamente `useJugadoresJornada` con `only_porteros=1`.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `jornada` (number | null, opcional): Número de jornada

**Endpoint que consume**:
```
GET /api/valoraciones/jugadores-jornada/?grupo_id={grupoId}&jornada={jornada}&only_porteros=1
```

**Retorna**:
```typescript
{
  data: {
    grupo: {...};
    jornada: number | null;
    jugador_de_la_jornada: PorteroJornada | null;
    ranking_jugadores: PorteroJornada[];
  } | null;
  porteroTop: PorteroJornada | null; // Primer elemento del ranking
  loading: boolean;
  error: string | null;
}
```

**Uso**: Especializado para porteros de la jornada.

---

### useMVPClassification

**Archivo**: `/frontend/hooks/useMVPClassification.ts`

**Descripción**: Obtiene la clasificación de MVP acumulada del grupo.

**Parámetros**:
- `grupoId` (number | null): ID del grupo
- `options` (opcional): Opciones adicionales
  - `jornada` (number | null, opcional): Número de jornada hasta la que calcular
  - `onlyPorteros` (boolean, opcional): Filtrar solo porteros

**Endpoint que consume**:
```
GET /api/valoraciones/mvp-clasificacion/?grupo_id={grupoId}&jornada={jornada}&only_porteros=1 (si aplica)
```

**Retorna**:
```typescript
{
  data: {
    grupo: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    jornada_aplicada: number | null;
    jornadas_disponibles: number[];
    ranking: Array<{
      jugador_id: number;
      nombre: string;
      foto: string;
      club_id: number | null;
      club_nombre: string;
      club_escudo: string;
      es_portero?: boolean;
      puntos_acumulados: number;
      puntos_jornada: number;
      posicion?: number;
    }>;
    prev_ranking?: Array<{ jugador_id: number; posicion: number }>;
  } | null;
  loading: boolean;
  error: string | null;
}
```

**Uso**: Clasificación MVP acumulada de un grupo.

---

## VALORACIONES GLOBALES (3 hooks)

### useGlobalJugadoresJornada

**Archivo**: `/frontend/hooks/useGlobalValoraciones.ts`

**Descripción**: Obtiene el top de jugadores globales de la jornada (todos los grupos combinados).

**Parámetros**:
- `temporadaId` (number | null | undefined): ID de la temporada
- `opts` (opcional): Opciones adicionales
  - `jornada` (number | null, opcional): Número de jornada
  - `weekend` (string | null, opcional): Fecha en formato YYYY-MM-DD
  - `top` (number, opcional, default: 50): Número de jugadores a devolver
  - `onlyPorteros` (boolean, opcional): Filtrar solo porteros
  - `strict` (boolean, opcional): Usar exactamente esa semana

**Endpoint que consume**:
```
GET /api/valoraciones/jugadores-jornada-global/?temporada_id={temporadaId}&jornada={jornada}&weekend={weekend}&top={top}&only_porteros={0|1}&strict={0|1}
```

**Retorna**:
```typescript
{
  data: {
    temporada_id: number;
    jornada?: number | null;
    window?: {
      start?: string | null;
      end?: string | null;
      effective_start?: string | null;
      effective_end?: string | null;
      mode?: string;
      status?: string;
      matched_games?: number;
      min_required?: number;
      fallback_weeks?: number;
    };
    jugador_de_la_jornada_global: GlobalJugador | null;
    ranking_global: GlobalJugador[];
  } | null;
  ranking: GlobalJugador[]; // Alias de ranking_global
  jugadorTop: GlobalJugador | null; // Alias de jugador_de_la_jornada_global
  loading: boolean;
  error: string | null;
}
```

**Uso**: Top jugadores globales de toda la temporada.

---

### useGlobalEquipoJornada

**Archivo**: `/frontend/hooks/useGlobalValoraciones.ts`

**Descripción**: Obtiene el top de equipos globales de la jornada (todos los grupos combinados).

**Parámetros**:
- `temporadaId` (number | null | undefined): ID de la temporada
- `opts` (opcional): Opciones adicionales
  - `jornada` (number | null, opcional): Número de jornada
  - `weekend` (string | null, opcional): Fecha en formato YYYY-MM-DD
  - `top` (number, opcional, default: 30): Número de equipos a devolver
  - `strict` (boolean, opcional): Usar exactamente esa semana

**Endpoint que consume**:
```
GET /api/valoraciones/equipo-jornada-global/?temporada_id={temporadaId}&jornada={jornada}&weekend={weekend}&top={top}&strict={0|1}
```

**Retorna**:
```typescript
{
  data: {
    temporada_id: number;
    jornada?: number | null;
    window?: {...};
    equipo_de_la_jornada_global: GlobalEquipo | null;
    ranking_global: GlobalEquipo[];
  } | null;
  ranking: GlobalEquipo[]; // Alias de ranking_global
  equipoTop: GlobalEquipo | null; // Alias de equipo_de_la_jornada_global
  loading: boolean;
  error: string | null;
}
```

**Uso**: Top equipos globales de toda la temporada.

---

### useMVPGlobal

**Archivo**: `/frontend/hooks/useMVPGlobal.ts`

**Descripción**: Obtiene el ranking global de MVP acumulado (todos los grupos combinados) con ventanas temporales flexibles.

**Parámetros**:
- `opts`: Opciones
  - `from` (string, opcional): Fecha inicio en formato YYYY-MM-DD
  - `to` (string, opcional): Fecha fin en formato YYYY-MM-DD
  - `temporadaId` (number, opcional): ID de la temporada
  - `onlyPorteros` (boolean, opcional): Filtrar solo porteros
  - `top` (number, opcional): Número de jugadores a devolver
  - `strict` (boolean, opcional): Modo estricto
  - `minMatches` (number, opcional): Número mínimo de partidos requeridos

**Endpoint que consume**:
```
GET /api/valoraciones/mvp-global/?from={from}&to={to}&temporada_id={temporadaId}&only_porteros={0|1}&top={top}&strict={0|1}&min_matches={minMatches}
```

**Retorna**:
```typescript
{
  data: {
    temporada_id: number;
    window: {
      start?: string | null;
      end?: string | null;
      effective_start?: string;
      effective_end?: string;
      status?: "ok" | "strict" | "fallback_failed" | "no-window";
      matched_games?: number;
      min_required?: number;
      fallback_weeks?: number;
      mode?: string;
      schema?: string;
    };
    jugador_de_la_jornada_global: MVPGlobalRow | null;
    ranking_global: MVPGlobalRow[];
    detail?: string;
  } | null;
  loading: boolean;
  error: string | null;
}
```

**Nota importante**: Este hook normaliza campos (`puntos`/`puntos_semana`/`puntos_global`/`puntos_totales`) y ordena el ranking por `puntos_global` descendente.

**Uso**: Ranking MVP global con ventanas temporales flexibles.

---

## CLUBES (3 hooks)

### useClubesPorGrupo

**Archivo**: `/frontend/hooks/useClubesPorGrupo.ts`

**Descripción**: Obtiene la lista de clubes de un grupo.

**Parámetros**:
- `grupoId` (number | null): ID del grupo

**Endpoint que consume**:
```
GET /api/clubes/lista/?grupo_id={grupoId}
```

**Retorna**:
```typescript
{
  data: {
    grupo?: {
      id: number;
      nombre: string;
      competicion: string;
      temporada: string;
    };
    count: number;
    results: Array<{
      id: number;
      nombre_oficial: string;
      nombre_corto?: string;
      localidad?: string;
      pabellon?: string;
      escudo_url?: string;
    }>;
  } | null;
  loading: boolean;
  error: string | null;
}
```

**Uso**: Lista de clubes de un grupo.

---

### useClubFull

**Archivo**: `/frontend/hooks/useClubFull.ts`

**Descripción**: Obtiene la ficha completa de un club con todos los bloques opcionales.

**Parámetros**:
- `params`: Objeto con opciones
  - `clubId` (number | null, opcional): ID del club
  - `slug` (string | null, opcional): Slug del club (alternativa a clubId)
  - `temporadaId` (number | null, opcional): ID de la temporada
  - `grupoId` (number | null, opcional): ID del grupo
  - `include` (string | string[], opcional): CSV o array de bloques a incluir: `progress,history,awards,media,notes,travel,staff,roster`
  - `enabled` (boolean, opcional, default: true): Auto-fetch al montar si hay clubId/slug válidos

**Endpoint que consume**:
```
GET /api/clubes/full/?club_id={clubId}|slug={slug}&temporada_id={temporadaId}&grupo_id={grupoId}&include={include}
```

**Retorna**:
```typescript
{
  data: ClubFullResponse | null; // Objeto complejo con:
  // - club: Información del club
  // - contexto: Temporada y grupo
  // - clasificacion_actual: Posición, puntos, estadísticas
  // - participaciones: Array de participaciones en grupos
  // - plantilla?: Roster de jugadores (si include='roster')
  // - staff?: Array de staff (si include='staff')
  // - valoracion?: Valoración del club
  // - series?: Gráficos de progreso y histórico
  // - awards?: Array de premios
  // - media?: Array de medios (vídeos, imágenes)
  // - notas?: Array de notas
  // - travel?: Estadísticas de viajes
  loading: boolean;
  error: string | null;
  refetch: (signal?: AbortSignal) => Promise<void>; // Método para recargar manualmente
}
```

**Uso**: Ficha completa de un club con todos los bloques opcionales. Incluye método `refetch()` para recargar manualmente.

---

### useClubHistorico

**Archivo**: `/frontend/hooks/useClubHistorico.ts`

**Descripción**: Obtiene el histórico de temporadas en las que un club ha participado, incluyendo división, posición y puntos de cada temporada.

**Parámetros**:
- `clubId` (string | string[] | undefined): ID numérico o slug del club

**Endpoint que consume**:
```
GET /api/clubes/historico/?club_id={clubId}
GET /api/clubes/historico/?slug={clubId}
```

**Retorna**:
```typescript
{
  data: ClubHistoricoResponse | null; // {
  //   club_id: number;
  //   club_nombre: string;
  //   historico: Array<{
  //     temporada: string;          // Ej: "2024/2025"
  //     division: string;            // Ej: "Tercera División"
  //     grupo: string;               // Ej: "Grupo XV"
  //     grupo_id: number;
  //     competicion_id: number;
  //     posicion: number | null;     // Posición final
  //     puntos: number;              // Puntos totales
  //   }>;
  // }
  loading: boolean;
  error: string | null;
}
```

**Uso**: Para mostrar el histórico de temporadas del club en la página de detalle. Se usa en el componente `HistoricoTemporadas`.

---

### useJugadorFull

**Archivo**: `/frontend/hooks/useJugadorFull.ts`

**Descripción**: Obtiene la ficha completa de un jugador con todos los bloques opcionales (similar a `useClubFull`).

**Parámetros**:
- `jugadorId` (number | string | null, opcional): ID numérico o slug del jugador
- `temporadaId` (number | null, opcional): ID de la temporada para filtrar datos
- `include` (string | string[], opcional): CSV o array de bloques a incluir: `valoraciones`, `historial`, `partidos`, `stats`, `fantasy`
- `enabled` (boolean, opcional, default: true): Auto-fetch al montar si hay jugadorId válido

**Endpoint que consume**:
```
GET /api/jugadores/full/?id_or_slug={jugadorId}&temporada_id={temporadaId}&include={include}
```

**Nota**: El hook acepta tanto ID numérico como slug del jugador. El slug se usa para URLs SEO-friendly (ej: `/jugadores/daniel-domene-garcia`).

**Retorna**:
```typescript
{
  data: JugadorFullResponse | null; // Objeto complejo con:
  // - jugador: Información básica del jugador
  // - club_actual: Club actual con enlace
  // - temporada_actual: Temporada actual
  // - dorsal_actual: Dorsal actual
  // - stats_actuales?: Estadísticas actuales (si include='stats')
  // - valoraciones?: Valoraciones FIFA (si include='valoraciones')
  // - historial?: Historial consolidado (si include='historial')
  // - partidos?: Partidos y estadísticas (si include='partidos')
  // - fantasy?: Puntos Fantasy MVP (si include='fantasy')
  loading: boolean;
  error: string | null;
  refetch: (signal?: AbortSignal) => Promise<void>; // Método para recargar manualmente
}
```

**Uso**: Ficha completa de un jugador con todos los bloques opcionales. Incluye método `refetch()` para recargar manualmente.

---

## MAPEO COMPLETO HOOKS ↔ ENDPOINTS

| Hook | Endpoint |
|------|----------|
| `useMiniClasificacion` | `/api/estadisticas/clasificacion-mini/` |
| `useClasificacionCompleta` | `/api/estadisticas/clasificacion-completa/` |
| `useClasificacionMultiScope` | `/api/estadisticas/clasificacion-completa/` (×3 scopes) |
| `useMatchdayKPIs` | `/api/estadisticas/kpis-jornada/` |
| `useTopScorerMatchday` | `/api/estadisticas/goleadores-jornada/` |
| `useSeasonTopScorers` | `/api/estadisticas/pichichi-temporada/` |
| `useTeamGoals` | `/api/estadisticas/goles-por-equipo/` |
| `useSancionesJornada` | `/api/estadisticas/sanciones-jornada/` |
| `useSancionesJugadores` | `/api/estadisticas/sanciones-jugadores/` |
| `useFairPlayEquipos` | `/api/estadisticas/fair-play-equipos/` |
| `usePartidoEstrella` | `/api/valoraciones/partido-estrella/` |
| `useEquipoJornada` | `/api/valoraciones/equipo-jornada/` |
| `useJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `useTopJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `usePorteroJornada` | `/api/valoraciones/jugadores-jornada/?only_porteros=1` |
| `useMVPClassification` | `/api/valoraciones/mvp-clasificacion/` |
| `useGlobalJugadoresJornada` | `/api/valoraciones/jugadores-jornada-global/` |
| `useGlobalEquipoJornada` | `/api/valoraciones/equipo-jornada-global/` |
| `useMVPGlobal` | `/api/valoraciones/mvp-global/` |
| `useClubesPorGrupo` | `/api/clubes/lista/` |
| `useClubFull` | `/api/clubes/full/` |
| `useClubHistorico` | `/api/clubes/historico/` |
| `useJugadorFull` | `/api/jugadores/full/` |

---

## NOTAS FINALES

- Todos los hooks validan `grupoId` antes de hacer fetch (excepto los globales que usan `temporadaId`)
- Patrón de cancelación: `AbortController` o flags `cancelled` para evitar race conditions
- URLs relativas en cliente para aprovechar proxy de Nginx y evitar CORS
- TypeScript: Todos los hooks tienen tipos exportados para los datos que devuelven
- Los hooks globales permiten filtrado por ventanas temporales (`from`, `to`, `weekend`)

**Última actualización**: 2025-11-28 (useJugadorFull actualizado para aceptar slugs)




## MAPEO COMPLETO HOOKS ↔ ENDPOINTS

| Hook | Endpoint |
|------|----------|
| `useMiniClasificacion` | `/api/estadisticas/clasificacion-mini/` |
| `useClasificacionCompleta` | `/api/estadisticas/clasificacion-completa/` |
| `useClasificacionMultiScope` | `/api/estadisticas/clasificacion-completa/` (×3 scopes) |
| `useMatchdayKPIs` | `/api/estadisticas/kpis-jornada/` |
| `useTopScorerMatchday` | `/api/estadisticas/goleadores-jornada/` |
| `useSeasonTopScorers` | `/api/estadisticas/pichichi-temporada/` |
| `useTeamGoals` | `/api/estadisticas/goles-por-equipo/` |
| `useSancionesJornada` | `/api/estadisticas/sanciones-jornada/` |
| `useSancionesJugadores` | `/api/estadisticas/sanciones-jugadores/` |
| `useFairPlayEquipos` | `/api/estadisticas/fair-play-equipos/` |
| `usePartidoEstrella` | `/api/valoraciones/partido-estrella/` |
| `useEquipoJornada` | `/api/valoraciones/equipo-jornada/` |
| `useJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `useTopJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `usePorteroJornada` | `/api/valoraciones/jugadores-jornada/?only_porteros=1` |
| `useMVPClassification` | `/api/valoraciones/mvp-clasificacion/` |
| `useGlobalJugadoresJornada` | `/api/valoraciones/jugadores-jornada-global/` |
| `useGlobalEquipoJornada` | `/api/valoraciones/equipo-jornada-global/` |
| `useMVPGlobal` | `/api/valoraciones/mvp-global/` |
| `useClubesPorGrupo` | `/api/clubes/lista/` |
| `useClubFull` | `/api/clubes/full/` |
| `useClubHistorico` | `/api/clubes/historico/` |
| `useJugadorFull` | `/api/jugadores/full/` |

---

## NOTAS FINALES

- Todos los hooks validan `grupoId` antes de hacer fetch (excepto los globales que usan `temporadaId`)
- Patrón de cancelación: `AbortController` o flags `cancelled` para evitar race conditions
- URLs relativas en cliente para aprovechar proxy de Nginx y evitar CORS
- TypeScript: Todos los hooks tienen tipos exportados para los datos que devuelven
- Los hooks globales permiten filtrado por ventanas temporales (`from`, `to`, `weekend`)

**Última actualización**: 2025-11-28 (useJugadorFull actualizado para aceptar slugs)




## MAPEO COMPLETO HOOKS ↔ ENDPOINTS

| Hook | Endpoint |
|------|----------|
| `useMiniClasificacion` | `/api/estadisticas/clasificacion-mini/` |
| `useClasificacionCompleta` | `/api/estadisticas/clasificacion-completa/` |
| `useClasificacionMultiScope` | `/api/estadisticas/clasificacion-completa/` (×3 scopes) |
| `useMatchdayKPIs` | `/api/estadisticas/kpis-jornada/` |
| `useTopScorerMatchday` | `/api/estadisticas/goleadores-jornada/` |
| `useSeasonTopScorers` | `/api/estadisticas/pichichi-temporada/` |
| `useTeamGoals` | `/api/estadisticas/goles-por-equipo/` |
| `useSancionesJornada` | `/api/estadisticas/sanciones-jornada/` |
| `useSancionesJugadores` | `/api/estadisticas/sanciones-jugadores/` |
| `useFairPlayEquipos` | `/api/estadisticas/fair-play-equipos/` |
| `usePartidoEstrella` | `/api/valoraciones/partido-estrella/` |
| `useEquipoJornada` | `/api/valoraciones/equipo-jornada/` |
| `useJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `useTopJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `usePorteroJornada` | `/api/valoraciones/jugadores-jornada/?only_porteros=1` |
| `useMVPClassification` | `/api/valoraciones/mvp-clasificacion/` |
| `useGlobalJugadoresJornada` | `/api/valoraciones/jugadores-jornada-global/` |
| `useGlobalEquipoJornada` | `/api/valoraciones/equipo-jornada-global/` |
| `useMVPGlobal` | `/api/valoraciones/mvp-global/` |
| `useClubesPorGrupo` | `/api/clubes/lista/` |
| `useClubFull` | `/api/clubes/full/` |
| `useClubHistorico` | `/api/clubes/historico/` |
| `useJugadorFull` | `/api/jugadores/full/` |

---

## NOTAS FINALES

- Todos los hooks validan `grupoId` antes de hacer fetch (excepto los globales que usan `temporadaId`)
- Patrón de cancelación: `AbortController` o flags `cancelled` para evitar race conditions
- URLs relativas en cliente para aprovechar proxy de Nginx y evitar CORS
- TypeScript: Todos los hooks tienen tipos exportados para los datos que devuelven
- Los hooks globales permiten filtrado por ventanas temporales (`from`, `to`, `weekend`)

**Última actualización**: 2025-11-28 (useJugadorFull actualizado para aceptar slugs)




## MAPEO COMPLETO HOOKS ↔ ENDPOINTS

| Hook | Endpoint |
|------|----------|
| `useMiniClasificacion` | `/api/estadisticas/clasificacion-mini/` |
| `useClasificacionCompleta` | `/api/estadisticas/clasificacion-completa/` |
| `useClasificacionMultiScope` | `/api/estadisticas/clasificacion-completa/` (×3 scopes) |
| `useMatchdayKPIs` | `/api/estadisticas/kpis-jornada/` |
| `useTopScorerMatchday` | `/api/estadisticas/goleadores-jornada/` |
| `useSeasonTopScorers` | `/api/estadisticas/pichichi-temporada/` |
| `useTeamGoals` | `/api/estadisticas/goles-por-equipo/` |
| `useSancionesJornada` | `/api/estadisticas/sanciones-jornada/` |
| `useSancionesJugadores` | `/api/estadisticas/sanciones-jugadores/` |
| `useFairPlayEquipos` | `/api/estadisticas/fair-play-equipos/` |
| `usePartidoEstrella` | `/api/valoraciones/partido-estrella/` |
| `useEquipoJornada` | `/api/valoraciones/equipo-jornada/` |
| `useJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `useTopJugadoresJornada` | `/api/valoraciones/jugadores-jornada/` |
| `usePorteroJornada` | `/api/valoraciones/jugadores-jornada/?only_porteros=1` |
| `useMVPClassification` | `/api/valoraciones/mvp-clasificacion/` |
| `useGlobalJugadoresJornada` | `/api/valoraciones/jugadores-jornada-global/` |
| `useGlobalEquipoJornada` | `/api/valoraciones/equipo-jornada-global/` |
| `useMVPGlobal` | `/api/valoraciones/mvp-global/` |
| `useClubesPorGrupo` | `/api/clubes/lista/` |
| `useClubFull` | `/api/clubes/full/` |
| `useClubHistorico` | `/api/clubes/historico/` |
| `useJugadorFull` | `/api/jugadores/full/` |

---

## NOTAS FINALES

- Todos los hooks validan `grupoId` antes de hacer fetch (excepto los globales que usan `temporadaId`)
- Patrón de cancelación: `AbortController` o flags `cancelled` para evitar race conditions
- URLs relativas en cliente para aprovechar proxy de Nginx y evitar CORS
- TypeScript: Todos los hooks tienen tipos exportados para los datos que devuelven
- Los hooks globales permiten filtrado por ventanas temporales (`from`, `to`, `weekend`)

**Última actualización**: 2025-11-28 (useJugadorFull actualizado para aceptar slugs)


