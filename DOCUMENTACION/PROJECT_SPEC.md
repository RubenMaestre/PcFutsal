PROJECT_SPEC.md — PC FUTSAL
1) Visión general del proyecto
Objetivo del proyecto

PC FUTSAL es una plataforma completa de datos, análisis, rankings, valoraciones y fantasy para el fútbol sala amateur y semiprofesional.

Integra:

Scraping automatizado de FFCV.

Modelos avanzados: partidos, jugadores, clubes, clasificaciones, coeficientes.

Sistema FIFA-like de valoraciones.

Fantasy semanal con jugadores reales.

Perfiles públicos y paneles privados.

Frontend Next.js multilenguaje, rápido y optimizado.

El objetivo es crear la referencia digital del futsal español, con un sistema robusto, escalable y visualmente impecable.

Estado actual
Backend (Django + DRF)

⚠️ Proyecto en PRODUCCIÓN en pcfutsal.es
Todo está configurado y funcionando: Nginx, Gunicorn, PM2, dominio, puertos.

Apps activas en /backend:

administracion

arbitros

clubes

destacados

estadisticas

fantasy

historial

jugadores

nucleo

partidos

scraping

staff

status

usuarios

valoraciones

Base de datos: MySQL
- Motor: django.db.backends.mysql
- Variables de entorno en: /home/rubenmaestre/pcfutsal.es/backend/.env
- Variables requeridas: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- Charset: utf8mb4
- Settings: /home/rubenmaestre/pcfutsal.es/backend/administracion/settings.py

Scraping funcional, actualizado por management commands.

Endpoints DRF operativos: clasificación, partidos, estrellas, estadísticas, fantasy, valoraciones.

Frontend (Next.js 15 + React + TS + Tailwind)

Estructura real dentro de /frontend:

/app/[lang] (App Router multilenguaje)

/components (25+ componentes principales)

/home_components (componentes específicos de home)

/rankings_components (componentes de rankings)

/hooks (19 hooks personalizados para data-fetching)

/i18n (7 idiomas: es, en, de, fr, it, pt, val)

/lib (utilidades)

/public (assets estáticos)

Componentes complejos funcionando:

GroupShell, HomeShell, GlobalMVPCard, GlobalTeamCard, GlobalTopMatches, etc.

Puerto de desarrollo y producción: 3055

Despliegue automatizado mediante script:

Script: /home/rubenmaestre/pcfutsal.es/deploy_pcfutsal.sh

Desde frontend: npm run deploy

O manualmente: ./deploy_pcfutsal.sh (desde raíz del proyecto)

Modo de trabajo

El director (Rubén) indica lo que hay que hacer.

El agente propone un plan breve (3–6 pasos).

Espera confirmación.

Ejecuta modificaciones solo dentro del workspace permitido.

2) Stack y versiones
Frontend

Framework: Next.js 15.5.6 + React 18.3.1

Lenguaje: TypeScript 5.3.0

Estilos: Tailwind CSS 3.4.0 + shadcn/ui

UI: lucide-react ^0.548.0, framer-motion ^12.23.24, recharts

i18n: JSON por idioma + App Router (7 idiomas: es, en, de, fr, it, pt, val)

Imágenes: /public

Build: next build

Runtime: PM2 en producción (proceso: pcfutsal-frontend, puerto 3055)

Scripts npm disponibles:
- dev: next dev -p 3055
- build: next build
- start: next start -p 3055
- lint: next lint
- deploy: bash ../deploy_pcfutsal.sh (ejecuta script de deploy)

Backend

Django 5.2.7

Django REST Framework

Base de datos: MySQL (variables de entorno en backend/.env)

Modelo de usuario personalizado: usuarios.Usuario

Configuración: /home/rubenmaestre/pcfutsal.es/backend/administracion/settings.py
- Carga variables de entorno con python-dotenv desde backend/.env
- Idioma: es-es, Zona horaria: Europe/Madrid
- Variables DB requeridas: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

Requests / BeautifulSoup (scraping)

Gestión del scraping: scraping.core + management commands

Autenticación: sistema propio simplificado (no JWT aún)

Servicios clave:

Partido Estrella

Sistema de coeficientes (Club + División)

Rankings

