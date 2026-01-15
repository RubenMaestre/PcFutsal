// /frontend/home_components/GlobalGoalkeepersList.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useGlobalJugadoresJornada } from "../hooks/useGlobalValoraciones";

type Props = {
  temporadaId: number | null;
  dict: any;
  jornada?: number | null;
  weekend?: string | null; // ← NUEVO
  top?: number; // por defecto 5
  lang?: string;
};

export default function GlobalGoalkeepersList({
  temporadaId,
  dict,
  jornada = null,
  weekend = null, // ← NUEVO
  top = 5,
  lang = "es",
}: Props) {
  const labels = dict?.home_matchday_gk_labels || {};
  const GK = dict?.goalkeeper_matchday || {};

  const { ranking, loading, error } = useGlobalJugadoresJornada(
    temporadaId,
    { jornada, weekend, top: Math.max(20, top), onlyPorteros: true, strict: !!weekend }
  );

  if (!temporadaId) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.hint_select_group || GK.hint_select_context || "Selecciona contexto para ver porteros."}
      </div>
    );
  }
  if (loading) return <div className="text-xs text-[var(--color-text-secondary)]">{labels.loading || GK.loading_global || "Cargando porteros de la jornada..."}</div>;
  if (error)   return <div className="text-xs text-[var(--color-error)]">{labels.error || GK.error || "Error al cargar."}</div>;

  const rows = (ranking || []).slice(0, top);
  if (!rows.length) {
    return <div className="text-xs text-[var(--color-text-secondary)]">{labels.no_data || GK.no_data_global || "No hay porteros valorados en esta jornada."}</div>;
  }

  return (
    <div className="flex flex-col gap-2 max-w-full overflow-hidden">
      <ul className="divide-y divide-white/10 rounded-md overflow-hidden bg-black/10 max-w-full">
        {rows.map((p, idx) => (
          <li key={p.jugador_id} className="px-1.5 sm:px-3 py-1.5 sm:py-2 flex items-center gap-2 sm:gap-3 max-w-full overflow-hidden">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full overflow-hidden bg-black/20 border border-white/10 shrink-0">
              {p.foto ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={p.foto} alt={p.nombre} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-[0.5rem] sm:text-[0.6rem] text-white text-center px-0.5 sm:px-1">
                  {p.nombre}
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0 overflow-hidden pr-1.5 sm:pr-2">
              <Link
                href={`/${lang}/jugadores/${p.slug || p.jugador_id}`}
                className="text-xs sm:text-sm text-white font-semibold truncate hover:text-brand-accent transition-colors block"
              >
                {idx + 1}. {p.nombre}
              </Link>
              <Link
                href={p.club_slug ? `/${lang}/clubes/${p.club_slug}` : `/${lang}/clubes/${p.club_id}`}
                className="text-[0.6rem] sm:text-[0.7rem] text-white/70 truncate hover:text-brand-accent transition-colors"
              >
                {p.club_nombre}
              </Link>
              <p className="text-[0.55rem] sm:text-[0.65rem] text-white/60 truncate">{p.competicion_nombre} · {p.grupo_nombre}</p>
            </div>

            <div className="flex flex-col items-end shrink-0">
              <span className="text-white text-sm sm:text-lg font-bold leading-none">{p.puntos_global}</span>
              <span className="text-[0.5rem] sm:text-[0.6rem] text-white/70 uppercase">{labels.points_label || GK.points_label || "pts"}</span>
            </div>
          </li>
        ))}
      </ul>
      <p className="text-[0.6rem] sm:text-[0.7rem] text-white/60">
        {labels.list_desc || GK.list_desc || "Top porteros ponderados por división en la jornada."}
      </p>
    </div>
  );
}
