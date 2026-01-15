// /frontend/components/MatchDaySection.tsx
"use client";

import React from "react";
import MatchCarousel from "./MatchCarousel";
import { MatchData } from "./MatchCard";

type ApiResponse = {
  grupo: {
    id: number;
    nombre: string;
    competicion: string;
    temporada: string;
  };
  jornada: number | null;
  jornadas_disponibles: number[];
  partidos: MatchData[];
};

export default function MatchDaySection({
  grupoId,
  divisionLogoSrc,
  dict,
  selectedJornada,
  onChangeJornada,
  lang = "es",
}: {
  grupoId: number | null;
  divisionLogoSrc: string;
  dict: any;
  selectedJornada: number | null;
  onChangeJornada: (j: number | null) => void;
  lang?: string;
}) {
  const [data, setData] = React.useState<ApiResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // 👇 nuevo
  const [starMatchId, setStarMatchId] = React.useState<
    string | number | null
  >(null);

  const labels = dict?.home_matches_labels || {};

  React.useEffect(() => {
    if (!grupoId) {
      setData(null);
      setError(null);
      setLoading(false);
      setStarMatchId(null);
      return;
    }

    let cancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        // 1) tu endpoint de SIEMPRE
        let url = `/api/estadisticas/resultados-jornada/?grupo_id=${grupoId}`;
        if (selectedJornada !== null) url += `&jornada=${selectedJornada}`;

        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error("HTTP " + res.status);

        const json = (await res.json()) as ApiResponse;

        if (!cancelled) {
          setData(json);

          // sincronizar con el padre
          if (selectedJornada === null && json.jornada !== null) {
            onChangeJornada(json.jornada);
          }
        }

        // 2) pedimos el partido estrella con el mismo grupo y jornada
        const jornadaParaStar =
          selectedJornada !== null
            ? selectedJornada
            : json.jornada !== null
            ? json.jornada
            : null;

        let starUrl = `/api/valoraciones/partido-estrella/?grupo_id=${grupoId}`;
        if (jornadaParaStar !== null) {
          starUrl += `&jornada=${jornadaParaStar}`;
        }

        const starRes = await fetch(starUrl, { cache: "no-store" });
        if (starRes.ok) {
          const starJson = await starRes.json();
          const pid = starJson?.partido_estrella?.partido_id ?? null;
          if (!cancelled) {
            setStarMatchId(pid);
          }
        } else {
          if (!cancelled) setStarMatchId(null);
        }
      } catch (err: any) {
        if (!cancelled) setError(err.message || "Error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchData();
    return () => {
      cancelled = true;
    };
  }, [grupoId, selectedJornada, onChangeJornada]);

  if (!grupoId) return null;

  const jornadas = data?.jornadas_disponibles ?? [];
  const jornadaActualApi = data?.jornada ?? null;

  const jornadaActualVisual =
    selectedJornada !== null ? selectedJornada : jornadaActualApi ?? "";

  return (
    <section className="w-full max-w-7xl mx-auto px-4 py-6 text-brand-text font-base">
      {/* Header + selector jornada */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-6">
        <div className="flex flex-col min-w-0">
          <div className="text-[12px] uppercase tracking-wide text-brand-textSecondary font-base truncate">
            {data?.grupo?.competicion ||
              labels.section_competition_fallback ||
              "Competición"}
          </div>

          <div className="text-[14px] font-base font-semibold text-brand-text leading-tight truncate">
            {data?.grupo?.nombre
              ? `${data.grupo.nombre} · ${data.grupo.temporada}`
              : labels.section_group_fallback || "Grupo / Temporada"}
          </div>
        </div>

        {/* Selector jornada */}
        <div className="flex flex-col text-[12px] font-base text-brand-textSecondary">
          <label className="mb-1">
            {labels.select_matchday_label || "Jornada"}
          </label>
          <select
            className="
              bg-brand-card text-brand-text px-3 py-2 rounded-md border border-brand-card
              focus:outline-none focus:ring-2 focus:ring-brand-accent text-[13px]
            "
            value={jornadaActualVisual}
            onChange={(e) => {
              const v = e.target.value;
              if (v === "" || v === "auto") {
                onChangeJornada(null);
              } else {
                onChangeJornada(Number(v));
              }
            }}
          >
            {jornadaActualApi !== null && (
              <option value={jornadaActualApi}>
                {(labels.matchday_label || "Jornada") + " " + jornadaActualApi}
              </option>
            )}

            {jornadas.map((j) => (
              <option key={j} value={j}>
                {(labels.matchday_label || "Jornada") + " " + j}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Estado de carga / error / resultados */}
      {loading ? (
        <div className="text-[13px] text-brand-textSecondary">
          {labels.loading || "Cargando resultados..."}
        </div>
      ) : error ? (
        <div className="text-[13px] text-red-500">
          {labels.error || "Error al cargar los resultados."}
        </div>
      ) : !data?.partidos?.length ? (
        <div className="text-[13px] text-brand-textSecondary">
          {labels.no_matches || "No hay partidos en esta jornada."}
        </div>
      ) : (
        <MatchCarousel
          matches={data.partidos.filter(Boolean)}
          divisionLogoSrc={divisionLogoSrc || "/placeholder_competicion.png"}
          dict={dict}
          starMatchId={starMatchId}
          lang={lang}
        />
      )}
    </section>
  );
}