Fantasy semanal

Gestión completa de jugadores/clubes/partidos

Infra

Servidor: Hetzner VPS

Dominio: pcfutsal.es (configurado y funcionando en producción)

Reverse proxy: Nginx (configurado y activo)

Backend: Gunicorn (servicio systemd: pcfutsal.service)

Frontend: Next.js + PM2 (proceso: pcfutsal-frontend, puerto 3055)

Variables de entorno:
- /home/rubenmaestre/pcfutsal.es/.env (GUNICORN_PASSWORD para script de deploy)
- /home/rubenmaestre/pcfutsal.es/backend/.env (DB_*, SECRET_KEY, DEBUG, etc. para Django)
- Variables del sistema en /etc/ (el agente no puede tocarlas)

Script de deploy automatizado:

Ubicación: /home/rubenmaestre/pcfutsal.es/deploy_pcfutsal.sh

El script automatiza:
1. Build del frontend (npm run build)
2. Reinicio de PM2 (pcfutsal-frontend)
3. Reinicio de Gunicorn (pcfutsal.service)
4. Test y reload de Nginx

Lee GUNICORN_PASSWORD desde: /home/rubenmaestre/pcfutsal.es/.env

Ejecución:
- Desde raíz: ./deploy_pcfutsal.sh
- Desde frontend: npm run deploy

Comandos manuales (si se necesita ejecutar por separado):

sudo systemctl restart pcfutsal
sudo systemctl restart nginx
npm run build (en /frontend)
pm2 restart pcfutsal-frontend

3) Estructura real del proyecto
/home/rubenmaestre/pcfutsal.es/
pcfutsal.es/
├── backend/
│   ├── administracion/
│   │   └── settings.py (configuración Django, carga .env)
│   ├── arbitros/
│   ├── clubes/
│   ├── destacados/
│   ├── estadisticas/
│   ├── fantasy/
│   ├── historial/
│   ├── jugadores/
│   ├── nucleo/
│   ├── partidos/
│   ├── scraping/
│   ├── staff/
│   ├── status/
│   ├── usuarios/
│   ├── valoraciones/
│   ├── data_clean/
│   ├── data_raw/
│   ├── media/
│   ├── logs/
│   ├── staticfiles/
│   ├── .env (variables de entorno: DB_*, SECRET_KEY, etc. - NO tocar)
│   ├── db.sqlite3
│   └── manage.py
│
├── frontend/
│   ├── app/
│   │   └── [lang]/
│   ├── components/
│   ├── home_components/
│   ├── rankings_components/
│   ├── hooks/
│   ├── i18n/
│   ├── lib/
│   ├── public/
│   ├── tailwind.config.js
│   ├── package.json
│   ├── next.config.js
│   └── tsconfig.json
│
├── DOCUMENTACION/
│   ├── AGENT_GLOBAL_PLAYBOOK.md
│   ├── DECISIONS.md
│   ├── DIARIO/
│   ├── PROJECT_SPEC.md
│   ├── PROJECT_TREE.md
│   ├── PROJECT_VISION.md
│   └── TASK.md
│
├── deploy_pcfutsal.sh
├── .env (GUNICORN_PASSWORD)
└── venv/

4) Endpoints y APIs activas

PC FUTSAL no está centralizado en una app api única, sino repartido por apps. Endpoints organizados por funcionalidad:

═══════════════════════════════════════════════════════════════════════════════

STATUS

/api/status/last_update/
- GET: Última actualización del scraping sincronizado
- Parámetros: Accept-Language (header, opcional)
- Retorna: last_update_display, detalle

═══════════════════════════════════════════════════════════════════════════════

NUCLEO (Configuración y filtros)

/api/nucleo/filter-context/
- GET: Contexto de filtros para temporadas, competiciones y grupos
- Retorna: temporada_activa, competiciones con sus grupos

═══════════════════════════════════════════════════════════════════════════════

ESTADISTICAS (14 endpoints principales)

Información general del grupo:
- GET /api/estadisticas/grupo-info/?competicion_slug=XX&grupo_slug=YY&temporada=ZZ&jornada=WW
  * Endpoint completo que devuelve TODO el paquete de datos del grupo en una sola llamada
  * Incluye: clasificación, resultados, KPIs, goleadores, pichichi, sanciones, fair play, etc.

