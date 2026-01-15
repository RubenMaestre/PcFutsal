// hooks/useJugadorFull.ts
"use client";

import { useEffect, useMemo, useState } from "react";

const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

// -------------------- Tipados de respuesta --------------------
export type JugadorFullResponse = {
  jugador: {
    id: number;
    nombre: string;
    apodo?: string;
    slug?: string | null;
    foto_url?: string;
    posicion_principal?: string;
    fecha_nacimiento?: string | null;
    edad_estimacion?: number | null;
    edad_display?: number | null;
    informe_scout?: string;
    activo: boolean;
  };

  club_actual?: {
    id: number;
    nombre: string;
    nombre_corto?: string;
    escudo_url?: string;
    slug?: string;
  } | null;

  temporada_actual?: {
    id: number;
    nombre: string;
  } | null;

  dorsal_actual?: string | null;

  stats_actuales?: {
    partidos_jugados: number;
    goles: number;
    tarjetas_amarillas: number;
    tarjetas_rojas: number;
    convocados: number;
    titular: number;
    suplente: number;
  };

  valoraciones?: {
    id: number;
    temporada: number;
    temporada_nombre: string;
    ataque: number;
    defensa: number;
    pase: number;
    regate: number;
    potencia: number;
    intensidad: number;
    vision: number;
    regularidad: number;
    carisma: number;
    media_global: number;
    total_votos?: number;
  } | null;

  historial?: Array<{
    temporada: string;
    temporada_id: number | null;
    competicion: string;
    competicion_id: number | null;
    grupo: string;
    grupo_id: number | null;
    club: string;
    club_id: number | null;
    club_nombre: string | null;
    club_slug: string | null;
    dorsal: string | null;
    partidos_jugados: number;
    goles: number;
    tarjetas_amarillas: number;
    tarjetas_rojas: number;
    es_scraped: boolean;
  }>;

  partidos?: {
    partidos: Array<{
      partido_id: number;
      fecha: string | null;
      jornada: number;
      local: string;
      local_id: number;
      visitante: string;
      visitante_id: number;
      goles_local: number;
      goles_visitante: number;
      goles_jugador: number;
      tarjetas_amarillas: number;
      tarjetas_rojas: number;
      titular: boolean;
      mvp: boolean;
      grupo_id: number | null;
    }>;
    totales: {
      partidos_jugados: number;
      goles: number;
      tarjetas_amarillas: number;
      tarjetas_rojas: number;
      partidos_titular: number;
      mvps: number;
    };
  };

  fantasy?: {
    temporada_id: number;
    temporada_nombre: string;
    puntos_base_total: number;
    puntos_con_coef_total: number;
    goles_total: number;
    partidos_total: number;
    puntos_por_jornada: Array<{
      jornada: number;
      grupo_id: number;
      grupo_nombre: string;
      puntos_base: number;
      puntos_con_coef: number;
      coef_division: number;
      goles: number;
      partidos_jugados: number;
      fecha_calculo: string | null;
    }>;
  } | null;
};

// -------------------- Parámetros del hook --------------------
export type UseJugadorFullParams = {
  jugadorId?: number | string | null; // Puede ser ID numérico o slug
  temporadaId?: number | null;
  /**
   * CSV con bloques a incluir.
   * Posibles: valoraciones,historial,partidos,stats,fantasy
   * Por defecto en backend: valoraciones,historial,stats,fantasy
   */
  include?: string | string[];
  /** Auto-fetch al montar si hay jugadorId válido (true por defecto) */
  enabled?: boolean;
};

export function useJugadorFull(params: UseJugadorFullParams) {
  const {
    jugadorId = null,
    temporadaId = null,
    include,
    enabled = true,
  } = params || {};

  const [data, setData] = useState<JugadorFullResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Normaliza include a CSV: el backend espera "valoraciones,historial,stats" como string
  // pero el hook acepta tanto array como string para mayor flexibilidad
  const includeCSV = useMemo(() => {
    if (!include) return undefined;
    if (Array.isArray(include)) return include.join(",");
    return include;
  }, [include]);

  // Construcción del URL: en navegador usa ruta relativa (aprovecha proxy de Nginx),
  // en SSR usa URL absoluta porque no hay proxy disponible
  const url = useMemo(() => {
    const qs = new URLSearchParams();
    // El backend acepta tanto ID numérico como slug (ej: "daniel-domene-garcia")
    if (jugadorId) qs.set("jugador_id", String(jugadorId));
    if (temporadaId) qs.set("temporada_id", String(temporadaId));
    if (includeCSV) qs.set("include", includeCSV);

    const base = isBrowser ? "" : API_BASE;
    return `${base}/api/jugadores/full/?${qs.toString()}`;
  }, [jugadorId, temporadaId, includeCSV]);

  // Clave de dependencia para evitar peticiones con params incompletos
  const canFetch = useMemo(() => {
    if (!enabled) return false;
    if (jugadorId) return true;
    return false;
  }, [enabled, jugadorId]);

  const refetch = async (signal?: AbortSignal) => {
    if (!canFetch) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(url, {
        signal,
        cache: "no-store",
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const json = (await res.json()) as JugadorFullResponse;
      setData(json);
    } catch (err: any) {
      if (err?.name !== "AbortError") {
        setError(err?.message || "Error al cargar el jugador");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!canFetch) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    refetch(controller.signal);
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, canFetch]);

  return { data, loading, error, refetch };
}



