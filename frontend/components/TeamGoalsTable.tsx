// /frontend/components/TeamGoalsTable.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useTeamGoals } from "../hooks/useTeamGoals";

export default function TeamGoalsTable({
  grupoId,
  jornada,
  dict,
  lang = "es",
}: {
  grupoId: number | null;
  jornada: number | null;
  dict: any;
  lang?: string;
}) {
  const { loading, error, equipos } = useTeamGoals(grupoId, jornada);

  const labels = dict?.home_team_goals_labels || {};

  // ESTADOS
  if (!grupoId) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.hint_select_group ||
          "Selecciona un grupo para ver los goles por equipo."}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.loading || "Cargando datos ofensivos..."}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-xs text-[var(--color-error,#7A0F2A)]">
        {labels.error || "Error al cargar los datos ofensivos."}
      </div>
    );
  }

  if (!equipos.length) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.no_data || "Sin goles registrados todavía."}
      </div>
    );
  }

  return (
    <div className="w-full text-[13px] leading-tight">
      {/* CABECERA DESKTOP */}
      <div className="hidden md:grid grid-cols-[28px_minmax(0,1fr)_90px_130px_130px] items-center text-[11px] font-semibold uppercase tracking-wide bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg px-3 py-2 text-[var(--color-text-secondary)]">
        <div>{labels.col_rank || "R"}</div>
        <div>{labels.col_team || "Equipo"}</div>
        <div className="text-right">
          {labels.col_goals_avg || "Goles (media)"}
        </div>
        <div className="text-right">
          {labels.col_home_away || "Local / Visitante"}
        </div>
        <div className="text-right">
          {labels.col_halves || "1ª / 2ª parte"}
        </div>
      </div>

      {/* CABECERA MOBILE */}
      <div className="md:hidden flex flex-col text-[10px] uppercase tracking-wide text-[var(--color-text-secondary)] mt-2 mb-1 px-1">
        <div className="flex w-full items-end">
          {/* Equipo */}
          <div className="flex-1">
            <div className="font-semibold">
              {labels.col_team_short || "EQ."}
            </div>
          </div>

          {/* GF + media */}
          <div className="flex flex-col items-end text-right ml-2 min-w-[70px]">
            <div className="font-semibold whitespace-nowrap">
              {labels.col_goals_avg_short || "GF (med.)"}
            </div>
          </div>

          {/* 1ª/2ª parte */}
          <div className="flex flex-col items-end text-right ml-4 min-w-[70px]">
            <div className="font-semibold whitespace-nowrap">
              {labels.col_halves_short || "1P / 2P"}
            </div>
          </div>
        </div>
      </div>

      {/* LISTA */}
      <ul className="mt-2 flex flex-col gap-2">
        {equipos.map((row, idx) => {
          const rank = idx + 1;

          return (
            <React.Fragment key={row.club_id}>
              {/* DESKTOP ROW (compactada) */}
              <li
                className="
                  hidden md:grid
                  grid-cols-[28px_minmax(0,1fr)_90px_130px_130px]
                  items-center gap-3
                  bg-[var(--color-card)]
                  border border-[var(--color-card)]
                  rounded-lg
                  px-3 py-0.5
                "
              >
                {/* Rank */}
                <div className="text-[11px] text-[var(--color-text-secondary)] leading-none">
                  {rank}
                </div>

                {/* Equipo (escudo + nombre + PJ) */}
                <Link
                  href={row.club_slug ? `/clubes/${row.club_slug}` : `/clubes/${row.club_id}`}
                  className="flex items-center gap-3 min-w-0 hover:text-brand-accent transition-colors"
                >
                  <div className="w-9 h-9 rounded-lg overflow-hidden bg-[#1c1c1c] border border-[var(--color-card)] flex items-center justify-center flex-shrink-0">
                    {row.club_escudo ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={row.club_escudo}
                        alt={row.club_nombre}
                        className="w-full h-full object-contain p-1"
                      />
                    ) : (
                      <div className="text-[10px] text-[var(--color-text-secondary)] leading-none">
                        -
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col min-w-0 leading-tight">
                    <span className="font-semibold truncate text-[var(--color-text)] text-[12px] leading-tight">
                      {row.club_nombre}
                    </span>
                    <span className="text-[10px] text-[var(--color-text-secondary)] leading-tight">
                      {(labels.matches_played_short || "PJ") +
                        " " +
                        row.partidos_jugados}
                    </span>
                  </div>
                </Link>

                {/* Goles totales + media (una sola columna, dos líneas pero muy pegadas) */}
                <div className="flex flex-col items-end text-right leading-tight">
                  <div className="text-[12px] font-semibold text-[var(--color-text)] leading-tight">
                    {row.goles_total}
                  </div>
                  <div className="text-[10px] text-[var(--color-text-secondary)] leading-tight">
                    {row.goles_por_partido}{" "}
                    {labels.per_match_suffix || "g/p"}
                  </div>
                </div>

                {/* Local / Visitante -> 1 sola línea compacta */}
                <div className="flex flex-col items-end text-right leading-tight">
                  <div className="text-[12px] font-semibold text-[var(--color-text)] leading-tight whitespace-nowrap">
                    {row.goles_local}
                    <span className="text-[10px] text-[var(--color-text-secondary)] ml-1">
                      {labels.home_short || "LOC"}
                    </span>
                    {" · "}
                    {row.goles_visitante}
                    <span className="text-[10px] text-[var(--color-text-secondary)] ml-1">
                      {labels.away_short || "VIS"}
                    </span>
                  </div>
                </div>

                {/* 1ª / 2ª parte -> 1 sola línea compacta */}
                <div className="flex flex-col items-end text-right leading-tight">
                  <div className="text-[12px] font-semibold text-[var(--color-text)] leading-tight whitespace-nowrap">
                    {row.goles_1parte}
                    <span className="text-[10px] text-[var(--color-text-secondary)] ml-1">
                      {labels.first_half_short || "1P"}
                    </span>
                    {" · "}
                    {row.goles_2parte}
                    <span className="text-[10px] text-[var(--color-text-secondary)] ml-1">
                      {labels.second_half_short || "2P"}
                    </span>
                  </div>
                </div>
              </li>

              {/* MOBILE ROW (igual que antes, nos gustaba) */}
              <li className="md:hidden bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg px-3 py-3 flex flex-col gap-2">
                <div className="flex items-start w-full gap-3">
                  {/* Rank + escudo */}
                  <div className="flex flex-col items-center flex-shrink-0">
                    <div className="text-[12px] text-[var(--color-text-secondary)]">
                      {rank}
                    </div>

                    <div className="mt-2 w-10 h-10 rounded-lg overflow-hidden bg-[#1c1c1c] border border-[var(--color-card)] flex items-center justify-center">
                      {row.club_escudo ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={row.club_escudo}
                          alt={row.club_nombre}
                          className="w-full h-full object-contain p-1"
                        />
                      ) : (
                        <div className="text-[10px] text-[var(--color-text-secondary)]">
                          -
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Datos equipo */}
                  <div className="flex-1 min-w-0 flex flex-col">
                    {/* línea superior: nombre + GF totales + media */}
                    <div className="flex flex-row flex-wrap items-baseline gap-x-2 w-full">
                      <Link
                        href={row.club_slug ? `/${lang}/clubes/${row.club_slug}` : `/${lang}/clubes/${row.club_id}`}
                        className="font-semibold text-[13px] truncate max-w-[60%] text-[var(--color-text)] hover:text-brand-accent transition-colors"
                      >
                        {row.club_nombre}
                      </Link>

                      <div className="text-[12px] font-semibold text-[var(--color-text)] whitespace-nowrap">
                        {row.goles_total}
                        <span className="text-[11px] text-[var(--color-text-secondary)]">
                          {" "}
                          ({row.goles_por_partido}{" "}
                          {labels.per_match_suffix || "g/p"})
                        </span>
                      </div>
                    </div>

                    {/* PJ */}
                    <div className="text-[11px] text-[var(--color-text-secondary)] leading-tight">
                      {(labels.matches_played_short || "PJ") +
                        " " +
                        row.partidos_jugados}
                    </div>

                    {/* splits */}
                    <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] leading-tight">
                      <div className="flex flex-col">
                        <div className="text-[var(--color-text-secondary)] uppercase font-semibold tracking-wide">
                          {labels.home_away_block || "Loc / Vis"}
                        </div>
                        <div className="text-[var(--color-text)] font-semibold">
                          {row.goles_local}{" "}
                          <span className="text-[var(--color-text-secondary)]">
                            {labels.home_short || "LOC"}
                          </span>{" "}
                          · {row.goles_visitante}{" "}
                          <span className="text-[var(--color-text-secondary)]">
                            {labels.away_short || "VIS"}
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-col items-start text-right">
                        <div className="text-[var(--color-text-secondary)] uppercase font-semibold tracking-wide">
                          {labels.halves_block || "1P / 2P"}
                        </div>
                        <div className="text-[var(--color-text)] font-semibold">
                          {row.goles_1parte}{" "}
                          <span className="text-[var(--color-text-secondary)]">
                            {labels.first_half_short || "1P"}
                          </span>{" "}
                          · {row.goles_2parte}{" "}
                          <span className="text-[var(--color-text-secondary)]">
                            {labels.second_half_short || "2P"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            </React.Fragment>
          );
        })}
      </ul>
    </div>
  );
}