Clasificaciones:
- GET /api/estadisticas/clasificacion-mini/?grupo_id=XX
  * Clasificación compacta con pos, club, escudo, PJ, puntos, racha
- GET /api/estadisticas/clasificacion-completa/?grupo_id=XX&scope=overall|home|away&jornada=YY
  * Clasificación completa con todos los detalles (PJ, PG, PE, PP, GF, GC, DG)
  * Scope: overall (total), home (local), away (visitante)
- GET /api/estadisticas/clasificacion-evolucion/?grupo_id=XX&scope=overall|home|away&parameter=pts|gf|gc
  * Evolución jornada a jornada para gráficos de líneas

Partidos y jornadas:
- GET /api/estadisticas/resultados-jornada/?grupo_id=XX&jornada=YY
  * Partidos de una jornada con marcadores, árbitros, pabellón, fechas
  * Si no se especifica jornada, devuelve la última jugada
- GET /api/estadisticas/kpis-jornada/?grupo_id=XX&jornada=YY
  * KPIs agregados de la jornada: goles totales, tarjetas, victorias local/visitante/empates

Goleadores:
- GET /api/estadisticas/goleadores-jornada/?grupo_id=XX&jornada=YY
  * Ranking de goleadores de una jornada específica con % de contribución
- GET /api/estadisticas/pichichi-temporada/?grupo_id=XX
  * Ranking acumulado de máximos goleadores de la temporada
- GET /api/estadisticas/goles-por-equipo/?grupo_id=XX
  * Ranking ofensivo de equipos: goles totales, media, local/visitante, 1ª/2ª parte

Disciplina:
- GET /api/estadisticas/sanciones-jornada/?grupo_id=XX&jornada=YY
  * Jugadores sancionados en una jornada (amarillas, dobles, rojas) con severidad
- GET /api/estadisticas/sanciones-jugadores/?grupo_id=XX
  * Ranking acumulado de jugadores más sancionados de la temporada
- GET /api/estadisticas/fair-play-equipos/?grupo_id=XX
  * Ranking de fair play entre equipos (menos puntos = mejor comportamiento)

Coeficientes:
- GET /api/estadisticas/coeficientes-clubes/?grupo_id=XX&jornada=YY
  * Coeficientes de valoración FIFA-like de los clubes
- POST /api/estadisticas/coeficientes-clubes/
  * Crear/actualizar coeficiente manual (admin)

═══════════════════════════════════════════════════════════════════════════════

CLUBES (3 endpoints)

- GET /api/clubes/lista/?grupo_id=XX
- GET /api/clubes/lista/?competicion_id=XX&temporada_id=YY
  * Lista de clubes del grupo/competición con mini-stats (posición, puntos, GF, GC, racha)
- GET /api/clubes/detalle/?club_id=XX&temporada_id=YY
  * Detalle básico del club + participaciones + plantilla y staff (si temporada_id)
- GET /api/clubes/full/?club_id=XX&temporada_id=YY&grupo_id=ZZ&include=progress,history,awards,media,notes,travel,staff,roster
  * Ficha completa del club con todos los bloques opcionales
  * Include: CSV de bloques a incluir (progress, history, awards, media, notes, travel, staff, roster)

═══════════════════════════════════════════════════════════════════════════════

VALORACIONES (8 endpoints)

Jornada específica:
- GET /api/valoraciones/partido-estrella/?grupo_id=XX&jornada=YY
  * Partido más interesante de la jornada según algoritmo de coeficientes
- GET /api/valoraciones/equipo-jornada/?grupo_id=XX&jornada=YY
  * Equipo ideal de la jornada (mejor formación tipo FIFA)
- GET /api/valoraciones/jugadores-jornada/?grupo_id=XX&jornada=YY
  * Top jugadores de la jornada con valoraciones
- GET /api/valoraciones/mvp-clasificacion/?grupo_id=XX
  * Clasificación de MVP acumulada del grupo

Global (todos los grupos):
- GET /api/valoraciones/equipo-jornada-global/?jornada=YY
  * Equipo ideal global de la jornada (todos los grupos)
