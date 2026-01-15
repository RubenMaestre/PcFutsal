// /frontend/rankings_components/SancionesGlobalTable.tsx
"use client";

import React from "react";
import Link from "next/link";

type SancionRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto?: string | null;
  club_id: number | null;
  club_nombre?: string | null;
  club_escudo?: string | null;
  // Sanciones de la semana
  amarillas_semana?: number | null;
  dobles_amarillas_semana?: number | null;
  rojas_semana?: number | null;
  puntos_semana?: number | null;
  // Sanciones totales
  amarillas_total: number;
  dobles_amarillas_total: number;
  rojas_total: number;
  puntos_total: number;
  grupo_nombre?: string | null;
  competicion_nombre?: string | null;
};

type Props = {
  dict: any;
  loading: boolean;
  error: string | null;
  data: SancionRow[];
  noWeekData?: boolean;
  lang?: string;
};

function normalizeImageUrl(raw?: string | null) {
  if (!raw) return "";
  let url = raw.trim();
  if (url.startsWith("http://")) url = "https://" + url.slice(7);
  return url;
}

export default function SancionesGlobalTable({
  dict,
  loading,
  error,
  data,
  noWeekData = false,
  lang = "es",
}: Props) {
  const labels = dict?.sanciones_global_labels || {};

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

  // Ya viene ordenado por puntos_total del backend
  const sorted = [...data];

  return (
    <div className="overflow-x-auto w-full">
      <table className="min-w-full border-collapse text-sm text-white/90">
        <thead className="bg-[#111] text-[0.7rem] uppercase text-white/70">
          <tr>
            <th className="px-3 py-2 text-left">#</th>
            <th className="px-3 py-2 text-left">
              {labels.player || dict?.tables?.player || "Jugador"}
            </th>
            <th className="px-3 py-2 text-left">
              {labels.division || dict?.tables?.division || "División"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.week_sanctions || dict?.tables?.week_sanctions || "Sanciones última semana"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.total_sanctions || dict?.tables?.total_sanctions || "Sanciones totales"}
            </th>
            <th className="px-3 py-2 text-right">
              {labels.total_points || dict?.tables?.total_points || "Puntos totales"}
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

            // Contar sanciones de la semana
            const sanciones_semana = (
              (row.amarillas_semana ?? 0) +
              (row.dobles_amarillas_semana ?? 0) +
              (row.rojas_semana ?? 0)
            );

            // Contar sanciones totales
            const sanciones_total = (
              row.amarillas_total +
              row.dobles_amarillas_total +
              row.rojas_total
            );

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
                        <div className="flex items-center gap-1">
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
                        </div>
                      )}
                    </div>
                  </Link>
                </td>

                {/* División */}
                <td className="px-3 py-2 text-left text-[0.75rem] text-white/70 truncate">
                  {divisionLabel || "-"}
                </td>

                {/* SANCIONES ÚLTIMA SEMANA */}
                <td className="px-3 py-2 text-right">
                  {noWeekData || (row.puntos_semana === null || row.puntos_semana === undefined) ? (
                    "—"
                  ) : (
                    <div className="flex items-center justify-end gap-1">
                      {(row.rojas_semana ?? 0) > 0 && (
                        <div className="flex items-center gap-1">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src="/iconos/roja.png" alt="roja" className="w-4 h-4" />
                          <span>{row.rojas_semana ?? 0}</span>
                        </div>
                      )}
                      {(row.dobles_amarillas_semana ?? 0) > 0 && (
                        <div className="flex items-center gap-1">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src="/iconos/doble_amarilla.png" alt="doble amarilla" className="w-4 h-4" />
                          <span>{row.dobles_amarillas_semana ?? 0}</span>
                        </div>
                      )}
                      {(row.amarillas_semana ?? 0) > 0 && (
                        <div className="flex items-center gap-1">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src="/iconos/amarilla.png" alt="amarilla" className="w-4 h-4" />
                          <span>{row.amarillas_semana ?? 0}</span>
                        </div>
                      )}
                      {sanciones_semana === 0 && <span className="text-white/50">0</span>}
                    </div>
                  )}
                </td>

                {/* SANCIONES TOTALES */}
                <td className="px-3 py-2 text-right font-semibold">
                  <div className="flex items-center justify-end gap-1">
                    {row.rojas_total > 0 && (
                      <div className="flex items-center gap-1">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src="/iconos/roja.png" alt="roja" className="w-4 h-4" />
                        <span>{row.rojas_total}</span>
                      </div>
                    )}
                    {row.dobles_amarillas_total > 0 && (
                      <div className="flex items-center gap-1">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src="/iconos/doble_amarilla.png" alt="doble amarilla" className="w-4 h-4" />
                        <span>{row.dobles_amarillas_total}</span>
                      </div>
                    )}
                    {row.amarillas_total > 0 && (
                      <div className="flex items-center gap-1">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src="/iconos/amarilla.png" alt="amarilla" className="w-4 h-4" />
                        <span>{row.amarillas_total}</span>
                      </div>
                    )}
                    {sanciones_total === 0 && <span className="text-white/50">0</span>}
                  </div>
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

