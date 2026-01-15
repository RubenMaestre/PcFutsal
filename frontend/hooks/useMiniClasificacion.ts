// hooks/useMiniClasificacion.ts
"use client";

import React from "react";

type ApiResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
  };
  tabla: {
    pos: number | null;
    club_id: number;
    nombre: string;
    escudo: string;
    pj: number;
    puntos: number;
  }[];
};

export function useMiniClasificacion(grupoId: number | null) {
  const [data, setData] = React.useState<ApiResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<null | string>(null);

  React.useEffect(() => {
    // si no hay grupoId válido, reseteamos y no pedimos nada
    if (!grupoId) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        // Este fetch sí es CLIENTE → dominio público, así que aquí
        // podemos usar la ruta /api/ que Nginx sirve.
        const res = await fetch(
          `/api/estadisticas/clasificacion-mini/?grupo_id=${grupoId}`,
          {
            method: "GET",
            cache: "no-store",
          }
        );

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const json = await res.json();
        if (!cancelled) {
          setData(json);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message || "Error");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [grupoId]);

  return { data, loading, error };
}