- GET /api/valoraciones/jugadores-jornada-global/?jornada=YY
  * Top jugadores globales de la jornada
- GET /api/valoraciones/partidos-top-global/?jornada=YY
- GET /api/valoraciones/partidos-estrella-global/?jornada=YY
  * Top partidos globales de la jornada
- GET /api/valoraciones/mvp-global/
  * Ranking global de MVP acumulado

═══════════════════════════════════════════════════════════════════════════════

APPS SIN ENDPOINTS REST PÚBLICOS

Las siguientes apps NO tienen views REST configuradas (solo modelos/lógica interna):
- partidos (modelos y eventos, usados por otras APIs)
- jugadores (modelos usados por otras APIs)
- destacados (modelos, posiblemente usado internamente)
- historial (modelos, posiblemente usado internamente)
- fantasy (modelos, endpoints pueden estar en desarrollo)
- scraping (management commands, no REST)
- arbitros (modelos, usados por otras APIs)
- staff (modelos, usados por APIs de clubes)
- usuarios (modelos de autenticación)

═══════════════════════════════════════════════════════════════════════════════

SCRAPING (Management Commands)

Estos se ejecutan desde Django shell o cron, no son endpoints REST:

python manage.py scrape_equipos
python manage.py scrape_jugadores
python manage.py scrape_partidos

═══════════════════════════════════════════════════════════════════════════════

HOOKS DEL FRONTEND (20 hooks personalizados)

Todos los hooks están en `/frontend/hooks/` y siguen un patrón consistente:

Patrones comunes:
- Todos son "use client" (React Server Components compatible)
- Manejan estado local: data, loading, error
- Usan useEffect con cleanup (AbortController o flags cancelled)
- URLs relativas en cliente (`/api/...`) para evitar CORS/proxy
- URLs absolutas en SSR usando NEXT_PUBLIC_API_BASE_URL (por defecto: https://pcfutsal.es)
- Cache: "no-store" en todas las peticiones fetch
- Validación de grupoId: si es null/undefined, limpian estado y no hacen fetch

Hooks por categoría:

1) CLASIFICACIONES (3 hooks)

useMiniClasificacion(grupoId)
- Endpoint: GET /api/estadisticas/clasificacion-mini/?grupo_id=XX
- Retorna: { grupo, tabla } con pos, club_id, nombre, escudo, pj, puntos
- Uso: Clasificación compacta para widgets o headers

useClasificacionCompleta(grupoId, scope, jornada?)
- Endpoint: GET /api/estadisticas/clasificacion-completa/?grupo_id=XX&scope=YY&jornada=ZZ
- Parámetros: scope ∈ { "overall", "home", "away" }, jornada opcional
- Retorna: { grupo, scope, jornada_aplicada, jornadas_disponibles, tabla }
- Uso: Clasificación completa con estadísticas detalladas por scope

useClasificacionMultiScope(grupoId, jornada?)
- Endpoint: Múltiples llamadas a /api/estadisticas/clasificacion-completa/ (overall, home, away)
- Retorna: { dataByScope: { overall, home, away }, loadingScope, error, fetchScope, fetchSingleScope }
- Uso: Cargar las 3 clasificaciones en paralelo, útil para tabs

2) ESTADÍSTICAS Y KPIs (7 hooks)

useMatchdayKPIs(grupoId, jornada?)
- Endpoint: GET /api/estadisticas/kpis-jornada/?grupo_id=XX&jornada=YY
- Retorna: { grupo, jornada, stats: { goles_totales, amarillas_totales, rojas_totales, victorias_local, empates, victorias_visitante } }
- Uso: KPIs agregados de la jornada

useTopScorerMatchday(grupoId, jornada?)
- Endpoint: GET /api/estadisticas/goleadores-jornada/?grupo_id=XX&jornada=YY
- Retorna: { grupo, jornada, goleadores[] } + topScorer (primer elemento)
- Uso: Ranking de goleadores de la jornada

useSeasonTopScorers(grupoId)
- Endpoint: GET /api/estadisticas/pichichi-temporada/?grupo_id=XX
- Retorna: { grupo, goleadores[] } + top10 (memoizado, top 12)
- Uso: Ranking acumulado de goleadores de la temporada

