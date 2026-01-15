// /components/PartidoEstadisticas.tsx
"use client";

import React from "react";

type PartidoEstadisticasProps = {
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
  dict: any;
  lang: string;
};

export default function PartidoEstadisticas({
  estadisticas,
  dict,
  lang,
}: PartidoEstadisticasProps) {
  return (
    <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
      <h2 className="text-2xl font-bold text-[var(--color-text)] mb-6 font-[var(--font-title)]">
        {dict?.partidos?.estadisticas_title || "Estadísticas del Partido"}
      </h2>

      {/* Grid responsive: 2 columnas en móvil, 4 en desktop.
          Muestra estadísticas clave del partido de forma visual y compacta. */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Goles totales del partido con desglose local/visitante */}
        <div className="bg-[var(--color-navy)] rounded-lg p-5 border border-[var(--color-accent)]/30 hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-bold text-white/60 mb-2 uppercase tracking-wide">
            {dict?.partidos?.goles_total || "Goles totales"}
          </div>
          <div className="text-4xl font-extrabold text-[var(--color-text)] mb-2 font-[var(--font-title)]">
            {estadisticas.goles_total}
          </div>
          <div className="text-xs text-white/60 font-semibold">
            {estadisticas.goles_local} - {estadisticas.goles_visitante}
          </div>
        </div>

        {/* Goles desglosados por parte del partido (primera y segunda parte) */}
        <div className="bg-[var(--color-navy)] rounded-lg p-5 border border-[var(--color-accent)]/30 hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-bold text-white/60 mb-2 uppercase tracking-wide">
            {dict?.partidos?.goles_por_parte || "Goles por parte"}
          </div>
          <div className="text-4xl font-extrabold text-[var(--color-text)] mb-2 font-[var(--font-title)]">
            {estadisticas.goles_primera_parte + estadisticas.goles_segunda_parte}
          </div>
          <div className="text-xs text-white/60 font-semibold">
            {estadisticas.goles_primera_parte} / {estadisticas.goles_segunda_parte}
          </div>
        </div>

        {/* Tarjetas */}
        <div className="bg-[var(--color-navy)] rounded-lg p-5 border border-[var(--color-accent)]/30 hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-bold text-white/60 mb-2 uppercase tracking-wide">
            {dict?.partidos?.tarjetas || "Tarjetas"}
          </div>
          <div className="text-4xl font-extrabold text-[var(--color-text)] mb-2 font-[var(--font-title)]">
            {estadisticas.amarillas_total + estadisticas.dobles_amarillas_total + estadisticas.rojas_total}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-[var(--color-warning)] font-bold">🟨 {estadisticas.amarillas_total}</span>
            <span className="text-[var(--color-error)] font-bold">🟥 {estadisticas.rojas_total}</span>
          </div>
        </div>

        {/* MVPs */}
        <div className="bg-[var(--color-navy)] rounded-lg p-5 border border-[var(--color-accent)]/30 hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-bold text-white/60 mb-2 uppercase tracking-wide">
            {dict?.partidos?.mvps || "MVPs"}
          </div>
          <div className="text-4xl font-extrabold text-[var(--color-gold)] mb-2 font-[var(--font-title)]">
            {estadisticas.mvps}
          </div>
          <div className="text-xs text-white/60 font-semibold">
            ⭐ Estrella{estadisticas.mvps !== 1 ? "s" : ""}
          </div>
        </div>
      </div>
    </div>
  );
}
