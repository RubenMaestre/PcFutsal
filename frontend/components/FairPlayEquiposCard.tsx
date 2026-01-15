"use client";

import React from "react";
import Link from "next/link";
import { useFairPlayEquipos } from "../hooks/useFairPlayEquipos";

export default function FairPlayEquiposCard({ grupoId, dict, lang = "es" }: any) {
  const { loading, error, equipos } = useFairPlayEquipos(grupoId);

  const labels = dict?.home_discipline_labels || {};
  const hintSelect = labels.hint_select_group || "Selecciona un grupo para ver las sanciones.";

  if (!grupoId)
    return (
      <p className="text-xs text-[var(--color-text-secondary)]">
        {hintSelect}
      </p>
    );

  if (loading)
    return (
      <p className="text-xs text-[var(--color-text-secondary)]">
        {labels.loading_fairplay || "Cargando equipos..."}
      </p>
    );

  if (error)
    return (
      <p className="text-xs text-[var(--color-error,#7A0F2A)]">
        {labels.error_generic || "Error al cargar los datos."}
      </p>
    );

  if (!equipos.length)
    return (
      <p className="text-xs text-[var(--color-text-secondary)]">
        {labels.no_data_equipos || "Sin datos todavía."}
      </p>
    );

  return (
    <ul className="flex flex-col gap-2 text-[13px] leading-tight">
      {equipos.map((e, idx) => (
        <li
          key={idx}
          className={`
            flex items-center
            bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg
            px-3 py-0.5 gap-3
            md:py-1 md:gap-2
          `}
        >
          {/* POS + ESCUDO + NOMBRE */}
          <div className="flex items-center flex-1 min-w-0 gap-3 md:gap-2">
            {/* Posición visual (1,2,3...) */}
            <div className="text-[11px] text-[var(--color-text-secondary)] font-semibold w-4 text-right md:text-[10px]">
              {idx + 1}
            </div>

            {/* Escudo */}
            <div
              className={`
                rounded-lg overflow-hidden bg-[#1c1c1c] border border-[var(--color-card)]
                flex-shrink-0 flex items-center justify-center
                w-9 h-9
                md:w-7 md:h-7
              `}
            >
              {e.club_escudo ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={e.club_escudo}
                  alt={e.club_nombre}
                  className="w-full h-full object-contain p-1"
                />
              ) : (
                <div className="text-[10px] text-[var(--color-text-secondary)]">
                  -
                </div>
              )}
            </div>

            {/* Nombre club */}
            <div className="min-w-0 flex-1">
              <Link
                href={e.club_slug ? `/${lang}/clubes/${e.club_slug}` : `/${lang}/clubes/${e.club_id}`}
                className={`
                  font-semibold truncate text-[var(--color-text)]
                  text-[13px] leading-tight
                  md:text-[12px]
                  hover:text-brand-accent transition-colors
                `}
              >
                {e.club_nombre}
              </Link>

              {/* Puntuación fair play (menos = mejor) */}
              <div
                className={`
                  text-[11px] text-[var(--color-text-secondary)] leading-tight truncate
                  md:text-[10px]
                `}
              >
                {e.puntos_fair_play} pts fair play
              </div>
            </div>
          </div>

          {/* BLOQUE TARJETAS */}
          <div
            className={`
              flex items-center flex-shrink-0 gap-3
              text-[12px] leading-none
              md:gap-2 md:text-[11px]
            `}
          >
            {/* Amarillas */}
            <div className="flex items-center gap-1 min-w-[32px] justify-end">
              <img
                src="/iconos/amarilla.png"
                alt="amarilla"
                className="w-4 h-4 md:w-3.5 md:h-3.5"
              />
              <span className="text-[var(--color-text)] font-semibold">
                {e.amarillas}
              </span>
            </div>

            {/* Dobles amarillas */}
            <div className="flex items-center gap-1 min-w-[32px] justify-end">
              <img
                src="/iconos/doble_amarilla.png"
                alt="doble"
                className="w-4 h-4 md:w-3.5 md:h-3.5"
              />
              <span className="text-[var(--color-text)] font-semibold">
                {e.dobles_amarillas}
              </span>
            </div>

            {/* Rojas */}
            <div className="flex items-center gap-1 min-w-[32px] justify-end">
              <img
                src="/iconos/roja.png"
                alt="roja"
                className="w-4 h-4 md:w-3.5 md:h-3.5"
              />
              <span className="text-[var(--color-text)] font-semibold">
                {e.rojas}
              </span>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