useTeamGoals(grupoId, jornada?)
- Endpoint: GET /api/estadisticas/goles-por-equipo/?grupo_id=XX
- Retorna: { grupo, equipos[] } con estadísticas ofensivas (goles por partido, local/visitante, 1parte/2parte)
- Uso: Ranking ofensivo de equipos

useSancionesJornada(grupoId, jornada?)
- Endpoint: GET /api/estadisticas/sanciones-jornada/?grupo_id=XX&jornada=YY
- Retorna: { grupo, jornada, sancionados[] } + sancionados (array)
- Uso: Sanciones de jugadores en una jornada específica

useSancionesJugadores(grupoId)
- Endpoint: GET /api/estadisticas/sanciones-jugadores/?grupo_id=XX
- Retorna: { grupo, jugadores[] } + jugadores (array acumulado)
- Uso: Ranking acumulado de sanciones de jugadores

useFairPlayEquipos(grupoId)
- Endpoint: GET /api/estadisticas/fair-play-equipos/?grupo_id=XX
- Retorna: { grupo, equipos[] } + equipos (ranking fair play)
- Uso: Ranking de fair play de equipos

3) VALORACIONES Y MVPs (6 hooks)

usePartidoEstrella(grupoId, jornada?)
- Endpoint: GET /api/valoraciones/partido-estrella/?grupo_id=XX&jornada=YY
- Retorna: Partido más destacado de la jornada con detalles
- Uso: Mostrar el partido estrella

useEquipoJornada(grupoId, jornada?)
- Endpoint: GET /api/valoraciones/equipo-jornada/?grupo_id=XX&jornada=YY
- Retorna: Equipo ideal de la jornada
- Uso: Mostrar el 5 ideal de la jornada

useJugadoresJornada(grupoId, jornada?)
- Endpoint: GET /api/valoraciones/jugadores-jornada/?grupo_id=XX&jornada=YY
- Retorna: { grupo, jornada, jugador_de_la_jornada, ranking_jugadores[] } + jugadorTop
- Uso: Top jugadores de la jornada

useTopJugadoresJornada(grupoId, jornada?, opts?)
- Endpoint: GET /api/valoraciones/jugadores-jornada/?grupo_id=XX&jornada=YY&only_porteros=1 (opcional)
- Parámetros: opts = { onlyPorteros?, limit? }
- Retorna: { data, jugadores[], loading, error }
- Uso: Ranking de jugadores con opciones de filtrado y límite

usePorteroJornada(grupoId, jornada?)
- Endpoint: GET /api/valoraciones/jugadores-jornada/?grupo_id=XX&jornada=YY&only_porteros=1
- Retorna: { data, porteroTop, loading, error }
- Uso: Especializado para porteros de la jornada

useMVPClassification(grupoId, options?)
- Endpoint: GET /api/valoraciones/mvp-clasificacion/?grupo_id=XX&jornada=YY&only_porteros=1 (opcional)
- Parámetros: options = { jornada?, onlyPorteros? }
- Retorna: { grupo, jornada_aplicada, jornadas_disponibles, ranking[], prev_ranking[] }
- Uso: Clasificación MVP acumulada de un grupo

4) VALORACIONES GLOBALES (2 hooks)

useGlobalJugadoresJornada(temporadaId, opts?)
- Endpoint: GET /api/valoraciones/jugadores-jornada-global/?temporada_id=XX&jornada=YY&weekend=ZZ&top=NN&only_porteros=0&strict=0
- Parámetros: opts = { jornada?, weekend? (YYYY-MM-DD), top? (default: 50), onlyPorteros?, strict? }
- Retorna: { data: { temporada_id, jornada?, window?, jugador_de_la_jornada_global, ranking_global[] }, ranking, jugadorTop, loading, error }
- Uso: Top jugadores globales de toda la temporada

useGlobalEquipoJornada(temporadaId, opts?)
- Endpoint: GET /api/valoraciones/equipo-jornada-global/?temporada_id=XX&jornada=YY&weekend=ZZ&top=NN&strict=0
- Parámetros: opts = { jornada?, weekend? (YYYY-MM-DD), top? (default: 30), strict? }
- Retorna: { data: { temporada_id, jornada?, window?, equipo_de_la_jornada_global, ranking_global[] }, ranking, equipoTop, loading, error }
- Uso: Top equipos globales de toda la temporada

