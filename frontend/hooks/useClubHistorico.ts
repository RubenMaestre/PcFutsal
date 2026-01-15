// Hook para obtener el histórico de temporadas de un club
"use client";

import { useState, useEffect } from "react";

const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en navegador → relativo

export interface HistoricoItem {
  temporada: string;
  division: string;
  grupo: string;
  grupo_id: number;
  competicion_id: number;
  posicion: number | null;
  puntos: number;
}

export interface ClubHistoricoResponse {
  club_id: number;
  club_nombre: string;
  historico: HistoricoItem[];
}

export function useClubHistorico(clubId: string | string[] | undefined) {
  const [data, setData] = useState<ClubHistoricoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!clubId) {
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    const load = async () => {
      try {
        setLoading(true);
        setError(null);

        // Determinar si es ID numérico o slug
        const isNumeric = typeof clubId === 'string' && /^\d+$/.test(clubId);
        const queryParam = isNumeric ? `club_id=${clubId}` : `slug=${clubId}`;
        
        const base = isBrowser ? "" : API_BASE;
        const res = await fetch(`${base}/api/clubes/historico/?${queryParam}`, {
          signal: controller.signal,
        });

        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Error ${res.status}: ${errorText || "Error cargando el histórico del club"}`);
        }

        const json = await res.json();

        if (!json || !json.historico) {
          throw new Error("Respuesta del servidor inválida: no se encontró el histórico");
        }

        setData(json);
      } catch (err: any) {
        if (err.name !== "AbortError") {
          console.error("Error loading club historico:", err);
          setError(err.message || "Error al cargar el histórico del club");
        }
      } finally {
        setLoading(false);
      }
    };

    load();
    return () => controller.abort();
  }, [clubId]);

  return { data, loading, error };
}

