"use client";

import React from "react";

export type SancionJornada = {
  jugador_id: number;
  nombre: string;
  apodo: string;
  slug?: string | null;
  foto: string;
  club_id: number;
  club_nombre: string;
  club_slug?: string | null;
  amarillas: number;
  dobles_amarillas: number;
  rojas: number;
  severidad_puntos: number;
};

export type SancionesJornadaResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornada: number | null;
  sancionados: SancionJornada[];
};

export function useSancionesJornada(grupoId: number | null, jornada: number | null) {
  const [data, setData] = React.useState<SancionesJornadaResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!grupoId) {
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
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        if (jornada != null) params.set("jornada", String(jornada));

        const res = await fetch(`/api/estadisticas/sanciones-jornada/?${params.toString()}`, { cache: "no-store" });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const json = (await res.json()) as SancionesJornadaResponse;

        if (!cancelled) setData(json);
      } catch (err: any) {
        if (!cancelled) setError(err.message || "Error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchData();
    return () => { cancelled = true; };
  }, [grupoId, jornada]);

  return { loading, error, data, sancionados: data?.sancionados ?? [] };
}
