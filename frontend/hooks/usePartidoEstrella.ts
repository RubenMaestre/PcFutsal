// /frontend/hooks/usePartidoEstrella.ts
"use client";

import React from "react";

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
    if (!grupoId) {
      setData(null);
      return;
    }

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
