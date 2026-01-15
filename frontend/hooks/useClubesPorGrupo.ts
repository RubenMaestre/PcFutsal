// hooks/useClubesPorGrupo.ts
"use client";

import { useEffect, useState } from "react";

// Determina la base de la URL de la API según el contexto (navegador vs servidor).
// En el navegador, se usa una URL relativa para aprovechar el proxy de Nginx.
// En SSR, se usa la variable de entorno NEXT_PUBLIC_API_BASE_URL.
const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

export type ClubLite = {
  id: number;
  slug?: string | null;  // Slug para URLs SEO-friendly
  nombre_oficial: string;
  nombre_corto?: string;
  localidad?: string;
  pabellon?: string;
  escudo_url?: string;
  competicion_nombre?: string;
  grupo_nombre?: string;
};

type ApiResponse = {
  grupo?: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  competicion?: {
    id: number;
    nombre: string;
  };
  temporada?: {
    id: number;
    nombre: string;
  };
  random?: boolean;
  count: number;
  results: ClubLite[];
};

export function useClubesPorGrupo(grupoId: number | null, random: boolean = false) {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchClubs = async () => {
      setLoading(true);
      setError(null);

      try {
        // Construir URL según los parámetros disponibles.
        // Prioridad: grupoId > random > todos.
        // Esto permite diferentes casos de uso: clubes de un grupo específico,
        // clubes aleatorios para destacados, o todos los clubes de la temporada activa.
        let url: string;
        if (grupoId) {
          // Clubes de un grupo específico
          url = isBrowser
            ? `/api/clubes/lista/?grupo_id=${grupoId}`
            : `${API_BASE}/api/clubes/lista/?grupo_id=${grupoId}`;
        } else if (random) {
          // Clubes aleatorios (útil para destacados en la home)
          url = isBrowser
            ? `/api/clubes/lista/?random=true`
            : `${API_BASE}/api/clubes/lista/?random=true`;
        } else {
          // Sin parámetros: todos los clubes de la temporada activa
          url = isBrowser
            ? `/api/clubes/lista/`
            : `${API_BASE}/api/clubes/lista/`;
        }

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
          setError(err.message || "Error al cargar clubes");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchClubs();

    return () => {
      controller.abort();
    };
  }, [grupoId, random]);

  return { data, loading, error };
}
