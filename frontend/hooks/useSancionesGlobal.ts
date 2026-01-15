// /frontend/hooks/useSancionesGlobal.ts
"use client";

import React from "react";

type SancionGlobalRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto?: string | null;
  club_id: number | null;
  club_nombre?: string | null;
  club_escudo?: string | null;
  // Sanciones de la semana
  amarillas_semana?: number | null;
  dobles_amarillas_semana?: number | null;
  rojas_semana?: number | null;
  puntos_semana?: number | null;
  // Sanciones totales
  amarillas_total: number;
  dobles_amarillas_total: number;
  rojas_total: number;
  puntos_total: number;
  grupo_id?: number | null;
  grupo_nombre?: string | null;
  competicion_id?: number | null;
  competicion_nombre?: string | null;
};

type SancionesGlobalResponse = {
  temporada_id: number;
  window?: {
    status?: string;
    matched_games?: number;
  };
  ranking_global: SancionGlobalRow[];
};

type Options = {
  from?: string;
  to?: string;
  temporadaId: number;
  top?: number;
};

export function useSancionesGlobal(opts: Options) {
  const { from, to, temporadaId, top = 100 } = opts;

  const [data, setData] = React.useState<SancionesGlobalResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!temporadaId) {
      setData(null);
      setLoading(false);
      setError(null);
      return;
    }

    const params = new URLSearchParams();
    params.append("temporada_id", String(temporadaId));
    if (from) params.append("from", from);
    if (to) params.append("to", to);
    if (top) params.append("top", String(top));

    const url = `/api/estadisticas/sanciones-global-optimized/?${params.toString()}`;

    let cancelled = false;
    setLoading(true);
    setError(null);

    const startTime = performance.now();
    
    fetch(url, { cache: "no-store" })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as SancionesGlobalResponse;
        
        if (!cancelled) {
          setData(json);
          const elapsed = performance.now() - startTime;
          console.log(`[SANCIONES] Endpoint optimizado usado: ${(elapsed / 1000).toFixed(2)}s`);
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
  }, [from, to, temporadaId, top]);

  return { data, loading, error };
}







