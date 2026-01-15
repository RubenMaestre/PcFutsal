// /frontend/hooks/usePartidoEstrella.ts
"use client";

import React from "react";

// API base para el hook. En el navegador, se usa la variable de entorno o un fallback.
// Este hook se usa principalmente en SSR, por lo que necesita una URL absoluta.
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es";

export function usePartidoEstrella(
  grupoId: number | null,
  jornada: number | null
) {
  const [data, setData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    // Si no hay grupoId, no tiene sentido hacer la petición.
    if (!grupoId) {
      setData(null);
      return;
    }

    // AbortController permite cancelar la petición si el componente se desmonta
    // o si cambian los parámetros antes de que termine la petición anterior.
    const controller = new AbortController();

    async function fetchStar() {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        if (jornada) {
          params.set("jornada", String(jornada));
        }

        const resp = await fetch(
          `${API_BASE}/api/valoraciones/partido-estrella/?${params.toString()}`,
          {
            signal: controller.signal,
          }
        );

        if (!resp.ok) {
          throw new Error(`Error ${resp.status}`);
        }

        const json = await resp.json();
        setData(json);
      } catch (err: any) {
        // Ignoramos AbortError porque es esperado cuando se cancela la petición.
        // Solo mostramos errores reales de red o del servidor.
        if (err.name !== "AbortError") {
          setError(err?.message || "Error al cargar el partido estrella");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchStar();

    return () => {
      controller.abort();
    };
  }, [grupoId, jornada]);

  return { data, loading, error };
}
