// /frontend/hooks/useEquipoReconocimientos.ts
"use client";

import { useEffect, useState } from "react";

const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

export type ReconocimientoEquipo = {
  club: {
    id: number;
    nombre: string;
    nombre_corto?: string | null;
    slug?: string | null;
  };
  mejor_equipo_jornadas_division: number;
  mejor_equipo_jornadas_global: number;
  detalle: {
    mejor_equipo_jornadas_division: Array<{
      temporada: string;
      grupo: string;
      jornada: number;
      fecha: string | null;
      puntos: number;
      victorias: number;
      empates: number;
      derrotas: number;
      goles_favor: number;
      goles_contra: number;
    }>;
    mejor_equipo_jornadas_global: Array<{
      temporada: string;
      semana: string;
      fecha_inicio: string;
      fecha_fin: string;
      puntos: number;
      puntos_base: number;
      coef_division: number;
      grupo: string;
      victorias: number;
      empates: number;
      derrotas: number;
    }>;
  };
};

export function useEquipoReconocimientos(
  clubId: number | string | null,
  enabled: boolean = true
) {
  const [data, setData] = useState<ReconocimientoEquipo | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !clubId) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const url = `${API_BASE}/api/fantasy/equipo/${clubId}/reconocimientos/`;
        const res = await fetch(url, {
          method: "GET",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!res.ok) {
          const errorText = await res.text();
          console.error("useEquipoReconocimientos error response:", res.status, errorText);
          if (res.status === 404) {
            throw new Error("Equipo no encontrado");
          }
          throw new Error(`Error ${res.status}: ${errorText || "No se pudieron cargar los reconocimientos"}`);
        }

        const json: ReconocimientoEquipo = await res.json();

        if (cancelled) return;

        setData(json);
      } catch (err: any) {
        if (cancelled) return;
        console.error("useEquipoReconocimientos error:", err);
        const errorMessage = err.message || "No se pudieron cargar los reconocimientos del equipo.";
        setError(errorMessage);
        setData(null);
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
  }, [clubId, enabled]);

  return {
    data,
    loading,
    error,
  };
}










