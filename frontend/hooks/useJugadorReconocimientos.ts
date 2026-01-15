// /frontend/hooks/useJugadorReconocimientos.ts
"use client";

import { useEffect, useState } from "react";

const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

export type ReconocimientoJugador = {
  jugador: {
    id: number;
    nombre: string;
    apodo?: string | null;
    slug?: string | null;
  };
  mvp_partidos: number;
  mvp_jornadas_division: number;
  mvp_jornadas_global: number;
  goleador_jornadas_division: number;
  detalle: {
    mvp_partidos: Array<{
      partido_id: number;
      fecha: string | null;
      puntos: number;
      local: string;
      visitante: string;
      goles: number;
      tarjetas_amarillas: number;
      tarjetas_rojas: number;
    }>;
    mvp_jornadas_division: Array<{
      temporada: string;
      grupo: string;
      jornada: number;
      fecha: string | null;
      puntos: number;
      puntos_base: number;
    }>;
    mvp_jornadas_global: Array<{
      temporada: string;
      semana: string;
      fecha_inicio: string;
      fecha_fin: string;
      puntos: number;
      puntos_base: number;
      coef_division: number;
      grupo: string;
    }>;
    goleador_jornadas_division: Array<{
      temporada: string;
      grupo: string;
      jornada: number;
      fecha: string | null;
      goles: number;
    }>;
  };
};

export function useJugadorReconocimientos(
  jugadorId: number | string | null,
  enabled: boolean = true
) {
  const [data, setData] = useState<ReconocimientoJugador | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !jugadorId) {
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
        const url = `${API_BASE}/api/fantasy/jugador/${jugadorId}/reconocimientos/`;
        const res = await fetch(url, {
          method: "GET",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!res.ok) {
          const errorText = await res.text();
          console.error("useJugadorReconocimientos error response:", res.status, errorText);
          if (res.status === 404) {
            throw new Error("Jugador no encontrado");
          }
          throw new Error(`Error ${res.status}: ${errorText || "No se pudieron cargar los reconocimientos"}`);
        }

        const json: ReconocimientoJugador = await res.json();

        if (cancelled) return;

        setData(json);
      } catch (err: any) {
        if (cancelled) return;
        console.error("useJugadorReconocimientos error:", err);
        const errorMessage = err.message || "No se pudieron cargar los reconocimientos del jugador.";
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
  }, [jugadorId, enabled]);

  return {
    data,
    loading,
    error,
  };
}










