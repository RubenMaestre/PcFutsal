// /frontend/components/SeasonTopScorersImpact.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useSeasonTopScorers } from "../hooks/useSeasonTopScorers";

export default function SeasonTopScorersImpact({
  grupoId,
  dict,
  lang = "es",
}: {
  grupoId: number | null;
  dict: any;
  lang?: string;
}) {
  const { loading, error, top10 } = useSeasonTopScorers(grupoId);
  const labels = dict?.home_season_scorers_labels || {};

  if (!grupoId)
    return (
      <p className="text-xs text-[var(--color-text-secondary)]">
        {labels.hint_select_group}
      </p>
    );
  if (loading)
    return (
      <p className="text-xs text-[var(--color-text-secondary)]">
        {labels.loading}
      </p>
    );
  if (error)
    return (
      <p className="text-xs text-[var(--color-error)]">
        {labels.error}
      </p>
    );
  if (!top10.length)
    return (
      <p className="text-xs text-[var(--color-text-secondary)]">
        {labels.no_data}
      </p>
    );

  return (
    <div className="w-full text-[13px] leading-tight">
      {/* CABECERA DESKTOP */}
      <div className="hidden md:grid grid-cols-[28px_minmax(0,1fr)_minmax(0,1fr)_50px] items-center text-[11px] font-semibold uppercase tracking-wide bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg px-3 py-2 text-[var(--color-text-secondary)]">
        <div>{labels.col_rank || "R"}</div>
        <div>
          {labels.col_player || "Jugador"} / {labels.col_team || "Equipo"}
        </div>
        <div>{labels.col_goals_block || "Goles jugador / Total del equipo"}</div>
        <div className="text-right">
          {labels.col_contrib || "Impacto"}
        </div>
      </div>

      {/* CABECERA MOBILE */}
      <div className="md:hidden flex flex-col text-[10px] uppercase tracking-wide text-[var(--color-text-secondary)] mt-2 mb-1 px-1">
        <div className="flex w-full items-end">
          {/* Izquierda: Jugador */}
          <div className="flex-1">
            <div className="font-semibold">
              {labels.col_player_short || "JUG."}
            </div>
          </div>

          {/* Centro: Goles jugador / total equipo */}
          <div className="flex flex-col items-end text-right ml-2">
            <div className="font-semibold whitespace-nowrap">
              {labels.col_goals_block_short || "GOLES / T. EQUIPO"}
            </div>
          </div>

          {/* Derecha: Impacto */}
          <div className="flex flex-col items-end text-right ml-4 min-w-[42px]">
            <div className="font-semibold">
              {labels.col_contrib_short || "IMPACTO"}
            </div>
          </div>
        </div>
      </div>

      {/* LISTA */}
      <ul className="mt-2 flex flex-col gap-2">
        {top10.map((row, idx) => {
          // Prioridad: apodo (más personal) > nombre (más formal)
          const name = row.apodo || row.nombre;
          const golesJugador = row.goles_total ?? 0;
          const golesEquipo = row.goles_equipo_total ?? 0;
          const pct = row.contribucion_pct ?? 0;
          // Calcular ratio de contribución: qué porcentaje de los goles del equipo
          // ha marcado este jugador. Se limita a 100% para evitar valores absurdos.
          const ratio =
            golesEquipo > 0
              ? Math.min(100, (golesJugador / golesEquipo) * 100)
              : 0;

          return (
            <React.Fragment
              key={row.jugador_id + "-" + row.club_id}
            >
              {/* DESKTOP ROW */}
              <li className="hidden md:grid grid-cols-[28px_minmax(0,1fr)_minmax(0,1fr)_50px] items-center gap-3 bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg px-3 py-2">
                <div className="text-[12px] text-[var(--color-text-secondary)]">
                  {idx + 1}
                </div>

                <Link
                  href={`/${lang}/jugadores/${row.slug || row.jugador_id}`}
                  className="flex items-center gap-3 min-w-0 hover:text-brand-accent transition-colors"
                >
                  <div className="w-10 h-10 rounded-lg overflow-hidden bg-[#1c1c1c] border border-[var(--color-card)] flex items-center justify-center">
                    {row.foto ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={row.foto}
                        alt={name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="text-[10px] text-[var(--color-text-secondary)]">
                        -
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col min-w-0">
                    <span className="font-semibold truncate text-[var(--color-text)]">
                      {name}
                    </span>
                    <Link
                      href={row.club_slug ? `/${lang}/clubes/${row.club_slug}` : `/${lang}/clubes/${row.club_id}`}
                      className="text-[11px] truncate text-[var(--color-text-secondary)] hover:text-brand-accent transition-colors"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {row.club_nombre}
                    </Link>
                  </div>
                </Link>

                <div className="flex flex-col min-w-0">
                  <div className="text-[12px] font-semibold mb-1">
                    {golesJugador}
                    <span className="text-[11px] text-[var(--color-text-secondary)]">
                      {" "}
                      / {golesEquipo}
                    </span>
                  </div>

                  <div className="h-3 rounded-md bg-[rgba(0,196,106,0.15)] overflow-hidden">
                    <div
                      className="h-full bg-[var(--color-success)]"
                      style={{ width: `${ratio}%` }}
                    />
                  </div>
                </div>

                <div className="text-right text-[12px] font-semibold">
                  {pct}%
                </div>
              </li>

              {/* MOBILE ROW */}
              <li className="md:hidden bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg px-3 py-3 flex flex-col gap-2">
                {/* top block */}
                <div className="flex items-start w-full gap-3">
                  {/* Ranking + foto */}
                  <div className="flex flex-col items-center flex-shrink-0">
                    <div className="text-[12px] text-[var(--color-text-secondary)]">
                      {idx + 1}
                    </div>

                    <div className="mt-2 w-10 h-10 rounded-lg overflow-hidden bg-[#1c1c1c] border border-[var(--color-card)] flex items-center justify-center">
                      {row.foto ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={row.foto}
                          alt={name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="text-[10px] text-[var(--color-text-secondary)]">
                          -
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Datos jugador */}
                  <div className="flex-1 min-w-0 flex flex-col">
                    <div className="flex flex-row flex-wrap items-baseline gap-x-2 w-full">
                      {/* nombre */}
                      <Link
                        href={`/${lang}/jugadores/${row.slug || row.jugador_id}`}
                        className="font-semibold text-[13px] truncate max-w-[60%] text-[var(--color-text)] hover:text-brand-accent transition-colors"
                      >
                        {name}
                      </Link>

                      {/* goles jugador/equipo */}
                      <div className="text-[12px] font-semibold text-[var(--color-text)] whitespace-nowrap">
                        {golesJugador}
                        <span className="text-[11px] text-[var(--color-text-secondary)]">
                          {" "}
                          / {golesEquipo}
                        </span>
                      </div>

                      {/* impacto % */}
                      <div className="ml-auto text-[12px] font-semibold text-[var(--color-text)] whitespace-nowrap">
                        {pct}%
                      </div>
                    </div>

                    <Link
                      href={row.club_slug ? `/${lang}/clubes/${row.club_slug}` : `/${lang}/clubes/${row.club_id}`}
                      className="text-[11px] text-[var(--color-text-secondary)] truncate hover:text-brand-accent transition-colors"
                    >
                      {row.club_nombre}
                    </Link>
                  </div>
                </div>

                {/* barra contribución */}
                <div className="h-3 rounded-md bg-[rgba(0,196,106,0.15)] overflow-hidden">
                  <div
                    className="h-full bg-[var(--color-success)]"
                    style={{ width: `${ratio}%` }}
                  />
                </div>
              </li>
            </React.Fragment>
          );
        })}
      </ul>
    </div>
  );
}
