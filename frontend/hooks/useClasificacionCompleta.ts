// /frontend/hooks/useClasificacionCompleta.ts
"use client";

import React from "react";

type ClasifRow = {
  club_id?: number;
  nombre?: string;
  club_nombre?: string;
  escudo?: string;
  club_escudo?: string;
  puntos?: number;
  pt?: number;
  pj?: number;
  pg?: number;
  pe?: number;
  pp?: number;
  gf?: number;
  gc?: number;
  dg?: number;
};

type ApiResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada?: string;
  };
  scope?: "overall" | "home" | "away";
  jornadas_disponibles?: number[];
  jornada_aplicada?: number | null;
  tabla: ClasifRow[];
};

export function useClasificacionCompleta(
  grupoId: number | null,
  scope: "overall" | "home" | "away" = "overall",
  jornada?: number | null
) {
  const [data, setData] = React.useState<ApiResponse | null>(null);
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
        // Construimos la URL con los parámetros de filtrado.
        // El scope permite obtener clasificación general, solo local o solo visitante.
        // La jornada es opcional y permite ver la clasificación en un momento específico.
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        params.set("scope", scope);
        if (jornada && Number.isFinite(jornada)) {
          params.set("jornada", String(jornada));
        }

        // Usamos ruta relativa /api/ para aprovechar el proxy de Nginx.
        // cache: "no-store" asegura que siempre obtenemos datos frescos.
        const res = await fetch(
          `/api/estadisticas/clasificacion-completa/?${params.toString()}`,
          {
            method: "GET",
            cache: "no-store",
          }
        );

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const json = await res.json();
        if (!cancelled) {
          setData(json);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message || "Error");
        }
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
  }, [grupoId, scope, jornada]); // 👈 añadimos jornada

  return { data, loading, error };
}
