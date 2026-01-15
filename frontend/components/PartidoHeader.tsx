// /components/PartidoHeader.tsx
"use client";

import React from "react";
import Link from "next/link";

type PartidoHeaderProps = {
  partido: {
    id: number;
    jornada_numero: number;
    fecha_hora: string | null;
    jugado: boolean;
    pabellon: string;
    indice_intensidad: number | null;
    grupo: {
      id: number;
      nombre: string;
      slug: string | null;
      competicion: {
        id: number;
        nombre: string;
        slug: string | null;
      } | null;
      temporada: {
        id: number;
        nombre: string;
      } | null;
    } | null;
    local: {
      id: number;
      nombre: string;
      escudo: string;
      slug: string | null;
    };
    visitante: {
      id: number;
      nombre: string;
      escudo: string;
      slug: string | null;
    };
    goles_local: number | null;
    goles_visitante: number | null;
  };
  arbitros: Array<{
    id: number | null;
    nombre: string;
    rol: string;
    slug: string | null;
  }>;
  puntosEquipos: Record<number, number>;
  dict: any;
  lang: string;
};

function formatDateTime(fecha_hora: string | null, locale: string = "es-ES") {
  if (!fecha_hora) return { fecha: "", hora: "" };

  try {
    const d = new Date(fecha_hora);
    const fecha = d.toLocaleDateString(locale, {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    });
    const hora = d.toLocaleTimeString(locale, {
      hour: "2-digit",
      minute: "2-digit",
    });
    return {
      fecha: fecha.charAt(0).toUpperCase() + fecha.slice(1),
      hora: `${hora}h`,
    };
  } catch {
    return { fecha: "", hora: "" };
  }
}

