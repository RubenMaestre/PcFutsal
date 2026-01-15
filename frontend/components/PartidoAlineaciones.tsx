// /components/PartidoAlineaciones.tsx
"use client";

import React from "react";
import Link from "next/link";

type JugadorAlineacion = {
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
};

type PartidoAlineacionesProps = {
  alineaciones: {
    local: {
      club_id: number;
      titulares: JugadorAlineacion[];
      suplentes: JugadorAlineacion[];
      staff: Array<{
        nombre: string;
        rol: string;
        staff_id: number | null;
      }>;
    };
    visitante: {
      club_id: number;
      titulares: JugadorAlineacion[];
      suplentes: JugadorAlineacion[];
      staff: Array<{
        nombre: string;
        rol: string;
        staff_id: number | null;
      }>;
    };
  };
  puntosJugadores: Record<number, number>;
  dict: any;
  lang: string;
};

// Renderiza un jugador individual en la alineación.
// Muestra foto (o inicial si no hay foto), dorsal, etiquetas (Pt, C, etc.),
// nombre con enlace al perfil, estadísticas del partido y puntos MVP.
function renderJugador(
  jugador: JugadorAlineacion,
  puntos: number | null,
  dict: any,
  lang: string
) {
  return (
    <div
      key={jugador.jugador_id || jugador.nombre}
      className="flex items-center gap-3 p-3 bg-[var(--color-navy)] rounded-lg border border-[var(--color-navy)]/50 hover:border-[var(--color-accent)]/50 transition-all group"
    >
      {/* Foto del jugador. Si no hay foto, muestra la inicial del nombre como fallback. */}
      <div className="w-12 h-12 bg-brand-card border-2 border-[var(--color-accent)] rounded-full flex items-center justify-center overflow-hidden flex-shrink-0">
        {jugador.foto ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={jugador.foto}
            alt={jugador.nombre}
            className="w-full h-full object-cover"
          />
        ) : (
          // Fallback: mostrar inicial del nombre si no hay foto
          <span className="text-sm text-white/60 font-bold">
            {jugador.nombre.charAt(0).toUpperCase()}
          </span>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          {jugador.dorsal && (
            <span className="text-xs font-bold text-brand-accent bg-brand-card px-2 py-0.5 rounded">
              {jugador.dorsal}
            </span>
          )}
          {jugador.etiqueta && (
            <span className="text-xs bg-[var(--color-accent)] text-white px-2 py-0.5 rounded font-semibold">
              {jugador.etiqueta}
            </span>
          )}
          {jugador.jugador_id ? (
            <Link
              href={
                jugador.slug
                  ? `/${lang}/jugadores/${jugador.slug}`
                  : `/${lang}/jugadores/${jugador.jugador_id}`
              }
              className="text-sm font-bold text-[var(--color-text)] hover:text-brand-accent transition-colors truncate"
            >
              {jugador.nombre}
            </Link>
          ) : (
            <span className="text-sm font-bold text-[var(--color-text)] truncate">
              {jugador.nombre}
            </span>
          )}
        </div>

        {/* Estadísticas */}
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          {puntos !== null && (
            <span className="text-xs font-bold text-brand-accent bg-brand-card px-2 py-0.5 rounded">
              {puntos.toFixed(1)} pts
            </span>
          )}
          {jugador.goles > 0 && (
            <span className="text-xs font-bold text-brand-success bg-brand-card px-2 py-0.5 rounded">
              ⚽ {jugador.goles}
            </span>
          )}
          {jugador.tarjetas_amarillas > 0 && (
            <span className="text-xs font-bold text-brand-warning bg-brand-card px-2 py-0.5 rounded">
              🟨 {jugador.tarjetas_amarillas}
            </span>
          )}
          {jugador.tarjetas_rojas > 0 && (
            <span className="text-xs font-bold text-brand-error bg-brand-card px-2 py-0.5 rounded">
              🟥 {jugador.tarjetas_rojas}
            </span>
          )}
          {jugador.mvp && (
            <span className="text-xs font-bold text-[#D4AF37] bg-brand-card px-2 py-0.5 rounded">
              ⭐ MVP
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PartidoAlineaciones({
  alineaciones,
  puntosJugadores,
  dict,
  lang,
}: PartidoAlineacionesProps) {
  return (
    <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
      <h2 className="text-2xl font-bold text-[var(--color-text)] mb-6 font-[var(--font-title)]">
        {dict?.partidos?.alineaciones_title || "Alineaciones"}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Equipo Local */}
        <div>
          <div className="bg-[var(--color-navy)] rounded-lg p-4 mb-4 border border-[var(--color-accent)]/30">
            <h3 className="text-lg font-bold text-[var(--color-text)]">
              {dict?.partidos?.local || "Local"}
            </h3>
          </div>

          {/* Titulares */}
          {alineaciones.local.titulares.length > 0 && (
            <div className="mb-6">
              <div className="text-sm font-bold text-white/60 mb-3 uppercase tracking-wide">
                {dict?.partidos?.titulares || "Titulares"}
              </div>
              <div className="space-y-2">
                {alineaciones.local.titulares.map((jugador) =>
                  renderJugador(
                    jugador,
                    jugador.jugador_id
                      ? puntosJugadores[jugador.jugador_id] || null
                      : null,
                    dict,
                    lang
                  )
                )}
              </div>
            </div>
          )}

          {/* Suplentes */}
          {alineaciones.local.suplentes.length > 0 && (
            <div>
              <div className="text-sm font-bold text-white/60 mb-3 uppercase tracking-wide">
                {dict?.partidos?.suplentes || "Suplentes"}
              </div>
              <div className="space-y-2">
                {alineaciones.local.suplentes.map((jugador) =>
                  renderJugador(
                    jugador,
                    jugador.jugador_id
                      ? puntosJugadores[jugador.jugador_id] || null
                      : null,
                    dict,
                    lang
                  )
                )}
              </div>
            </div>
          )}
        </div>

        {/* Equipo Visitante */}
        <div>
          <div className="bg-[var(--color-navy)] rounded-lg p-4 mb-4 border border-[var(--color-accent)]/30">
            <h3 className="text-lg font-bold text-[var(--color-text)]">
              {dict?.partidos?.visitante || "Visitante"}
            </h3>
          </div>

          {/* Titulares */}
          {alineaciones.visitante.titulares.length > 0 && (
            <div className="mb-6">
              <div className="text-sm font-bold text-white/60 mb-3 uppercase tracking-wide">
                {dict?.partidos?.titulares || "Titulares"}
              </div>
              <div className="space-y-2">
                {alineaciones.visitante.titulares.map((jugador) =>
                  renderJugador(
                    jugador,
                    jugador.jugador_id
                      ? puntosJugadores[jugador.jugador_id] || null
                      : null,
                    dict,
                    lang
                  )
                )}
              </div>
            </div>
          )}

          {/* Suplentes */}
          {alineaciones.visitante.suplentes.length > 0 && (
            <div>
              <div className="text-sm font-bold text-white/60 mb-3 uppercase tracking-wide">
                {dict?.partidos?.suplentes || "Suplentes"}
              </div>
              <div className="space-y-2">
                {alineaciones.visitante.suplentes.map((jugador) =>
                  renderJugador(
                    jugador,
                    jugador.jugador_id
                      ? puntosJugadores[jugador.jugador_id] || null
                      : null,
                    dict,
                    lang
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
