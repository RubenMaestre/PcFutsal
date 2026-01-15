// components/FullClassificationTable.tsx
"use client";

import React from "react";
import Link from "next/link";

type ApiRow = {
  club_id?: number;
  id?: number;
  nombre?: string;
  escudo?: string;
  slug?: string | null;
  puntos?: number;
  pj?: number;
  pg?: number;
  pe?: number;
  pp?: number;
  gf?: number;
  gc?: number;
  dg?: number;
  team_name?: string;
  badge?: string;
  logo?: string;
  pt?: number;
  points?: number;
  goles_favor?: number;
  goles_contra?: number;
  diferencia_goles?: number;
  puntos_casa?: number;
  puntos_fuera?: number;
  // 👇 nuevo
  racha?: string[];
};

type Props = {
  rows: ApiRow[] | undefined;
  dict: any;
  scope: "overall" | "home" | "away";
  setScope: (s: "overall" | "home" | "away") => void;
  loading: boolean;
  jornadasDisponibles: number[];
  jornadaAplicada: number | null;
  selectedJornada: number | null;
  onChangeJornada: (j: number | null) => void;
  prevRows?: ApiRow[] | null;
  lang?: string;
};

// Componente que muestra TODA la racha reciente de un equipo como puntos de colores.
// A diferencia de MiniClassificationTable que muestra solo 5, este muestra toda la racha.
// Cada punto es clickeable y puede tener un handler para navegar al partido correspondiente.
// Los colores indican: verde (V=Victoria), amarillo (E=Empate), rojo (D=Derrota).
function RachaDotsFull({
  racha,
  onClickDot,
  dict,
}: {
  racha?: string[];
  onClickDot?: (index: number, code: string) => void;
  dict?: any;
}) {
  if (!racha || !Array.isArray(racha) || racha.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {racha.map((res, idx) => {
        const code = (res || "").toUpperCase();

        // Mapeo de códigos de resultado a colores CSS variables.
        // Esto permite cambiar los colores globalmente desde el tema.
        let bgClass = "bg-[var(--color-error)]"; // derrota
        if (code === "V") {
          bgClass = "bg-[var(--color-success)]"; // victoria
        } else if (code === "E") {
          bgClass = "bg-[var(--color-warning)]"; // empate
        }

        return (
          <span
            key={idx}
            className={`inline-block w-2.5 h-2.5 rounded-full ${bgClass} cursor-pointer`}
            title={`${dict?.racha?.partido_prefix || "Partido"} ${idx + 1}: ${code}`}
            onClick={
              onClickDot ? () => onClickDot(idx, code) : undefined
            }
          />
        );
      })}
    </div>
  );
}

