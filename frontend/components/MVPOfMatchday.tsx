// /frontend/components/MVPOfMatchday.tsx
"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { useJugadoresJornada } from "../hooks/useJugadoresJornada";

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

export default function MVPOfMatchday({ grupoId, jornada, dict, lang = "es" }: Props) {
  const { loading, error, data, jugadorTop } = useJugadoresJornada(
    grupoId,
    jornada
  );

  const labels = dict?.home_matchday_mvp_labels || {};
  const GOLD = "#d4af37";

  if (!grupoId) {
    return (
      <div className="text-xs text-white/60">
        {labels.hint_select_group ||
          "Selecciona un grupo para ver el MVP de la jornada."}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-xs text-white/60">
        {labels.loading || "Cargando jugador de la jornada..."}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-xs text-red-500">
        {labels.error || "Error al cargar el MVP de la jornada."}
      </div>
    );
  }

  if (!jugadorTop) {
    return (
      <div className="text-xs text-white/60">
        {labels.no_data || "Todavía no hay datos en esta jornada."}
      </div>
    );
  }

  // --- datos principales que devuelve la API ---
  const displayName = jugadorTop.nombre || "—";
  const clubName = jugadorTop.club_nombre || "—";
  const clubInitials = getClubInitials(clubName);
  const puntos = jugadorTop.puntos ?? "—";
  const jornadaNum =
    jornada != null ? jornada : data?.jornada != null ? data.jornada : null;

  const fotoJugador = jugadorTop.foto || "";
  const clubEscudo =
    jugadorTop.club_escudo ||
    (jugadorTop.club_id
      ? `/media/clubes/escudos/${jugadorTop.club_id}.png`
      : "");

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
        src="/tarjetas/mvp_jornada_5.png"
        alt={dict?.tables?.mvp_alt || "MVP de la jornada"}
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

      {/* FOTO DEL JUGADOR */}
      {fotoJugador ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={fotoJugador}
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
            shadow-2xl
            bg-black/10
          "
          style={{ border: `3px solid ${GOLD}` }}
        />
      ) : (
        <div
          className="
            absolute
            top-[33%]
            left-1/2
            -translate-x-1/2
            w-[30%]
            aspect-square
            rounded-full
            flex
            items-center
            justify-center
            text-center
            px-2
            text-white
            text-[0.65rem]
            uppercase
            leading-tight
          "
          style={{
            border: `3px solid ${GOLD}`,
            background: "rgba(0,0,0,0.2)",
          }}
        >
          {displayName}
        </div>
      )}

      {/* ESCUDO */}
      {clubEscudo ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={clubEscudo}
          alt={clubName}
          className="
            absolute
            top-[38%]
            left-[60%]
            w-[16%]
            aspect-square
            rounded-full
            object-contain
            bg-black/20
            p-[3px]
          "
          style={{ border: `2px solid ${GOLD}` }}
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = "none";
          }}
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
            flex
            items-center
            justify-center
            text-white
            text-xs
            font-bold
            backdrop-blur
          "
          style={{
            backgroundColor: "rgba(0,0,0,0.25)",
            border: `2px solid ${GOLD}`,
          }}
        >
          {clubInitials || "FC"}
        </div>
      )}

      {/* NOMBRE */}
      <div
        className="
          absolute
          top-[59%]
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

      {/* PUNTOS */}
      <div
        className="
          absolute
          top-[67%]
          left-1/2
          -translate-x-1/2
          w-[78%]
          flex
          items-center
          justify-center
        "
      >
        <span className="text-[2.5rem] sm:text-[3rem] md:text-[4rem] leading-none text-white font-bold">
          {puntos}
        </span>
      </div>

      {/* CLUB (un poco más arriba que antes) */}
      <Link
        href={(jugadorTop as any)?.club_slug ? `/${lang}/clubes/${(jugadorTop as any).club_slug}` : `/${lang}/clubes/${jugadorTop.club_id}`}
        className="
          absolute
          bottom-[13%]
          left-1/2
          -translate-x-1/2
          w-[82%]
          text-center
          text-[0.55rem] sm:text-[0.65rem] md:text-[0.7rem]
          text-white/80
          uppercase
          leading-tight
          hover:text-brand-accent transition-colors
        "
      >
        {clubName}
      </Link>
    </div>
  );
}
