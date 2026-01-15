"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { useTopScorerMatchday } from "../hooks/useTopScorerMatchday";

type Props = {
  grupoId: number | null;
  jornada: number | null;
  dict: any;
  lang?: string;
};

function getClubInitials(clubName?: string | null): string {
  if (!clubName) return "";
  const parts = clubName.trim().split(/\s+/);
  const initials = parts.map((p) => p[0]).join("");
  return initials.slice(0, 3).toUpperCase();
}

export default function TopScorerOfMatchday({
  grupoId,
  jornada,
  dict,
  lang = "es",
}: Props) {
  const { loading, error, data, topScorer } = useTopScorerMatchday(
    grupoId,
    jornada
  );

  const labels = dict?.home_matchday_scorer_labels || {};

  if (!grupoId) {
    return (
      <div className="text-xs text-white/60">
        {labels.hint_select_group ||
          "Selecciona un grupo para ver el máximo goleador de la jornada."}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-xs text-white/60">
        {labels.loading || "Cargando goleadores de la jornada..."}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-xs text-red-500">
        {labels.error || "Error al cargar el goleador de la jornada."}
      </div>
    );
  }

  if (!topScorer) {
    return (
      <div className="text-xs text-white/60">
        {labels.no_data || "Todavía no hay goles registrados en esta jornada."}
      </div>
    );
  }

  const displayName =
    topScorer.apodo && topScorer.apodo.trim() !== ""
      ? topScorer.apodo
      : topScorer.nombre;

  const clubName = topScorer.club_nombre || "—";
  const clubInitials = getClubInitials(clubName);
  const goals = topScorer.goles_jornada ?? "—";
  const jornadaNum =
    jornada != null ? jornada : data?.jornada != null ? data.jornada : null;

  const pabellon = topScorer.pabellon || "— pabellón —";
  const fecha = topScorer.fecha_hora
    ? new Date(topScorer.fecha_hora).toLocaleDateString("es-ES")
    : "— fecha —";


  return (
    <div
      className="
        relative
        w-full
        max-w-full
        sm:max-w-[360px]
        md:max-w-[420px]
        mx-auto
        aspect-[854/1140]
      "
    >
      {/* FONDO */}
      <Image
        src="/tarjetas/top_goleadores.png"
        alt="Top Scorer of the Matchday"
        fill
        className="object-cover select-none pointer-events-none"
        priority
      />

      {/* JORNADA */}
      <div
        className="
          absolute
          top-[6%]
          left-1/2
          -translate-x-1/2
          w-[80%]
          text-center
          text-white
          text-[0.7rem]
          uppercase
          tracking-wide
        "
      >
        {(labels.matchday_prefix || "Jornada") + " " + (jornadaNum ?? "—")}
      </div>

      {/* FOTO (bajada un poco más) */}
      {topScorer.foto ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={topScorer.foto}
          alt={displayName}
          className="
            absolute
            top-[33%]
            left-1/2
            -translate-x-1/2
            w-[30%]
            aspect-square
            object-cover
            rounded-full
            border-[3px] border-white
            shadow-2xl
            bg-black/10
          "
        />
      ) : null}

      {/* ESCUDO / INICIALES */}
      {topScorer.club_escudo ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={topScorer.club_escudo}
          alt={topScorer.club_nombre}
          className="
            absolute
            top-[38%]
            left-[60%]
            w-[16%]
            aspect-square
            rounded-full
            object-contain
            bg-white/5
            border border-white/50
            p-[3px]
          "
        />
      ) : (
        <div
          className="
            absolute
            top-[38%]
            left-[60%]
            w-[16%]
            aspect-square
            rounded-full
            bg-white/10
            border border-white/40
            flex
            items-center
            justify-center
            text-white
            text-xs
            font-bold
            backdrop-blur
          "
        >
          {clubInitials || "FC"}
        </div>
      )}

      {/* NOMBRE (justo encima de la raya) */}
      <div
        className="
          absolute
          top-[61%]
          left-1/2
          -translate-x-1/2
          w-[82%]
          text-center
          text-white
          uppercase
          font-title
          text-[0.75rem]
          sm:text-[0.85rem]
          leading-tight
          drop-shadow-[0_4px_18px_rgba(0,0,0,0.3)]
        "
      >
        {displayName}
      </div>

      {/* GOLES (más grandes) */}
      <div
        className="
          absolute
          top-[71%]
          left-1/2
          -translate-x-1/2
          w-[78%]
          flex
          items-center
          justify-center
          gap-2
          sm:gap-3
        "
      >
        <span className="text-[2.5rem] sm:text-[3rem] md:text-[4rem] leading-none text-white font-bold">
          {goals}
        </span>
        <span className="text-white uppercase tracking-wide text-[0.75rem] sm:text-[0.9rem]">
          {labels.goals_label || "Goles"}
        </span>
      </div>

      {/* PABELLÓN */}
      <div
        className="
          absolute
          bottom-[11%]
          left-1/2
          -translate-x-1/2
          w-[82%]
          text-center
          text-[0.6rem]
          text-white/70
        "
      >
        {pabellon}
      </div>

      {/* FECHA */}
      <div
        className="
          absolute
          bottom-[7%]
          left-1/2
          -translate-x-1/2
          w-[82%]
          text-center
          text-[0.6rem]
          text-white/70
        "
      >
        {fecha}
      </div>
    </div>
  );
}
