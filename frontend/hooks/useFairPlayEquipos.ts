"use client";

import React from "react";

export type FairPlayEquipo = {
  club_id: number;
  club_nombre: string;
  club_escudo: string;
  club_slug?: string | null;
  amarillas: number;
  dobles_amarillas: number;
  rojas: number;
  puntos_fair_play: number;
};

export type FairPlayResponse = {
  grupo: { id: number; nombre: string; competicion: string; temporada: string };
  equipos: FairPlayEquipo[];
};

export function useFairPlayEquipos(grupoId: number | null) {
  const [data, setData] = React.useState<FairPlayResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    // Si no hay grupoId, no tiene sentido hacer la petición.
    if (!grupoId) {
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
        // Usamos ruta relativa /api/ para aprovechar el proxy de Nginx.
        // cache: "no-store" asegura que siempre obtenemos datos frescos.
        const url = `/api/estadisticas/fair-play-equipos/?grupo_id=${grupoId}`;
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const json = (await res.json()) as FairPlayResponse;
        if (!cancelled) setData(json);
      } catch (err: any) {
        if (!cancelled) setError(err.message || "Error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchData();
    return () => { cancelled = true; };
  }, [grupoId]);

  return { loading, error, data, equipos: data?.equipos ?? [] };
}
