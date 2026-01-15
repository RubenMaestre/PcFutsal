"use client";

import React from "react";
import Link from "next/link";

export type MatchData = {
  id: string | number;
  jornada: number;
  jugado: boolean;
  fecha_hora: string | null;
  pabellon: string;
  arbitros: string[];
  local: { id: number; nombre: string; escudo: string; slug?: string | null; goles: number | null };
  visitante: {
    id: number;
    nombre: string;
    escudo: string;
    slug?: string | null;
    goles: number | null;
  };
  // por si el endpoint de jornada ya trae esto
  identificador_federacion?: string | number | null;
};

function capFirst(s: string) {
  if (!s) return s;
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Formatea la fecha y hora del partido según el locale del usuario.
// Devuelve formato legible: "Jueves, 23 de octubre", "21:15h"
// El locale se determina desde el idioma de la página para mostrar fechas en el idioma correcto.
function formatDateTime(fecha_hora: string | null, locale: string = "es-ES") {
  if (!fecha_hora) return { fechaLinea: "", horaLinea: "" };

  try {
    const d = new Date(fecha_hora);

    // Formato de fecha con día de la semana y mes completo para mejor legibilidad.
    const fechaStr = d.toLocaleDateString(locale, {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
    // Formato de hora en 24h con minutos (ej: "21:15").
    const horaStr = d.toLocaleTimeString(locale, {
      hour: "2-digit",
      minute: "2-digit",
    });

    return {
      fechaLinea: capFirst(fechaStr),
      horaLinea: `${horaStr}h`, // Añadimos 'h' al final para indicar que es hora.
    };
  } catch {
    // Si hay error al parsear la fecha, devolvemos strings vacíos para evitar crashes.
    return { fechaLinea: "", horaLinea: "" };
  }
}

export default function MatchCard({
  match,
  divisionLogoSrc,
  dict,
  // 👇 nuevo
  isStar = false,
  lang = "es",
}: {
  match: MatchData;
  divisionLogoSrc: string;
  dict: any;
  isStar?: boolean;
  lang?: string;
}) {
  if (!match || !match.local || !match.visitante) return null;

  const labels = dict?.home_matches_labels || {};
  const starLabel =
    labels.star_match_label || dict?.match?.star_match_label || "PARTIDO ESTRELLA DE LA JORNADA";

  // Mapeo de códigos de idioma de la app a locales de Intl.DateTimeFormat.
  // Esto permite mostrar fechas en el formato correcto según el idioma seleccionado.
  const localeMap: Record<string, string> = {
    es: "es-ES",
    en: "en-US",
    val: "ca-ES",
    fr: "fr-FR",
    it: "it-IT",
    pt: "pt-PT",
    de: "de-DE",
  };
  const locale = localeMap[lang] || "es-ES"; // Fallback a español si el idioma no está mapeado.

  const { fechaLinea, horaLinea } = formatDateTime(match.fecha_hora, locale);

  const marcadorLocal =
    match.jugado && match.local.goles !== null ? match.local.goles : null;

  const marcadorVisitante =
    match.jugado && match.visitante.goles !== null
      ? match.visitante.goles
      : null;

  const bottomClasses = isStar
    ? "bg-[var(--color-gold)] text-black"
    : "bg-[var(--color-accent)] text-white";

  return (
    <div
      className={`
        rounded-xl
        text-white
        shadow-lg
        overflow-hidden
        flex
        flex-col
        h-full
        ${isStar ? "border border-[var(--color-gold)]" : "border border-[var(--color-accent)]"}
      `}
      style={
        isStar
          ? {
              background:
                "linear-gradient(150deg, rgba(212,175,55,0.12), rgba(0,0,0,0))",
            }
          : {}
      }
    >
      {/* TOP (blanco) */}
      <div className="bg-white text-black px-4 pt-4 pb-3 flex flex-col">
        {(fechaLinea || horaLinea) && (
          <div className="w-full text-center mb-3">
            <div className="text-[11px] font-semibold leading-tight text-[var(--color-navy)]">
              {fechaLinea}
            </div>
            <div className="text-[11px] font-semibold leading-tight text-[var(--color-navy)]">
              {horaLinea}
            </div>
          </div>
        )}

        <div className="flex items-start justify-between gap-2">
          {/* LOCAL */}
          <div className="flex flex-col items-center flex-1 min-w-0">
            <Link
              href={match.local.slug ? `/${lang}/clubes/${match.local.slug}` : `/${lang}/clubes/${match.local.id}`}
              className="flex flex-col items-center flex-1 min-w-0 hover:opacity-80 transition-opacity"
            >
              <div className="w-11 h-11 bg-neutral-100 border border-neutral-300 rounded flex items-center justify-center overflow-hidden">
                {match.local.escudo ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={match.local.escudo}
                    alt={match.local.nombre}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <span className="text-[10px] text-neutral-500">?</span>
                )}
              </div>

              <div className="text-[11px] font-semibold text-center text-neutral-800 leading-tight mt-1 truncate max-w-[90px]">
                {match.local.nombre}
              </div>
            </Link>

            {marcadorLocal !== null && (
              <div
                className="
                  text-[20px] leading-none font-extrabold
                  text-[var(--color-navy)]
                  font-[var(--font-title)]
                "
                style={{ fontFamily: "var(--font-title)" }}
              >
                {marcadorLocal}
              </div>
            )}
          </div>

          {/* LOGO COMPETICIÓN / DIVISIÓN */}
          <div className="flex flex-col items-center flex-shrink-0 px-2">
            <div className="w-9 h-9 rounded bg-white flex items-center justify-center overflow-hidden border border-neutral-300">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={divisionLogoSrc || "/placeholder_competicion.png"}
                alt={dict?.match?.competition_alt || "Competición"}
                className="w-full h-full object-contain"
              />
            </div>
          </div>

          {/* VISITANTE */}
          <div className="flex flex-col items-center flex-1 min-w-0">
            <Link
              href={match.visitante.slug ? `/${lang}/clubes/${match.visitante.slug}` : `/${lang}/clubes/${match.visitante.id}`}
              className="flex flex-col items-center flex-1 min-w-0 hover:opacity-80 transition-opacity"
            >
              <div className="w-11 h-11 bg-neutral-100 border border-neutral-300 rounded flex items-center justify-center overflow-hidden">
                {match.visitante.escudo ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={match.visitante.escudo}
                    alt={match.visitante.nombre}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <span className="text-[10px] text-neutral-500">?</span>
                )}
              </div>

              <div className="text-[11px] font-semibold text-center text-neutral-800 leading-tight mt-1 truncate max-w-[90px]">
                {match.visitante.nombre}
              </div>
            </Link>

            {marcadorVisitante !== null && (
              <div
                className="
                  text-[20px] leading-none font-extrabold
                  text-[var(--color-navy)]
                "
                style={{ fontFamily: "var(--font-title)" }}
              >
                {marcadorVisitante}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* BOTTOM */}
      <div
        className={`
          flex flex-col gap-2 px-4 py-3 text-[12px] leading-snug flex-1
          ${bottomClasses}
        `}
      >
        {/* ⭐ etiqueta partido estrella */}
        {isStar ? (
          <div className="flex justify-center mb-1">
            <div className="flex items-center gap-2 bg-black/10 rounded-full px-3 py-1">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/iconos/estrella.png"
                alt={starLabel}
                className="w-4 h-4"
              />
              <span className="text-[10px] font-semibold uppercase tracking-wide">
                {starLabel}
              </span>
            </div>
          </div>
        ) : null}

        {/* Jornada */}
        <div className="flex items-start gap-2 text-[11px] leading-tight opacity-90">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/iconos/calendario.png"
            alt={labels.matchday_label || dict?.match?.matchday_alt || "Jornada"}
            className="w-4 h-4 flex-shrink-0 mt-[1px]"
          />
          <div className="flex-1">
            {(labels.matchday_label || dict?.match?.matchday_alt || "Jornada") + " " + match.jornada}
          </div>
        </div>

        {/* Pabellón */}
        {match.pabellon ? (
          <div className="flex items-start gap-2 text-[11px] leading-tight opacity-90">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/iconos/pabellon.png"
              alt={labels.field_venue || dict?.match?.venue_alt || "Pabellón"}
              className="w-4 h-4 flex-shrink-0 mt-[1px]"
            />
            <div className="flex-1">{match.pabellon}</div>
          </div>
        ) : null}

        {/* Árbitros */}
        {match.arbitros && match.arbitros.length > 0 ? (
          <div className="flex items-start gap-2 text-[11px] leading-tight opacity-90">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/iconos/arbitros.png"
              alt={labels.field_referees || "Árbitros:"}
              className="w-4 h-4 flex-shrink-0 mt-[1px]"
            />
            <div className="flex-1">
              {(labels.field_referees || "Árbitros:") +
                " " +
                match.arbitros.join(" · ")}
            </div>
          </div>
        ) : null}

        {/* CTA */}
        <div className="mt-2 w-full flex justify-center">
          <Link
            href={`/${lang}/partidos/${match.identificador_federacion || match.id}`}
            className="
              text-[11px] font-semibold
              bg-[var(--color-navy)]
              text-white
              px-3 py-2
              rounded-lg
              leading-none
              hover:opacity-90
              transition
              whitespace-nowrap
              inline-block
            "
          >
            {labels.cta_match_sheet || "Ficha del partido"}
          </Link>
        </div>
      </div>
    </div>
  );
}
