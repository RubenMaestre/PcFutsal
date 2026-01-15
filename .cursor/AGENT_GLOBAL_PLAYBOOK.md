AGENT GLOBAL PLAYBOOK — PC FUTSAL

Rol del agente: desarrollador autónomo supervisado
Rol del usuario: director técnico del proyecto
Regla de oro: antes de actuar, el agente propone un plan breve (3–6 pasos) y espera confirmación.

═══════════════════════════════════════════════════════════════════════════════

0) Propósito

Definir cómo debe operar el agente en PC FUTSAL (plataforma Django + Next.js en Hetzner en PRODUCCIÓN) garantizando:

⚠️ IMPORTANTE: El proyecto está en PRODUCCIÓN en pcfutsal.es
Todo está configurado (Nginx, Gunicorn, PM2, dominio, puertos).
NO estamos configurando, estamos trabajando en producción activa.

- No romper producción (proyecto activo en pcfutsal.es)
- No tocar infraestructura del servidor (ya está configurada)
- Entregas incrementales y controladas
- Respeto absoluto por la arquitectura actual del backend y frontend
- Seguridad, limpieza y control del contexto en cada operación

═══════════════════════════════════════════════════════════════════════════════

1) Alcance del workspace (rutas permitidas y prohibidas)

✅ Permitido (lectura/escritura SOLO dentro de):

/home/rubenmaestre/pcfutsal.es/backend
/home/rubenmaestre/pcfutsal.es/frontend
/home/rubenmaestre/pcfutsal.es/.cursor
  * /home/rubenmaestre/pcfutsal.es/.cursor/BACKEND (scripts y recursos del backend)
  * /home/rubenmaestre/pcfutsal.es/.cursor/FRONTEND (scripts y recursos del frontend)
/home/rubenmaestre/pcfutsal.es/deploy_pcfutsal.sh

❌ Prohibido:

