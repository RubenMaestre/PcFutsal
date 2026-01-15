// /app/[lang]/clubes/ClubsPageClient.tsx
"use client";

import React from "react";
import CompetitionFilter from "../../../components/CompetitionFilter";
import HomeSectionCard from "../../../components/HomeSectionCard";
import { useClubesPorGrupo } from "../../../hooks/useClubesPorGrupo";

type ClubsPageClientProps = {
  dict: any;
  lang: "es" | "val" | "en" | "fr" | "it" | "pt" | "de";
  filterData?: any | null;
};

type ClubLite = {
  id: number;
  slug?: string | null; // Slug para URLs SEO-friendly (siempre debería estar presente)
  nombre_oficial: string;
  nombre_corto?: string;
  localidad?: string; // alias de ciudad
  escudo_url?: string;
  competicion_nombre?: string; // división a la que pertenece
  grupo_nombre?: string; // grupo al que pertenece

  // Mini-stats
  posicion_actual?: number | null;
  puntos?: number | null;
  diferencia_goles?: number | null;
  racha?: string; // ej. "VVEED"

  // 👉 añade estos dos:
  goles_favor?: number | null;
  goles_contra?: number | null;

  color_primario?: string;
  color_secundario?: string;
};

export default function ClubsPageClient({
  dict,
  lang,
  filterData: filterDataFromSSR = null,
}: ClubsPageClientProps) {
  const [selectedCompeticionId, setSelectedCompeticionId] =
    React.useState<number | null>(null);
  const [selectedGrupoId, setSelectedGrupoId] =
    React.useState<number | null>(null);
  const [scope, setScope] = React.useState<"GLOBAL" | "COMPETICIONES">(
    "COMPETICIONES"
  );
  const [filterData, setFilterData] = React.useState<any>(
    filterDataFromSSR ?? null
  );

  // UI local
  const [search, setSearch] = React.useState("");
  const [sortBy, setSortBy] = React.useState<"pos" | "pts" | "name">("pos");
  const [compact, setCompact] = React.useState(false);

  // Si hay búsqueda activa, necesitamos todos los clubes para buscar
  // Si no hay búsqueda, mostrar solo 20-30 aleatorios
  const hasSearch = (search || "").trim().length > 0;
  const shouldShowRandom = !selectedGrupoId && !hasSearch;
  
  // Cargar clubes aleatorios por defecto, o todos si hay búsqueda
  const { data: dataRandom, loading: loadingRandom, error: errorRandom } = useClubesPorGrupo(
    selectedGrupoId,
    shouldShowRandom  // random=true solo si no hay grupo y no hay búsqueda
  );
  
  // Cargar todos los clubes cuando hay búsqueda (para poder buscar entre todos)
  const { data: dataAll, loading: loadingAll, error: errorAll } = useClubesPorGrupo(
    selectedGrupoId,
    false  // Sin random, todos los de temporada activa
  );
  
  // Usar datos según si hay búsqueda o no
  const data = hasSearch ? dataAll : dataRandom;
  const loading = hasSearch ? loadingAll : loadingRandom;
  const error = hasSearch ? errorAll : errorRandom;

  // Cargar filter-context en cliente si no vino por SSR
  React.useEffect(() => {
    if (filterDataFromSSR) return;
    let cancelled = false;
    async function loadFilter() {
      try {
        const res = await fetch("/api/nucleo/filter-context/", { cache: "no-store" });
        const json = await res.json();
        if (!cancelled) setFilterData(json);
      } catch {
        if (!cancelled) setFilterData({ temporada_activa: null, competiciones: [] });
      }
    }
    loadFilter();
    return () => {
      cancelled = true;
    };
  }, [filterDataFromSSR]);

  // -------- Helpers de UI --------
  const clubs: ClubLite[] = Array.isArray(data?.results) ? data.results : [];

  const filtered = React.useMemo(() => {
    const q = (search || "").trim().toLowerCase();
    let arr = [...clubs];
    if (q) {
      arr = arr.filter((c) => {
        const name = (c.nombre_corto || c.nombre_oficial || "").toLowerCase();
        const loc = (c.localidad || "").toLowerCase();
        return name.includes(q) || loc.includes(q);
      });
    }
    // Ordenación
    arr.sort((a, b) => {
      if (sortBy === "name") {
        const an = (a.nombre_corto || a.nombre_oficial || "").toLowerCase();
        const bn = (b.nombre_corto || b.nombre_oficial || "").toLowerCase();
        return an.localeCompare(bn);
      }
      if (sortBy === "pts") {
        const ap = a.puntos ?? -Infinity;
        const bp = b.puntos ?? -Infinity;
        if (bp !== ap) return bp - ap; // desc
        return (a.posicion_actual ?? Infinity) - (b.posicion_actual ?? Infinity);
      }
      // pos (por defecto): asc
      const ap = a.posicion_actual ?? Infinity;
      const bp = b.posicion_actual ?? Infinity;
      if (ap !== bp) return ap - bp;
      return (b.puntos ?? -Infinity) - (a.puntos ?? -Infinity);
    });
    return arr;
  }, [clubs, search, sortBy]);

  // Resumen (si hay stats)
  const summary = React.useMemo(() => {
    const withPts = clubs.filter((c) => typeof c.puntos === "number");
    const count = clubs.length;
    const avg =
      withPts.length > 0
        ? (withPts.reduce((acc, c) => acc + (c.puntos as number), 0) / withPts.length).toFixed(1)
        : null;
    return { count, avgPts: avg };
  }, [clubs]);

  // -------- Render --------
  return (
    <main className="flex flex-col w-full text-white font-base">
      <CompetitionFilter
        dict={dict}
        data={filterData}
        scope={scope}
        setScope={(newScope: "GLOBAL" | "COMPETICIONES") => {
          setScope(newScope);
          if (newScope === "GLOBAL") {
            setSelectedCompeticionId(null);
            setSelectedGrupoId(null);
          }
        }}
        selectedCompeticionId={selectedCompeticionId}
        setSelectedCompeticionId={(id: number | null) => {
          setSelectedCompeticionId(id);
          setSelectedGrupoId(null);
        }}
        selectedGrupoId={selectedGrupoId}
        setSelectedGrupoId={setSelectedGrupoId}
        disableNavigation={true}
      />

      <div className="max-w-7xl mx-auto px-4 py-6 w-full space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          {/* Resumen del grupo */}
          <div className="text-sm text-white/80">
            {loading ? (
              <span className="text-white/60">
                {dict?.clubs_page?.loading || "Cargando…"}
              </span>
            ) : error ? (
              <span className="text-[var(--color-error)]">
                {dict?.clubs_page?.error || "Error al cargar los clubes."}
              </span>
            ) : (
              <span>
                {selectedGrupoId == null && data?.random ? (
                  <span>{dict?.clubs_page?.random_clubs || "Clubes destacados"} · {summary.count} {dict?.clubs_page?.clubs || "clubes"}</span>
                ) : (
                  <>
                    {summary.count} {dict?.clubs_page?.clubs || "clubes"}
                    {summary.avgPts !== null ? (
                      <span className="text-white/60"> · {dict?.clubs_page?.avg_points || "media puntos"}: {summary.avgPts}</span>
                    ) : null}
                  </>
                )}
              </span>
            )}
          </div>

          {/* Controles */}
          <div className="flex flex-wrap gap-2">
            <div className="relative">
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={dict?.common?.search || "Buscar…"}
                className="h-9 w-56 rounded-lg bg-white/5 border border-white/10 px-3 text-sm outline-none focus:border-white/30"
              />
              <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-xs text-white/40">⌘K</span>
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="h-9 rounded-lg bg-white/5 border border-white/10 px-3 text-sm outline-none focus:border-white/30"
            >
              <option value="pos">{dict?.clubs_page?.sort_pos || "Ordenar: Posición"}</option>
              <option value="pts">{dict?.clubs_page?.sort_pts || "Ordenar: Puntos"}</option>
              <option value="name">{dict?.clubs_page?.sort_name || "Ordenar: Nombre"}</option>
            </select>

            <label className="flex items-center gap-2 text-xs text-white/80 bg-white/5 border border-white/10 rounded-lg px-3">
              <input
                type="checkbox"
                className="accent-[var(--brand)]"
                checked={compact}
                onChange={(e) => setCompact(e.target.checked)}
              />
              {dict?.clubs_page?.compact || "Vista compacta"}
            </label>
          </div>
        </div>

        <HomeSectionCard
          title={dict?.clubs_page?.title || "Clubes del grupo"}
          description={
            selectedGrupoId == null && data?.random
              ? dict?.clubs_page?.desc_random || "Clubes destacados de todas las competiciones."
              : selectedGrupoId == null
              ? dict?.clubs_page?.desc_all || "Todos los clubes que participan en la temporada activa."
              : dict?.clubs_page?.desc ||
                "Listado de clubes de la competición / grupo seleccionado."
          }
        >
          {loading ? (
            <ClubsSkeleton />
          ) : error ? (
            <div className="text-xs text-[var(--color-error)]">
              {dict?.clubs_page?.error || "Error al cargar los clubes."}
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-xs text-white/60">
              {dict?.clubs_page?.no_data || "No hay clubes en este grupo."}
            </div>
          ) : (
            <ul
              className={`grid gap-3 ${
                compact
                  ? "grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5"
                  : "sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
              }`}
            >
              {filtered.map((club) => (
                <li key={club.id}>
                  <ClubCard club={club} lang={lang} dict={dict} compact={compact} />
                </li>
              ))}
            </ul>
          )}
        </HomeSectionCard>
      </div>
    </main>
  );
}

