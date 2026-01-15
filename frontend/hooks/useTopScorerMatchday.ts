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
        // La jornada es opcional: si no se especifica, se obtienen los goleadores de la última jornada jugada.
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        if (jornada != null) {
          params.set("jornada", String(jornada));
        }

        // Usamos ruta relativa /api/ para aprovechar el proxy de Nginx.
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

  // El primer goleador de la lista ya es el máximo goleador (ordenado por goles descendente).
  // Esto permite mostrar directamente el top scorer sin procesamiento adicional.
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
