// /components/MiniClassificationTable.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";

export type MiniRow = {
  pos: number | null;
  club_id: number | null;
  nombre: string;
  escudo: string;
  slug?: string | null;
  pj: number;
  puntos: number;
  racha?: string[];
};

type Props = {
  rows: MiniRow[] | undefined;
  dict: any;
  // opcionales: si el padre lo sabe, lo puede pasar
  lang?: string; // "es"
  competitionSlug?: string; // "tercera-division"
  groupSlug?: string; // "grupo-xv"
  onSeeAll?: () => void; // override manual
};

function RachaDots({ racha }: { racha?: string[] }) {
  if (!racha || !Array.isArray(racha) || racha.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-1 mt-1">
      {racha.slice(0, 5).map((res, idx) => {
        const code = (res || "").toUpperCase();

        let bgClass = "bg-[var(--color-error)]"; // derrota
        if (code === "V") bgClass = "bg-[var(--color-success)]"; // victoria
        else if (code === "E") bgClass = "bg-[var(--color-warning)]"; // empate

        return (
          <span
            key={idx}
            className={`inline-block w-2 h-2 rounded-full ${bgClass}`}
          />
        );
      })}
    </div>
  );
}

export default function MiniClassificationTable({
  rows,
  dict,
  lang,
  competitionSlug,
  groupSlug,
  onSeeAll,
}: Props) {
  const router = useRouter();
  const pathname = usePathname();

  // 1) intentamos deducirlo de la URL si no nos lo pasan
  // ej: /es/competicion/tercera-division/grupo-xv
  let inferredLang = lang || "es";
  let inferredCompetition = competitionSlug;
  let inferredGroup = groupSlug;

  if (!competitionSlug || !groupSlug || !lang) {
    const segments = pathname.split("/").filter(Boolean);
    // segments[0] = es
    // segments[1] = competicion
    // segments[2] = tercera-division
    // segments[3] = grupo-xv
    if (segments.length >= 4 && segments[1] === "competicion") {
      inferredLang = segments[0] || inferredLang;
      inferredCompetition = segments[2];
      inferredGroup = segments[3];
    }
  }

  const labels = dict?.home_table_labels || {};
  const titleLabel = labels.title || "Clasificación";
  const descLabel = labels.desc || "Tabla rápida: PTS · GF · GC · Racha.";
  const seeAllLabel = labels.see_all || "VER TODO";
  const pjLabel = labels.pj || "PJ";
  const ptLabel = labels.pt || "PT";
  const noDataLabel = labels.no_data || "Sin datos de clasificación todavía.";

  const handleSeeAll = () => {
    // 1) si el padre ha pasado un handler, usamos ese
    if (onSeeAll) {
      onSeeAll();
      return;
    }

    // 2) si tenemos competición y grupo (pasados o inferidos) → vamos a la específica
    if (inferredCompetition && inferredGroup) {
      router.push(
        `/${inferredLang}/clasificacion/${inferredCompetition}/${inferredGroup}`
      );
      return;
    }

    // 3) fallback
    router.push(`/${inferredLang}/clasificacion`);
  };

  if (!rows || !Array.isArray(rows)) {
    return (
      <div className="py-4 text-brand-textSecondary text-[12px] leading-tight">
        {noDataLabel}
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* CABECERA */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-4">
        <div className="flex-1 min-w-0">
          <div
            className="text-[13px] font-semibold leading-none text-brand-text tracking-wide uppercase"
            style={{ fontFamily: "var(--font-title)" }}
          >
            {titleLabel}
          </div>
          <div
            className="text-[11px] leading-snug text-brand-textSecondary font-base mt-1"
            style={{ fontFamily: "var(--font-base)" }}
          >
            {descLabel}
          </div>
        </div>

        <div className="flex-shrink-0 flex sm:justify-end">
          <button
            className="text-[11px] font-semibold bg-[var(--color-navy)] text-white px-3 py-2 rounded-lg leading-none hover:opacity-90 transition whitespace-nowrap"
            onClick={handleSeeAll}
          >
            {seeAllLabel}
          </button>
        </div>
      </div>

      {/* LISTA */}
      <div className="w-full overflow-x-auto scrollbar-thin scrollbar-thumb-[#333] scrollbar-track-transparent">
        <div className="min-w-[280px] text-brand-text font-base divide-y divide-brand-card">
          {rows.length === 0 ? (
            <div className="py-4 text-brand-textSecondary text-[12px] leading-tight">
              {noDataLabel}
            </div>
          ) : (
            rows.map((teamRaw, idx) => {
              const safe = {
                pos: teamRaw?.pos ?? null,
                club_id:
                  typeof teamRaw?.club_id === "number"
                    ? teamRaw.club_id
                    : idx,
                nombre: teamRaw?.nombre || "—",
                escudo: teamRaw?.escudo || "",
                slug: teamRaw?.slug || null,
                pj: typeof teamRaw?.pj === "number" ? teamRaw.pj : 0,
                puntos:
                  typeof teamRaw?.puntos === "number" ? teamRaw.puntos : 0,
                racha: Array.isArray(teamRaw?.racha) ? teamRaw.racha : [],
              };

              return (
                <div
                  key={safe.club_id ?? idx}
                  className="flex items-center justify-between py-2"
                >
                  {/* IZQUIERDA */}
                  <Link
                    href={safe.slug ? `/${inferredLang}/clubes/${safe.slug}` : `/${inferredLang}/clubes/${safe.club_id}`}
                    className="flex items-start gap-2 min-w-0 flex-1 hover:text-brand-accent transition-colors"
                  >
                    {/* escudo */}
                    <div className="w-7 h-7 rounded bg-neutral-800 flex items-center justify-center overflow-hidden border border-brand-card shrink-0">
                      {safe.escudo ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={safe.escudo}
                          alt={safe.nombre}
                          className="w-full h-full object-contain"
                        />
                      ) : (
                        <span className="text-[10px] text-brand-textSecondary font-base">
                          ?
                        </span>
                      )}
                    </div>

                    {/* pos */}
                    <div
                      className="text-[13px] leading-none font-base font-semibold w-5 text-brand-textSecondary tabular-nums shrink-0 text-right mt-[2px]"
                      style={{ fontFamily: "var(--font-base)" }}
                    >
                      {safe.pos ?? "-"}
                    </div>

                    {/* nombre + racha */}
                    <div className="flex flex-col min-w-0">
                      <div
                        className="text-[13px] leading-tight font-base font-medium text-brand-text truncate"
                        style={{ fontFamily: "var(--font-base)" }}
                      >
                        {safe.nombre}
                      </div>
                      <RachaDots racha={safe.racha} />
                    </div>
                  </Link>

                  {/* DERECHA */}
                  <div className="flex items-center gap-4 text-brand-textSecondary shrink-0 pl-2">
                    {/* PJ */}
                    <div className="flex flex-col items-end leading-tight">
                      <span
                        className="uppercase text-[10px] leading-none tracking-wide text-brand-textSecondary font-base font-normal"
                        style={{ fontFamily: "var(--font-base)" }}
                      >
                        {pjLabel}
                      </span>
                      <span
                        className="text-[13px] leading-none tabular-nums text-brand-text font-base font-semibold"
                        style={{ fontFamily: "var(--font-base)" }}
                      >
                        {safe.pj}
                      </span>
                    </div>

                    {/* PT */}
                    <div className="flex flex-col items-end leading-tight">
                      <span
                        className="uppercase text-[10px] leading-none tracking-wide text-brand-textSecondary font-base font-normal"
                        style={{ fontFamily: "var(--font-base)" }}
                      >
                        {ptLabel}
                      </span>
                      <span
                        className="text-[13px] leading-none tabular-nums text-brand-text font-base font-semibold"
                        style={{ fontFamily: "var(--font-base)" }}
                      >
                        {safe.puntos}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
