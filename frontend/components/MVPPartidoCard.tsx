// /frontend/components/MVPPartidoCard.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useMVPPartido } from "../hooks/useMVPPartido";

type Props = {
  partidoId: number | string | null;
  dict: any;
  lang?: string;
};

export default function MVPPartidoCard({ partidoId, dict, lang = "es" }: Props) {
  const { data, loading, error } = useMVPPartido(partidoId, !!partidoId);

  const labels = dict?.partido_mvp || {};

  if (!partidoId) {
    return null;
  }

  if (loading) {
    return (
      <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
        <div className="text-center text-sm text-white/60">
          {labels.loading || "Cargando MVP del partido..."}
        </div>
      </div>
    );
  }

  // Si hay error o no hay MVP, no mostramos nada en lugar de mostrar un error.
  // Esto evita mostrar mensajes de error cuando simplemente no hay MVP asignado aún.
  if (error || !data || !data.mvp) {
    return null; // No mostrar si no hay MVP o hay error
  }

  const mvp = data.mvp;
  const jugador = mvp.jugador;
  // Prioridad: apodo (más personal) > nombre (más formal)
  const nombreJugador = jugador.apodo || jugador.nombre || "";
  const fotoJugador = jugador.foto || "";

  return (
    <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6 relative overflow-hidden">
      {/* Badge decorativo de MVP */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 rounded-bl-full -z-0"></div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-[var(--color-text)] mb-1">
              {labels.title || "MVP del Partido"}
            </h3>
            <p className="text-sm text-white/60">
              {labels.subtitle || "Jugador destacado del encuentro"}
            </p>
          </div>
          <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border-2 border-yellow-500/30">
            <span className="text-2xl">⭐</span>
          </div>
        </div>

        <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
          {/* Foto del jugador */}
          <div className="flex-shrink-0">
            {fotoJugador ? (
              <Link
                href={jugador.slug ? `/${lang}/jugadores/${jugador.slug}` : `/${lang}/jugadores/${jugador.id}`}
                className="block hover:opacity-80 transition-opacity"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={fotoJugador}
                  alt={nombreJugador}
                  className="w-32 h-32 rounded-xl object-cover border-4 border-yellow-500/50 shadow-2xl"
                />
              </Link>
            ) : (
              <Link
                href={jugador.slug ? `/${lang}/jugadores/${jugador.slug}` : `/${lang}/jugadores/${jugador.id}`}
                className="block hover:opacity-80 transition-opacity"
              >
                <div className="w-32 h-32 rounded-xl bg-[var(--color-navy)] border-4 border-yellow-500/50 shadow-2xl flex items-center justify-center">
                  <span className="text-3xl font-bold text-white/60">
                    {nombreJugador.charAt(0).toUpperCase()}
                  </span>
                </div>
              </Link>
            )}
          </div>

          {/* Información del MVP */}
          <div className="flex-1 text-center md:text-left">
            <Link
              href={jugador.slug ? `/${lang}/jugadores/${jugador.slug}` : `/${lang}/jugadores/${jugador.id}`}
              className="block hover:opacity-80 transition-opacity"
            >
              <h4 className="text-3xl font-bold text-[var(--color-text)] mb-3">
                {nombreJugador}
              </h4>
            </Link>

          {/* Puntos destacados */}
          <div className="flex items-center justify-center md:justify-start gap-4 mb-4">
            <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border border-yellow-500/30 rounded-lg px-4 py-2">
              <div className="text-xs text-yellow-300/80 uppercase tracking-wide mb-1">
                {labels.puntos || "Puntos"}
              </div>
              <div className="text-2xl font-bold text-yellow-400">
                {mvp.puntos.toFixed(1)}
              </div>
            </div>

            {mvp.goles > 0 && (
              <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 rounded-lg px-4 py-2">
                <div className="text-xs text-green-300/80 uppercase tracking-wide mb-1">
                  {labels.goles || "Goles"}
                </div>
                <div className="text-2xl font-bold text-green-400">
                  {mvp.goles}
                </div>
              </div>
            )}
          </div>

            {/* Estadísticas adicionales */}
            <div className="flex flex-wrap gap-3 justify-center md:justify-start mt-4">
              {mvp.equipo_ganador && (
                <span className="px-3 py-1.5 rounded-full text-xs font-semibold bg-green-500/20 text-green-300 border border-green-500/30">
                  {labels.equipo_ganador || "Equipo ganador"}
                </span>
              )}
              {mvp.mvp_evento && (
                <span className="px-3 py-1.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {labels.mvp_evento || "Evento MVP"}
                </span>
              )}
              {mvp.tarjetas_amarillas > 0 && (
                <span className="px-3 py-1.5 rounded-full text-xs font-semibold bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
                  {mvp.tarjetas_amarillas} {labels.tarjetas_amarillas || "amarillas"}
                </span>
              )}
              {mvp.tarjetas_rojas > 0 && (
                <span className="px-3 py-1.5 rounded-full text-xs font-semibold bg-red-500/20 text-red-300 border border-red-500/30">
                  {mvp.tarjetas_rojas} {labels.tarjetas_rojas || "rojas"}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

