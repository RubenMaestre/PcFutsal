// /frontend/home_components/GlobalTeamCard.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useGlobalEquipoJornada } from "../hooks/useGlobalValoraciones";

type Props = {
  temporadaId: number | null;
  dict: any;
  lang?: string;
  jornada?: number | null;
  weekend?: string | null; // ← NUEVO
};

function normalizeShieldUrl(raw?: string | null) {
  if (!raw) return "";
  let url = raw.trim();
  if (url.startsWith("http://")) url = "https://" + url.slice(7);
  return url;
}

export default function GlobalTeamCard({
  temporadaId,
  dict,
  lang = "es",
  jornada = null,
  weekend = null, // ← NUEVO
}: Props) {
  const labels = dict?.home_matchday_team_labels || {};
  const { equipoTop, ranking, loading, error } = useGlobalEquipoJornada(
    temporadaId,
    { jornada, weekend, top: 10, strict: !!weekend }
  );

  if (!temporadaId) {
    return (
      <div className="text-xs text-white/60">
        {labels.hint_select_group ||
          "Selecciona contexto para ver el equipo de la jornada."}
      </div>
    );
  }
  if (loading)
    return (
      <div className="text-xs text-white/60">
        {labels.loading || "Cargando…"}{" "}
      </div>
    );
  if (error)
    return (
      <div className="text-xs text-brand-error">
        {labels.error || "Error al cargar."}
      </div>
    );
  if (!equipoTop) {
    return (
      <div className="text-xs text-white/60">
        {labels.no_data || "Sin datos para esta jornada."}
      </div>
    );
  }

  const escudoUrl = normalizeShieldUrl(equipoTop.escudo);
  const extra = ranking.slice(1, 10);

  const divisionLabelTop = [
    equipoTop.competicion_nombre,
    equipoTop.grupo_nombre,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="flex flex-col gap-3 max-w-full overflow-hidden">
      <div className="flex items-center gap-2 sm:gap-5 max-w-full overflow-hidden">
        <div className="w-14 h-14 sm:w-20 sm:h-20 rounded-full bg-[#121212] flex items-center justify-center overflow-hidden border-2 border-brand-card shrink-0 shadow-md">
          {escudoUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={escudoUrl}
              alt={equipoTop.nombre}
              className="w-full h-full object-contain p-1"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          ) : (
            <span className="text-xs sm:text-base text-brand-textSecondary font-semibold">
              {equipoTop.nombre.slice(0, 3).toUpperCase()}
            </span>
          )}
        </div>

        <div className="flex flex-col gap-1 min-w-0 flex-1 overflow-hidden">
          <Link
            href={equipoTop.slug ? `/${lang}/clubes/${equipoTop.slug}` : `/${lang}/clubes/${equipoTop.club_id}`}
            className="text-sm sm:text-lg font-bold leading-tight truncate text-white hover:text-brand-accent transition-colors"
          >
            {equipoTop.nombre}
          </Link>

          {divisionLabelTop ? (
            <div className="text-[0.6rem] sm:text-[0.7rem] text-white/60 uppercase tracking-wide truncate">
              {divisionLabelTop}
            </div>
          ) : null}

          <div className="text-xs sm:text-sm text-white/60 leading-snug">
            {labels.default_comment || "Jornada destacada ponderada por división."}
          </div>
          <div className="text-xs sm:text-sm text-brand-accent font-semibold mt-1">
            {(labels.score_label || "score")}: {equipoTop.score_global.toFixed(2)}
          </div>
        </div>
      </div>

      {extra.length > 0 && (
        <div className="flex flex-col gap-1 max-w-full overflow-hidden">
          {extra.map((club, i) => {
            const divisionLabelItem = [
              club.competicion_nombre,
              club.grupo_nombre,
            ]
              .filter(Boolean)
              .join(" · ");

            return (
              <div
                key={club.club_id || i}
                className="flex items-center justify-between bg-black/10 rounded-lg px-1.5 sm:px-2 py-1 max-w-full overflow-hidden"
              >
                <div className="flex items-center gap-1.5 sm:gap-2 min-w-0 flex-1 overflow-hidden pr-1.5 sm:pr-2">
                  <span className="text-[0.6rem] sm:text-xs text-white/60 font-semibold shrink-0">
                    {i + 2}º
                  </span>
                  <div className="flex flex-col min-w-0 overflow-hidden">
                    <Link
                      href={club.slug ? `/${lang}/clubes/${club.slug}` : `/${lang}/clubes/${club.club_id}`}
                      className="text-xs sm:text-sm text-white truncate hover:text-brand-accent transition-colors"
                    >
                      {club.nombre}
                    </Link>
                    {divisionLabelItem ? (
                      <span className="text-[0.55rem] sm:text-[0.65rem] text-white/60 uppercase tracking-wide truncate">
                        {divisionLabelItem}
                      </span>
                    ) : null}
                  </div>
                </div>
                <span className="text-[0.6rem] sm:text-xs text-white/60 shrink-0">
                  {club.score_global.toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
