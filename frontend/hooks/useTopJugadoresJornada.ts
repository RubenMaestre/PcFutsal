"use client";

import { useEffect, useState } from "react";

export type JugadorJornada = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
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
  jugador_de_la_jornada: JugadorJornada | null;
  ranking_jugadores: JugadorJornada[];
};

export function useTopJugadoresJornada(
  grupoId: number | null,
  jornada: number | null,
  opts?: { onlyPorteros?: boolean; limit?: number }
) {
  const { onlyPorteros = false, limit } = opts || {};
  const [data, setData] = useState<ApiResponse | null>(null);
  const [jugadores, setJugadores] = useState<JugadorJornada[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!grupoId) {
      setData(null);
      setJugadores([]);
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
        if (onlyPorteros) {
          params.set("only_porteros", "1");
        }

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

        // Aplicar límite si se especifica. Esto permite mostrar solo los top N jugadores
        // en lugar de toda la lista, útil para componentes compactos o destacados.
        let lista = json.ranking_jugadores || [];
        if (limit && limit > 0) {
          lista = lista.slice(0, limit);
        }

        setData(json);
        setJugadores(lista);
      } catch (err) {
        if (cancelled) return;
        console.error("useTopJugadoresJornada error:", err);
        setError("No se pudo cargar el ranking de la jornada.");
        setData(null);
        setJugadores([]);
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
  }, [grupoId, jornada, onlyPorteros, limit]);

  return { data, jugadores, loading, error };
}



