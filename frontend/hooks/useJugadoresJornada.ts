// /frontend/hooks/useJugadoresJornada.ts
"use client";

import { useEffect, useState } from "react";

type JugadorJornada = {
  jugador_id: number;
  nombre: string;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  club_slug?: string | null;
  puntos: number;
  detalles?: string[];
};

type ApiResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornada: number | null;
  jugador_de_la_jornada: JugadorJornada | null;
  ranking_jugadores: JugadorJornada[];
};

export function useJugadoresJornada(
  grupoId: number | null,
  jornada: number | null
) {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [jugadorTop, setJugadorTop] = useState<JugadorJornada | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Si no hay grupo seleccionado, limpiar todos los estados.
    if (!grupoId) {
      setData(null);
      setJugadorTop(null);
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
        // Construir parámetros de la petición.
        // La jornada es opcional: si no se especifica, se obtiene el jugador de la última jornada jugada.
        const params = new URLSearchParams();
        params.set("grupo_id", String(grupoId));
        if (jornada != null) {
          params.set("jornada", String(jornada));
        }

        // Usamos ruta relativa /api/ para aprovechar el proxy de Nginx.
        // Esto evita problemas de CORS y permite que el mismo dominio sirva
        // tanto el frontend como el backend.
        const res = await fetch(
          `/api/valoraciones/jugadores-jornada/?${params.toString()}`,
          {
            method: "GET",
            cache: "no-store", // Siempre obtener datos frescos
          }
        );

        if (!res.ok) {
          throw new Error("Bad status " + res.status);
        }

        const json: ApiResponse = await res.json();

        if (cancelled) return;

        // Normalizar datos del jugador top con fallbacks para campos opcionales.
        // Esto asegura que siempre tengamos valores válidos incluso si el backend
        // no envía algunos campos (foto, escudo, nombre del club).
        let top: JugadorJornada | null = json.jugador_de_la_jornada || null;
        if (top) {
          top = {
            ...top,
            foto: top.foto || "",
            club_escudo: top.club_escudo || "",
            club_nombre: top.club_nombre || "",
          };
        }

        setData(json);
        setJugadorTop(top);
      } catch (err: any) {
        if (cancelled) return;
        console.error("useJugadoresJornada error:", err);
        setError("No se pudo cargar la valoración de jugadores.");
        setData(null);
        setJugadorTop(null);
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
  }, [grupoId, jornada]);

  return {
    data,
    jugadorTop,
    loading,
    error,
  };
}
