// /frontend/hooks/useTopScorerMatchday.ts
"use client";

import React from "react";

export type MatchdayScorer = {
  jugador_id: number;
  nombre: string;
  apodo: string;
  club_id: number;
  club_nombre: string;
  club_slug?: string | null;
  club_posicion: number | null;
  goles_jornada: number;
  foto: string;
  club_escudo?: string;
  pabellon?: string;
  fecha_hora?: string | null;
  partido_id?: number | null;
};


type ApiResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornada: number | null;
  goleadores: MatchdayScorer[];
};

export function useTopScorerMatchday(
  grupoId: number | null,
  jornada: number | null
) {
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
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        if (jornada != null) {
          params.set("jornada", String(jornada));
        }

        const url = `/api/estadisticas/goleadores-jornada/?${params.toString()}`;

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
  }, [grupoId, jornada]);

  const topScorer: MatchdayScorer | null =
    data?.goleadores && data.goleadores.length > 0
      ? data.goleadores[0]
      : null;

  return {
    loading,
    error,
    data,
    topScorer,
  };
}
