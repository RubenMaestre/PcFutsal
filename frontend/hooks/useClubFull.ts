// hooks/useClubFull.ts
"use client";

import { useEffect, useMemo, useState } from "react";

// Determina la base de la URL de la API según el contexto (navegador vs servidor).
// En el navegador, se usa una URL relativa para aprovechar el proxy de Nginx.
// En SSR, se usa la variable de entorno NEXT_PUBLIC_API_BASE_URL.
const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

// -------------------- Tipados de respuesta (resumen) --------------------
export type ClubFullResponse = {
  club: {
    id: number;
    slug?: string | null;
    nombre_oficial: string;
    nombre_corto?: string;
    siglas?: string;
    escudo_url?: string;
    colores?: { primario?: string; secundario?: string };
    pabellon?: string;
    direccion?: string;
    ciudad?: string;
    provincia?: string;
    lat?: number | null;
    lng?: number | null;
    aforo_aprox?: number | null;
    web?: string;
    contacto?: { email?: string; telefono?: string };
    redes?: {
      twitter?: string;
      instagram?: string;
      facebook?: string;
      tiktok?: string;
      youtube?: string;
    };
    fundado_en?: number | null;
    historia_resumida?: string;
  };

  contexto?: {
    temporada?: { id: number; nombre: string };
    grupo?: { id: number; nombre: string; competicion: string; temporada: string };
  } | null;

  clasificacion_actual?: {
    posicion?: number | null;
    puntos: number;
    pj: number;
    v: number;
    e: number;
    d: number;
    gf: number;
    gc: number;
    dg: number;
    racha: string;
    casa: { puntos: number; gf: number; gc: number };
    fuera: { puntos: number; gf: number; gc: number };
    ult_5: string;
    clean_sheets: number;
    goles_pp: number;
    menciones: {
      equipo_de_la_jornada: number;
      partido_estrella: number;
      mvp_jornada: number;
    };
  } | null;

  participaciones: Array<{
    grupo_id: number;
    grupo_nombre: string;
    competicion: string;
    temporada: string;
    puntos: number;
    posicion_actual?: number | null;
    racha: string;
  }>;

  plantilla?: {
    temporada_id: number;
    jugadores: any[]; // mismo shape que JugadorEnClubTemporadaSerializer
  } | null;

  staff?: any[] | null;       // StaffClubSerializer o estructura equivalente ClubStaffMember
  valoracion?: any | null;    // ValoracionClubSerializer
  series?: {
    progreso_jornada: { labels: number[]; puntos_acum: number[]; posicion: (number | null)[] };
    historico_pos_final: { labels: string[]; pos_final: (number | null)[]; puntos: number[] };
  } | null;

  awards?: Array<{ tipo: string; grupo_id: number; jornada: number; notas: string }>;
  media?: Array<{ tipo: string; titulo: string; url: string }>;
  notas?: Array<{ titulo: string; texto: string; enlace: string; grupo_id: number }>;
  travel?: {
    resumen: { total_km: number; avg_km: number; max_km: number; min_km: number };
    max_km_rival?: { id: number | null; nombre: string };
    min_km_rival?: { id: number | null; nombre: string };
  } | null;
};

// -------------------- Parámetros del hook --------------------
export type UseClubFullParams = {
  clubId?: number | null;
  slug?: string | null;
  temporadaId?: number | null;
  grupoId?: number | null;
  /**
   * CSV con bloques a incluir.
   * Posibles: progress,history,awards,media,notes,travel,staff,roster
   * Por defecto en backend: progress,history,staff,roster
   */
  include?: string | string[];
  /** Auto-fetch al montar si hay clubId/slug válidos (true por defecto) */
  enabled?: boolean;
};

export function useClubFull(params: UseClubFullParams) {
  const {
    clubId = null,
    slug = null,
    temporadaId = null,
    grupoId = null,
    include,
    enabled = true,
  } = params || {};

  const [data, setData] = useState<ClubFullResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Normaliza include a CSV
  const includeCSV = useMemo(() => {
    if (!include) return undefined;
    if (Array.isArray(include)) return include.join(",");
    return include;
  }, [include]);

  // Construcción segura del URL (server vs browser)
  const url = useMemo(() => {
    const qs = new URLSearchParams();
    if (clubId) qs.set("club_id", String(clubId));
    if (!clubId && slug) qs.set("slug", String(slug));
    if (temporadaId) qs.set("temporada_id", String(temporadaId));
    if (grupoId) qs.set("grupo_id", String(grupoId));
    if (includeCSV) qs.set("include", includeCSV);

    const base = isBrowser ? "" : API_BASE;
    return `${base}/api/clubes/full/?${qs.toString()}`;
  }, [clubId, slug, temporadaId, grupoId, includeCSV]);

  // Clave de dependencia para evitar peticiones con params incompletos
  const canFetch = useMemo(() => {
    if (!enabled) return false;
    if (clubId || slug) return true;
    return false;
  }, [enabled, clubId, slug]);

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
      const json = (await res.json()) as ClubFullResponse;
      setData(json);
    } catch (err: any) {
      if (err?.name !== "AbortError") {
        setError(err?.message || "Error al cargar el club");
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
