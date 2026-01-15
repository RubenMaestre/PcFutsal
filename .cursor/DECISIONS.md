DECISIONS.md — Registro oficial de decisiones técnicas en PC FUTSAL

Este documento registra todas las decisiones técnicas relevantes y permanentes del proyecto.
El agente NO puede modificar ni añadir entradas aquí por su cuenta.
Solo debe actualizarlo cuando el director lo ordene explícitamente (“Registra esta decisión”).

🔹 Formato obligatorio de cada decisión

[Fecha YYYY-MM-DD] — Título breve
Contexto:
(Qué estaba pasando, qué problema se detectó, qué necesitábamos resolver)

Decisión:
(Qué se decidió exactamente, con detalle técnico claro)

Motivo:
(Por qué esta solución es mejor, impacto, razones)

Impacto en el proyecto:
(Cómo afecta a frontend, backend, deploy, archivos, arquitectura…)

Archivos afectados:
(Listar claramente, si aplica; rutas absolutas dentro de /home/rubenmaestre/pcfutsal.es)

El agente DEBE usar exactamente este formato al añadir una entrada.

🔷 Decisiones registradas (cronología)

(Vacío por ahora — se llenará cuando el director lo indique)

🔹 Reglas para este archivo

El agente NO puede escribir nuevas decisiones por iniciativa propia.

Solo se añaden entradas después de una orden explícita del director:
“Registra esta decisión”.

Deben registrarse, entre otras:

Cambios de arquitectura del backend Django o del frontend Next.js.

Introducción/eliminación de dependencias en cualquiera de los dos proyectos.

Cambios en el modelo de datos o en la estructura de scraping.

Cambios en endpoints críticos, flujos de ratings, clasificaciones o fantasy.

Modificaciones de infraestructura (routing, middlewares, estructura de carpetas).

Cambios que afecten a seguridad (CORS/CSRF/SECURE_*, autenticación, permisos).

Actualizaciones en los flujos de deploy del frontend o backend.

No registrar tareas, ideas o pendientes:
este documento es únicamente para DECISIONES técnicas permanentes.

Mantener orden cronológico.

Si una decisión se revierte, se debe crear una nueva entrada que indique la reversión y referencie la decisión original.

🔹 Ejemplo ilustrativo (no copiar a producción)

2025-01-12 — Ajuste del fetch global de clasificación
Contexto:
Las clasificaciones de varios grupos estaban tardando en cargar por exceso de llamadas simultáneas.

Decisión:
Implementar un hook unificado useClasificacionMultiScope que centraliza el fetch y cachea por grupoId.

Motivo:
Reduce llamadas repetidas, mejora la performance y unifica la lógica del frontend.

Impacto en el proyecto:
Frontend únicamente. No afecta al backend. Sin impacto en deploy.

Archivos afectados:
/home/rubenmaestre/pcfutsal.es/frontend/hooks/useClasificacionMultiScope.ts
/home/rubenmaestre/pcfutsal.es/frontend/components/ClasificacionShell.tsx

🔹 Instrucción para el agente

Siempre que el director indique "Registra esta decisión",
el agente debe añadir una nueva entrada al final siguiendo el formato exacto,
sin modificar ninguna entrada anterior.