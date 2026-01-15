// /frontend/hooks/useEquipoJornada.ts
"use client";

import React from "react";

/**
 * Hook para traer el EQUIPO DE LA JORNADA
 * GET /api/valoraciones/equipo-jornada/?grupo_id=...&jornada=...
 */
export function useEquipoJornada(
  grupoId: number | null,
  jornada: number | null
) {
  const [data, setData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    // Si no hay grupoId, no tiene sentido hacer la petición.
    // Esto es especialmente importante en móvil donde el grupo puede no estar disponible
    // en el primer render.
    if (!grupoId) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    // AbortController permite cancelar la petición si el componente se desmonta
    // o si cambian los parámetros antes de que termine la petición anterior.
    const controller = new AbortController();
    const params = new URLSearchParams();
    params.set("grupo_id", String(grupoId));
    if (jornada !== null && jornada !== undefined) {
      params.set("jornada", String(jornada));
    }

    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        // Usamos ruta relativa /api/ para aprovechar el proxy de Nginx.
        // Esto evita problemas de CORS y permite que el mismo dominio sirva
        // tanto el frontend como el backend.
        const res = await fetch(
          `/api/valoraciones/equipo-jornada/?${params.toString()}`,
          {
            method: "GET",
            signal: controller.signal,
            cache: "no-store", // Siempre obtener datos frescos
          }
        );

        if (!res.ok) {
          throw new Error("Bad status " + res.status);
        }

        const json = await res.json();
        setData(json);
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError(err.message || "Error al cargar equipo de la jornada");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();

    return () => {
      controller.abort();
    };
  }, [grupoId, jornada]);

  return { data, loading, error };
}

// por si en algún sitio lo importaste sin llaves
export default useEquipoJornada;
