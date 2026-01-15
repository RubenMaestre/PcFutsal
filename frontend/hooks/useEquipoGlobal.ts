// /frontend/hooks/useEquipoGlobal.ts
"use client";

import React from "react";

type EquipoGlobalRow = {
  club_id: number | null;
  nombre: string;
  escudo?: string | null;
  competicion_nombre?: string | null;
  grupo_nombre?: string | null;
  // Puntos de la semana
  score?: number | null;
  score_week?: number | null;
  score_semana?: number | null;
  puntos?: number | null;
  // Puntos totales acumulados
  score_global?: number | null;
  score_total?: number | null;
  total_score?: number | null;
  acumulado?: number | null;
};

type EquipoGlobalResponse = {
  temporada_id: number;
  window?: {
    status?: string;
    matched_games?: number;
    effective_start?: string;
    effective_end?: string;
  };
  equipo_de_la_jornada_global: EquipoGlobalRow | null;
  ranking_global: EquipoGlobalRow[];
};

type Options = {
  from?: string;
  to?: string;
  temporadaId: number;
  top?: number;
  strict?: boolean;
};

export function useEquipoGlobal(opts: Options) {
  const { from, to, temporadaId, top = 100, strict = false } = opts;

  const [data, setData] = React.useState<EquipoGlobalResponse | null>(null);
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
    if (strict) params.append("strict", "1");

    // Usar endpoint optimizado si está disponible (lee de PuntosEquipoTotal y PuntosEquipoJornada)
    // Fallback al endpoint original si falla
    const url = `/api/fantasy/equipo-global-optimized/?${params.toString()}`;
    const fallbackUrl = `/api/valoraciones/equipo-jornada-global/?${params.toString()}`;

    let cancelled = false;
    setLoading(true);
    setError(null);

    // Función auxiliar para procesar la respuesta
    const processResponse = async (res: Response) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as any;

      // Normalización de campos
      if (Array.isArray(json.ranking_global)) {
        let mapped: EquipoGlobalRow[] = json.ranking_global.map(
          (row: any): EquipoGlobalRow => {
            // Puntos de la semana
            const puntosSemana: number | null =
              row.score ??
              row.score_week ??
              row.score_semana ??
              row.puntos ??
              null;

            // Puntos totales
            const puntosGlobal: number =
              row.score_global ??
              row.score_total ??
              row.total_score ??
              row.acumulado ??
              0;

            return {
              club_id: row.club_id,
              nombre: row.nombre,
              escudo: row.escudo,
              competicion_nombre: row.competicion_nombre,
              grupo_nombre: row.grupo_nombre,
              score: puntosSemana,
              score_week: puntosSemana,
              score_semana: puntosSemana,
              puntos: puntosSemana,
              score_global: puntosGlobal,
              score_total: puntosGlobal,
              total_score: puntosGlobal,
              acumulado: puntosGlobal,
            };
          }
        );

        // Ordenar por puntos totales (descendente)
        mapped.sort(
          (a: EquipoGlobalRow, b: EquipoGlobalRow) =>
            (b.score_global ?? 0) - (a.score_global ?? 0)
        );

        json.ranking_global = mapped;
      }

      if (!cancelled) {
        setData(json as EquipoGlobalResponse);
      }
    };

    const startTime = performance.now();
    // Intentar primero con endpoint optimizado
    fetch(url, { cache: "no-store" })
      .then(async (res) => {
        const elapsed = performance.now() - startTime;
        console.log(`[EQUIPO] Endpoint optimizado usado: ${(elapsed / 1000).toFixed(2)}s`);
        return processResponse(res);
      })
      .catch(async (e) => {
        console.warn(`[EQUIPO] Endpoint optimizado falló, usando fallback:`, e);
        // Si falla el endpoint optimizado, intentar con el original
        if (!cancelled) {
          try {
            const fallbackStart = performance.now();
            const fallbackRes = await fetch(fallbackUrl, { cache: "no-store" });
            const fallbackElapsed = performance.now() - fallbackStart;
            console.log(`[EQUIPO] Endpoint fallback usado: ${(fallbackElapsed / 1000).toFixed(2)}s`);
            await processResponse(fallbackRes);
          } catch (fallbackError) {
            if (!cancelled) {
              setError((fallbackError as Error).message || "Error");
            }
          }
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [from, to, temporadaId, top, strict]);

  return { data, loading, error };
}




