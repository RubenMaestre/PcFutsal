// /frontend/components/GoalkeeperOfMatchday.tsx
"use client";

import React from "react";
import Link from "next/link";
import { usePorteroJornada } from "../hooks/usePorteroJornada";

type Props = {
  grupoId: number | null;
  jornada: number | null;
  dict: any;
  lang?: string;
};

export default function GoalkeeperOfMatchday({
  grupoId,
  jornada,
  dict,
  lang = "es",
}: Props) {
  const { data, porteroTop, loading, error } = usePorteroJornada(
    grupoId,
    jornada
  );

  const labels = dict?.home_matchday_gk_labels || {};
  const GK = dict?.goalkeeper_matchday || {};

  if (!grupoId) {
    return (
      <div className="text-xs text-white/60">
        {labels.hint_select_group || GK.hint_select_group || "Selecciona un grupo para ver al portero."}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-xs text-white/60">
        {labels.loading || GK.loading || "Cargando portero de la jornada..."}
      </div>
    );
  }

  if (error) {
    return <div className="text-xs text-red-500">{error}</div>;
  }

  if (!porteroTop) {
    return (
      <div className="text-xs text-white/60">
        {labels.no_data || GK.no_data || "No hay porteros valorados en esta jornada."}
      </div>
    );
  }

  const jornadaNum =
    jornada != null ? jornada : data?.jornada != null ? data.jornada : null;

  return (
    <div className="flex items-center gap-3 bg-[#121212] rounded-xl px-3 py-2 shadow-sm">
      {/* Foto */}
      <div className="relative w-14 h-14 rounded-full overflow-hidden bg-black/20 border border-[#d4af37]/50">
        {porteroTop.foto ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={porteroTop.foto}
            alt={porteroTop.nombre}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[0.6rem] text-white text-center px-1">
            {porteroTop.nombre}
          </div>
        )}
      </div>

      {/* Centro */}
      <div className="flex-1 min-w-0">
        <p className="text-[0.7rem] uppercase text-[#B3B3B3] tracking-wide">
          {labels.title || GK.title || "Portero de la jornada"}
          {jornadaNum ? ` · J${jornadaNum}` : null}
        </p>
        <Link
          href={`/${lang}/jugadores/${(porteroTop as any).slug || porteroTop.jugador_id}`}
          className="block hover:text-brand-accent transition-colors"
        >
          <p className="text-sm text-white font-semibold truncate">
            {porteroTop.nombre}
          </p>
        </Link>
        <Link
          href={(porteroTop as any).club_slug ? `/${lang}/clubes/${(porteroTop as any).club_slug}` : `/${lang}/clubes/${porteroTop.club_id}`}
          className="text-[0.65rem] text-[#B3B3B3] truncate hover:text-brand-accent transition-colors"
        >
          {porteroTop.club_nombre || "—"}
        </Link>
      </div>

      {/* Escudo */}
      <div className="w-10 h-10 flex items-center justify-center">
        {porteroTop.club_escudo ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={porteroTop.club_escudo}
            alt={porteroTop.club_nombre}
            className="max-w-full max-h-full object-contain"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div className="w-9 h-9 rounded-full bg-black/30 border border-white/10 flex items-center justify-center text-[0.6rem] text-white">
            GK
          </div>
        )}
      </div>

      {/* Puntos */}
      <div className="flex flex-col items-end">
        <span className="text-white text-lg font-bold leading-none">
          {porteroTop.puntos}
        </span>
        <span className="text-[0.6rem] text-[#B3B3B3] uppercase">
          {labels.points_label || GK.points_label || "pts"}
        </span>
      </div>
    </div>
  );
}
