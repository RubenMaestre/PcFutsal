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
    // si no hay grupo todavía (móvil en primer render), no pedimos nada
    if (!grupoId) {
      setData(null);
      setError(null);
      setLoading(false); // 👈 lo dejamos claro
      return;
    }

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
        // 👇 IMPORTANTE: igual que en los otros hooks, ruta RELATIVA
        const res = await fetch(
          `/api/valoraciones/equipo-jornada/?${params.toString()}`,
          {
            method: "GET",
            signal: controller.signal,
            cache: "no-store",
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
