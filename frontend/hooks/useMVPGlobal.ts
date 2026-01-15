// hooks/useMVPGlobal.ts
"use client";

import { useEffect, useState } from "react";

type MVPGlobalRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  puntos: number | null;        // puntos semana (puede ser null si no hay dato)
  puntos_global: number;        // puntos acumulados globales
  coef_division: number;
  goles_jornada?: number;
  grupo_id: number;
  grupo_nombre: string;
  competicion_id: number;
  competicion_nombre: string;

  // alias opcionales
  puntos_semana?: number | null;
  puntos_totales?: number;
  total_points?: number;
};

type MVPGlobalResponse = {
  temporada_id: number;
  window: {
    start?: string | null;
    end?: string | null;
    effective_start?: string;
    effective_end?: string;
    status?: "ok" | "strict" | "fallback_failed" | "no-window";
    matched_games?: number;
    min_required?: number;
    fallback_weeks?: number;
    mode?: string;
    schema?: string;
  };
  jugador_de_la_jornada_global: MVPGlobalRow | null;
  ranking_global: MVPGlobalRow[];
  detail?: string;
};

type Options = {
  from?: string; // YYYY-MM-DD
  to?: string;   // YYYY-MM-DD
  temporadaId?: number;
  onlyPorteros?: boolean;
  top?: number;
  strict?: boolean;
  minMatches?: number;
  offset?: number; // Empezar desde el N-ésimo jugador (para empezar desde el 4º)
};

export function useMVPGlobal(opts: Options) {
  const {
    from,
    to,
    temporadaId,
    onlyPorteros,
    top,
    strict,
    minMatches,
    offset,
  } = opts;

  const [data, setData] = useState<MVPGlobalResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (from) params.set("from", from);
    if (to) params.set("to", to);
    if (typeof temporadaId === "number") {
      params.set("temporada_id", String(temporadaId));
    }
    if (onlyPorteros) params.set("only_porteros", "1");
    if (typeof top === "number") params.set("top", String(top));
    if (strict) params.set("strict", "1");
    if (typeof minMatches === "number") {
      params.set("min_matches", String(minMatches));
    }
    if (typeof offset === "number") {
      params.set("offset", String(offset));
    }

    // Usar endpoint optimizado si está disponible (lee de PuntosMVPJornada)
    // Fallback al endpoint original si falla
    const url = `/api/fantasy/mvp-global-optimized/?${params.toString()}`;
    const fallbackUrl = `/api/valoraciones/mvp-global/?${params.toString()}`;

    let cancelled = false;
    setLoading(true);
    setError(null);

    // Función auxiliar para procesar la respuesta
    const processResponse = async (res: Response) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as any;

      // ————————————————————————————————
      // Normalización de campos + ordenación
      // ————————————————————————————————
      if (Array.isArray(json.ranking_global)) {
        let mapped: MVPGlobalRow[] = json.ranking_global.map(
          (row: any): MVPGlobalRow => {
            // Puntos de la semana (si no viene nada, lo dejamos en null)
            const puntosSemana: number | null =
              row.puntos ??
              row.puntos_semana ??
              row.points_week ??
              null;

            // Puntos totales/globales (si no viene nada, 0)
            const puntosGlobal: number =
              row.puntos_global ??
              row.puntos_totales ??
              row.total_points ??
              0;

            const normalizado: MVPGlobalRow = {
              jugador_id: row.jugador_id,
              nombre: row.nombre,
              foto: row.foto,
              club_id: row.club_id ?? null,
              club_nombre: row.club_nombre,
              club_escudo: row.club_escudo,
              coef_division: row.coef_division ?? 1,
              goles_jornada: row.goles_jornada,
              grupo_id: row.grupo_id,
              grupo_nombre: row.grupo_nombre,
              competicion_id: row.competicion_id,
              competicion_nombre: row.competicion_nombre,

              // principales
              puntos: puntosSemana,
              puntos_global: puntosGlobal,

              // alias
              puntos_semana: puntosSemana,
              puntos_totales: puntosGlobal,
              total_points: puntosGlobal,
            };

            return normalizado;
          }
        );

        // 👉 Ordenar por PTS TOTALES (puntos_global) de mayor a menor
        mapped.sort(
          (a: MVPGlobalRow, b: MVPGlobalRow) =>
            (b.puntos_global ?? 0) - (a.puntos_global ?? 0)
        );

        json.ranking_global = mapped;
      }

      // normalizamos también el jugador de la jornada global
      if (json.jugador_de_la_jornada_global) {
        const row: any = json.jugador_de_la_jornada_global;
        const puntosSemana: number | null =
          row.puntos ??
          row.puntos_semana ??
          row.points_week ??
          null;
        const puntosGlobal: number =
          row.puntos_global ??
          row.puntos_totales ??
          row.total_points ??
          0;

        const normalizadoJugador: MVPGlobalRow = {
          jugador_id: row.jugador_id,
          nombre: row.nombre,
          foto: row.foto,
          club_id: row.club_id ?? null,
          club_nombre: row.club_nombre,
          club_escudo: row.club_escudo,
          coef_division: row.coef_division ?? 1,
          goles_jornada: row.goles_jornada,
          grupo_id: row.grupo_id,
          grupo_nombre: row.grupo_nombre,
          competicion_id: row.competicion_id,
          competicion_nombre: row.competicion_nombre,
          puntos: puntosSemana,
          puntos_global: puntosGlobal,
          puntos_semana: puntosSemana,
          puntos_totales: puntosGlobal,
          total_points: puntosGlobal,
        };

        json.jugador_de_la_jornada_global = normalizadoJugador;
      }

      if (!cancelled) {
        setData(json as MVPGlobalResponse);
      }
    };

    // Intentar primero con endpoint optimizado
    const startTime = performance.now();
    fetch(url, { cache: "no-store" })
      .then(async (res) => {
        const elapsed = performance.now() - startTime;
        console.log(`[MVP] Endpoint optimizado usado: ${(elapsed / 1000).toFixed(2)}s`);
        return processResponse(res);
      })
      .catch(async (e) => {
        console.warn(`[MVP] Endpoint optimizado falló, usando fallback:`, e);
        // Si falla el endpoint optimizado, intentar con el original
        if (!cancelled) {
          try {
            const fallbackStart = performance.now();
            const fallbackRes = await fetch(fallbackUrl, { cache: "no-store" });
            const fallbackElapsed = performance.now() - fallbackStart;
            console.log(`[MVP] Endpoint fallback usado: ${(fallbackElapsed / 1000).toFixed(2)}s`);
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
  }, [from, to, temporadaId, onlyPorteros, top, strict, minMatches, offset]);

  return { data, loading, error };
}



