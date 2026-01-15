// /frontend/hooks/useSeasonTopScorers.ts
"use client";

import React from "react";

export type SeasonScorer = {
  jugador_id: number;
  nombre: string;
  apodo: string;
  slug?: string | null;
  club_id: number;
  club_nombre: string;
  club_slug?: string | null;
  goles_total: number;
  goles_equipo_total: number;
  contribucion_pct: number; // 0-100 redondeado
  foto: string;
};

type ApiResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  goleadores: SeasonScorer[];
};

export function useSeasonTopScorers(grupoId: number | null) {
  const [data, setData] = React.useState<ApiResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
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
        const url = `/api/estadisticas/pichichi-temporada/?grupo_id=${grupoId}`;
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error("HTTP " + res.status);

        const json = (await res.json()) as ApiResponse;
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

  const top10: SeasonScorer[] = React.useMemo(() => {
    if (!data?.goleadores) return [];
    return data.goleadores.slice(0, 12);
  }, [data]);

  return {
    loading,
    error,
    top10,
  };
}



