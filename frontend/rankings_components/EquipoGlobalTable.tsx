// /frontend/rankings_components/EquipoGlobalTable.tsx
"use client";

import React from "react";

type TeamRow = {
  club_id: number | null;
  nombre: string;
  escudo?: string | null;

  competicion_nombre?: string | null;
  grupo_nombre?: string | null;

  // Puntos de la semana (ventana seleccionada)
  score?: number | null;
  score_week?: number | null;
  score_semana?: number | null;
  puntos?: number | null;

  // Puntos TOTALES acumulados
  score_global?: number | null;
  score_total?: number | null;
  total_score?: number | null;
  acumulado?: number | null;
};

type Props = {
  dict: any;
  loading: boolean;
  error: string | null;
  data: TeamRow[];
  noWeekData?: boolean; // si no hay partidos en esa semana
};

function normalizeShieldUrl(raw?: string | null) {
  if (!raw) return "";
  let url = raw.trim();
  if (url.startsWith("http://")) url = "https://" + url.slice(7);
  return url;
}

function getTotalScore(row: TeamRow): number {
  return (
    row.score_global ??
    row.score_total ??
    row.total_score ??
    row.acumulado ??
    0
  );
}

export default function EquipoGlobalTable({
  dict,
  loading,
  error,
  data,
  noWeekData = false,
}: Props) {
  const labels = dict?.team_global_labels || dict?.mvp_labels || {};
  const T = dict?.tables || {};

  if (loading) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.loading || "Cargando..."}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-xs text-red-500">
        {labels.error || "Error al cargar datos."}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.no_data || "Sin datos disponibles."}
      </div>
    );
  }

  // Ordenamos por PUNTOS TOTALES desc
  const sorted = [...data].sort((a, b) => getTotalScore(b) - getTotalScore(a));

  return (
    <div className="overflow-x-auto w-full">
      <table className="min-w-full border-collapse text-sm text-white/90">
        <thead className="bg-[#111] text-[0.7rem] uppercase text-white/70">
          <tr>
            <th className="px-3 py-2 text-left">#</th>
            <th className="px-3 py-2 text-left">
              {labels.team || T.team || "Equipo"}
            </th>
            <th className="px-3 py-2 text-left">
              {labels.division || T.division || "División"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.week_points || T.week_points || "Pts semana"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.total_points || T.total_points_short || "Pts totales"}
            </th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, idx) => {
            const total = getTotalScore(row);

            // Puntos de la semana: probamos varios nombres
            const rawWeekPts: number =
              (typeof row.score_week === "number"
                ? row.score_week
                : typeof row.score_semana === "number"
                ? row.score_semana
                : typeof row.score === "number"
                ? row.score
                : typeof row.puntos === "number"
                ? row.puntos
                : 0) ?? 0;

            const escudoUrl = normalizeShieldUrl(row.escudo);

            const divisionLabel = [row.competicion_nombre, row.grupo_nombre]
              .filter(Boolean)
              .join(" · ");

            return (
              <tr
                key={row.club_id ?? idx}
                className={`border-b border-[#222] hover:bg-[#222]/50 ${
                  idx === 0 ? "bg-[#A51B3D]/20 font-bold" : ""
                }`}
              >
                <td className="px-3 py-2 text-left">{idx + 1}</td>

                {/* Equipo */}
                <td className="px-3 py-2 text-left">
                  <div className="flex items-center gap-2">
                    {escudoUrl ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={escudoUrl}
                        alt={row.nombre}
                        className="h-6 w-6 rounded-full object-contain bg-[#111]"
                      />
                    ) : (
                      <div className="h-6 w-6 rounded-full bg-[#333] flex items-center justify-center text-[0.6rem]">
                        {row.nombre?.[0] ?? "-"}
                      </div>
                    )}
                    <span className="truncate">{row.nombre}</span>
                  </div>
                </td>

                {/* División */}
                <td className="px-3 py-2 text-left text-[0.75rem] text-white/70 truncate">
                  {divisionLabel || "-"}
                </td>

                {/* PTS semana */}
                <td className="px-3 py-2 text-right">
                  {noWeekData ? (
                    "—"
                  ) : (
                    rawWeekPts.toLocaleString(undefined, {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 2,
                    })
                  )}
                </td>

                {/* PTS totales */}
                <td className="px-3 py-2 text-right font-semibold">
                  {total.toLocaleString(undefined, {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2,
                  })}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
