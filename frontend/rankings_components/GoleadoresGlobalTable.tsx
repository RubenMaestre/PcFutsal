// /frontend/rankings_components/GoleadoresGlobalTable.tsx
"use client";

import React from "react";
import Link from "next/link";

type GoleadorRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto?: string | null;
  club_id: number | null;
  club_nombre?: string | null;
  club_escudo?: string | null;
  club_slug?: string | null;
  goles_semana?: number | null;
  goles_total: number;
  puntos_total: number;
  grupo_nombre?: string | null;
  competicion_nombre?: string | null;
};

type Props = {
  dict: any;
  loading: boolean;
  error: string | null;
  data: GoleadorRow[];
  noWeekData?: boolean;
  lang?: string;
};

function normalizeImageUrl(raw?: string | null) {
  if (!raw) return "";
  let url = raw.trim();
  if (url.startsWith("http://")) url = "https://" + url.slice(7);
  return url;
}

export default function GoleadoresGlobalTable({
  dict,
  loading,
  error,
  data,
  noWeekData = false,
  lang = "es",
}: Props) {
  const labels = dict?.goleadores_global_labels || dict?.tables || {};
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

  // Ya viene ordenado por puntos_total del backend
  const sorted = [...data];

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
              {labels.division || T.division || "División"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.week_goals || T.week_goals || "Goles última semana"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.total_goals || T.total_goals || "Goles totales"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.total_points || T.total_points || "Puntos totales"}
            </th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, idx) => {
            const fotoUrl = normalizeImageUrl(row.foto);
            const escudoUrl = normalizeImageUrl(row.club_escudo);
            
            const divisionLabel = [row.competicion_nombre, row.grupo_nombre]
              .filter(Boolean)
              .join(" · ");

            return (
              <tr
                key={row.jugador_id}
                className={`border-b border-[#222] hover:bg-[#222]/50 ${
                  idx === 0 ? "bg-[#A51B3D]/20 font-bold" : ""
                }`}
              >
                <td className="px-3 py-2 text-left">{idx + 1}</td>

                {/* Jugador */}
                <td className="px-3 py-2 text-left">
                  <Link
                    href={`/${lang}/jugadores/${row.slug || row.jugador_id}`}
                    className="flex items-center gap-2 hover:text-brand-accent transition-colors"
                  >
                    {fotoUrl ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={fotoUrl}
                        alt={row.nombre}
                        className="h-8 w-8 rounded-full object-cover bg-[#111]"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = "none";
                        }}
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-[#333] flex items-center justify-center text-[0.6rem] font-semibold">
                        {row.nombre?.[0] ?? "?"}
                      </div>
                    )}
                    <div className="flex flex-col min-w-0">
                      <span className="truncate font-medium">{row.nombre}</span>
                      {row.club_nombre && (
                        <Link
                          href={row.club_slug ? `/${lang}/clubes/${row.club_slug}` : `/${lang}/clubes/${row.club_id}`}
                          className="flex items-center gap-1 hover:text-brand-accent transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {escudoUrl ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img
                              src={escudoUrl}
                              alt={row.club_nombre}
                              className="h-3 w-3 rounded-full object-contain"
                              onError={(e) => {
                                (e.target as HTMLImageElement).style.display = "none";
                              }}
                            />
                          ) : null}
                          <span className="text-[0.65rem] text-white/60 truncate">
                            {row.club_nombre}
                          </span>
                        </Link>
                      )}
                    </div>
                  </Link>
                </td>

                {/* División */}
                <td className="px-3 py-2 text-left text-[0.75rem] text-white/70 truncate">
                  {divisionLabel || "-"}
                </td>

                {/* GOLES ÚLTIMA SEMANA */}
                <td className="px-3 py-2 text-right">
                  {noWeekData || (row.goles_semana === null || row.goles_semana === undefined) ? (
                    "—"
                  ) : (
                    row.goles_semana  // Mostrar 0 si tiene 0 goles en la semana
                  )}
                </td>

                {/* GOLES TOTALES */}
                <td className="px-3 py-2 text-right font-semibold">
                  {row.goles_total}
                </td>

                {/* PUNTOS TOTALES */}
                <td className="px-3 py-2 text-right font-bold text-white">
                  {row.puntos_total}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