/* ---------- Subcomponentes ---------- */

function ClubsSkeleton() {
  return (
    <ul className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <li key={i} className="py-3 px-3 bg-white/5 rounded-xl border border-white/10">
          <div className="w-14 h-14 rounded bg-white/10 animate-pulse mb-3" />
          <div className="h-3 w-32 bg-white/10 rounded mb-2 animate-pulse" />
          <div className="h-3 w-20 bg-white/10 rounded animate-pulse" />
        </li>
      ))}
    </ul>
  );
}

function ClubCard({
  club,
  dict,
  lang,
  compact = false,
}: {
  club: ClubLite;
  dict: any;
  lang: string;
  compact?: boolean;
}) {
  const nombre = club.nombre_corto || club.nombre_oficial;
  // Siempre usar slug para SEO (mejor para SEO que usar ID numérico)
  // Si no tiene slug, debería generarse automáticamente en el backend
  const href = club.slug 
    ? `/${lang}/clubes/${club.slug}` 
    : `/${lang}/clubes/${club.id}`; // Fallback solo si no hay slug

  const haloStyle =
    club.color_primario
      ? { boxShadow: `0 0 0 1px ${club.color_primario}33 inset` }
      : {};

  const racha = formatRacha(club.racha || "", dict);

  return (
    <a
      href={href}
      className={`block py-3 px-3 bg-white/5 rounded-xl border border-white/10 hover:border-white/30 hover:bg-white/10 transition`}
      style={haloStyle}
      aria-label={`${dict?.clubs_page?.see_more || "ver club"}: ${nombre}`}
      rel="prefetch"
    >
      <div className="flex flex-col items-center gap-3">
        <div className="w-14 h-14 rounded bg-[#111] border border-[var(--color-card)] flex items-center justify-center overflow-hidden">
          {club.escudo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={club.escudo_url}
              alt={nombre}
              className="w-full h-full object-contain"
              loading="lazy"
            />
          ) : (
            <span className="text-[0.6rem] text-white/40">
              {nombre?.slice(0, 2)?.toUpperCase()}
            </span>
          )}
        </div>

        <div className="flex flex-col items-center text-center">
          <span className="text-sm font-medium text-white">{nombre}</span>
          {(club.competicion_nombre || club.grupo_nombre) ? (
            <span className="text-xs text-white/60">
              {[club.competicion_nombre, club.grupo_nombre].filter(Boolean).join(" · ")}
            </span>
          ) : null}
          {club.localidad ? (
            <span className="text-xs text-white/50">{club.localidad}</span>
          ) : null}
        </div>

        {/* Mini-stats (si están disponibles en la respuesta) */}
        {(club.posicion_actual != null ||
          club.puntos != null ||
          club.goles_favor != null ||
          club.goles_contra != null) && (
          <div
            className={`flex flex-wrap items-center justify-center gap-2 ${
              compact ? "text-[10px]" : "text-[11px]"
            } text-white/80`}
          >
            {club.posicion_actual != null && (
              <Chip label="POS" value={club.posicion_actual} />
            )}
            {club.puntos != null && <Chip label="PTS" value={club.puntos} />}
            {club.goles_favor != null && (
              <Chip label="GF" value={club.goles_favor} />
            )}
            {club.goles_contra != null && (
              <Chip label="GC" value={club.goles_contra} />
            )}
          </div>
        )}


        {/* Racha */}
        {racha.length > 0 && (
          <div className="flex items-center gap-1">
            {racha.map((r, idx) => (
              <span
                key={idx}
                title={r.full}
                className={`inline-flex items-center justify-center rounded w-5 h-5 text-[10px] font-semibold ${badgeColor(r.code)}`}
              >
                {r.code}
              </span>
            ))}
          </div>
        )}

        {/* CTA */}
        <div className="text-[0.65rem] uppercase tracking-wide text-brand-accent hover:underline">
          {dict?.clubs_page?.see_more || "ver club"}
        </div>
      </div>
    </a>
  );
}

function Chip({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-white/5 border border-white/10 px-2 py-0.5">
      <span className="text-white/50">{label}</span>
      <span className="text-white">{value}</span>
    </span>
  );
}

/* ---------- Utilidades ---------- */

function formatRacha(raw: string, dict?: any): { code: "V" | "E" | "D"; full: string }[] {
  const R = dict?.club_detail?.racha || {};
  const clean = (raw || "").toUpperCase().replace(/[^VED]/g, "");
  return clean.split("").map((c) => ({
    code: (c as any) === "V" ? "V" : (c as any) === "E" ? "E" : "D",
    full: c === "V" ? (R.victoria || "Victoria") : c === "E" ? (R.empate || "Empate") : (R.derrota || "Derrota"),
  }));
}

function badgeColor(code: "V" | "E" | "D") {
  if (code === "V") return "bg-green-600/20 text-green-300 border border-green-500/20";
  if (code === "E") return "bg-yellow-600/20 text-yellow-200 border border-yellow-500/20";
  return "bg-red-600/20 text-red-300 border border-red-500/20";
}
