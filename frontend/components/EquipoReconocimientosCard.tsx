// /frontend/components/EquipoReconocimientosCard.tsx
"use client";

import React, { useState } from "react";
import { useEquipoReconocimientos } from "../hooks/useEquipoReconocimientos";

type Props = {
  clubId: number | string | null;
  dict: any;
  lang?: string;
};

export default function EquipoReconocimientosCard({ clubId, dict, lang = "es" }: Props) {
  const { data, loading, error } = useEquipoReconocimientos(clubId, !!clubId);
  const [expanded, setExpanded] = useState<{ [key: string]: boolean }>({});

  const labels = dict?.reconocimientos || {};

  if (!clubId) {
    return null;
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-4">
        <div className="text-sm text-slate-300">{labels.loading || "Cargando reconocimientos..."}</div>
      </div>
    );
  }

  if (error || !data) {
    return null; // No mostrar error, simplemente no mostrar la tarjeta
  }

  const reconocimientos = data;
  const totalReconocimientos = 
    reconocimientos.mejor_equipo_jornadas_division +
    reconocimientos.mejor_equipo_jornadas_global;

  // Si no hay reconocimientos, no mostrar la tarjeta
  if (totalReconocimientos === 0) {
    return null;
  }

  const toggleExpand = (key: string) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "—";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(lang === "es" ? "es-ES" : lang, {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-white">
          {labels.title_equipo || "Reconocimientos del Equipo"}
        </h3>
        <div className="text-sm text-slate-300">
          {totalReconocimientos} {labels.total || "reconocimientos"}
        </div>
      </div>

      {/* Badges de resumen */}
      <div className="grid grid-cols-2 gap-3">
        {reconocimientos.mejor_equipo_jornadas_division > 0 && (
          <div className="rounded-lg bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 p-3">
            <div className="text-xs text-blue-300/80 uppercase tracking-wide mb-1">
              {labels.mejor_equipo_jornada || "Mejor Equipo Jornada"}
            </div>
            <div className="text-2xl font-bold text-blue-400">
              {reconocimientos.mejor_equipo_jornadas_division}
            </div>
          </div>
        )}

        {reconocimientos.mejor_equipo_jornadas_global > 0 && (
          <div className="rounded-lg bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 p-3">
            <div className="text-xs text-purple-300/80 uppercase tracking-wide mb-1">
              {labels.mejor_equipo_global || "Mejor Equipo Global"}
            </div>
            <div className="text-2xl font-bold text-purple-400">
              {reconocimientos.mejor_equipo_jornadas_global}
            </div>
          </div>
        )}
      </div>

      {/* Detalles expandibles */}
      <div className="space-y-2 pt-4 border-t border-white/10">
        {/* Mejor Equipo Jornada División */}
        {reconocimientos.detalle.mejor_equipo_jornadas_division.length > 0 && (
          <div>
            <button
              onClick={() => toggleExpand("mejor_equipo_division")}
              className="w-full flex items-center justify-between text-left text-sm font-semibold text-white hover:text-slate-200 transition py-2"
            >
              <span>
                {labels.mejor_equipo_jornada || "Mejor Equipo de Jornada"} ({reconocimientos.detalle.mejor_equipo_jornadas_division.length})
              </span>
              <span className="text-slate-400">
                {expanded["mejor_equipo_division"] ? "▲" : "▼"}
              </span>
            </button>
            {expanded["mejor_equipo_division"] && (
              <div className="mt-2 space-y-2 pl-4">
                {reconocimientos.detalle.mejor_equipo_jornadas_division.map((equipo, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-white/5 text-sm"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-white font-medium">
                          {equipo.grupo} - {labels.jornada || "J"} {equipo.jornada}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {equipo.temporada} • {formatDate(equipo.fecha)}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {equipo.victorias}V {equipo.empates}E {equipo.derrotas}D
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-blue-400 font-bold">{equipo.puntos.toFixed(1)} pts</div>
                        <div className="text-xs text-slate-400">
                          {equipo.goles_favor}-{equipo.goles_contra}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Mejor Equipo Global */}
        {reconocimientos.detalle.mejor_equipo_jornadas_global.length > 0 && (
          <div>
            <button
              onClick={() => toggleExpand("mejor_equipo_global")}
              className="w-full flex items-center justify-between text-left text-sm font-semibold text-white hover:text-slate-200 transition py-2"
            >
              <span>
                {labels.mejor_equipo_global || "Mejor Equipo Global"} ({reconocimientos.detalle.mejor_equipo_jornadas_global.length})
              </span>
              <span className="text-slate-400">
                {expanded["mejor_equipo_global"] ? "▲" : "▼"}
              </span>
            </button>
            {expanded["mejor_equipo_global"] && (
              <div className="mt-2 space-y-2 pl-4">
                {reconocimientos.detalle.mejor_equipo_jornadas_global.map((equipo, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-white/5 text-sm"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-white font-medium">
                          {equipo.grupo} • {equipo.temporada}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {formatDate(equipo.fecha_inicio)} - {formatDate(equipo.fecha_fin)}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {equipo.victorias}V {equipo.empates}E {equipo.derrotas}D
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-purple-400 font-bold">{equipo.puntos.toFixed(1)} pts</div>
                        <div className="text-xs text-slate-400">
                          coef: {equipo.coef_division.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}


