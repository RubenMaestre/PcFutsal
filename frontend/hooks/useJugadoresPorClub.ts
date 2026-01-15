// hooks/useJugadoresPorClub.ts
"use client";

import { useEffect, useState } from "react";

// Determina la base de la URL de la API según el contexto (navegador vs servidor).
// En el navegador, se usa una URL relativa para aprovechar el proxy de Nginx.
// En SSR, se usa la variable de entorno NEXT_PUBLIC_API_BASE_URL.
const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

export type JugadorLite = {
  id: number;
  nombre: string;
  apodo?: string;
  slug?: string | null;
  foto_url?: string;
  posicion_principal?: string;
  edad_display?: number | null;
  club_id?: number | null;
  club_nombre?: string | null;
  club_slug?: string | null;
  club_escudo_url?: string | null;
  temporada_nombre?: string | null;
  dorsal?: string | null;
  partidos_jugados?: number;
  goles?: number;
};

type ApiResponse = {
  club?: {
    id: number;
    nombre: string;
    slug?: string;
  };
  temporada?: {
    id: number;
    nombre: string;
  };
  random?: boolean;
  search?: string | null;
  count: number;
  results: JugadorLite[];
};

export function useJugadoresPorClub(clubId: number | null, random: boolean = false, search?: string) {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Si no hay parámetros válidos (clubId, random o search), no hacer la petición.
    // Esto evita peticiones innecesarias cuando el componente aún no tiene datos.
    if (!clubId && !random && !search) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    // AbortController permite cancelar la petición si el componente se desmonta
    // o si cambian los parámetros antes de que termine la petición anterior.
    const controller = new AbortController();

    const fetchJugadores = async () => {
      setLoading(true);
      setError(null);

      try {
        // Construir URL con parámetros según lo disponible.
        // Prioridad: clubId > random > search.
        // Esto permite diferentes casos de uso: jugadores de un club, aleatorios, o búsqueda.
        const params = new URLSearchParams();
        if (clubId) {
          params.set("club_id", String(clubId));
        } else if (random || !clubId) {
          params.set("random", "true");
        }
        if (search && search.trim()) {
          params.set("search", search.trim());
        }

        const url = isBrowser
          ? `/api/jugadores/lista/?${params.toString()}`
          : `${API_BASE}/api/jugadores/lista/?${params.toString()}`;

        const res = await fetch(url, {
          signal: controller.signal,
          cache: "no-store",
        });

        if (!res.ok) {
          throw new Error(`Error ${res.status}`);
        }

        const json = await res.json();
        setData(json);
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError(err.message || "Error al cargar jugadores");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchJugadores();

    return () => {
      controller.abort();
    };
  }, [clubId, random, search]);

  return { data, loading, error };
}

