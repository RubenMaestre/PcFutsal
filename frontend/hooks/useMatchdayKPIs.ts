// /frontend/hooks/useMatchdayKPIs.ts
"use client";

import React from "react";

export type MatchdayKPIsResponse = {
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
};

export function useMatchdayKPIs(
  grupoId: number | null,
  jornada: number | null
) {
  const [data, setData] = React.useState<MatchdayKPIsResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    // Si no hay grupoId, no tiene sentido hacer la petición.
    if (!grupoId) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    // Flag para cancelar la petición si el componente se desmonta antes de que termine.
    // Evita errores de "Can't perform a React state update on an unmounted component".
    let cancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        // Construir parámetros de la petición.
        // La jornada es opcional: si no se especifica, se obtienen los KPIs de la última jornada jugada.
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        if (jornada != null) {
          params.set("jornada", String(jornada));
        }

        // Usamos ruta relativa /api/ para aprovechar el proxy de Nginx.
        const url = `/api/estadisticas/kpis-jornada/?${params.toString()}`;

        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error("HTTP " + res.status);

        const json = (await res.json()) as MatchdayKPIsResponse;
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
  }, [grupoId, jornada]);

  return {
    loading,
    error,
    data,
  };
}
