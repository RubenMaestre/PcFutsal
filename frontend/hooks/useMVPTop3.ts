// /frontend/hooks/useMVPTop3.ts
"use client";

import { useEffect, useState } from "react";

type MVPTop3Row = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  puntos: number | null;
  puntos_semana?: number | null;
  puntos_global: number;
  puntos_totales?: number;
  total_points?: number;
  coef_division: number;
  goles_jornada?: number;
  grupo_id: number;
  grupo_nombre: string;
  competicion_id: number;
  competicion_nombre: string;
};

type MVPTop3Response = {
  temporada_id: number;
  window: {
    start?: string | null;
    end?: string | null;
    status?: string;
    matched_games?: number;
  };
  top3: MVPTop3Row[];
};

type Options = {
  from?: string;
  to?: string;
  temporadaId?: number;
  onlyPorteros?: boolean;
};

export function useMVPTop3(opts: Options) {
  const { from, to, temporadaId, onlyPorteros } = opts;

  const [data, setData] = useState<MVPTop3Response | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Construir parámetros de la petición.
    // Los parámetros 'from' y 'to' permiten filtrar por rango de fechas (ventana de tiempo).
    // El parámetro 'only_porteros' permite filtrar solo porteros del ranking.
    const params = new URLSearchParams();
    if (from) params.set("from", from);
    if (to) params.set("to", to);
    if (typeof temporadaId === "number") {
      params.set("temporada_id", String(temporadaId));
    }
    if (onlyPorteros) params.set("only_porteros", "1");

    // Usamos el endpoint optimizado que precalcula los datos en lugar de calcularlos en tiempo real.
    const url = `/api/fantasy/mvp-top3-optimized/?${params.toString()}`;

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch(url, { cache: "no-store" })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as MVPTop3Response;
        if (!cancelled) {
          setData(json);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError((e as Error).message || "Error");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [from, to, temporadaId, onlyPorteros]);

  return { data, loading, error };
}









