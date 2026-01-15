// components/MVPClassificationTable.tsx
"use client";

import React from "react";
import Link from "next/link";

type MVPRankingRow = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  es_portero?: boolean;
  // 👇 del endpoint mvp-clasificacion
  puntos_acumulados: number;   // total hasta la jornada aplicada
  puntos_jornada: number;      // puntos en la jornada aplicada
  posicion?: number;           // posición actual (opcional si lo quieres mostrar en otro sitio)
};

type MVPData = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornada_aplicada: number | null;
  jornadas_disponibles: number[];
  ranking: MVPRankingRow[]; // acumulado hasta jornada_aplicada
  prev_ranking?: { jugador_id: number; posicion: number }[]; // clasificación hasta la jornada anterior
};

type Props = {
  dict: any;
  loading: boolean;
  error: string | null;
  data: MVPData | null;
  lang?: string;

  /**
   * "by_matchday" → ordena por puntos_jornada (top de esa jornada)
   * "general"     → ordena por puntos_acumulados (acumulado hasta la jornada)
   */
  mode?: "general" | "by_matchday";
  onModeChange?: (m: "general" | "by_matchday") => void;

  /** Jornada seleccionada de forma controlada (opcional) */
  selectedJornada?: number | null;
  onChangeJornada?: (j: number | null) => void;
};

