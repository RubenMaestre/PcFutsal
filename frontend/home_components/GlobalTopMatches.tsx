"use client";

import React from "react";
import Link from "next/link";
import { getWeekRangeFromTuesday } from "./GlobalWeekSelector";
import EmptyState from "../components/EmptyState";

type ClubSide = {
  id: number | null;
  nombre: string;
  escudo: string;
  slug?: string | null;
  posicion?: number | null;
  coeficiente?: number | null;
  racha?: string | null;
  goles_temporada?: number | null;
  goles?: number | null; // marcador si jugado
};

type Resultado = {
  gl: number;
  gv: number;
  texto: string; // ej "3-2"
  ganador: "local" | "visitante" | "empate";
};

type GlobalMatch = {
  pk?: number;
  partido_id: string | number;
  identificador_federacion?: string | number | null;

  jornada?: number | null;
  jornada_numero?: number | null;

  fecha_hora: string | null;
  pabellon?: string | null;

  competicion_nombre?: string | null;
  grupo_nombre?: string | null;
  competicion_logo?: string | null; // <- si no viene, usamos el default

  jugado?: boolean | null;
  estado?: "finalizado" | "programado" | null;
  resultado?: Resultado | null;
  arbitros?: string[];

  local: ClubSide;
  visitante: ClubSide;

  score: number;
  score_global?: number;
};

type ApiResponse = {
  temporada_id: number;
  window?: any;
  top_matches?: GlobalMatch[];
  ranking_partidos?: GlobalMatch[];
};

export type GlobalTopMatchesProps = {
  temporadaId: number | null;
  dict: any;
  weekend?: string | null; // YYYY-MM-DD
  top?: number; // por defecto 3
  lang?: string;
};

function capFirst(s: string) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

