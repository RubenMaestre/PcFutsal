// /frontend/hooks/usePartidosList.ts
"use client";

import { useEffect, useState } from "react";

// Determina la base de la URL de la API según el contexto (navegador vs servidor).
// En el navegador, se usa window.location.origin para aprovechar el proxy de Nginx.
// En SSR, se usa la variable de entorno o un fallback.
const API_BASE =
  typeof window !== "undefined"
    ? window.location.origin
    : process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es";

export type PartidoListItem = {
  id: number;
  identificador_federacion: string | null;
  jornada_numero: number;
  fecha_hora: string | null;
  jugado: boolean;
  local: {
    id: number;
    nombre: string;
    escudo: string;
    slug: string | null;
  };
  visitante: {
    id: number;
    nombre: string;
    escudo: string;
    slug: string | null;
  };
  goles_local: number | null;
  goles_visitante: number | null;
  grupo: {
    id: number;
    nombre: string;
    slug: string | null;
    competicion: {
      id: number;
      nombre: string;
      slug: string | null;
    } | null;
    temporada: {
      id: number;
      nombre: string;
    } | null;
  } | null;
};

export type PartidosListResponse = {
  scope: "GLOBAL" | "COMPETICIONES";
  filtros: {
    competicion_id: number | null;
    grupo_id: number | null;
    jornada: number | null;
  };
  partidos: PartidoListItem[];
};

export function usePartidosList(
  scope: "GLOBAL" | "COMPETICIONES" = "GLOBAL",
  competicionId?: number | null,
  grupoId?: number | null,
  jornada?: number | null,
  random?: boolean,
  limit?: number,
  week?: string | null // fecha del martes en formato YYYY-MM-DD
) {
  const [data, setData] = useState<PartidosListResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Flag para cancelar la petición si el componente se desmonta antes de que termine.
    // Evita errores de "Can't perform a React state update on an unmounted component".
    let cancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        params.set("scope", scope);
        
        // Los filtros de competición/grupo/jornada solo se aplican cuando el scope es "COMPETICIONES".
        // En scope "GLOBAL", se ignoran estos filtros para mostrar partidos de todas las competiciones.
        if (scope === "COMPETICIONES") {
          if (competicionId) {
            params.set("competicion_id", String(competicionId));
          }
          if (grupoId) {
            params.set("grupo_id", String(grupoId));
          }
          if (jornada != null) {
            params.set("jornada", String(jornada));
          }
        }
        
        // El parámetro 'random' permite obtener partidos aleatorios, útil para destacados en la home.
        if (random) {
          params.set("random", "true");
        }
        
        // El parámetro 'week' permite filtrar por semana (fecha del martes en formato YYYY-MM-DD).
        // Esto es útil para mostrar partidos de una semana específica en la home.
        if (week) {
          params.set("week", week);
        }
        
        if (limit) {
          params.set("limit", String(limit));
        }

        const url = `${API_BASE}/api/partidos/lista/?${params.toString()}`;
        const res = await fetch(url, {
          method: "GET",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!res.ok) {
          const errorText = await res.text();
          console.error("usePartidosList error response:", res.status, errorText);
          throw new Error(`Error ${res.status}: ${errorText || "No se pudo cargar la lista de partidos"}`);
        }

        const json: PartidosListResponse = await res.json();

        if (cancelled) return;

        setData(json);
      } catch (err: any) {
        if (cancelled) return;
        console.error("usePartidosList error:", err);
        const errorMessage = err.message || "No se pudo cargar la lista de partidos.";
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
  }, [scope, competicionId, grupoId, jornada, random, limit, week]);

  return {
    data,
    loading,
    error,
  };
}

export default usePartidosList;

