// /frontend/components/TeamOfMatchday.tsx
"use client";

import React from "react";
import Link from "next/link";

type Props = {
  grupoId: number | null;
  jornada: number | null;
  dict: any;
  lang?: string;
  hookData: {
    data: any;
    loading: boolean;
    error: string | null;
  };
};

// función para asegurar https
function normalizeShieldUrl(raw: string | null | undefined): string {
  if (!raw) return "";
  let url = raw.trim();
  if (url.startsWith("http://")) {
    url = "https://" + url.slice("http://".length);
  }
  return url;
}

export default function TeamOfMatchday({
  grupoId,
  jornada,
  dict,
  lang = "es",
  hookData,
}: Props) {
  const { data, loading, error } = hookData;

  // CLAVES específicas
  const teamLabels = dict?.home_matchday_team_labels || {};

  const hintSelectGroup =
    teamLabels.hint_select_group ||
    dict?.home_matchday_stats_labels?.hint_select_group ||
    "Selecciona un grupo para ver los datos de la jornada.";

  const loadingText =
    teamLabels.loading ||
    dict?.home_table_labels?.loading ||
    "Cargando equipo de la jornada…";

  const errorText =
    teamLabels.error ||
    dict?.home_table_labels?.error ||
    "Error al cargar el equipo de la jornada.";

  const noDataText =
    teamLabels.no_data ||
    dict?.home_table_labels?.no_data ||
    "Sin datos para esta jornada.";

  const defaultComment =
    teamLabels.default_comment || "Jornada destacada. Equipo muy completo.";

  const scoreLabel = teamLabels.score_label || "score";

  if (!grupoId) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {hintSelectGroup}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {loadingText}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-xs text-[var(--color-error)]">{errorText}</div>
    );
  }

  if (!data || !data.equipo_de_la_jornada) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {noDataText}
      </div>
    );
  }

  const equipo = data.equipo_de_la_jornada;
  const motivos: string[] = Array.isArray(equipo.motivos)
    ? equipo.motivos
    : [];

  // normalizamos escudo
  const escudoUrl = normalizeShieldUrl(equipo.escudo);

  // top 5 si viene ranking
  const ranking: any[] = Array.isArray(data.ranking_clubes)
    ? data.ranking_clubes.slice(0, 5)
    : [];

  const extra = ranking.slice(1); // del 2º al 5º

  return (
    <div className="flex flex-col gap-3">
      {/* bloque principal: campeón de la jornada */}
      <div className="flex items-center gap-5">
        {/* ESCUDO grande */}
        <div className="w-20 h-20 rounded-full bg-[var(--color-surface-muted)] flex items-center justify-center overflow-hidden border-2 border-brand-card shrink-0 shadow-md">
          {escudoUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={escudoUrl}
              alt={equipo.nombre || "Escudo"}
              className="w-full h-full object-contain p-1"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          ) : (
            <span className="text-base text-brand-textSecondary font-semibold">
              {equipo.nombre ? equipo.nombre.slice(0, 3).toUpperCase() : "?"}
            </span>
          )}
        </div>

        {/* TEXTO */}
        <div className="flex flex-col gap-1 min-w-0">
          {/* nombre */}
          <Link
            href={equipo.slug ? `/${lang}/clubes/${equipo.slug}` : `/${lang}/clubes/${equipo.club_id}`}
            className="text-lg font-bold leading-tight truncate text-[var(--color-text-primary)] hover:text-brand-accent transition-colors"
          >
            {equipo.nombre}
          </Link>

          {/* comentario / motivo */}
          {motivos.length > 0 ? (
            <div className="text-sm text-[var(--color-text-secondary)] leading-snug line-clamp-2">
              {motivos[0]}
            </div>
          ) : (
            <div className="text-sm text-[var(--color-text-secondary)] leading-snug">
              {defaultComment}
            </div>
          )}

          {/* score */}
          {typeof equipo.score === "number" ? (
            <div className="text-sm text-[var(--color-accent)] font-semibold mt-1">
              {scoreLabel}: {equipo.score.toFixed(2)}
            </div>
          ) : null}
        </div>
      </div>

      {/* lista con 2º a 5º */}
      {extra.length > 0 && (
        <div className="flex flex-col gap-1">
          {extra.map((club, i) => (
            <div
              key={club.club_id || i}
              className="flex items-center justify-between bg-black/10 rounded-lg px-2 py-1"
            >
              <Link
                href={club.slug ? `/${lang}/clubes/${club.slug}` : `/${lang}/clubes/${club.club_id}`}
                className="flex items-center gap-2 min-w-0 flex-1 hover:text-brand-accent transition-colors"
              >
                <span className="text-xs text-[var(--color-text-secondary)] font-semibold">
                  {i + 2}º
                </span>
                <span className="text-sm text-[var(--color-text-primary)] truncate">
                  {club.nombre}
                </span>
              </Link>
              {typeof club.score === "number" ? (
                <span className="text-xs text-[var(--color-text-secondary)]">
                  {club.score.toFixed(2)}
                </span>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
