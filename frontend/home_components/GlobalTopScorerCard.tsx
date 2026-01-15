// /frontend/home_components/GlobalTopScorerCard.tsx
"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { useGlobalJugadoresJornada } from "../hooks/useGlobalValoraciones";

type Props = {
  temporadaId: number | null;
  dict: any;
  jornada?: number | null;
  weekend?: string | null; // ← NUEVO
  topListSize?: number; // por defecto 10
  lang?: string;
};

function initials(text?: string | null) {
  if (!text) return "";
  const parts = text.trim().split(/\s+/);
  return parts.map((p) => p[0]).join("").slice(0, 3).toUpperCase();
}

export default function GlobalTopScorerCard({
  temporadaId,
  dict,
  jornada = null,
  weekend = null, // ← NUEVO
  topListSize = 10,
  lang = "es",
}: Props) {
  const labels = dict?.home_matchday_scorer_labels || {};
  const { ranking, loading, error, data } = useGlobalJugadoresJornada(
    temporadaId,
    { jornada, weekend, top: Math.max(12, topListSize), strict: !!weekend }
  );

  if (!temporadaId) {
    return (
      <div className="text-xs text-[var(--color-text-secondary)]">
        {labels.hint_select_group || "Selecciona contexto para ver el máximo goleador global."}
      </div>
    );
  }
  if (loading) return <div className="text-xs text-[var(--color-text-secondary)]">{labels.loading || "Cargando goleadores de la jornada..."}</div>;
  if (error)   return <div className="text-xs text-[var(--color-error)]">{labels.error || "Error al cargar el goleador de la jornada."}</div>;

  if (!ranking?.length) {
    return <div className="text-xs text-[var(--color-text-secondary)]">{labels.no_data || "Todavía no hay datos en esta jornada."}</div>;
  }

  const ordered = [...ranking].sort((a, b) => (b.goles_jornada ?? 0) - (a.goles_jornada ?? 0));
  const top = ordered[0];
  const jornadaNum = data?.jornada ?? jornada ?? null;
  const clubInitials = initials(top.club_nombre);

  const goals = top.goles_jornada ?? 0;
  const divisionLabelTop = [top.competicion_nombre, top.grupo_nombre].filter(Boolean).join(" · ");

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-full max-w-[360px] md:max-w-[420px] mx-auto aspect-[854/1140]">
        <Image
          src="/tarjetas/top_goleadores.png"
          alt="Top Scorer of the Matchday (Global)"
          fill
          className="object-cover select-none pointer-events-none"
          priority
        />

        {/* JORNADA */}
        <div className="absolute top-[6%] left-1/2 -translate-x-1/2 w-[80%] text-center text-white text-[0.7rem] uppercase tracking-wide">
          {(labels.matchday_prefix || "Jornada") + " " + (jornadaNum ?? "—")}
        </div>

        {/* FOTO */}
        {top.foto ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={top.foto}
            alt={top.nombre}
            className="absolute top-[33%] left-1/2 -translate-x-1/2 w-[30%] aspect-square object-cover rounded-full border-[3px] border-white shadow-2xl bg-black/10"
          />
        ) : null}

        {/* ESCUDO / INICIALES */}
        {top.club_escudo ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={top.club_escudo}
            alt={top.club_nombre}
            className="absolute top-[38%] left-[60%] w-[16%] aspect-square rounded-full object-contain bg-white/5 border border-white/50 p-[3px]"
            onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
          />
        ) : (
          <div className="absolute top-[38%] left-[60%] w-[16%] aspect-square rounded-full bg-white/10 border border-white/40 flex items-center justify-center text-white text-xs font-bold backdrop-blur">
            {clubInitials || "FC"}
          </div>
        )}

        {/* NOMBRE */}
        <Link
          href={`/${lang}/jugadores/${top.slug || top.jugador_id}`}
          className="absolute top-[61%] left-1/2 -translate-x-1/2 w-[82%] text-center text-white uppercase font-title text-[0.85rem] leading-tight drop-shadow-[0_4px_18px_rgba(0,0,0,0.3)] hover:text-brand-accent transition-colors"
        >
          {top.nombre}
        </Link>

        {/* GOLES (grande) */}
        <div className="absolute top-[71%] left-1/2 -translate-x-1/2 w-[78%] flex items-center justify-center gap-3">
          <span className="text-[3rem] md:text-[4rem] leading-none text-white font-bold">
            {goals}
          </span>
          <span className="text-white uppercase tracking-wide text-[0.9rem]">
            {labels.goals_label || "Goles"}
          </span>
        </div>
      </div>

      {divisionLabelTop ? (
        <p className="text-center text-[0.7rem] text-white/70">
          {divisionLabelTop}
        </p>
      ) : null}

      {ordered.length > 1 && (
        <div className="w-full flex flex-col gap-1">
          {ordered.slice(1, Math.min(topListSize, ordered.length)).map((j, i) => (
            <div
              key={j.jugador_id}
              className="flex items-center justify-between bg-black/10 rounded-lg px-2 py-1"
            >
              <div className="min-w-0">
                <Link
                  href={`/${lang}/jugadores/${j.slug || j.jugador_id}`}
                  className="text-sm text-white truncate hover:text-brand-accent transition-colors block"
                >
                  {i + 2}. {j.nombre}
                </Link>
                <Link
                  href={j.club_slug ? `/${lang}/clubes/${j.club_slug}` : `/${lang}/clubes/${j.club_id}`}
                  className="text-[0.7rem] text-white/70 truncate hover:text-brand-accent transition-colors"
                >
                  {j.club_nombre}
                </Link>
                <div className="text-[0.65rem] text-white/60 truncate">
                  {j.competicion_nombre} · {j.grupo_nombre}
                </div>
              </div>
              <div className="ml-2 shrink-0 text-right">
                <div className="text-sm text-white font-semibold leading-none">{j.goles_jornada ?? 0}</div>
                <div className="text-[0.6rem] text-white/70 uppercase">{labels.goals_label || "Goles"}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
