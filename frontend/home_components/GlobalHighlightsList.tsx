// /frontend/home_components/GlobalHighlightsList.tsx
"use client";

import React from "react";
import { useGlobalJugadoresJornada } from "../hooks/useGlobalValoraciones";

type Props = {
  temporadaId: number | null;
  dict: any;
  jornada?: number | null;
};

export default function GlobalHighlightsList({ temporadaId, dict, jornada = null }: Props) {
  const G = dict?.global || {};
  const labels = dict?.home?.highlights_players_title
    ? { title: dict.home.highlights_players_title, desc: dict.home.highlights_players_desc }
    : { title: G.highlights_title || "Destacados", desc: G.highlights_desc || "Top jugadores ponderados por división" };

  const { ranking, loading, error } = useGlobalJugadoresJornada(
    temporadaId,
    { jornada, top: 12 }
  );

  if (!temporadaId) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {dict?.global?.select_context || "Selecciona contexto para ver destacados."}
      </div>
    );
  }
  const T = dict?.tables || {};
  if (loading) return <div className="text-xs text-[var(--color-text-secondary)]">{T.loading || "Cargando…"}</div>;
  if (error)   return <div className="text-xs text-[var(--color-error)]">{error}</div>;
  if (!ranking.length) {
    return <div className="text-xs text-[var(--color-text-secondary)]">{dict?.global?.no_data_jornada || "Sin datos para esta jornada."}</div>;
  }

  return (
    <div className="flex flex-col gap-2">
      <ul className="divide-y divide-white/10 rounded-md overflow-hidden bg-black/10">
        {ranking.map((j, idx) => (
          <li key={j.jugador_id} className="px-3 py-2 flex items-center gap-3">
            {/* Foto */}
            <div className="w-10 h-10 rounded-full overflow-hidden bg-black/20 border border-white/10 shrink-0">
              {j.foto ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={j.foto} alt={j.nombre} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-[0.6rem] text-white text-center px-1">
                  {j.nombre}
                </div>
              )}
            </div>

            {/* Centro */}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-semibold truncate">{idx + 1}. {j.nombre}</p>
              <p className="text-[0.7rem] text-white/70 truncate">{j.club_nombre}</p>
              <p className="text-[0.65rem] text-white/60 truncate">{j.competicion_nombre} · {j.grupo_nombre}</p>
            </div>

            {/* Puntos */}
            <div className="flex flex-col items-end">
              <span className="text-white text-lg font-bold leading-none">{j.puntos_global}</span>
              <span className="text-[0.6rem] text-white/70 uppercase">pts</span>
            </div>
          </li>
        ))}
      </ul>
      <p className="text-[0.7rem] text-white/60">{labels.desc || ""}</p>
    </div>
  );
}