useMVPGlobal(opts)
- Endpoint: GET /api/valoraciones/mvp-global/?from=XX&to=YY&temporada_id=ZZ&only_porteros=0&top=NN&strict=0&min_matches=MM
- Parámetros: opts = { from? (YYYY-MM-DD), to? (YYYY-MM-DD), temporadaId?, onlyPorteros?, top?, strict?, minMatches? }
- Retorna: { temporada_id, window: { start, end, status, matched_games, ... }, jugador_de_la_jornada_global, ranking_global[] }
- Nota: Normaliza campos (puntos/puntos_semana/puntos_global/puntos_totales) y ordena por puntos_global descendente
- Uso: Ranking MVP global con ventanas temporales flexibles

5) CLUBES (3 hooks)

useClubesPorGrupo(grupoId)
- Endpoint: GET /api/clubes/lista/?grupo_id=XX
- Retorna: { grupo?, count, results: ClubLite[] } donde ClubLite = { id, nombre_oficial, nombre_corto?, localidad?, pabellon?, escudo_url? }
- Uso: Lista de clubes de un grupo

useClubFull(params)
- Endpoint: GET /api/clubes/full/?club_id=XX|slug=YY&temporada_id=ZZ&grupo_id=WW&include=progress,history,awards,...
- Parámetros: { clubId?, slug?, temporadaId?, grupoId?, include? (CSV o array), enabled? (default: true) }
- Retorna: ClubFullResponse completo con: club, contexto, clasificacion_actual, participaciones[], plantilla?, staff?, valoracion?, series?, awards?, media?, notas?, travel?
- Métodos: refetch(signal?) para recargar manualmente
- Uso: Ficha completa de un club con todos los bloques opcionales

useClubHistorico(clubId)
- Endpoint: GET /api/clubes/historico/?club_id=XX|slug=YY
- Parámetros: clubId (string | string[] | undefined): ID numérico o slug del club
- Retorna: ClubHistoricoResponse con histórico de temporadas (temporada, division, grupo, posicion, puntos)
- Uso: Histórico de temporadas del club

6) JUGADORES (1 hook)

useJugadorFull(params)
- Endpoint: GET /api/jugadores/full/?jugador_id=XX&temporada_id=YY&include=valoraciones,historial,partidos,stats,fantasy
- Parámetros: { jugadorId?, temporadaId?, include? (CSV o array), enabled? (default: true) }
- Retorna: JugadorFullResponse completo con: jugador, club_actual, temporada_actual, dorsal_actual, stats_actuales?, valoraciones?, historial?, partidos?, fantasy?
- Métodos: refetch(signal?) para recargar manualmente
- Uso: Ficha completa de un jugador con todos los bloques opcionales

Mapeo completo hooks ↔ endpoints:
- useMiniClasificacion → /api/estadisticas/clasificacion-mini/
- useClasificacionCompleta → /api/estadisticas/clasificacion-completa/
- useClasificacionMultiScope → /api/estadisticas/clasificacion-completa/ (×3 scopes)
- useMatchdayKPIs → /api/estadisticas/kpis-jornada/
- useTopScorerMatchday → /api/estadisticas/goleadores-jornada/
- useSeasonTopScorers → /api/estadisticas/pichichi-temporada/
- useTeamGoals → /api/estadisticas/goles-por-equipo/
- useSancionesJornada → /api/estadisticas/sanciones-jornada/
- useSancionesJugadores → /api/estadisticas/sanciones-jugadores/
- useFairPlayEquipos → /api/estadisticas/fair-play-equipos/
- usePartidoEstrella → /api/valoraciones/partido-estrella/
- useEquipoJornada → /api/valoraciones/equipo-jornada/
- useJugadoresJornada → /api/valoraciones/jugadores-jornada/
- useTopJugadoresJornada → /api/valoraciones/jugadores-jornada/
- usePorteroJornada → /api/valoraciones/jugadores-jornada/ (with only_porteros=1)
- useMVPClassification → /api/valoraciones/mvp-clasificacion/
- useGlobalJugadoresJornada → /api/valoraciones/jugadores-jornada-global/
- useGlobalEquipoJornada → /api/valoraciones/equipo-jornada-global/
- useMVPGlobal → /api/valoraciones/mvp-global/
- useClubesPorGrupo → /api/clubes/lista/
- useClubFull → /api/clubes/full/
- useClubHistorico → /api/clubes/historico/
- useJugadorFull → /api/jugadores/full/

