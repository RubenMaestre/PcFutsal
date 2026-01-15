// /frontend/hooks/useTeamGoals.ts
"use client";

import React from "react";

export type TeamGoalsRow = {
  club_id: number;
  club_nombre: string;
  club_escudo: string;
  club_slug?: string | null;

  partidos_jugados: number;

  goles_total: number;
  goles_por_partido: number;

  goles_local: number;
  goles_visitante: number;

  goles_1parte: number;
  goles_2parte: number;
};

export type TeamGoalsResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  equipos: TeamGoalsRow[];
};

export function useTeamGoals(
  grupoId: number | null,
  jornada: number | null // la aceptamos ya para futura extensión
) {
  const [data, setData] = React.useState<TeamGoalsResponse | null>(null);
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

        // TODO jornada: cuando el backend acepte ?jornada=,
        // descomentar esto:
        // if (jornada != null) {
        //   params.set("jornada", String(jornada));
        // }

        const url = `/api/estadisticas/goles-por-equipo/?${params.toString()}`;

        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error("HTTP " + res.status);

        const json = (await res.json()) as TeamGoalsResponse;
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
  }, [grupoId, jornada]); // jornada incluida para que reactive el fetch en el futuro

  return {
    loading,
    error,
    data,
    equipos: data?.equipos ?? [],
  };
}
