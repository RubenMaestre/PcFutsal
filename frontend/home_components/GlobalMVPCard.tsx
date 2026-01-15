// /frontend/home_components/GlobalMVPCard.tsx
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
  lang?: string;
};

function initials(text?: string | null) {
  if (!text) return "";
  const parts = text.trim().split(/\s+/);
  return parts.map((p) => p[0]).join("").slice(0, 3).toUpperCase();
}

export default function GlobalMVPCard({
  temporadaId,
  dict,
  jornada = null,
  weekend = null, // ← NUEVO
  lang = "es",
}: Props) {
  const labels = dict?.home_matchday_mvp_labels || {};
  const GOLD = "#d4af37";

  const { jugadorTop, ranking, data, loading, error } = useGlobalJugadoresJornada(
    temporadaId,
    { jornada, weekend, top: 50, strict: !!weekend }
  );

  if (!temporadaId) {
    return (
      <div className="text-xs text-white/60">
        {labels.hint_select_group || "Selecciona contexto para ver datos."}
      </div>
    );
  }
  if (loading) {
    return (
      <div className="text-xs text-white/60">
        {labels.loading || "Cargando..."}
      </div>
    );
  }
  if (error) {
    return (
      <div className="text-xs text-red-500">
        {labels.error || "Error al cargar."}
      </div>
    );
  }
  if (!jugadorTop) {
    return (
      <div className="text-xs text-white/60">
        {labels.no_data || "Sin datos en esta jornada."}
      </div>
    );
  }

  const j = jugadorTop;
  const jor = data?.jornada ?? jornada ?? null;

  const foto = j.foto || "";
  const clubEscudo = j.club_escudo || "";
  const clubInit = initials(j.club_nombre);

  const divisionLabel = [j.competicion_nombre, j.grupo_nombre]
    .filter(Boolean)
    .join(" · ");

  const extraList = Array.isArray(ranking) ? ranking.slice(1, 10) : [];

  return (
    <div className="w-full flex flex-col items-stretch gap-2 sm:gap-3 px-1 sm:px-2">
      <div className="relative w-full max-w-[200px] sm:max-w-[360px] md:max-w-[420px] mx-auto" style={{ aspectRatio: '854/1140', maxHeight: 'calc(100vh - 200px)' }}>
        <Image
          src="/tarjetas/mvp_jornada_5.png"
          alt={dict?.global?.mvp_alt || "MVP global"}
          fill
          className="object-cover select-none pointer-events-none"
          priority
        />

        {/* JORNADA (si no hay número porque es por ventana, deja raya) */}
        <div className="absolute top-[6%] left-1/2 -translate-x-1/2 w-[80%] text-center text-white text-[0.6rem] sm:text-[0.7rem] uppercase tracking-wide">
          {(labels.matchday_prefix || "Jornada") + " " + (jor ?? "—")}
        </div>

        {foto ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={foto}
            alt={j.nombre}
            className="absolute top-[33%] left-1/2 -translate-x-1/2 w-[30%] aspect-square object-cover rounded-full shadow-2xl bg-black/10"
            style={{ border: `3px solid ${GOLD}` }}
          />
        ) : (
          <div
            className="absolute top-[33%] left-1/2 -translate-x-1/2 w-[30%] aspect-square rounded-full flex items-center justify-center text-center px-2 text-white text-[0.65rem] uppercase leading-tight"
            style={{ border: `3px solid ${GOLD}`, background: "rgba(0,0,0,0.2)" }}
          >
            {j.nombre}
          </div>
        )}

        {clubEscudo ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={clubEscudo}
            alt={j.club_nombre}
            className="absolute top-[38%] left-[60%] w-[16%] aspect-square rounded-full object-contain bg-black/20 p-[3px]"
            style={{ border: `2px solid ${GOLD}` }}
            onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
          />
        ) : (
          <div
            className="absolute top-[38%] left-[60%] w-[16%] aspect-square rounded-full flex items-center justify-center text-white text-xs font-bold backdrop-blur"
            style={{ backgroundColor: "rgba(0,0,0,0.25)", border: `2px solid ${GOLD}` }}
          >
            {clubInit || "FC"}
          </div>
        )}

        <Link
          href={`/${lang}/jugadores/${j.slug || j.jugador_id}`}
          className="absolute top-[59%] left-1/2 -translate-x-1/2 w-[82%] text-center text-white uppercase font-title text-[0.65rem] sm:text-[0.75rem] md:text-[0.85rem] leading-tight drop-shadow-[0_4px_18px_rgba(0,0,0,0.3)] hover:text-brand-accent transition-colors"
        >
          {j.nombre}
        </Link>

        <div className="absolute top-[67%] left-1/2 -translate-x-1/2 w-[78%] flex items-center justify-center">
          <span className="text-[6rem] sm:text-[3rem] md:text-[4rem] lg:text-[5rem] leading-none text-white font-bold">
            {j.puntos_global}
          </span>
        </div>

        <Link
          href={j.club_slug ? `/${lang}/clubes/${j.club_slug}` : `/${lang}/clubes/${j.club_id}`}
          className="absolute bottom-[13%] left-1/2 -translate-x-1/2 w-[82%] text-center text-[0.55rem] sm:text-[0.6rem] md:text-[0.7rem] text-white/80 uppercase leading-tight hover:text-brand-accent transition-colors"
        >
          {j.club_nombre}
        </Link>
      </div>

      {divisionLabel ? (
        <div className="text-center text-[0.7rem] text-white/60 uppercase tracking-wide">
          {divisionLabel}
        </div>
      ) : null}

      {extraList.length > 0 && (
        <div className="w-full flex flex-col gap-1 max-w-full overflow-hidden">
          {extraList.map((row, idx) => (
            <div
              key={row.jugador_id}
              className="flex items-center justify-between bg-black/10 rounded-lg px-1.5 sm:px-2 py-1 max-w-full overflow-hidden"
            >
              <div className="min-w-0 flex-1 overflow-hidden pr-1.5 sm:pr-2">
                <Link
                  href={`/${lang}/jugadores/${row.slug || row.jugador_id}`}
                  className="text-xs sm:text-sm text-white truncate hover:text-brand-accent transition-colors block"
                >
                  {idx + 2}. {row.nombre}
                </Link>
                <Link
                  href={row.club_slug ? `/${lang}/clubes/${row.club_slug}` : `/${lang}/clubes/${row.club_id}`}
                  className="text-[0.6rem] sm:text-[0.7rem] text-white/70 truncate hover:text-brand-accent transition-colors"
                >
                  {row.club_nombre}
                </Link>
                <div className="text-[0.55rem] sm:text-[0.65rem] text-white/60 truncate">
                  {row.competicion_nombre} · {row.grupo_nombre}
                </div>
              </div>
              <div className="ml-1 sm:ml-2 shrink-0 text-right">
                <div className="text-xs sm:text-sm text-white font-semibold leading-none">
                  {row.puntos_global}
                </div>
                <div className="text-[0.5rem] sm:text-[0.6rem] text-white/70 uppercase">pts</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