Notas importantes:
- Todos los hooks validan grupoId antes de hacer fetch (excepto los globales que usan temporadaId)
- Patrón de cancelación: AbortController o flags `cancelled` para evitar race conditions
- URLs relativas en cliente para aprovechar proxy de Nginx y evitar CORS
- TypeScript: Todos los hooks tienen tipos exportados para los datos que devuelven

5) Permisos para edición — Frontend
Permitido

Crear/modificar componentes en:

/components

/home_components

/rankings_components

Crear hooks dentro de /hooks

Ajustar Tailwind (solo clases)

Mejoras visuales o UX locales

Cambios en i18n (solo contenido, no estructura)

Restringido (requiere permiso)

Instalar librerías npm

Cambiar estructura de /app/[lang]

Cambiar archivos de configuración: next.config.js, tailwind.config.js

Tocar scripts o runtime de PM2

Modificar el script deploy_pcfutsal.sh

6) Permisos para edición — Backend
Permitido

Editar views existentes

Editar serializers existentes

Crear utilidades internas

Mejorar logique de scraping

Mejorar performance o agregar filtros

Restringido (requiere permiso explícito)

Crear apps Django nuevas

Añadir modelos nuevos

Ejecutar migraciones

Instalar librerías pip

Alterar settings críticos (CORS, DB, SECURE_*, middleware)

Modificar administracion/settings.py (especialmente configuración de base de datos)

Tocar archivo backend/.env (contiene credenciales sensibles)

Cambiar el flujo del scraping de forma estructural

7) Comandos permitidos
Frontend

npm run dev (solo desarrollo local)

npm run build (solo si el usuario lo autoriza explícitamente)

npm run lint

npm run typecheck

❌ NO puede ejecutar: npm run deploy (solo el usuario lo ejecuta)

Backend

Activar venv (si existe)

python manage.py runserver (solo desarrollo local)

python manage.py check (verificación de sintaxis y configuración)

python -m py_compile (verificación de sintaxis Python)

python3 -c "..." (scripts Python inline para correcciones)

Comandos de navegación y utilidades: cd, head, tail, grep, sed, cat, ls, find (dentro del workspace)

❌ NO PERMITIDO

PM2

systemctl

sudo

nginx

certbot

comandos fuera del workspace

⚠️ REGLA CRÍTICA: Ejecución automática de comandos de backend y solución de errores

El agente DEBE ejecutar automáticamente (sin preguntar) los siguientes comandos cuando sea necesario para el trabajo en curso o para solucionar errores:

Comandos de backend que se ejecutan automáticamente:
- cd /home/rubenmaestre/pcfutsal.es/backend (navegación)
- source ../venv/bin/activate (activación de entorno virtual)
- python manage.py check (verificación de sintaxis y configuración)
- python -m py_compile archivo.py (verificación de sintaxis Python)
- python3 -c "..." (scripts Python inline para correcciones)
- head, tail, grep, sed (utilidades para procesamiento de archivos)
- Cualquier comando relacionado con la solución de errores de sintaxis, indentación, o configuración del backend

Solución de errores:
- Cuando se detecta un error (sintaxis, indentación, configuración, etc.), el agente DEBE:
  1. Identificar el error específico
  2. Ejecutar comandos de diagnóstico automáticamente (python manage.py check, python -m py_compile, etc.)
  3. Corregir el problema
  4. Verificar que el error está resuelto
  5. Continuar hasta que todos los errores estén solucionados
  6. NO preguntar al usuario durante este proceso de corrección

Esta regla aplica especialmente cuando:
- Se están corrigiendo errores de sintaxis o indentación
- Se está verificando que el backend funciona correctamente
- Se están aplicando correcciones iterativas hasta resolver un problema
- Se está trabajando en tareas relacionadas con el backend que requieren verificación continua