function formatDateTime(fecha_hora: string | null, locale: string = "es-ES") {
  if (!fecha_hora) return { fechaLinea: "", horaLinea: "" };
  try {
    const d = new Date(fecha_hora);
    const fechaStr = d.toLocaleDateString(locale, {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
    const horaStr = d.toLocaleTimeString(locale, {
      hour: "2-digit",
      minute: "2-digit",
    });
    return { fechaLinea: capFirst(fechaStr), horaLinea: `${horaStr}h` };
  } catch {
    return { fechaLinea: "", horaLinea: "" };
  }
}

function Shield({
  src,
  alt,
  size = 44,
}: {
  src?: string | null;
  alt: string;
  size?: number;
}) {
  return (
    <div
      className="bg-neutral-100 border border-neutral-300 rounded flex items-center justify-center overflow-hidden"
      style={{ width: size, height: size }}
    >
      {src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={src} alt={alt} className="w-full h-full object-contain" />
      ) : (
        <span className="text-[10px] text-neutral-500">?</span>
      )}
    </div>
  );
}

function isPlayed(match: GlobalMatch) {
  if (match.estado) return match.estado === "finalizado";
  if (typeof match.jugado === "boolean") return match.jugado;
  const glOk = typeof match?.local?.goles === "number";
  const gvOk = typeof match?.visitante?.goles === "number";
  return glOk && gvOk;
}

function getJornada(match: GlobalMatch): number | null {
  return (
    (typeof match.jornada === "number" ? match.jornada : null) ??
    (typeof match.jornada_numero === "number" ? match.jornada_numero : null)
  );
}

function matchUrl(match: GlobalMatch, lang: string = "es") {
  // Usar identificador_federacion si está disponible, sino usar partido_id o pk
  const id = match.identificador_federacion || match.partido_id || match.pk;
  return `/${lang}/partidos/${id}`;
}

function MatchMiniCard({
  match,
  highlight = false,
  dict,
  locale = "es-ES",
  lang = "es",
}: {
  match: GlobalMatch;
  highlight?: boolean;
  dict: any;
  locale?: string;
  lang?: string;
}) {
  const labels = dict?.home_matches_labels || {};
  const { fechaLinea, horaLinea } = formatDateTime(match.fecha_hora, locale);
  const jornada = getJornada(match);
  const played = isPlayed(match);
  const resultado = match.resultado ?? null;

  const frameBorder = highlight
    ? "border border-[var(--color-gold)]"
    : "border border-[var(--color-accent)]";

  const bottomClasses = highlight
    ? "bg-[var(--color-gold)] text-black"
    : "bg-[var(--color-accent)] text-white";

  const marcadorLocal =
    played && (resultado?.gl ?? match.local.goles) !== null
      ? (resultado?.gl ?? match.local.goles)!
      : null;

  const marcadorVisitante =
    played && (resultado?.gv ?? match.visitante.goles) !== null
      ? (resultado?.gv ?? match.visitante.goles)!
      : null;

  // LOGO POR DEFECTO
  const divisionLogoSrc = match.competicion_logo || "/ligas/tercera_xv.png";

  return (
    <div
      className={`rounded-xl overflow-hidden shadow-lg flex flex-col h-full ${frameBorder}`}
      style={
        highlight
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
              <Shield src={match.local.escudo} alt={match.local.nombre} size={44} />
              <div className="text-[11px] font-semibold text-center text-neutral-800 leading-tight mt-1 truncate max-w-[90px]">
                {match.local.nombre}
              </div>
            </Link>

            {marcadorLocal !== null && (
              <div
                className="text-[20px] leading-none font-extrabold text-[var(--color-navy)]"
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
                src={divisionLogoSrc}
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
              <Shield src={match.visitante.escudo} alt={match.visitante.nombre} size={44} />
              <div className="text-[11px] font-semibold text-center text-neutral-800 leading-tight mt-1 truncate max-w-[90px]">
                {match.visitante.nombre}
              </div>
            </Link>

            {marcadorVisitante !== null && (
              <div
                className="text-[20px] leading-none font-extrabold text-[var(--color-navy)]"
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
        className={`flex flex-col gap-2 px-4 py-3 text-[12px] leading-snug flex-1 ${bottomClasses}`}
      >
        {/* ⭐ etiqueta partido estrella (aquí va solo por “top 1”, no por endpoint jornada) */}
        {highlight ? (
          <div className="flex justify-center mb-1">
            <div className="flex items-center gap-2 bg-black/10 rounded-full px-3 py-1">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/iconos/estrella.png"
                alt={labels.star_match_label || "PARTIDO ESTRELLA DE LA JORNADA"}
                className="w-4 h-4"
              />
              <span className="text-[10px] font-semibold uppercase tracking-wide">
                {labels.star_match_label || dict?.match?.star_match_label || "PARTIDO ESTRELLA DE LA JORNADA"}
              </span>
            </div>
          </div>
        ) : null}

        {/* Competición · Grupo */}
        {(match.competicion_nombre || match.grupo_nombre) && (
          <div className="opacity-90">
            {[match.competicion_nombre, match.grupo_nombre]
              .filter(Boolean)
              .join(" · ")}
          </div>
        )}

        {/* Jornada */}
        {typeof getJornada(match) === "number" && (
          <div className="flex items-start gap-2 text-[11px] leading-tight opacity-90">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/iconos/calendario.png"
              alt={labels.matchday_label || dict?.match?.matchday_alt || "Jornada"}
              className="w-4 h-4 flex-shrink-0 mt-[1px]"
            />
            <div className="flex-1">
              {(labels.matchday_label || dict?.match?.matchday_alt || "Jornada") + " " + getJornada(match)}
            </div>
          </div>
        )}

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
        {Array.isArray(match.arbitros) && match.arbitros.length > 0 && (
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
        )}

        {/* Score relativo */}
        <div className="mt-1 text-[10px] opacity-80">
          {labels.field_interest_score || "Interés:"}{" "}
          {typeof match.score === "number" ? match.score.toFixed(3) : "—"}
        </div>

        {/* CTA: Ver ficha SOLO si jugado */}
        {isPlayed(match) && (
          <div className="mt-2 w-full flex justify-center">
            <a
              href={matchUrl(match, lang)}
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
              "
            >
              {labels.cta_match_sheet || "Ficha del partido"}
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default function GlobalTopMatches({
  temporadaId,
  dict,
  weekend = undefined,
  top = 3,
  lang = "es",
}: GlobalTopMatchesProps) {
  const labels = dict?.home_matches_labels || {};
  // Mapeo de idiomas a locales
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
  const [rows, setRows] = React.useState<GlobalMatch[] | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;

    async function run() {
      if (!temporadaId) {
        setRows(null);
        setLoading(false);
        setError(null);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        params.set("temporada_id", String(temporadaId));
        params.set("top", String(Math.max(3, top ?? 3)));
        
        // Si weekend está presente, interpretarlo como martes y calcular rango miércoles-martes
        if (weekend) {
          const { wed, tue } = getWeekRangeFromTuesday(weekend);
          params.set("date_from", wed.toISOString().slice(0, 10)); // YYYY-MM-DD
          params.set("date_to", tue.toISOString().slice(0, 10)); // YYYY-MM-DD
        }

        const res = await fetch(
          `/api/valoraciones/partidos-top-global/?${params.toString()}`,
          { cache: "no-store" }
        );

        if (!res.ok) {
          setRows([]);
          setError("Endpoint no disponible (partidos-top-global).");
          setLoading(false);
          return;
        }

        const json = (await res.json()) as ApiResponse;

        let list =
          (Array.isArray(json.top_matches) && json.top_matches) ||
          (Array.isArray(json.ranking_partidos) && json.ranking_partidos) ||
          [];

        // orden y recorte
        list = [...list]
          .sort(
            (a, b) =>
              (b.score_global ?? b.score ?? 0) -
              (a.score_global ?? a.score ?? 0)
          )
          .slice(0, top ?? 3);

        if (!cancelled) setRows(list);
      } catch (e: any) {
        if (!cancelled) setError(e?.message || "Error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [temporadaId, weekend, top]);

  // estados
  if (!temporadaId) {
    return (
      <div className="text-xs text-white/60">
        {labels.hint_select_group ||
          "Selecciona temporada para ver los mejores partidos."}
      </div>
    );
  }
  if (loading) {
    return <EmptyState dict={dict} type="home" variant="loading" />;
  }
  if (error && (!rows || rows.length === 0)) {
    return <EmptyState dict={dict} type="general" variant="error" customMessage={error} />;
  }
  if (!rows || rows.length === 0) {
    return <EmptyState dict={dict} type="home" variant="no_matches" />;
  }

  return (
    <section className="w-full">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {rows.map((m, idx) => (
          <MatchMiniCard
            key={`${m.pk ?? m.partido_id}`}
            match={m}
            dict={dict}
            highlight={idx === 0}
            locale={locale}
            lang={lang}
          />
        ))}
      </div>
    </section>
  );
}
