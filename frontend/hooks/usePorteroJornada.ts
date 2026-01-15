"use client";

import { useEffect, useState } from "react";

type PorteroJornada = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  club_slug?: string | null;
  puntos: number;
  es_portero?: boolean;
  detalles?: string[];
};

type ApiResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornada: number | null;
  jugador_de_la_jornada: PorteroJornada | null;
  ranking_jugadores: PorteroJornada[];
};

export function usePorteroJornada(
  grupoId: number | null,
  jornada: number | null
) {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [porteroTop, setPorteroTop] = useState<PorteroJornada | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!grupoId) {
      setData(null);
      setPorteroTop(null);
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
        params.set("only_porteros", "1");

        const res = await fetch(
          `/api/valoraciones/jugadores-jornada/?${params.toString()}`,
          {
            method: "GET",
            cache: "no-store",
          }
        );

        if (!res.ok) {
          throw new Error("Bad status " + res.status);
        }

        const json: ApiResponse = await res.json();
        if (cancelled) return;

        // el primero ya es el portero de la jornada
        const top =
          json.ranking_jugadores && json.ranking_jugadores.length > 0
            ? json.ranking_jugadores[0]
            : null;

        setData(json);
        setPorteroTop(top);
      } catch (err: any) {
        if (cancelled) return;
        console.error("usePorteroJornada error:", err);
        setError("No se pudo cargar el portero de la jornada.");
        setData(null);
        setPorteroTop(null);
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

  return { data, porteroTop, loading, error };
}
