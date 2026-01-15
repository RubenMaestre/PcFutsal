// rankings_components/MVPGlobalTable.tsx
"use client";

import React from "react";
import Link from "next/link";

type MVPGlobalRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  club_slug?: string | null;

  // Puntos de la semana (ventana seleccionada)
  puntos: number | null;              // principal (muchas veces usado como "pts semana")
  puntos_semana?: number | null;      // alias

  // Puntos TOTALES acumulados
  puntos_global: number | null;       // principal esperado

  coef_division: number;
  goles_jornada?: number;
  grupo_id: number;
  grupo_nombre: string;
  competicion_id: number;
  competicion_nombre: string;

  // campos opcionales para el TOTAL acumulado (por si backend usa otros nombres)
  total_puntos?: number | null;
  total_puntos_global?: number | null;
  puntos_totales?: number | null;
  puntos_totales_global?: number | null;
  acumulado?: number | null;
  acumulado_global?: number | null;
  puntos_acumulados?: number | null;
};

type Props = {
  dict: any;
  loading: boolean;
  error: string | null;
  data: MVPGlobalRow[];
  noWeekData?: boolean; // indica que en esta semana no hay partidos (vista "solo global")
  lang?: string; // Idioma para construir URLs
};

// Helper: puntos de la semana
function getWeekPoints(row: MVPGlobalRow): number {
  // Prioridad: puntos_semana -> puntos
  const value =
    typeof row.puntos_semana === "number"
      ? row.puntos_semana
      : typeof row.puntos === "number"
      ? row.puntos
      : 0;

  return value ?? 0;
}

// Helper: puntos totales (acumulados)
function getTotalPoints(row: MVPGlobalRow, noWeekData: boolean): number {
  // 1) Intentar campos explícitos de "TOTAL"
  const explicitTotal =
    row.puntos_global ??
    row.total_puntos_global ??
    row.puntos_totales_global ??
    row.puntos_totales ??
    row.total_puntos ??
    row.acumulado_global ??
    row.acumulado ??
    row.puntos_acumulados;

  if (typeof explicitTotal === "number" && !Number.isNaN(explicitTotal)) {
    return explicitTotal;
  }

  // 2) Fallback: si estamos en modo "no hay semana" (solo global),
  // usamos 'puntos' como total acumulado.
  if (noWeekData && typeof row.puntos === "number" && !Number.isNaN(row.puntos)) {
    return row.puntos;
  }

  // 3) Último recurso: 0
  return 0;
}

export default function MVPGlobalTable({
  dict,
  loading,
  error,
  data,
  noWeekData = false,
  lang = "es",
}: Props) {
  const labels = dict?.mvp_labels || {};
  const T = dict?.tables || {};

  if (loading) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.loading || T.loading || "Cargando..."}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-xs text-red-500">
        {labels.error || T.error || "Error al cargar datos."}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.no_data || T.no_data || "Sin datos disponibles."}
      </div>
    );
  }

  // (Opcional) inspeccionar qué llega del backend:
  // console.log("DEBUG MVP GLOBAL ROW SAMPLE:", data[0]);

  // Ordenamos por PUNTOS TOTALES desc (siempre por puntos_global)
  // Los datos ya vienen ordenados del componente padre, pero re-ordenamos por seguridad
  const sorted = [...data].sort(
    (a, b) => {
      const totalA = getTotalPoints(a, noWeekData);
      const totalB = getTotalPoints(b, noWeekData);
      // Ordenar por puntos totales descendente
      if (totalB !== totalA) {
        return totalB - totalA;
      }
      // Si empatan, ordenar por puntos semana
      const weekA = getWeekPoints(a);
      const weekB = getWeekPoints(b);
      return weekB - weekA;
    }
  );

  return (
    <div className="overflow-x-auto w-full">
      <table className="min-w-full border-collapse text-sm text-white/90">
        <thead className="bg-[#111] text-[0.7rem] uppercase text-white/70">
          <tr>
            <th className="px-3 py-2 text-left">#</th>
            <th className="px-3 py-2 text-left">
              {labels.player || T.player || "Jugador"}
            </th>
            <th className="px-3 py-2 text-left">
              {labels.club || T.club || "Club"}
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
            const total = getTotalPoints(row, noWeekData);
            const weekPoints = getWeekPoints(row);

            return (
              <tr
                key={row.jugador_id}
                className={`border-b border-[#222] hover:bg-[#222]/50 ${
                  idx === 0 ? "bg-[#A51B3D]/20 font-bold" : ""
                }`}
              >
                <td className="px-3 py-2 text-left">{idx + 4}</td>

                {/* Jugador */}
                <td className="px-3 py-2 text-left">
                  <Link
                    href={`/${lang}/jugadores/${row.slug || row.jugador_id}`}
                    className="flex items-center gap-2 hover:text-brand-accent transition-colors"
                  >
                    {row.foto ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={row.foto}
                        alt={row.nombre}
                        className="h-6 w-6 rounded-full object-cover"
                      />
                    ) : (
                      <div className="h-6 w-6 rounded-full bg-[#333] flex items-center justify-center text-[0.6rem]">
                        {row.nombre?.[0] ?? "-"}
                      </div>
                    )}
                    <span className="truncate">{row.nombre}</span>
                  </Link>
                </td>

                {/* Club */}
                <td className="px-3 py-2 text-left truncate">
                  <Link
                    href={row.club_slug ? `/${lang}/clubes/${row.club_slug}` : `/${lang}/clubes/${row.club_id}`}
                    className="hover:text-brand-accent transition-colors"
                  >
                    {row.club_nombre || "-"}
                  </Link>
                </td>

                {/* División */}
                <td className="px-3 py-2 text-left text-[0.75rem] text-white/70 truncate">
                  {[row.competicion_nombre, row.grupo_nombre]
                    .filter(Boolean)
                    .join(" · ")}
                </td>

                {/* PTS semana */}
                <td className="px-3 py-2 text-right">
                  {noWeekData ? (
                    "—"
                  ) : (
                    weekPoints.toLocaleString(undefined, {
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
