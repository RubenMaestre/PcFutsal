Este archivo define:

La tarea permanente del proyecto

Las tareas activas (ahora)

Las tareas siguientes (próximas)

Las tareas completadas

El agente DEBE consultar este archivo SIEMPRE antes de trabajar.

🟦 0) TAREAS PERMANENTES (OBLIGATORIAS)
✔ 0.1 — Trabajo seguro en producción

⚠️ PC FUTSAL está en PRODUCCIÓN en pcfutsal.es
Funciona en modo producción real, en un servidor Hetzner con Nginx + Gunicorn + PM2.
Todo está configurado y funcionando. Para evitar caídas, el agente debe seguir SIEMPRE estas normas:

Nunca ejecutar comandos fuera de /home/rubenmaestre/pcfutsal.es/.

Nunca usar sudo, systemctl, service, pm2, nginx, gunicorn, ni reiniciar servicios.

Nunca ejecutar el script de deploy (deploy_pcfutsal.sh o npm run deploy), EXCEPTO cuando el director lo solicite explícitamente con "haz run deploy" o similar. En ese caso, el agente puede ejecutarlo directamente sin pedir confirmación adicional.

Nunca tocar /etc/* ni revelar variables de entorno.

Siempre proponer un plan de 3–6 pasos antes de modificar código.

Siempre esperar confirmación explícita del director antes de ejecutar cambios.

⚠️ EXCEPCIÓN: Si el director ha aprobado un roadmap o fases específicas, el agente puede ejecutar directamente sin pedir confirmación adicional para cada paso, siguiendo las instrucciones del roadmap/fase aprobada.

Siempre entregar al finalizar:

Archivos modificados

Pasos de prueba

Plan de rollback rápido

Nunca instalar dependencias (npm/pip) sin autorización.

Nunca hacer migraciones sin autorización.

No modificar arquitectura de carpetas sin permiso.

No modificar el script deploy_pcfutsal.sh sin permiso explícito.

Puede ejecutar comandos npm (npm run build, npm run lint, npm run typecheck, etc.) cuando sea necesario sin pedir verificación.

Puede hacer cambios en backend y frontend siguiendo las instrucciones de roadmap o fases aprobadas por el director (no requiere confirmación adicional por cada paso).

✔ 0.2 — Mantener el archivo .cursor/PROJECT_TREE.md ACTUALIZADO

El agente DEBE mantener SIEMPRE este archivo:

.cursor/PROJECT_TREE.md

Este archivo debe contener SIEMPRE:

Estructura real, actualizada, hasta nivel L2 del proyecto:

/backend/ → apps, modelos, serializers, urls, views, utils

/frontend/ → app router, components, home_components, rankings_components, hooks, i18n, lib, public

/.cursor/ → archivos de control y documentación

Archivos raíz importantes (package.json, tailwind.config.js, manage.py, deploy_pcfutsal.sh, .env…)

Normas:

Tras cualquier cambio estructural (crear, renombrar o eliminar archivo/carpeta):

Actualizar inmediatamente PROJECT_TREE.md al finalizar la tarea.

El formato debe ser tipo tree, limpio y consistente.

NO listar:

node_modules/

__pycache__/

migrations/* internas

Logs

Archivos temporales

Objetivo:

Garantizar que Cursor siempre conoce la estructura real del proyecto, sobre todo ahora que el repositorio es grande y altamente modular.

✔ 0.3 — Documentar APIs y Hooks

El agente DEBE documentar SIEMPRE las nuevas APIs y hooks que se creen.

Ubicación:

.cursor/DOCUMENTACION/APIS.md — Documentación de todas las APIs del backend
.cursor/DOCUMENTACION/HOOKS.md — Documentación de todos los hooks del frontend

Normas:

Al crear una NUEVA API (nuevo endpoint en views.py):
1. Documentarla inmediatamente en .cursor/DOCUMENTACION/APIS.md
2. Incluir: URL, método HTTP, parámetros, tipo de retorno, descripción de funcionalidad
3. Indicar a qué app pertenece
4. Actualizar también .cursor/AGENT_GLOBAL_PLAYBOOK.md en la sección correspondiente de endpoints

Al crear un NUEVO hook (nuevo archivo en /frontend/hooks/):
1. Documentarlo inmediatamente en .cursor/DOCUMENTACION/HOOKS.md
2. Incluir: nombre del hook, parámetros, tipo de retorno, endpoint que consume, descripción de funcionalidad
3. Indicar categoría (clasificaciones, estadísticas, valoraciones, globales, clubes)
4. Actualizar también .cursor/AGENT_GLOBAL_PLAYBOOK.md en la sección de hooks personalizados

Objetivo:

Mantener un registro centralizado y actualizado de todas las APIs y hooks del proyecto para facilitar el mantenimiento y la comprensión del sistema.

✔ 0.4 — Organización de scripts y recursos

El agente DEBE guardar scripts y recursos en las carpetas correspondientes dentro de .cursor/:

Scripts del backend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/BACKEND/
- Incluye: scripts de migración, utilidades Django, management commands auxiliares, scripts de datos, etc.

Scripts del frontend:
- Ubicación: /home/rubenmaestre/pcfutsal.es/.cursor/FRONTEND/
- Incluye: scripts de build, utilidades Next.js, scripts de datos, helpers, etc.

Normas:
- Crear las carpetas si no existen
- Nombrar archivos de forma descriptiva
- Documentar el propósito de cada script
- Registrar en el diario cuando se crean nuevos scripts

Objetivo:
- Mantener organizados todos los scripts y recursos auxiliares del proyecto
- Facilitar la reutilización y el mantenimiento de scripts

✔ 0.5 — Registro obligatorio de cambios

⚠️ REGLA FUNDAMENTAL: Cada cambio realizado DEBE quedar registrado.

El agente DEBE registrar TODOS los cambios en:
- .cursor/DIARIO/YYYY-MM-DD.txt (obligatorio para cada cambio)
- .cursor/DOCUMENTACION/APIS.md (si se crea/modifica una API)
- .cursor/DOCUMENTACION/HOOKS.md (si se crea/modifica un hook)
- .cursor/PROJECT_TREE.md (si hay cambios estructurales)
- .cursor/DOCUMENTOS/ (si se crean documentos de estrategia o análisis)

Normas:
- Registrar inmediatamente después de realizar el cambio
- Incluir descripción clara del cambio
- Indicar archivos modificados/creados
- Registrar scripts creados en BACKEND/ o FRONTEND/

Objetivo:
- Mantener un historial completo y trazable de todos los cambios
- Facilitar la comprensión del proyecto y su evolución

🔹 1) TAREAS ACTUALES (Ahora)

(Vacío por ahora — el director añadirá aquí las tareas que deben ejecutarse.)

🔸 2) TAREAS SIGUIENTES (Siguiente)

(Vacío por ahora — tareas para la siguiente iteración.)

🔘 3) TAREAS COMPLETADAS (Hecho)

(Vacío por ahora — el agente moverá aquí tareas solo cuando el director lo indique.)

📝 Notas para el agente

Consultar SIEMPRE este archivo antes de iniciar cualquier tarea.

No inventar tareas.

No mover tareas de sección sin aprobación.

No modificar TASK.md sin instrucciones explícitas.

Puede sugerir mejoras, pero NUNCA añadirlas a este archivo sin permiso del director.

📌 Instrucción permanente

"Para cada tarea, el agente deberá leer AGENT_GLOBAL_PLAYBOOK.md, PROJECT_SPEC.md, PROJECT_VISION.md, DECISIONS.md y TASK.md, proponer un plan de 3–6 pasos, esperar confirmación del director y ejecutar únicamente lo aprobado.

⚠️ EXCEPCIÓN: Si el director ha aprobado un roadmap o fases específicas, el agente puede ejecutar directamente siguiendo las instrucciones aprobadas sin pedir confirmación adicional.

Tras cualquier cambio estructural, actualizar .cursor/PROJECT_TREE.md.
Registrar TODOS los cambios en .cursor/DIARIO/YYYY-MM-DD.txt (OBLIGATORIO).
Guardar scripts del backend en .cursor/BACKEND/ y scripts del frontend en .cursor/FRONTEND/.
Puede ejecutar comandos npm cuando sea necesario sin pedir verificación."