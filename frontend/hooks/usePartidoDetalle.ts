// /frontend/hooks/usePartidoDetalle.ts
"use client";

import { useEffect, useState } from "react";

const API_BASE =
  typeof window !== "undefined"
    ? window.location.origin
    : process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es";

export type PartidoDetalle = {
  partido: {
    id: number;
    identificador_federacion: string | null;
    jornada_numero: number;
    fecha_hora: string | null;
    jugado: boolean;
    pabellon: string;
    indice_intensidad: number | null;
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
  };
  arbitros: Array<{
    id: number | null;
    nombre: string;
    rol: string;
    slug: string | null;
  }>;
  eventos: Array<{
    id: number;
    minuto: number | null;
    tipo_evento: "gol" | "gol_pp" | "amarilla" | "doble_amarilla" | "roja" | "mvp";
    parte: "primera" | "segunda" | "prorroga" | "desconocida";
    jugador: {
      id: number;
      nombre: string;
      slug: string | null;
      foto: string;
    } | null;
    club: {
      id: number;
      nombre: string;
      slug: string | null;
      lado: "local" | "visitante" | null;
    } | null;
    nota: string;
  }>;
  alineaciones: {
    local: {
      club_id: number;
      titulares: Array<{
        jugador_id: number | null;
        nombre: string;
        slug: string | null;
        foto: string;
        dorsal: string;
        etiqueta: string;
        titular: boolean;
        goles: number;
        tarjetas_amarillas: number;
        tarjetas_dobles_amarillas: number;
        tarjetas_rojas: number;
        mvp: boolean;
      }>;
      suplentes: Array<{
        jugador_id: number | null;
        nombre: string;
        slug: string | null;
        foto: string;
        dorsal: string;
        etiqueta: string;
        titular: boolean;
        goles: number;
        tarjetas_amarillas: number;
        tarjetas_dobles_amarillas: number;
        tarjetas_rojas: number;
        mvp: boolean;
      }>;
      staff: Array<{
        nombre: string;
        rol: string;
        staff_id: number | null;
      }>;
    };
    visitante: {
      club_id: number;
      titulares: Array<{
        jugador_id: number | null;
        nombre: string;
        slug: string | null;
        foto: string;
        dorsal: string;
        etiqueta: string;
        titular: boolean;
        goles: number;
        tarjetas_amarillas: number;
        tarjetas_dobles_amarillas: number;
        tarjetas_rojas: number;
        mvp: boolean;
      }>;
      suplentes: Array<{
        jugador_id: number | null;
        nombre: string;
        slug: string | null;
        foto: string;
        dorsal: string;
        etiqueta: string;
        titular: boolean;
        goles: number;
        tarjetas_amarillas: number;
        tarjetas_dobles_amarillas: number;
        tarjetas_rojas: number;
        mvp: boolean;
      }>;
      staff: Array<{
        nombre: string;
        rol: string;
        staff_id: number | null;
      }>;
    };
  };
  estadisticas: {
    goles_total: number;
    goles_local: number;
    goles_visitante: number;
    goles_primera_parte: number;
    goles_segunda_parte: number;
    amarillas_total: number;
    dobles_amarillas_total: number;
    rojas_total: number;
    mvps: number;
  };
};

export function usePartidoDetalle(
  partidoId: number | string | null,
  identificadorFederacion?: string | null
) {
  const [data, setData] = useState<PartidoDetalle | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Validar que tenemos un partidoId válido o un identificador_federacion
    const hasPartidoId = partidoId !== null && partidoId !== undefined && partidoId !== '';
    const hasIdentificador = identificadorFederacion !== null && identificadorFederacion !== undefined && identificadorFederacion !== '';
    
    if (!hasPartidoId && !hasIdentificador) {
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
        // Determinar si el partidoId es un ID interno o un identificador_federacion
        // Los IDs internos suelen ser números más pequeños (< 10000)
        // Los identificadores_federacion son números más grandes
        const partidoIdNum = typeof partidoId === 'number' ? partidoId : (partidoId ? parseInt(String(partidoId), 10) : null);
        const isLikelyFederacionId = partidoIdNum && partidoIdNum > 10000;
        
        const params = new URLSearchParams();
        
        if (identificadorFederacion) {
          // Si hay identificadorFederacion explícito, usarlo directamente
          params.set("identificador_federacion", identificadorFederacion);
        } else if (partidoId) {
          // Si parece ser un identificador_federacion (número grande), intentar primero por ahí
          if (isLikelyFederacionId) {
            params.set("identificador_federacion", String(partidoId));
          } else {
            params.set("partido_id", String(partidoId));
          }
        }

        const url = `${API_BASE}/api/partidos/detalle/?${params.toString()}`;
        let res = await fetch(url, {
          method: "GET",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
        });

        // Si falló y era un número, intentar con el otro método
        if (!res.ok && res.status === 404 && partidoId && !identificadorFederacion) {
          const alternateParams = new URLSearchParams();
          if (isLikelyFederacionId) {
            // Ya intentó por identificador_federacion, ahora intentar por partido_id
            alternateParams.set("partido_id", String(partidoId));
          } else {
            // Ya intentó por partido_id, ahora intentar por identificador_federacion
            alternateParams.set("identificador_federacion", String(partidoId));
          }
          
          const alternateUrl = `${API_BASE}/api/partidos/detalle/?${alternateParams.toString()}`;
          res = await fetch(alternateUrl, {
            method: "GET",
            cache: "no-store",
            headers: {
              "Content-Type": "application/json",
            },
          });
        }

        if (!res.ok) {
          const errorText = await res.text();
          console.error("usePartidoDetalle error response:", res.status, errorText);
          if (res.status === 404) {
            throw new Error("Partido no encontrado");
          }
          throw new Error(`Error ${res.status}: ${errorText || "No se pudo cargar el detalle del partido"}`);
        }

        const json: PartidoDetalle = await res.json();

        if (cancelled) return;

        setData(json);
      } catch (err: any) {
        if (cancelled) return;
        console.error("usePartidoDetalle error:", err);
        const errorMessage = err.message || "No se pudo cargar el detalle del partido.";
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
  }, [partidoId, identificadorFederacion]);

  return {
    data,
    loading,
    error,
  };
}

export default usePartidoDetalle;

