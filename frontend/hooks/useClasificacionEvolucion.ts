"use client";

import { useEffect, useState } from "react";

const API_BASE =
  typeof window !== "undefined"
    ? window.location.origin
    : process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es";

export type EquipoEvolucion = {
  club_id: number;
  nombre: string;
  escudo: string;
  slug: string | null;
  posicion_actual: number | null;
  evolucion: Array<{
    jornada: number;
    posicion: number | null;
    puntos: number;
    goles_favor: number;
    goles_contra: number;
  }>;
};

export type ClasificacionEvolucionResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornadas: number[];
  equipos: EquipoEvolucion[];
};

export function useClasificacionEvolucion(
  grupoId: number | string | null,
  enabled: boolean = true
) {
  const [data, setData] = useState<ClasificacionEvolucionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!grupoId || !enabled) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    // Flag de cancelación para evitar actualizar estado si el componente se desmonta
    // durante el fetch (evita race conditions y warnings de React)
    let cancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const url = `${API_BASE}/api/clubes/clasificacion-evolucion/?grupo_id=${grupoId}`;
        const res = await fetch(url, {
          method: "GET",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!res.ok) {
          const errorText = await res.text();
          console.error(
            "useClasificacionEvolucion error response:",
            res.status,
            errorText
          );
          throw new Error(
            `Error ${res.status}: ${
              errorText || "No se pudo cargar la evolución de clasificación"
            }`
          );
        }

        const json: ClasificacionEvolucionResponse = await res.json();

        // Verificar cancelación antes de actualizar estado
        if (cancelled) return;

        setData(json);
      } catch (err: any) {
        // Verificar cancelación antes de actualizar estado con error
        if (cancelled) return;
        console.error("useClasificacionEvolucion error:", err);
        const errorMessage =
          err.message || "No se pudo cargar la evolución de clasificación.";
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
  }, [grupoId, enabled]);

  return {
    data,
    loading,
    error,
  };
}