export default function PartidoHeader({
  partido,
  arbitros,
  puntosEquipos,
  dict,
  lang,
}: PartidoHeaderProps) {
  const localeMap: Record<string, string> = {
    es: "es-ES",
    en: "en-US",
    val: "ca-ES",
    fr: "fr-FR",
    it: "it-IT",
    pt: "pt-PT",
    de: "de-DE",
  };
  const locale = localeMap[lang] || "es-ES";
  const { fecha, hora } = formatDateTime(partido.fecha_hora, locale);

  const puntosLocal = puntosEquipos[partido.local.id] || null;
  const puntosVisitante = puntosEquipos[partido.visitante.id] || null;

  return (
    <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
      {/* Header principal con equipos y marcador */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 mb-8">
        {/* Equipo Local */}
        <div className="flex flex-col items-center flex-1 min-w-0">
          <Link
            href={
              partido.local.slug
                ? `/${lang}/clubes/${partido.local.slug}`
                : `/${lang}/clubes/${partido.local.id}`
            }
            className="flex flex-col items-center hover:opacity-80 transition-opacity group"
          >
            <div className="w-24 h-24 bg-[var(--color-navy)] border-2 border-[var(--color-accent)] rounded-full flex items-center justify-center overflow-hidden mb-3 shadow-lg group-hover:border-[var(--color-accent)]/80 transition-colors">
              {partido.local.escudo ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={partido.local.escudo}
                  alt={partido.local.nombre}
                  className="w-full h-full object-contain p-2"
                />
              ) : (
                <span className="text-lg text-white/60">?</span>
              )}
            </div>
            <div className="text-xl font-bold text-center text-white truncate max-w-[200px] mb-1">
              {partido.local.nombre}
            </div>
            {puntosLocal !== null && (
              <div className="text-sm text-[var(--color-accent)] font-bold mt-1 bg-[var(--color-navy)] px-3 py-1 rounded-full">
                {puntosLocal.toFixed(2)} pts
              </div>
            )}
          </Link>
        </div>

        {/* Marcador */}
        <div className="flex flex-col items-center flex-shrink-0 px-6">
          {partido.jugado && partido.goles_local !== null && partido.goles_visitante !== null ? (
            <div className="text-6xl font-extrabold text-white mb-2 font-[var(--font-title)]">
              {partido.goles_local} - {partido.goles_visitante}
            </div>
          ) : (
            <div className="text-3xl font-semibold text-white/60 mb-2">
              VS
            </div>
          )}
          {partido.indice_intensidad !== null && (
            <div className="flex items-center gap-2 mt-2">
              <div className="text-xs text-white/60 font-semibold">
                Intensidad:
              </div>
              <div className="flex-1 w-24 h-2 bg-[var(--color-navy)] rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-warning)]"
                  style={{ width: `${partido.indice_intensidad}%` }}
                />
              </div>
              <div className="text-xs text-white/60 font-bold">
                {partido.indice_intensidad}/100
              </div>
            </div>
          )}
        </div>

        {/* Equipo Visitante */}
        <div className="flex flex-col items-center flex-1 min-w-0">
          <Link
            href={
              partido.visitante.slug
                ? `/${lang}/clubes/${partido.visitante.slug}`
                : `/${lang}/clubes/${partido.visitante.id}`
            }
            className="flex flex-col items-center hover:opacity-80 transition-opacity group"
          >
            <div className="w-24 h-24 bg-[var(--color-navy)] border-2 border-[var(--color-accent)] rounded-full flex items-center justify-center overflow-hidden mb-3 shadow-lg group-hover:border-[var(--color-accent)]/80 transition-colors">
              {partido.visitante.escudo ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={partido.visitante.escudo}
                  alt={partido.visitante.nombre}
                  className="w-full h-full object-contain p-2"
                />
              ) : (
                <span className="text-lg text-white/60">?</span>
              )}
            </div>
            <div className="text-xl font-bold text-center text-white truncate max-w-[200px] mb-1">
              {partido.visitante.nombre}
            </div>
            {puntosVisitante !== null && (
              <div className="text-sm text-[var(--color-accent)] font-bold mt-1 bg-[var(--color-navy)] px-3 py-1 rounded-full">
                {puntosVisitante.toFixed(2)} pts
              </div>
            )}
          </Link>
        </div>
      </div>

      {/* Información adicional en cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Fecha y hora */}
        {(fecha || hora) && (
          <div className="bg-[var(--color-navy)] rounded-lg p-4 border border-[var(--color-navy)]/50">
            <div className="text-xs font-semibold text-white/60 mb-2 uppercase tracking-wide">
              {dict?.partidos?.fecha_hora || "Fecha y hora"}
            </div>
            <div className="text-sm text-white font-medium">
              {fecha}
            </div>
            <div className="text-sm text-[var(--color-accent)] font-bold">
              {hora}
            </div>
          </div>
        )}

        {/* Jornada y grupo */}
        {partido.grupo && (
          <div className="bg-[var(--color-navy)] rounded-lg p-4 border border-[var(--color-navy)]/50">
            <div className="text-xs font-semibold text-white/60 mb-2 uppercase tracking-wide">
              {dict?.partidos?.jornada_grupo || "Jornada y grupo"}
            </div>
            <div className="text-sm text-white font-medium">
              Jornada {partido.jornada_numero}
            </div>
            {partido.grupo.competicion && (
              <Link
                href={
                  partido.grupo.competicion.slug && partido.grupo.slug
                    ? `/${lang}/competicion/${partido.grupo.competicion.slug}/${partido.grupo.slug}`
                    : `/${lang}/competicion/${partido.grupo.competicion.id}/${partido.grupo.id}`
                }
                className="text-sm text-[var(--color-accent)] hover:text-[var(--color-accent)]/80 transition-colors font-semibold"
              >
                {partido.grupo.nombre}
              </Link>
            )}
          </div>
        )}

        {/* Pabellón */}
        {partido.pabellon && (
          <div className="bg-[var(--color-navy)] rounded-lg p-4 border border-[var(--color-navy)]/50">
            <div className="text-xs font-semibold text-white/60 mb-2 uppercase tracking-wide">
              {dict?.partidos?.pabellon || "Pabellón"}
            </div>
            <div className="text-sm text-white font-medium">{partido.pabellon}</div>
          </div>
        )}

        {/* Árbitros */}
        {arbitros.length > 0 && (
          <div className="bg-[var(--color-navy)] rounded-lg p-4 border border-[var(--color-navy)]/50">
            <div className="text-xs font-semibold text-white/60 mb-2 uppercase tracking-wide">
              {dict?.partidos?.arbitros || "Árbitros"}
            </div>
            <div className="text-sm text-white font-medium space-y-1">
              {arbitros.map((arb, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <span>{arb.nombre}</span>
                  {arb.rol && (
                    <span className="text-xs text-white/60">({arb.rol})</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Botón para volver a partidos de la división */}
      {partido.grupo && partido.grupo.competicion && (
        <div className="pt-4 border-t border-[var(--color-navy)]">
          <Link
            href={`/${lang}/partidos?competicion_id=${partido.grupo.competicion.id}&grupo_id=${partido.grupo.id}&jornada=${partido.jornada_numero}`}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[var(--color-accent)] text-white rounded-lg hover:bg-[var(--color-accent)]/90 transition-all text-sm font-bold shadow-lg hover:shadow-xl"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            {dict?.partidos?.volver_partidos || "Volver a partidos de la división"}
          </Link>
        </div>
      )}
    </div>
  );
}
