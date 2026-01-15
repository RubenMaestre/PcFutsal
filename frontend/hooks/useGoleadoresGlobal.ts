// /frontend/hooks/useGoleadoresGlobal.ts
"use client";

import React from "react";

type GoleadorGlobalRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto?: string | null;
  club_id: number | null;
  club_nombre?: string | null;
  club_escudo?: string | null;
  goles_semana?: number | null;  // Goles de la última semana (si hay filtro)
  goles_total: number;  // Goles totales de la temporada
  puntos_total: number;  // Puntos = goles_total * coef_division * 3.1416
  coef_division?: number;
  grupo_id?: number | null;
  grupo_nombre?: string | null;
  competicion_id?: number | null;
  competicion_nombre?: string | null;
};

type GoleadoresGlobalResponse = {
  temporada_id: number;
  window?: {
    status?: string;
    matched_games?: number;
  };
  ranking_global: GoleadorGlobalRow[];
};

type Options = {
  from?: string;
  to?: string;
  temporadaId: number;
  top?: number;
};

export function useGoleadoresGlobal(opts: Options) {
  const { from, to, temporadaId, top = 100 } = opts;

  const [data, setData] = React.useState<GoleadoresGlobalResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!temporadaId) {
      setData(null);
      setLoading(false);
      setError(null);
      return;
    }

    // Construir parámetros de la petición.
    // Los parámetros 'from' y 'to' permiten filtrar por rango de fechas (ventana de tiempo).
    // El parámetro 'top' limita el número de resultados para mejorar el rendimiento.
    const params = new URLSearchParams();
    params.append("temporada_id", String(temporadaId));
    if (from) params.append("from", from);
    if (to) params.append("to", to);
    if (top) params.append("top", String(top));

    // Usamos el endpoint optimizado que precalcula los datos en lugar de calcularlos en tiempo real.
    const url = `/api/estadisticas/goleadores-global-optimized/?${params.toString()}`;

    let cancelled = false;
    setLoading(true);
    setError(null);

    // Medimos el tiempo de respuesta para debugging y monitoreo de rendimiento.
    const startTime = performance.now();
    
    fetch(url, { cache: "no-store" })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as GoleadoresGlobalResponse;
        
        if (!cancelled) {
          setData(json);
          const elapsed = performance.now() - startTime;
          // Log de rendimiento para identificar si el endpoint optimizado está funcionando correctamente.
          console.log(`[GOLEADORES] Endpoint optimizado usado: ${(elapsed / 1000).toFixed(2)}s`);
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







