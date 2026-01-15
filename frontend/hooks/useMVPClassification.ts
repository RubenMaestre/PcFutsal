// hooks/useMVPClassification.ts
"use client";

import { useEffect, useState } from "react";

type MVPRankingRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  es_portero?: boolean;
  // 👇 campos del endpoint mvp-clasificacion
  puntos_acumulados: number;
  puntos_jornada: number;
  posicion?: number;
};

type MVPAccumData = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornada_aplicada: number | null;
  jornadas_disponibles: number[];
  ranking: MVPRankingRow[];
  prev_ranking?: { jugador_id: number; posicion: number }[];
};

type UseMVPOptions = {
  jornada?: number | null;
  onlyPorteros?: boolean;
};

export function useMVPClassification(
  grupoId: number | null,
  options: UseMVPOptions = {}
) {
  const { jornada = null, onlyPorteros = false } = options;

  const [data, setData] = useState<MVPAccumData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!grupoId) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchAccum() {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        if (jornada !== null && jornada !== undefined) {
          params.set("jornada", String(jornada));
        }
        if (onlyPorteros) {
          params.set("only_porteros", "1");
        }

        // usamos el endpoint de ACUMULADO
        const res = await fetch(
          `/api/valoraciones/mvp-clasificacion/?${params.toString()}`,
          { cache: "no-store" }
        );
        if (!res.ok) throw new Error("Error al cargar clasificación MVP");
        const json = (await res.json()) as MVPAccumData;

        if (!cancelled) setData(json);
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message || "Error desconocido");
          setData(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchAccum();
    return () => {
      cancelled = true;
    };
  }, [grupoId, jornada, onlyPorteros]);

  return { data, loading, error };
}