export default function MVPClassificationTable({
  dict,
  loading,
  error,
  data,
  lang = "es",
  mode: externalMode,
  onModeChange,
  selectedJornada,
  onChangeJornada,
}: Props) {
  const labels = dict?.mvp_labels || {};
  const M = dict?.mvp_table || {};

  // Estado interno (si no se controla desde fuera)
  const [internalMode, setInternalMode] =
    React.useState<"general" | "by_matchday">("general");
  const [internalJornada, setInternalJornada] = React.useState<number | null>(
    null
  );

  const mode = externalMode ?? internalMode;

  // Jornada efectiva: controlada o interna o la aplicada por backend
  const jornadaAplicadaBackend = data?.jornada_aplicada ?? null;
  const jornadaEffective =
    selectedJornada ?? internalJornada ?? jornadaAplicadaBackend ?? null;

  // Mapa jugador_id → posición previa (para mostrar flechitas de subida/bajada).
  // Esto permite indicar visualmente si un jugador subió o bajó en el ranking.
  const prevPosByJugador = React.useMemo(() => {
    const map: Record<number, number> = {};
    (data?.prev_ranking || []).forEach((r) => {
      map[r.jugador_id] = r.posicion;
    });
    return map;
  }, [data?.prev_ranking]);

  // Ordenamos según el modo seleccionado.
  // "general" = ranking acumulado (más útil para ver evolución)
  // "by_matchday" = top de esa jornada específica (más útil para destacados)
  const sortedRows: MVPRankingRow[] = React.useMemo(() => {
    const base = data?.ranking ?? [];
    const copy = [...base];

    if (mode === "by_matchday") {
      // Top por jornada → orden descendente por puntos_jornada
      copy.sort((a, b) => {
        if (b.puntos_jornada !== a.puntos_jornada)
          return b.puntos_jornada - a.puntos_jornada;
        // tie-break: acumulado
        if (b.puntos_acumulados !== a.puntos_acumulados)
          return b.puntos_acumulados - a.puntos_acumulados;
        return a.nombre.localeCompare(b.nombre);
      });
    } else {
      // General → orden descendente por acumulado
      copy.sort((a, b) => {
        if (b.puntos_acumulados !== a.puntos_acumulados)
          return b.puntos_acumulados - a.puntos_acumulados;
        // tie-break: puntos de la jornada
        if (b.puntos_jornada !== a.puntos_jornada)
          return b.puntos_jornada - a.puntos_jornada;
        return a.nombre.localeCompare(b.nombre);
      });
    }
    return copy;
  }, [data?.ranking, mode]);

  const handleChangeMode = (m: "general" | "by_matchday") => {
    if (externalMode && onModeChange) onModeChange(m);
    else setInternalMode(m);
  };

  const handleChangeJornada = (value: string) => {
    const next = value ? Number(value) : null;
    if (onChangeJornada) onChangeJornada(next);
    else setInternalJornada(next);
  };

  // Icono variación respecto a prev_ranking
  const renderVariationIcon = (currentIndex: number, jugadorId: number) => {
    const currentPos = currentIndex + 1;
    const prevPos = prevPosByJugador[jugadorId];
    if (!prevPos) return null;

    let variation: "up" | "down" | "same" = "same";
    if (currentPos < prevPos) variation = "up";
    else if (currentPos > prevPos) variation = "down";

    let iconSrc = "/iconos/mantiene.png";
    if (variation === "up") iconSrc = "/iconos/mejora.png";
    if (variation === "down") iconSrc = "/iconos/empeora.png";

    const M = dict?.mvp_table || {};
    const altText =
      variation === "up"
        ? labels.variation_up || M.variation_up || "Mejora"
        : variation === "down"
        ? labels.variation_down || M.variation_down || "Empeora"
        : labels.variation_same || M.variation_same || "Mantiene";

    return (
      <img
        src={iconSrc}
        alt={altText}
        width={16}
        height={16}
        className="mx-auto"
      />
    );
  };

  return (
    <div className="w-full flex flex-col gap-3">
      {/* CABECERA: título, chip de jornada + select + modos */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
        {/* título + chip jornada */}
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-white">
            {labels.table_title || "Clasificación MVP"}
          </h2>

          {jornadaEffective ? (
            <span className="text-[0.65rem] px-2 py-0.5 rounded-full bg-white/5 text-[#B3B3B3] uppercase tracking-wide">
              {labels.matchday_label
                ? `${labels.matchday_label} ${jornadaEffective}`
                : `Jornada ${jornadaEffective}`}
            </span>
          ) : null}
        </div>

        {/* selector jornada + botones modo */}
        <div className="flex items-center gap-2">
          {/* SELECT JORNADA */}
          {data?.jornadas_disponibles?.length ? (
            <select
              value={jornadaEffective ?? ""}
              onChange={(e) => handleChangeJornada(e.target.value)}
              className="bg-[#0B1C2E] text-white border border-white/10 text-xs rounded px-2 py-1 outline-none hover:bg-[#0B2538] transition"
              title={labels.select_matchday_title || M.select_matchday_title || "Selecciona jornada"}
            >
              {data.jornadas_disponibles.map((j) => (
                <option key={j} value={j}>
                  {labels.matchday_label
                    ? `${labels.matchday_label} ${j}`
                    : `Jornada ${j}`}
                </option>
              ))}
            </select>
          ) : null}

          {/* BOTONES modo */}
          <div className="flex gap-1 bg-white/5 rounded-full p-1">
            <button
              onClick={() => handleChangeMode("general")}
              className={`px-3 py-1 rounded-full text-[0.65rem] transition ${
                mode === "general"
                  ? "bg-[#A51B3D] text-white"
                  : "text-[#B3B3B3] hover:text-white"
              }`}
            >
              {labels.mode_general || M.mode_general || "General"}
            </button>
            <button
              onClick={() => handleChangeMode("by_matchday")}
              className={`px-3 py-1 rounded-full text-[0.65rem] transition ${
                mode === "by_matchday"
                  ? "bg-[#A51B3D] text-white"
                  : "text-[#B3B3B3] hover:text-white"
              }`}
            >
              {labels.mode_by_matchday || M.mode_by_matchday || "Por jornada"}
            </button>
          </div>
        </div>
      </div>

      {/* TABLA */}
      <div className="w-full overflow-x-auto border border-white/5 rounded-xl bg-[#0A0A0A]/40">
        <table
          className={`min-w-full text-sm ${
            loading ? "opacity-70" : "opacity-100"
          }`}
        >
          <thead className="bg-white/5 text-left text-[0.65rem] uppercase tracking-wide text-[#B3B3B3]">
            <tr>
              <th className="py-3 px-3 w-10">#</th>
              {/* Variación */}
              {data?.prev_ranking && data.prev_ranking.length > 0 ? (
                <th className="py-3 px-2 w-8"></th>
              ) : null}
              <th className="py-3 px-3">
                {labels.col_player || M.col_player || "Jugador"}
              </th>
              <th className="py-3 px-3">
                {labels.col_club || M.col_club || "Club"}
              </th>
              {/* Puntos jornada aplicada */}
              <th className="py-3 px-3 text-right">
                {labels.col_last_md_points || "Pts última J."}
              </th>
              {/* Puntos acumulados (siempre visibles) */}
              <th className="py-3 px-3 text-right">
                {labels.col_total_points || M.col_total_points || "Total"}
              </th>
            </tr>
          </thead>
          <tbody>
            {error ? (
              <tr>
                <td
                  colSpan={6}
                  className="py-6 px-3 text-center text-red-400 text-sm"
                >
                  {error}
                </td>
              </tr>
            ) : (sortedRows?.length ?? 0) === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="py-6 px-3 text-center text-[#B3B3B3] text-sm"
                >
                  {labels.no_data ||
                    "No hay datos disponibles para esta jornada."}
                </td>
              </tr>
            ) : (
              sortedRows.map((jug, idx) => (
                <tr
                  key={jug.jugador_id ?? idx}
                  className="border-b border-white/5 hover:bg-white/5 transition"
                >
                  <td className="py-2 px-3 text-sm text-[#B3B3B3]">
                    {idx + 1}
                  </td>

                  {/* flechita variación */}
                  {data?.prev_ranking && data.prev_ranking.length > 0 ? (
                    <td className="py-2 px-2 text-center">
                      {renderVariationIcon(idx, jug.jugador_id)}
                    </td>
                  ) : null}

                  <td className="py-2 px-3">
                    <Link
                      href={`/${lang}/jugadores/${jug.slug || jug.jugador_id}`}
                      className="flex items-center gap-3 hover:text-brand-accent transition-colors"
                    >
                      <div className="w-9 h-9 rounded-full overflow-hidden bg-white/5 flex-shrink-0">
                        {jug.foto ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={jug.foto}
                            alt={jug.nombre}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-[0.5rem] text-white/60 text-center px-1">
                            {jug.nombre}
                          </div>
                        )}
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="text-white text-sm font-medium truncate">
                          {jug.nombre}
                        </span>
                        {jug.es_portero ? (
                          <span className="text-[0.6rem] text-[#A51B3D] uppercase">
                            {labels.role_gk || "Portero"}
                          </span>
                        ) : null}
                      </div>
                    </Link>
                  </td>

                  <td className="py-2 px-3">
                    <div className="flex items-center gap-2 min-w-0">
                      {jug.club_escudo ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={jug.club_escudo}
                          alt={jug.club_nombre}
                          className="w-5 h-5 object-contain"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display =
                              "none";
                          }}
                        />
                      ) : null}
                      <span className="text-[#B3B3B3] text-xs truncate">
                        {jug.club_nombre || "—"}
                      </span>
                    </div>
                  </td>

                  {/* puntos jornada aplicada */}
                  <td className="py-2 px-3 text-right">
                    <span className="text-white text-base font-semibold">
                      {jug.puntos_jornada ?? 0}
                    </span>
                  </td>

                  {/* total acumulado */}
                  <td className="py-2 px-3 text-right">
                    <span className="text-white text-base font-semibold">
                      {jug.puntos_acumulados ?? 0}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Nota contextual del modo */}
      <p className="text-[0.6rem] text-[#B3B3B3]">
        {mode === "general"
          ? labels.general_hint ||
            "Mostrando la clasificación acumulada hasta la jornada seleccionada."
          : labels.by_matchday_hint ||
            "Mostrando el top de la jornada (ordenado por puntos de esa jornada)."}
      </p>
    </div>
  );
}
