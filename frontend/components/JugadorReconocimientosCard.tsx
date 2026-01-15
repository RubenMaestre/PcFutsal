// /frontend/components/JugadorReconocimientosCard.tsx
"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useJugadorReconocimientos } from "../hooks/useJugadorReconocimientos";

type Props = {
  jugadorId: number | string | null;
  dict: any;
  lang?: string;
};

export default function JugadorReconocimientosCard({ jugadorId, dict, lang = "es" }: Props) {
  const { data, loading, error } = useJugadorReconocimientos(jugadorId, !!jugadorId);
  const [expanded, setExpanded] = useState<{ [key: string]: boolean }>({});

  const labels = dict?.reconocimientos || {};

  if (!jugadorId) {
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
    reconocimientos.mvp_partidos +
    reconocimientos.mvp_jornadas_division +
    reconocimientos.mvp_jornadas_global +
    reconocimientos.goleador_jornadas_division;

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
          {labels.title || "Reconocimientos"}
        </h3>
        <div className="text-sm text-slate-300">
          {totalReconocimientos} {labels.total || "reconocimientos"}
        </div>
      </div>

      {/* Badges de resumen */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {reconocimientos.mvp_partidos > 0 && (
          <div className="rounded-lg bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border border-yellow-500/30 p-3">
            <div className="text-xs text-yellow-300/80 uppercase tracking-wide mb-1">
              {labels.mvp_partidos || "MVP Partido"}
            </div>
            <div className="text-2xl font-bold text-yellow-400">
              {reconocimientos.mvp_partidos}
            </div>
          </div>
        )}

        {reconocimientos.mvp_jornadas_division > 0 && (
          <div className="rounded-lg bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 p-3">
            <div className="text-xs text-blue-300/80 uppercase tracking-wide mb-1">
              {labels.mvp_jornada_division || "MVP Jornada"}
            </div>
            <div className="text-2xl font-bold text-blue-400">
              {reconocimientos.mvp_jornadas_division}
            </div>
          </div>
        )}

        {reconocimientos.mvp_jornadas_global > 0 && (
          <div className="rounded-lg bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 p-3">
            <div className="text-xs text-purple-300/80 uppercase tracking-wide mb-1">
              {labels.mvp_global || "MVP Global"}
            </div>
            <div className="text-2xl font-bold text-purple-400">
              {reconocimientos.mvp_jornadas_global}
            </div>
          </div>
        )}

        {reconocimientos.goleador_jornadas_division > 0 && (
          <div className="rounded-lg bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 p-3">
            <div className="text-xs text-green-300/80 uppercase tracking-wide mb-1">
              {labels.goleador_jornada || "Goleador"}
            </div>
            <div className="text-2xl font-bold text-green-400">
              {reconocimientos.goleador_jornadas_division}
            </div>
          </div>
        )}
      </div>

      {/* Detalles expandibles */}
      <div className="space-y-2 pt-4 border-t border-white/10">
        {/* MVP Partidos */}
        {reconocimientos.detalle.mvp_partidos.length > 0 && (
          <div>
            <button
              onClick={() => toggleExpand("mvp_partidos")}
              className="w-full flex items-center justify-between text-left text-sm font-semibold text-white hover:text-slate-200 transition py-2"
            >
              <span>
                {labels.mvp_partidos || "MVP del Partido"} ({reconocimientos.detalle.mvp_partidos.length})
              </span>
              <span className="text-slate-400">
                {expanded["mvp_partidos"] ? "▲" : "▼"}
              </span>
            </button>
            {expanded["mvp_partidos"] && (
              <div className="mt-2 space-y-2 pl-4">
                {reconocimientos.detalle.mvp_partidos.map((mvp, idx) => (
                  <Link
                    key={idx}
                    href={`/${lang}/partidos/${mvp.partido_id}`}
                    className="block p-2 rounded bg-white/5 hover:bg-white/10 transition text-sm"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-white font-medium">
                          {mvp.local} vs {mvp.visitante}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {formatDate(mvp.fecha)}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-yellow-400 font-bold">{mvp.puntos} pts</div>
                        {mvp.goles > 0 && (
                          <div className="text-xs text-slate-400">{mvp.goles} {labels.goles || "goles"}</div>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}

        {/* MVP Jornada División */}
        {reconocimientos.detalle.mvp_jornadas_division.length > 0 && (
          <div>
            <button
              onClick={() => toggleExpand("mvp_jornadas_division")}
              className="w-full flex items-center justify-between text-left text-sm font-semibold text-white hover:text-slate-200 transition py-2"
            >
              <span>
                {labels.mvp_jornada_division || "MVP de Jornada por División"} ({reconocimientos.detalle.mvp_jornadas_division.length})
              </span>
              <span className="text-slate-400">
                {expanded["mvp_jornadas_division"] ? "▲" : "▼"}
              </span>
            </button>
            {expanded["mvp_jornadas_division"] && (
              <div className="mt-2 space-y-2 pl-4">
                {reconocimientos.detalle.mvp_jornadas_division.map((mvp, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-white/5 text-sm"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-white font-medium">
                          {mvp.grupo} - {labels.jornada || "J"} {mvp.jornada}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {mvp.temporada} • {formatDate(mvp.fecha)}
                        </div>
                      </div>
                      <div className="text-blue-400 font-bold text-right">
                        {mvp.puntos.toFixed(1)} pts
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* MVP Global */}
        {reconocimientos.detalle.mvp_jornadas_global.length > 0 && (
          <div>
            <button
              onClick={() => toggleExpand("mvp_jornadas_global")}
              className="w-full flex items-center justify-between text-left text-sm font-semibold text-white hover:text-slate-200 transition py-2"
            >
              <span>
                {labels.mvp_global || "MVP Global"} ({reconocimientos.detalle.mvp_jornadas_global.length})
              </span>
              <span className="text-slate-400">
                {expanded["mvp_jornadas_global"] ? "▲" : "▼"}
              </span>
            </button>
            {expanded["mvp_jornadas_global"] && (
              <div className="mt-2 space-y-2 pl-4">
                {reconocimientos.detalle.mvp_jornadas_global.map((mvp, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-white/5 text-sm"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-white font-medium">
                          {mvp.grupo} • {mvp.temporada}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {formatDate(mvp.fecha_inicio)} - {formatDate(mvp.fecha_fin)}
                        </div>
                      </div>
                      <div className="text-purple-400 font-bold text-right">
                        {mvp.puntos.toFixed(1)} pts
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Goleador Jornada */}
        {reconocimientos.detalle.goleador_jornadas_division.length > 0 && (
          <div>
            <button
              onClick={() => toggleExpand("goleador_jornadas_division")}
              className="w-full flex items-center justify-between text-left text-sm font-semibold text-white hover:text-slate-200 transition py-2"
            >
              <span>
                {labels.goleador_jornada || "Goleador de Jornada"} ({reconocimientos.detalle.goleador_jornadas_division.length})
              </span>
              <span className="text-slate-400">
                {expanded["goleador_jornadas_division"] ? "▲" : "▼"}
              </span>
            </button>
            {expanded["goleador_jornadas_division"] && (
              <div className="mt-2 space-y-2 pl-4">
                {reconocimientos.detalle.goleador_jornadas_division.map((goleador, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-white/5 text-sm"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-white font-medium">
                          {goleador.grupo} - {labels.jornada || "J"} {goleador.jornada}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                          {goleador.temporada} • {formatDate(goleador.fecha)}
                        </div>
                      </div>
                      <div className="text-green-400 font-bold text-right">
                        {goleador.goles} {labels.goles || "goles"}
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