- Cualquier ruta fuera de /home/rubenmaestre/pcfutsal.es/
- Directorios del sistema: /etc/*, /var/*, /usr/*, /opt/*, /lib/*
- Otros proyectos del servidor (rumaza, danbegre, meiva, noghi, etc.)
- Variables de entorno del sistema (/etc/*)
- Configuración de Nginx, PM2 o systemd fuera del workspace

═══════════════════════════════════════════════════════════════════════════════

2) Infraestructura y entorno del proyecto

Backend (Django 5 + DRF)

- Framework: Django 5.2.7 + Django REST Framework
- Base de datos: MySQL
  * Motor: django.db.backends.mysql
  * Variables de entorno: /home/rubenmaestre/pcfutsal.es/backend/.env
  * Variables requeridas: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
  * Charset: utf8mb4
- Settings: /home/rubenmaestre/pcfutsal.es/backend/administracion/settings.py
  * Carga variables con python-dotenv desde backend/.env
  * Idioma: es-es, Zona horaria: Europe/Madrid
- Modelo de usuario personalizado: usuarios.Usuario
- Autenticación: sistema propio simplificado (no JWT aún)
- 15 apps activas (NO inventar nuevas sin permiso):
  * administracion (settings, configuración principal)
  * arbitros
  * clubes
  * destacados
  * estadisticas
  * fantasy
  * historial
  * jugadores
  * nucleo (modelos base)
  * partidos
  * scraping
  * staff
  * status
  * usuarios
  * valoraciones

Servicios críticos del backend:
- Partido Estrella (sistema de valoración de partidos)
- Sistema de coeficientes (Club + División)
- Rankings globales y por posición
- Fantasy semanal
- Scraping automatizado de FFCV (management commands)
- Gestión completa de jugadores/clubes/partidos/clasificaciones

Frontend (Next.js 15 + React + TypeScript)

- Framework: Next.js 15.5.6 + React 18.3.1
- Lenguaje: TypeScript 5.3.0
- Estilos: Tailwind CSS 3.4.0 + shadcn/ui
- UI: lucide-react, framer-motion, recharts
- i18n: Sistema multilenguaje con 7 idiomas (es, en, de, fr, it, pt, val)
- Estructura: App Router con /app/[lang]/...
- Puerto de desarrollo: 3055
- Puerto de producción: 3055 (PM2)

Estructura del frontend:
- /app/[lang]/ (rutas multilenguaje)
  * clasificacion/
  * clubes/
  * competicion/
  * mvp/
  * rankings/
- /components (25+ componentes principales)
- /home_components (componentes específicos de la home)
- /rankings_components (componentes de rankings)
- /hooks (19 hooks personalizados para data-fetching)
- /i18n (archivos JSON por idioma)
- /lib (utilidades, i18n.ts)
- /public (assets estáticos)

Servidor e infraestructura

⚠️ PROYECTO EN PRODUCCIÓN ⚠️
El proyecto está publicado y funcionando en pcfutsal.es
Todo está configurado: Nginx, Gunicorn, PM2, puertos, dominio.
NO se requiere configuración inicial ni setup de servidor.

- Servidor: Hetzner VPS
- Dominio: pcfutsal.es (configurado y funcionando)
- Reverse proxy: Nginx (configurado y activo)
- Backend runtime: Gunicorn (servicio systemd: pcfutsal.service, en producción)
- Frontend runtime: PM2 (proceso: pcfutsal-frontend, puerto 3055, en producción)
- Variables de entorno:
  * /home/rubenmaestre/pcfutsal.es/.env (GUNICORN_PASSWORD para deploy)
  * /home/rubenmaestre/pcfutsal.es/backend/.env (DB_*, SECRET_KEY, etc. para Django)
  * Variables del sistema en /etc/ (el agente NO puede tocarlas)
- Script de deploy: /home/rubenmaestre/pcfutsal.es/deploy_pcfutsal.sh (para actualizaciones)

Regla clave: El agente no toca nada fuera del workspace.
No toca Nginx, PM2 ni Gunicorn directamente.
No toca systemctl ni servicios del sistema.
El script de deploy solo REINICIA servicios ya existentes, no los configura.

═══════════════════════════════════════════════════════════════════════════════

3) Herramientas / acciones PROHIBIDAS

Comandos prohibidos:
- sudo, systemctl, service, pm2, nginx, certbot, kill, reboot, etc.
- Cualquier comando que requiera privilegios de root

Acciones prohibidas:
- Tocar /etc/* o variables del sistema
- Ejecutar comandos de servidor directamente
- Instalar paquetes (npm/pip) sin autorización explícita
- Tocar producción sin confirmación del usuario
- Modificar configuración de servicios (Nginx, PM2, systemd)

═══════════════════════════════════════════════════════════════════════════════

4) Despliegue (flujo y script automatizado)

⚠️ CONTEXTO: El proyecto ya está en producción en pcfutsal.es
El script de deploy solo actualiza el código desplegado, NO configura servidor.

Script de deploy automatizado

Ubicación: /home/rubenmaestre/pcfutsal.es/deploy_pcfutsal.sh

El script actualiza la producción existente:
1. Build del frontend (Next.js)
2. Reinicio de PM2 (pcfutsal-frontend ya existente, puerto 3055)
3. Reinicio del servicio Gunicorn (pcfutsal.service ya configurado)
4. Test y reload de Nginx (ya configurado para pcfutsal.es)

El script lee GUNICORN_PASSWORD desde:
/home/rubenmaestre/pcfutsal.es/.env

Importante: Todo (Nginx, puertos, dominio) ya está configurado.
Este script solo actualiza el código y reinicia servicios existentes.

Comandos manuales (usuario ejecuta cuando es necesario):

sudo systemctl restart pcfutsal
sudo systemctl restart nginx
npm run build (en /frontend)
pm2 restart pcfutsal-frontend

REGLA FUNDAMENTAL

El agente NO puede ejecutar NINGUNO de esos comandos.
Ni el script de deploy ni los comandos individuales.
Solo puede sugerirlos cuando el usuario los solicite explícitamente.

Flujo permitido del agente:

1. El agente analiza cambios realizados
2. Propone un plan breve (3–6 pasos)
3. Espera confirmación explícita
4. Aplica cambios en el workspace (solo archivos)
5. Proporciona al finalizar:
   - Rutas de archivos modificados
   - Pasos de prueba recomendados
   - Indicación de si requiere build
   - Si requiere deploy, informa qué comandos ejecutar

El usuario ejecuta manualmente el script de deploy cuando corresponda:
./deploy_pcfutsal.sh

═══════════════════════════════════════════════════════════════════════════════

5) Backend — reglas específicas

NO crear nuevas apps Django sin permiso explícito.

NO ejecutar migraciones sin autorización.

Si el cambio requiere migración:
- Lo detecta
- Propone la migración
- Espera confirmación
- Solo entonces la crea (no la ejecuta)

Mantener integridad de:
- Sistema de scraping (core y management commands)
- Vistas de valoraciones
- Endpoints de estadísticas
- Sistema de coeficientes
- Estructura actual de apps multipartidas

Endpoints principales activos (26 endpoints en total):

STATUS (1 endpoint):
- GET /api/status/last_update/ (última actualización del scraping)

NUCLEO (1 endpoint):
- GET /api/nucleo/filter-context/ (contexto de temporadas, competiciones, grupos)

ESTADISTICAS (14 endpoints):
- GET /api/estadisticas/grupo-info/ (endpoint completo con todos los datos del grupo)
- GET /api/estadisticas/clasificacion-mini/ (clasificación compacta)
- GET /api/estadisticas/clasificacion-completa/ (clasificación completa, scope: overall/home/away)
- GET /api/estadisticas/clasificacion-evolucion/ (evolución jornada a jornada)
- GET /api/estadisticas/resultados-jornada/ (partidos de una jornada)
- GET /api/estadisticas/kpis-jornada/ (KPIs agregados de la jornada)
- GET /api/estadisticas/goleadores-jornada/ (ranking goleadores jornada)
- GET /api/estadisticas/pichichi-temporada/ (ranking acumulado goleadores)
- GET /api/estadisticas/goles-por-equipo/ (ranking ofensivo de equipos)
- GET /api/estadisticas/sanciones-jornada/ (sanciones de una jornada)
- GET /api/estadisticas/sanciones-jugadores/ (ranking acumulado sanciones)
- GET /api/estadisticas/fair-play-equipos/ (ranking fair play)
- GET /api/estadisticas/coeficientes-clubes/ (coeficientes FIFA-like)
- POST /api/estadisticas/coeficientes-clubes/ (crear/actualizar coeficiente, admin)

CLUBES (3 endpoints):
- GET /api/clubes/lista/ (lista por grupo o competición+temporada)
- GET /api/clubes/detalle/ (detalle básico + plantilla/staff)
- GET /api/clubes/full/ (ficha completa con bloques opcionales)

VALORACIONES (8 endpoints):
- GET /api/valoraciones/partido-estrella/ (partido más interesante de la jornada)
- GET /api/valoraciones/equipo-jornada/ (equipo ideal de la jornada)
- GET /api/valoraciones/jugadores-jornada/ (top jugadores jornada)
- GET /api/valoraciones/mvp-clasificacion/ (clasificación MVP acumulada)
- GET /api/valoraciones/equipo-jornada-global/ (equipo ideal global)
- GET /api/valoraciones/jugadores-jornada-global/ (top jugadores globales)
- GET /api/valoraciones/partidos-top-global/ (top partidos globales)
- GET /api/valoraciones/mvp-global/ (ranking MVP global)

Management commands de scraping:
- scrape_equipos
- scrape_jugadores
- scrape_partidos

Nota: Apps sin endpoints REST públicos: partidos, jugadores, destacados, historial, fantasy, scraping, arbitros, staff, usuarios (solo modelos/lógica interna)

En cambios críticos:
- Debe proveer un plan de rollback explícito
- Documentar impacto en endpoints existentes

═══════════════════════════════════════════════════════════════════════════════

6) Frontend — reglas específicas

No introducir librerías nuevas sin permiso explícito.

Mantener arquitectura Next.js 15 + App Router.

Mantener Tailwind como fuente principal de estilos.

Evitar CSS externo innecesario.

No tocar i18n sin confirmación (solo contenido permitido, no estructura).

No modificar rutas /app/[lang]/... sin análisis previo.

Componentes principales existentes:
- GroupShell, HomeShell
- GlobalMVPCard, GlobalTeamCard, GlobalTopMatches
- ClasificacionShell, FullClassificationShell
- MatchCard, MatchCarousel
- Y muchos más (consultar /components, /home_components, /rankings_components)

Hooks personalizados (20 hooks en /frontend/hooks/):

Patrones comunes:
- Todos son "use client" (React Server Components compatible)
- Manejan estado: data, loading, error
- URLs relativas en cliente (`/api/...`), absolutas en SSR (NEXT_PUBLIC_API_BASE_URL)
- Validación de grupoId: si es null, limpian estado y no hacen fetch
- Cache: "no-store" en todas las peticiones
- Cancelación: AbortController o flags `cancelled` para evitar race conditions

Hooks por categoría:

CLASIFICACIONES (3):
- useMiniClasificacion(grupoId) → /api/estadisticas/clasificacion-mini/
- useClasificacionCompleta(grupoId, scope, jornada?) → /api/estadisticas/clasificacion-completa/
- useClasificacionMultiScope(grupoId, jornada?) → carga overall/home/away en paralelo

ESTADÍSTICAS Y KPIs (7):
- useMatchdayKPIs(grupoId, jornada?) → /api/estadisticas/kpis-jornada/
- useTopScorerMatchday(grupoId, jornada?) → /api/estadisticas/goleadores-jornada/
- useSeasonTopScorers(grupoId) → /api/estadisticas/pichichi-temporada/
- useTeamGoals(grupoId, jornada?) → /api/estadisticas/goles-por-equipo/
- useSancionesJornada(grupoId, jornada?) → /api/estadisticas/sanciones-jornada/
- useSancionesJugadores(grupoId) → /api/estadisticas/sanciones-jugadores/
- useFairPlayEquipos(grupoId) → /api/estadisticas/fair-play-equipos/

VALORACIONES Y MVPs (6):
- usePartidoEstrella(grupoId, jornada?) → /api/valoraciones/partido-estrella/
- useEquipoJornada(grupoId, jornada?) → /api/valoraciones/equipo-jornada/
- useJugadoresJornada(grupoId, jornada?) → /api/valoraciones/jugadores-jornada/
- useTopJugadoresJornada(grupoId, jornada?, opts?) → /api/valoraciones/jugadores-jornada/ (con filtros)
- usePorteroJornada(grupoId, jornada?) → /api/valoraciones/jugadores-jornada/?only_porteros=1
- useMVPClassification(grupoId, options?) → /api/valoraciones/mvp-clasificacion/

VALORACIONES GLOBALES (2):
- useGlobalJugadoresJornada(temporadaId, opts?) → /api/valoraciones/jugadores-jornada-global/
- useGlobalEquipoJornada(temporadaId, opts?) → /api/valoraciones/equipo-jornada-global/
- useMVPGlobal(opts) → /api/valoraciones/mvp-global/ (normaliza campos y ordena por puntos_global)

CLUBES (3):
- useClubesPorGrupo(grupoId) → /api/clubes/lista/
- useClubFull(params) → /api/clubes/full/ (ficha completa con bloques opcionales, incluye refetch())
- useClubHistorico(clubId) → /api/clubes/historico/ (histórico de temporadas)

JUGADORES (1):
- useJugadorFull(params) → /api/jugadores/full/ (ficha completa con bloques opcionales, incluye refetch())

Ver PROJECT_SPEC.md sección "HOOKS DEL FRONTEND" para detalles completos de parámetros, tipos de retorno y ejemplos de uso.

Idiomas soportados:
- es (español)
- en (inglés)
- de (alemán)
- fr (francés)
- it (italiano)
- pt (portugués)
- val (valenciano)

═══════════════════════════════════════════════════════════════════════════════

7) Terminal — lista blanca de comandos

✅ El agente puede usar:

Frontend:
- npm run lint
- npm run typecheck
- npm run dev (solo para desarrollo local, no en producción)
- npm run build (solo si el usuario lo autoriza explícitamente)

Backend:
- Activar venv (si existe): source venv/bin/activate
- python manage.py runserver (solo desarrollo local, nunca en producción)
- python manage.py makemigrations (solo si autorizado, nunca migrate)
- python manage.py check (verificación de sintaxis y configuración)
- python -m py_compile (verificación de sintaxis Python)
- Comandos de gestión de datos (si autorizados)

Utilitarios:
- date, ls, cat, grep, find (dentro del workspace)
- git status, git diff (solo lectura, nunca commit/push)
- cd, head, tail, sed (para navegación y procesamiento de archivos)

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

❌ NO puede:

- Ejecutar PM2 (start, restart, stop, list, etc.)
- Ejecutar systemctl (cualquier comando)
- Ejecutar sudo (cualquier comando)
- Ejecutar nginx (cualquier comando)
- Ejecutar comandos root
- Reiniciar servicios
- Ejecutar el script deploy_pcfutsal.sh

═══════════════════════════════════════════════════════════════════════════════

8) Proceso obligatorio antes de cualquier acción

Documentación obligatoria a leer:

1. .cursor/AGENT_GLOBAL_PLAYBOOK.md (este archivo)
2. .cursor/PROJECT_SPEC.md
3. .cursor/PROJECT_VISION.md
4. .cursor/DECISIONS.md
5. .cursor/TASK.md
6. .cursor/PROJECT_TREE.md (para conocer estructura actual)

Flujo de trabajo:

1. Leer documentación relevante
2. Analizar el problema o tarea
3. Proponer plan breve de 3–6 pasos
4. Esperar confirmación explícita del director
   ⚠️ EXCEPCIÓN: Si el director ha aprobado un roadmap o fases específicas, el agente puede ejecutar directamente sin pedir confirmación adicional para cada paso, siguiendo las instrucciones del roadmap/fase aprobada.
5. Ejecutar cambios mínimos necesarios
6. Al finalizar, entregar:
   - Lista de archivos modificados (rutas completas)
   - Pasos de prueba recomendados
   - Indicación de si requiere build
   - Si requiere deploy, indicar qué comandos ejecutar
   - Plan de rollback (si aplica)
   - Registro en diario/documentación (OBLIGATORIO)

═══════════════════════════════════════════════════════════════════════════════

9) Estilo de código

Backend (Python/Django)

- Variables y funciones: snake_case
- Clases: PascalCase
- Lógica limpia en serializers y views
- Evitar lógica duplicada
- Respetar patrones de apps actuales
- Comentarios claros cuando la lógica es compleja

Frontend (React/TypeScript)

- Componentes: PascalCase
- Funciones y variables: camelCase
- Componentes pequeños y tipados
- Hooks personalizados cuando haya repetición
- Mantener estilo UI actual (PC FUTSAL)
- Tailwind consistente (evitar clases inline excesivas)
- Nada de "CSS suelto" sin motivo justificado
- TypeScript estricto (evitar any innecesarios)

═══════════════════════════════════════════════════════════════════════════════

10) Seguridad

Nunca mostrar valores de variables de entorno.

Nunca exponer secretos, contraseñas o API keys.

Nunca mostrar valores de variables de base de datos (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT).

El archivo .env en backend/.env contiene credenciales sensibles — no acceder ni mostrar contenido.

No alterar CORS/CSRF sin permiso y análisis previo.

No imprimir trazas sensibles en logs.

No modificar configuración de seguridad (SECURE_*, ALLOWED_HOSTS, etc.) sin permiso.

No modificar settings.py sin permiso explícito (especialmente configuración de base de datos).

═══════════════════════════════════════════════════════════════════════════════

11) Documentación viva obligatoria

⚠️ REGLA FUNDAMENTAL: Cada cambio realizado DEBE quedar registrado en diario, documentación o documentos.

El agente debe actualizar estos archivos cuando los cambios lo requieran:

Estructura:
- .cursor/PROJECT_TREE.md (tras cambios estructurales: crear, renombrar, eliminar archivos/carpetas)

Tareas y decisiones:
- .cursor/TASK.md (solo si el director lo indica explícitamente)
- .cursor/DECISIONS.md (solo si el director ordena "Registra esta decisión")

Diario diario:
- .cursor/DIARIO/YYYY-MM-DD.txt (registrar cada cambio realizado el día) — OBLIGATORIO

Formato del diario:
- Un archivo por día: YYYY-MM-DD.txt
- Una línea por cambio
- Crear archivo si no existe
- Añadir entradas al final
- Registrar: cambios frontend, backend, mejoras, refactors, documentación, tareas completadas, scripts creados

Documentación técnica:
- .cursor/DOCUMENTACION/APIS.md (al crear nuevas APIs)
- .cursor/DOCUMENTACION/HOOKS.md (al crear nuevos hooks)

Scripts y recursos:
- Scripts del backend: .cursor/BACKEND/ (guardar scripts relacionados con backend)
- Scripts del frontend: .cursor/FRONTEND/ (guardar scripts relacionados con frontend)

Especificaciones:
- .cursor/PROJECT_SPEC.md (solo si hay cambios arquitectónicos significativos y el director lo solicita)
- .cursor/PROJECT_VISION.md (no modificar sin autorización explícita)

═══════════════════════════════════════════════════════════════════════════════

12) Acciones permitidas sin permiso

Ajustes menores visuales (colores, espaciados, tamaños).

Reescritura de textos (sin cambiar estructura).

Refactors locales sin cambiar APIs ni contratos.

Mejoras UX seguras (sin tocar lógica crítica).

Ordenar componentes o hooks sin alterar funcionalidad.

Actualizar PROJECT_TREE.md tras cambios estructurales.

Añadir entradas al diario del día.

Ejecutar comandos npm (npm run build, npm run lint, npm run typecheck, etc.) cuando sea necesario para el trabajo en curso.

Cambios en backend y frontend siguiendo instrucciones de roadmap o fases aprobadas por el director (no requiere confirmación adicional por cada paso).

Guardar scripts en las carpetas correspondientes:
- Scripts del backend → .cursor/BACKEND/
- Scripts del frontend → .cursor/FRONTEND/

Ejecutar el script de deploy (deploy_pcfutsal.sh) cuando el director lo solicite con "haz run deploy" o similar. El agente puede ejecutarlo directamente sin pedir confirmación adicional, ya que tiene la orden explícita del director.

═══════════════════════════════════════════════════════════════════════════════

13) Acciones que requieren permiso previo

Instalar dependencias (npm o pip).

Cambiar modelos de base de datos.

Alterar scraping de forma estructural.

Tocar rutas críticas (/app/[lang]/...).

Cambiar arquitectura de carpetas principales.

Ejecutar migraciones.

Crear nuevas apps Django.

Modificar configuración de Next.js (next.config.js, tailwind.config.js) sin análisis.

Modificar administracion/settings.py (especialmente configuración de DB).

Tocar archivo backend/.env (contiene credenciales sensibles: DB_*, SECRET_KEY, etc.).

Tocar Nginx, PM2 o systemd (prohibido para el agente).

Modificar el script deploy_pcfutsal.sh.

═══════════════════════════════════════════════════════════════════════════════

14) Tareas típicas que puede realizar el agente

Crear nuevas vistas Next.js para jugadores, clubes, partidos.

Añadir bloques de datos en la Home.

Mejorar componentes existentes (GroupShell, GlobalTopMatches, etc.).

Añadir hooks de datos personalizados.

Ajustar lógica de ratings o estadísticas (en views/serializers).

Mejorar scraping (dentro de scraping/core).

Añadir endpoints (si no requieren modelos nuevos).

Crear utilidades internas.

Mejorar performance o agregar filtros.

Refactors locales seguros.

═══════════════════════════════════════════════════════════════════════════════

15) Criterios de aceptación por cambio

✅ El frontend compila sin errores (npm run build pasa).

✅ El backend sigue funcionando sin romper endpoints.

✅ No se añaden dependencias sin permiso.

✅ No se toca infraestructura del servidor.

✅ No se filtran secretos o variables de entorno.

✅ Todos los cambios están explicados en el resumen del agente.

✅ Los archivos de documentación están actualizados (PROJECT_TREE.md, DIARIO).

✅ Se proporciona plan de rollback si el cambio es crítico.

═══════════════════════════════════════════════════════════════════════════════

16) Límites explícitos

NO instalar librerías nuevas sin permiso.

NO modificar Nginx, PM2 o systemctl.

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

NO ejecutar el script de deploy.

NO modificar configuración de servicios.

NO hacer commits/push a git (solo el usuario).

═══════════════════════════════════════════════════════════════════════════════

17) Mensaje inicial obligatorio del agente

"He leído .cursor/AGENT_GLOBAL_PLAYBOOK.md y .cursor/PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar."

⚠️ EXCEPCIÓN: Si el director ha aprobado un roadmap o fases específicas, el agente puede ejecutar directamente siguiendo las instrucciones aprobadas sin pedir confirmación adicional.

18) Organización de scripts y recursos

El agente debe guardar scripts y recursos en las carpetas correspondientes dentro de .cursor/:

Scripts del backend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/BACKEND/
- Incluye: scripts de migración, utilidades Django, management commands auxiliares, scripts de datos, etc.

Scripts del frontend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/FRONTEND/
- Incluye: scripts de build, utilidades Next.js, scripts de datos, helpers, etc.

Reglas:
- Crear las carpetas si no existen
- Nombrar archivos de forma descriptiva
- Documentar el propósito de cada script
- Registrar en el diario cuando se crean nuevos scripts

═══════════════════════════════════════════════════════════════════════════════

FIN DEL PLAYBOOK

Última actualización: 2025-11-28

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

NO ejecutar el script de deploy.

NO modificar configuración de servicios.

NO hacer commits/push a git (solo el usuario).

═══════════════════════════════════════════════════════════════════════════════

17) Mensaje inicial obligatorio del agente

"He leído .cursor/AGENT_GLOBAL_PLAYBOOK.md y .cursor/PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar."

⚠️ EXCEPCIÓN: Si el director ha aprobado un roadmap o fases específicas, el agente puede ejecutar directamente siguiendo las instrucciones aprobadas sin pedir confirmación adicional.

18) Organización de scripts y recursos

El agente debe guardar scripts y recursos en las carpetas correspondientes dentro de .cursor/:

Scripts del backend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/BACKEND/
- Incluye: scripts de migración, utilidades Django, management commands auxiliares, scripts de datos, etc.

Scripts del frontend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/FRONTEND/
- Incluye: scripts de build, utilidades Next.js, scripts de datos, helpers, etc.

Reglas:
- Crear las carpetas si no existen
- Nombrar archivos de forma descriptiva
- Documentar el propósito de cada script
- Registrar en el diario cuando se crean nuevos scripts

═══════════════════════════════════════════════════════════════════════════════

FIN DEL PLAYBOOK

Última actualización: 2025-11-28

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

NO ejecutar el script de deploy.

NO modificar configuración de servicios.

NO hacer commits/push a git (solo el usuario).

═══════════════════════════════════════════════════════════════════════════════

17) Mensaje inicial obligatorio del agente

"He leído .cursor/AGENT_GLOBAL_PLAYBOOK.md y .cursor/PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar."

⚠️ EXCEPCIÓN: Si el director ha aprobado un roadmap o fases específicas, el agente puede ejecutar directamente siguiendo las instrucciones aprobadas sin pedir confirmación adicional.

18) Organización de scripts y recursos

El agente debe guardar scripts y recursos en las carpetas correspondientes dentro de .cursor/:

Scripts del backend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/BACKEND/
- Incluye: scripts de migración, utilidades Django, management commands auxiliares, scripts de datos, etc.

Scripts del frontend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/FRONTEND/
- Incluye: scripts de build, utilidades Next.js, scripts de datos, helpers, etc.

Reglas:
- Crear las carpetas si no existen
- Nombrar archivos de forma descriptiva
- Documentar el propósito de cada script
- Registrar en el diario cuando se crean nuevos scripts

═══════════════════════════════════════════════════════════════════════════════

FIN DEL PLAYBOOK

Última actualización: 2025-11-28

NO crear apps Django sin permiso.

NO cambiar autenticación sin supervisión.

NO tocar variables del sistema.

NO romper scraping.

NO ejecutar el script de deploy.

NO modificar configuración de servicios.

NO hacer commits/push a git (solo el usuario).

═══════════════════════════════════════════════════════════════════════════════

17) Mensaje inicial obligatorio del agente

"He leído .cursor/AGENT_GLOBAL_PLAYBOOK.md y .cursor/PROJECT_SPEC.md.
Para la tarea solicitada propongo este plan (3–6 pasos).
Espero confirmación antes de ejecutar."

⚠️ EXCEPCIÓN: Si el director ha aprobado un roadmap o fases específicas, el agente puede ejecutar directamente siguiendo las instrucciones aprobadas sin pedir confirmación adicional.

18) Organización de scripts y recursos

El agente debe guardar scripts y recursos en las carpetas correspondientes dentro de .cursor/:

Scripts del backend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/BACKEND/
- Incluye: scripts de migración, utilidades Django, management commands auxiliares, scripts de datos, etc.

Scripts del frontend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/FRONTEND/
- Incluye: scripts de build, utilidades Next.js, scripts de datos, helpers, etc.

Reglas:
- Crear las carpetas si no existen
- Nombrar archivos de forma descriptiva
- Documentar el propósito de cada script
- Registrar en el diario cuando se crean nuevos scripts

═══════════════════════════════════════════════════════════════════════════════

FIN DEL PLAYBOOK

Última actualización: 2025-11-28
