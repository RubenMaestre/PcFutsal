// /frontend/hooks/useGlobalValoraciones.ts
"use client";

import React from "react";
import { getWeekRangeFromTuesday } from "../home_components/GlobalWeekSelector";

type GlobalJugador = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number;
  club_nombre: string;
  club_escudo: string;
  club_slug?: string | null;
  puntos: number;
  puntos_global: number;
  es_portero?: boolean;
  grupo_id: number;
  grupo_nombre: string;
  competicion_id: number;
  competicion_nombre: string;
  jornada: number | null;
  goles_jornada?: number;
};

type GlobalEquipo = {
  club_id: number;
  nombre: string;
  escudo: string;
  slug?: string | null;
  score: number;
  score_global: number;
  grupo_id: number;
  grupo_nombre: string;
  competicion_id: number;
  competicion_nombre: string;
  jornada: number | null;
};

// Backwards compatible: algunos endpoints devolverán `jornada` y otros `window`
type WindowMeta = {
  start?: string | null;
  end?: string | null;
  effective_start?: string | null;
  effective_end?: string | null;
  mode?: string;
  status?: string;
  matched_games?: number;
  min_required?: number;
  fallback_weeks?: number;
};

type JugadoresGlobalResponse = {
  temporada_id: number;
  jornada?: number | null;
  window?: WindowMeta;
  jugador_de_la_jornada_global: GlobalJugador | null;
  ranking_global: GlobalJugador[];
};

type EquiposGlobalResponse = {
  temporada_id: number;
  jornada?: number | null;
  window?: WindowMeta;
  equipo_de_la_jornada_global: GlobalEquipo | null;
  ranking_global: GlobalEquipo[];
};

function buildQuery(params: Record<string, any>) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === null || v === undefined || v === "") return;
    q.set(k, String(v));
  });
  const s = q.toString();
  return s ? `?${s}` : "";
}

type JugadoresOpts = {
  jornada?: number | null;
  weekend?: string | null; // YYYY-MM-DD
  top?: number;
  onlyPorteros?: boolean;
  strict?: boolean; // para forzar usar exactamente esa semana
};

export function useGlobalJugadoresJornada(
  temporadaId: number | null | undefined,
  opts?: JugadoresOpts
) {
  const jornada = opts?.jornada ?? null;
  const weekend = opts?.weekend ?? null;
  const top = opts?.top ?? 50;
  const only_porteros = opts?.onlyPorteros ? 1 : 0;
  const strict = opts?.strict ? 1 : 0;

  const [data, setData] = React.useState<JugadoresGlobalResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!temporadaId) {
        setData(null);
        setLoading(false);
        setError(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        // Si weekend está presente, interpretarlo como martes y calcular rango miércoles-martes
        let queryParams: Record<string, any> = {
          temporada_id: temporadaId,
          jornada: jornada ?? "",
          top,
          only_porteros,
          strict,
        };
        
        if (weekend) {
          // weekend es la fecha del martes, calcular el rango completo
          const { wed, tue } = getWeekRangeFromTuesday(weekend);
          queryParams.date_from = wed.toISOString().slice(0, 10); // YYYY-MM-DD
          queryParams.date_to = tue.toISOString().slice(0, 10); // YYYY-MM-DD
        }
        
        const query = buildQuery(queryParams);
        const res = await fetch(
          `/api/valoraciones/jugadores-jornada-global/${query}`,
          { cache: "no-store" }
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as JugadoresGlobalResponse;
        if (cancelled) return;
        setData(json);
      } catch (e: any) {
        if (!cancelled) setError(e?.message || "Error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [temporadaId, jornada, weekend, top, only_porteros, strict]);

  const jugadorTop = data?.jugador_de_la_jornada_global ?? null;
  const ranking = data?.ranking_global ?? [];

  return { data, ranking, jugadorTop, loading, error };
}

type EquiposOpts = {
  jornada?: number | null;
  weekend?: string | null; // YYYY-MM-DD
  top?: number;
  strict?: boolean;
};

export function useGlobalEquipoJornada(
  temporadaId: number | null | undefined,
  opts?: EquiposOpts
) {
  const jornada = opts?.jornada ?? null;
  const weekend = opts?.weekend ?? null;
  const top = opts?.top ?? 30;
  const strict = opts?.strict ? 1 : 0;

  const [data, setData] = React.useState<EquiposGlobalResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!temporadaId) {
        setData(null);
        setLoading(false);
        setError(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        // Si weekend está presente, interpretarlo como martes y calcular rango miércoles-martes
        let queryParams: Record<string, any> = {
          temporada_id: temporadaId,
          jornada: jornada ?? "",
          top,
          strict,
        };
        
        if (weekend) {
          // weekend es la fecha del martes, calcular el rango completo
          const { wed, tue } = getWeekRangeFromTuesday(weekend);
          queryParams.date_from = wed.toISOString().slice(0, 10); // YYYY-MM-DD
          queryParams.date_to = tue.toISOString().slice(0, 10); // YYYY-MM-DD
        }
        
        const query = buildQuery(queryParams);
        const res = await fetch(
          `/api/valoraciones/equipo-jornada-global/${query}`,
          { cache: "no-store" }
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as EquiposGlobalResponse;
        if (cancelled) return;
        setData(json);
      } catch (e: any) {
        if (!cancelled) setError(e?.message || "Error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [temporadaId, jornada, weekend, top, strict]);

  const equipoTop = data?.equipo_de_la_jornada_global ?? null;
  const ranking = data?.ranking_global ?? [];

  return { data, ranking, equipoTop, loading, error };
}
