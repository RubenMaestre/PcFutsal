// /frontend/hooks/useMVPPartido.ts
"use client";

import { useEffect, useState } from "react";

// Determina la base de la URL de la API según el contexto (navegador vs servidor).
// En el navegador, se usa una URL relativa para aprovechar el proxy de Nginx.
// En SSR, se usa la variable de entorno NEXT_PUBLIC_API_BASE_URL.
const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

export type MVPPartidoResponse = {
  partido: {
    id: number;
    local: string;
    visitante: string;
    fecha: string | null;
  };
  mvp: {
    jugador: {
      id: number;
      nombre: string;
      apodo?: string | null;
      slug?: string | null;
      foto?: string;
    };
    puntos: number;
    goles: number;
    tarjetas_amarillas: number;
    tarjetas_rojas: number;
    mvp_evento: boolean;
    equipo_ganador: boolean;
  } | null;
  detail?: string;
};

export function useMVPPartido(
  partidoId: number | string | null,
  enabled: boolean = true
) {
  const [data, setData] = useState<MVPPartidoResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Si el hook está deshabilitado o no hay partidoId, no hacer la petición.
    if (!enabled || !partidoId) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    // Flag para cancelar la petición si el componente se desmonta antes de que termine.
    // Evita errores de "Can't perform a React state update on an unmounted component".
    let cancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const url = `${API_BASE}/api/fantasy/partido/${partidoId}/mvp/`;
        const res = await fetch(url, {
          method: "GET",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!res.ok) {
          const errorText = await res.text();
          console.error("useMVPPartido error response:", res.status, errorText);
          if (res.status === 404) {
            throw new Error("MVP del partido no encontrado");
          }
          throw new Error(`Error ${res.status}: ${errorText || "No se pudo cargar el MVP del partido"}`);
        }

        const json: MVPPartidoResponse = await res.json();

        if (cancelled) return;

        setData(json);
      } catch (err: any) {
        if (cancelled) return;
        console.error("useMVPPartido error:", err);
        const errorMessage = err.message || "No se pudo cargar el MVP del partido.";
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
  }, [partidoId, enabled]);

  return {
    data,
    loading,
    error,
  };
}