export default function FullClassificationTable({
  rows,
  dict,
  scope,
  setScope,
  loading,
  jornadasDisponibles,
  jornadaAplicada,
  selectedJornada,
  onChangeJornada,
  prevRows = null,
  lang = "es",
}: Props) {
  const labels = dict?.classification_labels || {};
  const noDataLabel = labels.no_data || "Sin datos disponibles";

  const [sortField, setSortField] = React.useState<
    "pos" | "nombre" | "pj" | "pg" | "pe" | "pp" | "gf" | "gc" | "dg" | "pts"
  >("pts");
  const [sortDir, setSortDir] = React.useState<"asc" | "desc">("desc");

  // 👇 normalizamos por si el backend cambia nombres
  const normalizedRows: ApiRow[] = rows || [];

  // ⬇️ variación respecto a jornada anterior
  const prevPosByClub = React.useMemo(() => {
    if (!prevRows || prevRows.length === 0) return {};
    const normPrev = prevRows.map((raw) => {
      const clubKey = raw.club_id ?? raw.id;
      const nombre = raw.nombre || raw.team_name || "—";
      return {
        key: clubKey ?? nombre,
        club_id: clubKey,
        nombre,
      };
    });
    const m: Record<string | number, number> = {};
    normPrev.forEach((r, idx) => {
      if (r.club_id) {
        m[r.club_id] = idx + 1;
      } else {
        m[r.key] = idx + 1;
      }
    });
    return m;
  }, [prevRows]);

  // si el backend nos dice una jornada y no hay seleccionada, la fijamos
  React.useEffect(() => {
    if (jornadaAplicada && !selectedJornada) {
      onChangeJornada(jornadaAplicada);
    }
  }, [jornadaAplicada, selectedJornada, onChangeJornada]);

  const handleSort = (
    field:
      | "pos"
      | "nombre"
      | "pj"
      | "pg"
      | "pe"
      | "pp"
      | "gf"
      | "gc"
      | "dg"
      | "pts"
  ) => {
    if (sortField === field) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      const defaultDir = field === "nombre" ? "asc" : "desc";
      setSortField(field);
      setSortDir(defaultDir);
    }
  };

  const sortIcon = (field: string) => {
    if (sortField !== field) return <span className="opacity-30">↕</span>;
    return sortDir === "asc" ? (
      <span className="opacity-80">▲</span>
    ) : (
      <span className="opacity-80">▼</span>
    );
  };

  const sortedRows = React.useMemo(() => {
    const base = (normalizedRows || []).map((raw) => {
      const nombre = raw.nombre || raw.team_name || "—";
      const escudo = raw.escudo || raw.badge || raw.logo || "";
      const pj = raw.pj ?? 0;
      const pg = raw.pg ?? 0;
      const pe = raw.pe ?? 0;
      const pp = raw.pp ?? 0;
      const gf = raw.gf ?? raw.goles_favor ?? 0;
      const gc = raw.gc ?? raw.goles_contra ?? 0;
      const dg = raw.dg ?? raw.diferencia_goles ?? gf - gc;

      let pts: number;
      if (scope === "overall") {
        pts = raw.puntos ?? raw.pt ?? raw.points ?? pg * 3 + pe;
      } else if (scope === "home") {
        pts = raw.puntos_casa ?? pg * 3 + pe;
      } else {
        pts = raw.puntos_fuera ?? pg * 3 + pe;
      }

      return {
        key: raw.club_id ?? raw.id ?? nombre,
        club_id: raw.club_id ?? raw.id,
        nombre,
        escudo,
        slug: raw.slug || null,
        pj,
        pg,
        pe,
        pp,
        gf,
        gc,
        dg,
        pts,
        // 👇 guardamos la racha si viene
        racha: Array.isArray(raw.racha) ? raw.racha : undefined,
      };
    });

    return base.sort((a, b) => {
      let va: any;
      let vb: any;

      switch (sortField) {
        case "nombre":
          va = a.nombre.toLowerCase();
          vb = b.nombre.toLowerCase();
          break;
        case "pj":
          va = a.pj;
          vb = b.pj;
          break;
        case "pg":
          va = a.pg;
          vb = b.pg;
          break;
        case "pe":
          va = a.pe;
          vb = b.pe;
          break;
        case "pp":
          va = a.pp;
          vb = b.pp;
          break;
        case "gf":
          va = a.gf;
          vb = b.gf;
          break;
        case "gc":
          va = a.gc;
          vb = b.gc;
          break;
        case "dg":
          va = a.dg;
          vb = b.dg;
          break;
        case "pts":
        default:
          va = a.pts;
          vb = b.pts;
          break;
      }

      if (va < vb) return sortDir === "asc" ? -1 : 1;
      if (va > vb) return sortDir === "asc" ? 1 : -1;

      if (a.dg !== b.dg) {
        return sortDir === "asc" ? a.dg - b.dg : b.dg - a.dg;
      }

      return a.nombre.localeCompare(b.nombre);
    });
  }, [normalizedRows, scope, sortField, sortDir]);

  return (
    <section className="w-full text-brand-text font-base max-w-7xl mx-auto px-0 py-0">
      {/* encabezado + selector + botones */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-3">
        <h2 className="text-lg font-bold uppercase tracking-wide">
          {labels.title || "Clasificación completa"}
        </h2>

        <div className="flex items-center gap-2">
          {/* SELECT DE JORNADA */}
          {jornadasDisponibles && jornadasDisponibles.length > 0 ? (
            <select
              value={selectedJornada ?? ""}
              onChange={(e) => {
                const val = e.target.value;
                onChangeJornada(val ? Number(val) : null);
              }}
              className="bg-[var(--color-navy)] text-white border border-[var(--color-card)] text-sm rounded px-3 py-2 outline-none hover:bg-[var(--color-accent)] transition-colors duration-200"
            >
              {jornadasDisponibles.map((j) => (
                <option key={j} value={j}>
                  {labels.matchday_label
                    ? `${labels.matchday_label} ${j}`
                    : `Jornada ${j}`}
                </option>
              ))}
            </select>
          ) : null}

          {/* BOTONES scope */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setScope("overall")}
              className={`px-3 py-1 rounded-lg text-sm font-semibold transition ${
                scope === "overall"
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-card)] text-[var(--color-text-secondary)] hover:text-white"
              }`}
            >
              {labels.scope_overall || "General"}
            </button>
            <button
              type="button"
              onClick={() => setScope("home")}
              className={`px-3 py-1 rounded-lg text-sm font-semibold transition ${
                scope === "home"
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-card)] text-[var(--color-text-secondary)] hover:text-white"
              }`}
            >
              {labels.scope_home || "Casa"}
            </button>
            <button
              type="button"
              onClick={() => setScope("away")}
              className={`px-3 py-1 rounded-lg text-sm font-semibold transition ${
                scope === "away"
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-card)] text-[var(--color-text-secondary)] hover:text-white"
              }`}
            >
              {labels.scope_away || "Fuera"}
            </button>
          </div>
        </div>
      </div>

      {/* tabla */}
      <div className="overflow-x-auto border border-brand-card rounded-lg">
        <table
          className={`min-w-full text-sm text-center transition-opacity ${
            loading ? "opacity-75" : "opacity-100"
          }`}
        >
          <thead className="bg-[var(--color-card)]/40 text-xs uppercase">
            <tr>
              <th className="py-3 px-4 text-left w-10">#</th>
              {prevRows && prevRows.length > 0 ? (
                <th className="py-3 px-2 w-8"></th>
              ) : null}
              <th
                className="py-3 px-4 text-left cursor-pointer"
                onClick={() => handleSort("nombre")}
              >
                {labels.col_team || "Equipo"} {sortIcon("nombre")}
              </th>
              <th
                className="py-3 px-2 cursor-pointer"
                onClick={() => handleSort("pj")}
              >
                PJ {sortIcon("pj")}
              </th>
              <th
                className="py-3 px-2 cursor-pointer"
                onClick={() => handleSort("pg")}
              >
                PG {sortIcon("pg")}
              </th>
              <th
                className="py-3 px-2 cursor-pointer"
                onClick={() => handleSort("pe")}
              >
                PE {sortIcon("pe")}
              </th>
              <th
                className="py-3 px-2 cursor-pointer"
                onClick={() => handleSort("pp")}
              >
                PP {sortIcon("pp")}
              </th>
              <th
                className="py-3 px-2 cursor-pointer"
                onClick={() => handleSort("gf")}
              >
                GF {sortIcon("gf")}
              </th>
              <th
                className="py-3 px-2 cursor-pointer"
                onClick={() => handleSort("gc")}
              >
                GC {sortIcon("gc")}
              </th>
              <th
                className="py-3 px-2 cursor-pointer"
                onClick={() => handleSort("dg")}
              >
                DG {sortIcon("dg")}
              </th>
              <th
                className="py-3 px-3 cursor-pointer"
                onClick={() => handleSort("pts")}
              >
                PTS {sortIcon("pts")}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedRows.length === 0 ? (
              <tr>
                <td
                  colSpan={prevRows && prevRows.length > 0 ? 11 : 10}
                  className="py-6 text-center text-[var(--color-text-secondary)]"
                >
                  {noDataLabel}
                </td>
              </tr>
            ) : (
              sortedRows.map((row, idx) => {
                const currentPos = idx + 1;
                const clubKey = row.club_id ?? row.key;
                const prevPos = prevPosByClub[clubKey as any];

                let variation: "up" | "down" | "same" = "same";
                if (prevPos) {
                  if (currentPos < prevPos) variation = "up";
                  else if (currentPos > prevPos) variation = "down";
                  else variation = "same";
                }

                let iconSrc = "/iconos/mantiene.png";
                if (variation === "up") iconSrc = "/iconos/mejora.png";
                if (variation === "down") iconSrc = "/iconos/empeora.png";

                return (
                  <tr
                    key={row.key}
                    className="border-b"
                    style={{ borderColor: "rgba(179, 179, 179, 0.15)" }}
                  >
                    <td className="py-2 px-4 text-left">{currentPos}</td>
                    {prevRows && prevRows.length > 0 ? (
                      <td className="py-2 px-2 text-center">
                        <img
                          src={iconSrc}
                          alt={variation}
                          width={16}
                          height={16}
                          className="mx-auto"
                        />
                      </td>
                    ) : null}
                    <td className="py-2 px-4 text-left">
                      <Link
                        href={row.slug ? `/${lang}/clubes/${row.slug}` : `/${lang}/clubes/${row.club_id}`}
                        className="flex items-center gap-3 hover:text-brand-accent transition-colors"
                      >
                        {row.escudo ? (
                          <img
                            src={row.escudo}
                            alt={row.nombre}
                            className="w-7 h-7 rounded-full object-cover bg-white/10"
                          />
                        ) : (
                          <div className="w-7 h-7 rounded-full bg-white/10" />
                        )}

                        {/* nombre + racha */}
                        <div className="flex flex-col min-w-0">
                          <span className="truncate">{row.nombre}</span>

                          <RachaDotsFull
                            racha={row.racha}
                            dict={dict}
                            onClickDot={(index, code) => {
                              // FUTURO: router.push(`/partidos/${matchId}`)
                              console.log(
                                "Click racha",
                                index,
                                code,
                                "equipo:",
                                row.nombre
                              );
                            }}
                          />
                        </div>
                      </Link>
                    </td>
                    <td className="py-2 px-2">{row.pj}</td>
                    <td className="py-2 px-2">{row.pg}</td>
                    <td className="py-2 px-2">{row.pe}</td>
                    <td className="py-2 px-2">{row.pp}</td>
                    <td className="py-2 px-2">{row.gf}</td>
                    <td className="py-2 px-2">{row.gc}</td>
                    <td className="py-2 px-2">
                      <span
                        className={
                          row.dg > 0
                            ? "text-green-400"
                            : row.dg < 0
                            ? "text-red-400"
                            : ""
                        }
                      >
                        {row.dg}
                      </span>
                    </td>
                    <td className="py-2 px-3 font-semibold">{row.pts}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