8) Flow real de deploy (PC FUTSAL)

⚠️ CONTEXTO: Proyecto en PRODUCCIÓN en pcfutsal.es
Todo está configurado. El deploy solo actualiza código y reinicia servicios.

Script de deploy automatizado:

El usuario ejecuta el script de deploy cuando hay cambios:

Opción 1 (recomendada): Desde la carpeta frontend
cd /home/rubenmaestre/pcfutsal.es/frontend
npm run deploy

Opción 2: Desde la raíz del proyecto
cd /home/rubenmaestre/pcfutsal.es
./deploy_pcfutsal.sh

El script automatiza todo el proceso:
1. Build del frontend (Next.js)
2. Reinicio de PM2 (pcfutsal-frontend)
3. Reinicio de Gunicorn (pcfutsal.service)
4. Test y reload de Nginx

El agente nunca ejecuta estos comandos.

Si se necesitan comandos manuales por separado:

sudo systemctl restart pcfutsal
sudo systemctl restart nginx
npm run build (en /frontend)
pm2 restart pcfutsal-frontend

Flujo para el agente:

1. Detecta que un cambio requiere deploy

2. Informa:
   - Qué ha cambiado
   - Si requiere build
   - Qué servicios necesitan reinicio

3. Espera confirmación

4. NO ejecuta nada relacionado con deploy

5. El usuario ejecuta el script de deploy cuando corresponda

9) Tareas típicas que puede realizar el agente

Crear nuevas vistas Next.js para jugadores, clubes, partidos.

Añadir bloques de datos en la Home.

Mejorar componentes existentes (GroupShell, GlobalTopMatches, etc.).

Añadir hooks de datos.

Ajustar lógica de ratings o estadísticas.

Mejorar scraping.

Añadir endpoints (si no requieren modelos nuevos).

10) Conexión obligatoria con archivos de control DOCUMENTACION

El agente SIEMPRE debe leer antes de actuar:

DOCUMENTACION/AGENT_GLOBAL_PLAYBOOK.md (guía principal de trabajo)

DOCUMENTACION/PROJECT_SPEC.md (este archivo)

DOCUMENTACION/PROJECT_VISION.md (visión y objetivos del proyecto)

DOCUMENTACION/DECISIONS.md (decisiones técnicas registradas)

DOCUMENTACION/TASK.md (tareas activas, siguientes y completadas)

DOCUMENTACION/PROJECT_TREE.md (estructura actual del proyecto)

DOCUMENTACION/DIARIO/YYYY-MM-DD.txt (registro diario de cambios)

11) Diario de trabajo (DOCUMENTACION/DIARIO/)

Reglas:

Un archivo por día: YYYY-MM-DD.txt

Ubicación: /home/rubenmaestre/pcfutsal.es/DOCUMENTACION/DIARIO/

Registrar:

Cambios en frontend

Cambios en backend

Mejoras

Refactors

Documentación

Tareas completadas

— Una línea por cambio
— Crear archivo si no existe
— Añadir entradas al final

12) Criterios de aceptación por cambio

El frontend compila y se renderiza correctamente.

El backend sigue funcionando sin romper endpoints.

No se añaden dependencias sin permiso.

No se toca infraestructura del servidor.

No se filtran secretos.

Todos los cambios están explicados en el resumen del agente.

13) Límites explícitos

NO instalar librerías nuevas.

NO modificar Nginx, PM2 o systemctl.

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

14) Mensaje inicial recomendado del agente

“He leído AGENT_GLOBAL_PLAYBOOK.md y PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar.”
NO instalar librerías nuevas.

NO modificar Nginx, PM2 o systemctl.

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

14) Mensaje inicial recomendado del agente

“He leído AGENT_GLOBAL_PLAYBOOK.md y PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar.”
NO instalar librerías nuevas.

NO modificar Nginx, PM2 o systemctl.

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

14) Mensaje inicial recomendado del agente

“He leído AGENT_GLOBAL_PLAYBOOK.md y PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar.”
NO instalar librerías nuevas.

NO modificar Nginx, PM2 o systemctl.

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

14) Mensaje inicial recomendado del agente

“He leído AGENT_GLOBAL_PLAYBOOK.md y PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar.”