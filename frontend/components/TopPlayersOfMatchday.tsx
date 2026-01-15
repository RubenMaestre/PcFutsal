"use client";

import React, { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useTopJugadoresJornada } from "../hooks/useTopJugadoresJornada";

type Props = {
  grupoId: number | null;
  jornada: number | null;
  dict: any;
  lang?: string;
  /** Opcionales: si vienes desde una página con slugs, puedes pasarlos explícitamente */
  competicionSlug?: string;
  grupoSlug?: string;
};

export default function TopPlayersOfMatchday({
  grupoId,
  jornada,
  dict,
  lang = "es",
  competicionSlug,
  grupoSlug,
}: Props) {
  const [showKeepers, setShowKeepers] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const { data, jugadores, loading, error } = useTopJugadoresJornada(
    grupoId,
    jornada,
    {
      onlyPorteros: showKeepers,
      limit: 5,
    }
  );

  const labels = dict?.home_matchday_list_labels || {};
  const jornadaNum =
    jornada != null ? jornada : data?.jornada != null ? data.jornada : null;

  // 1) Si vienen por props, priorízalos
  let compSlug = competicionSlug;
  let grpSlug = grupoSlug;

  // 2) Si no vienen, intenta deducirlos de la URL actual
  //    - Ej: /es/competicion/tercera-division/grupo-xv
  //    - Ej MVP: /es/competicion/mvp/tercera-division/grupo-xv
  if ((!compSlug || !grpSlug) && pathname) {
    const parts = pathname.split("/").filter(Boolean); // sin vacíos
    // parts: ["es","competicion","...","..."] o ["es","competicion","mvp","...","..."]
    const idxCompeticion = parts.indexOf("competicion");
    if (idxCompeticion !== -1) {
      // Si es /competicion/mvp/<comp>/<grupo>
      if (parts[idxCompeticion + 1] === "mvp" && parts.length >= idxCompeticion + 4) {
        compSlug = compSlug || parts[idxCompeticion + 2];
        grpSlug  = grpSlug  || parts[idxCompeticion + 3];
      }
      // Si es /competicion/<comp>/<grupo>
      else if (parts.length >= idxCompeticion + 3) {
        compSlug = compSlug || parts[idxCompeticion + 1];
        grpSlug  = grpSlug  || parts[idxCompeticion + 2];
      }
    }
  }

  // 3) Construir ruta destino
  const mvpRoute =
    compSlug && grpSlug
      ? `/${lang}/competicion/mvp/${compSlug}/${grpSlug}`
      : `/${lang}/mvp`;

  if (!grupoId) {
    return (
      <div className="bg-[#121212] rounded-xl px-3 py-3 text-[0.7rem] text-[#B3B3B3]">
        {labels.hint_select_group ||
          "Selecciona un grupo para ver los jugadores de la jornada."}
      </div>
    );
  }

  return (
    <div className="bg-[#121212] rounded-xl p-3 flex flex-col gap-3 h-full">
      {/* Cabecera */}
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-[0.65rem] uppercase text-[#B3B3B3] tracking-wide">
            {showKeepers
              ? labels.title_gk || "Porteros de la jornada"
              : labels.title || "Top jugadores de la jornada"}
            {jornadaNum ? ` · J${jornadaNum}` : null}
          </p>
          {showKeepers ? (
            labels.subtitle_gk ? (
              <h3 className="text-sm font-semibold text-white leading-tight">
                {labels.subtitle_gk}
              </h3>
            ) : null
          ) : labels.subtitle ? (
            <h3 className="text-sm font-semibold text-white leading-tight">
              {labels.subtitle}
            </h3>
          ) : null}
        </div>

        {/* Toggle */}
        <div className="flex items-center gap-1 bg-black/20 rounded-full p-1">
          <button
            onClick={() => setShowKeepers(false)}
            className={`px-2 py-[2px] rounded-full text-[0.6rem] transition ${
              !showKeepers
                ? "bg-[#A51B3D] text-white"
                : "text-[#B3B3B3] hover:text-white"
            }`}
          >
            {labels.tab_players || "Jugadores"}
          </button>
          <button
            onClick={() => setShowKeepers(true)}
            className={`px-2 py-[2px] rounded-full text-[0.6rem] transition ${
              showKeepers
                ? "bg-[#A51B3D] text-white"
                : "text-[#B3B3B3] hover:text-white"
            }`}
          >
            {labels.tab_keepers || "Porteros"}
          </button>
        </div>
      </div>

      {/* Lista */}
      {loading ? (
        <div className="text-[0.7rem] text-[#B3B3B3]">
          {labels.loading || "Cargando jugadores..."}
        </div>
      ) : error ? (
        <div className="text-[0.7rem] text-red-500">{error}</div>
      ) : !jugadores || jugadores.length === 0 ? (
        <div className="text-[0.7rem] text-[#B3B3B3]">
          {labels.no_data || "No hay jugadores valorados en esta jornada."}
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {jugadores.map((jug, idx) => (
            <li
              key={jug.jugador_id ?? idx}
              className="flex items-center gap-2 bg-black/10 hover:bg-black/20 rounded-lg px-2 py-1.5 transition"
            >
              <div className="w-6 text-center text-[0.65rem] text-[#B3B3B3] font-semibold">
                {idx + 1}
              </div>

              <Link
                href={`/${lang}/jugadores/${jug.slug || jug.jugador_id}`}
                className="flex items-center gap-2 flex-1 min-w-0 hover:text-brand-accent transition-colors"
              >
                <div className="relative w-10 h-10 rounded-full overflow-hidden bg:black/30 flex-shrink-0 border border-white/5">
                  {jug.foto ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={jug.foto}
                      alt={jug.nombre}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items:center justify-center text-[0.55rem] text-white text-center px-1">
                      {jug.nombre}
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium truncate">
                    {jug.nombre}
                  </p>
                  <div className="flex items-center gap-1">
                    {jug.club_escudo ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={jug.club_escudo}
                        alt={jug.club_nombre}
                        className="w-4 h-4 object-contain"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = "none";
                        }}
                      />
                    ) : null}
                    <p className="text-[0.6rem] text-[#B3B3B3] truncate">
                      {jug.club_nombre || "—"}
                    </p>
                  </div>
                </div>
              </Link>

              <div className="flex flex-col items-end gap-0">
                <span className="text-white text-base font-bold leading-none">
                  {jug.puntos}
                </span>
                <span className="text-[0.55rem] text-[#B3B3B3] uppercase">
                  {labels.points_label || "pts"}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Botón */}
      <div className="pt-1">
        <button
          onClick={() => router.push(mvpRoute)}
          className="w-full text-center text-[0.65rem] font-medium bg-[#A51B3D] hover:bg-[#7A0F2A] text-white rounded-lg py-1.5 transition"
        >
          {labels.btn_view_mvp || "VER CLASIFICACIÓN MVP"}
        </button>
      </div>
    </div>
  );
}
