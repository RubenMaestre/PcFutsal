// /app/[lang]/jugadores/JugadoresPageClient.tsx
"use client";

import React from "react";
import CompetitionFilter from "../../../components/CompetitionFilter";
import HomeSectionCard from "../../../components/HomeSectionCard";
import { useJugadoresPorClub, type JugadorLite } from "../../../hooks/useJugadoresPorClub";
import { useClubesPorGrupo, type ClubLite } from "../../../hooks/useClubesPorGrupo";

type JugadoresPageClientProps = {
  dict: any;
  lang: "es" | "val" | "en" | "fr" | "it" | "pt" | "de";
  filterData?: any | null;
};

export default function JugadoresPageClient({
  dict,
  lang,
  filterData: filterDataFromSSR = null,
}: JugadoresPageClientProps) {
  const [selectedCompeticionId, setSelectedCompeticionId] =
    React.useState<number | null>(null);
  const [selectedGrupoId, setSelectedGrupoId] =
    React.useState<number | null>(null);
  const [selectedClubId, setSelectedClubId] =
    React.useState<number | null>(null);
  const [scope, setScope] = React.useState<"GLOBAL" | "COMPETICIONES">(
    "COMPETICIONES"
  );
  const [filterData, setFilterData] = React.useState<any>(
    filterDataFromSSR ?? null
  );

  // UI local
  const [search, setSearch] = React.useState("");
  const [sortBy, setSortBy] = React.useState<"name" | "goles" | "partidos">("name");
  const [compact, setCompact] = React.useState(false);

  // Obtener clubes del grupo seleccionado
  const { data: clubesData, loading: clubesLoading } = useClubesPorGrupo(
    selectedGrupoId,
    false
  );

  // Obtener jugadores: si hay club seleccionado, por club; si no, aleatorios
  // Si hay búsqueda, buscar en todos los jugadores (no solo en los aleatorios)
  const searchForApi = search.trim() || undefined;
  const { data: jugadoresData, loading: jugadoresLoading, error: jugadoresError } = 
    useJugadoresPorClub(selectedClubId, !selectedClubId && !searchForApi, searchForApi);

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

  // Resetear club seleccionado cuando cambia el grupo
  React.useEffect(() => {
    setSelectedClubId(null);
  }, [selectedGrupoId]);

  // -------- Helpers de UI --------
  const clubes: ClubLite[] = Array.isArray(clubesData?.results) ? clubesData.results : [];
  const jugadores: JugadorLite[] = Array.isArray(jugadoresData?.results) ? jugadoresData.results : [];

  // Si hay búsqueda, el filtrado ya se hace en el backend
  // Solo aplicamos ordenación local
  const filteredJugadores = React.useMemo(() => {
    let arr = [...jugadores];
    
    // Ordenación
    arr.sort((a, b) => {
      if (sortBy === "goles") {
        const ag = a.goles ?? -Infinity;
        const bg = b.goles ?? -Infinity;
        if (bg !== ag) return bg - ag; // desc
        return (a.nombre || "").localeCompare(b.nombre || "");
      }
      if (sortBy === "partidos") {
        const ap = a.partidos_jugados ?? -Infinity;
        const bp = b.partidos_jugados ?? -Infinity;
        if (bp !== ap) return bp - ap; // desc
        return (a.nombre || "").localeCompare(b.nombre || "");
      }
      // name (por defecto)
      const an = (a.nombre || "").toLowerCase();
      const bn = (b.nombre || "").toLowerCase();
      return an.localeCompare(bn);
    });
    return arr;
  }, [jugadores, sortBy]);

  // Resumen
  const summary = React.useMemo(() => {
    const count = jugadores.length;
    const totalGoles = jugadores.reduce((acc, j) => acc + (j.goles || 0), 0);
    const totalPartidos = jugadores.reduce((acc, j) => acc + (j.partidos_jugados || 0), 0);
    return { count, totalGoles, totalPartidos };
  }, [jugadores]);

  // -------- Render --------
  return (
    <main className="flex flex-col w-full text-[var(--color-text)] font-base">
      <CompetitionFilter
        dict={dict}
        data={filterData}
        scope={scope}
        setScope={setScope}
        selectedCompeticionId={selectedCompeticionId}
        setSelectedCompeticionId={(id: number | null) => {
          setSelectedCompeticionId(id);
          setSelectedGrupoId(null);
          setSelectedClubId(null);
        }}
        selectedGrupoId={selectedGrupoId}
        setSelectedGrupoId={(id: number | null) => {
          setSelectedGrupoId(id);
          setSelectedClubId(null);
        }}
        disableNavigation={true}
      />

      <div className="max-w-7xl mx-auto px-4 py-6 w-full space-y-4">
        {/* Selector de club (si hay grupo seleccionado) */}
        {selectedGrupoId && clubes.length > 0 && (
          <HomeSectionCard
            title={dict?.jugadores_page?.select_club || "Selecciona un club"}
            description={dict?.jugadores_page?.select_club_desc || "Elige un club para ver sus jugadores"}
          >
            {clubesLoading ? (
              <ClubesSkeleton />
            ) : (
              <ul className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                {clubes.map((club) => (
                  <li key={club.id}>
                    <button
                      onClick={() => setSelectedClubId(club.id)}
                      className={`w-full py-3 px-3 bg-white/5 rounded-xl border transition ${
                        selectedClubId === club.id
                          ? "border-[var(--brand)] bg-[var(--brand)]/10"
                          : "border-white/10 hover:border-white/30 hover:bg-white/10"
                      }`}
                    >
                      <div className="flex flex-col items-center gap-3">
                        <div className="w-14 h-14 rounded bg-[#111] border border-[var(--color-card)] flex items-center justify-center overflow-hidden">
                          {club.escudo_url ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img
                              src={club.escudo_url}
                              alt={club.nombre_oficial}
                              className="w-full h-full object-contain"
                              loading="lazy"
                            />
                          ) : (
                            <span className="text-[0.6rem] text-white/40">
                              {(club.nombre_corto || club.nombre_oficial)?.slice(0, 2)?.toUpperCase()}
                            </span>
                          )}
                        </div>
                        <span className="text-sm font-medium text-white text-center">
                          {club.nombre_corto || club.nombre_oficial}
                        </span>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </HomeSectionCard>
        )}

        {/* Listado de jugadores */}
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          {/* Resumen */}
          <div className="text-sm text-white/80">
            {jugadoresLoading ? (
              <span className="text-[var(--color-text-secondary)]">
                {dict?.jugadores_page?.loading || "Cargando…"}
              </span>
            ) : jugadoresError ? (
              <span className="text-[var(--color-error)]">
                {dict?.jugadores_page?.error || "Error al cargar los jugadores."}
              </span>
            ) : (
              <span>
                {selectedClubId == null && jugadoresData?.random && !jugadoresData?.search ? (
                  <span>
                    {dict?.jugadores_page?.random_players || "Jugadores destacados"} · {summary.count} {dict?.jugadores_page?.players || "jugadores"}
                  </span>
                ) : jugadoresData?.search ? (
                  <span>
                    {summary.count} {dict?.jugadores_page?.players || "jugadores"} {dict?.jugadores_page?.found_for || "encontrados para"} "{search}"
                  </span>
                ) : (
                  <>
                    {summary.count} {dict?.jugadores_page?.players || "jugadores"}
                    {summary.totalGoles > 0 ? (
                      <span className="text-white/60"> · {dict?.jugadores_page?.total_goals || "goles totales"}: {summary.totalGoles}</span>
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
              <option value="name">{dict?.jugadores_page?.sort_name || "Ordenar: Nombre"}</option>
              <option value="goles">{dict?.jugadores_page?.sort_goals || "Ordenar: Goles"}</option>
              <option value="partidos">{dict?.jugadores_page?.sort_matches || "Ordenar: Partidos"}</option>
            </select>

            <label className="flex items-center gap-2 text-xs text-white/80 bg-white/5 border border-white/10 rounded-lg px-3">
              <input
                type="checkbox"
                className="accent-[var(--brand)]"
                checked={compact}
                onChange={(e) => setCompact(e.target.checked)}
              />
              {dict?.jugadores_page?.compact || "Vista compacta"}
            </label>
          </div>
        </div>

        <HomeSectionCard
          title={
            selectedClubId
              ? dict?.jugadores_page?.title_club || "Jugadores del club"
              : jugadoresData?.search
              ? dict?.jugadores_page?.title_search || "Resultados de búsqueda"
              : dict?.jugadores_page?.title || "Jugadores"
          }
          description={
            jugadoresData?.search
              ? dict?.jugadores_page?.desc_search || `Resultados de búsqueda para "${search}" en la temporada actual.`
              : selectedClubId == null && jugadoresData?.random
              ? dict?.jugadores_page?.desc_random || "Jugadores destacados de todas las competiciones."
              : selectedClubId
              ? dict?.jugadores_page?.desc_club || "Listado de jugadores del club seleccionado."
              : dict?.jugadores_page?.desc || "Selecciona una división y un club para ver sus jugadores."
          }
        >
          {jugadoresLoading ? (
            <JugadoresSkeleton />
          ) : jugadoresError ? (
            <div className="text-xs text-[var(--color-error)]">
              {dict?.jugadores_page?.error || "Error al cargar los jugadores."}
            </div>
          ) : filteredJugadores.length === 0 ? (
            <div className="text-xs text-[var(--color-text-secondary)]">
              {dict?.jugadores_page?.no_data || "No hay jugadores disponibles."}
            </div>
          ) : (
            <ul
              className={`grid gap-3 ${
                compact
                  ? "grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5"
                  : "sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
              }`}
            >
              {filteredJugadores.map((jugador) => (
                <li key={jugador.id}>
                  <JugadorCard jugador={jugador} lang={lang} dict={dict} compact={compact} />
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

function ClubesSkeleton() {
  return (
    <ul className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <li key={i} className="py-3 px-3 bg-white/5 rounded-xl border border-white/10">
          <div className="w-14 h-14 rounded bg-white/10 animate-pulse mb-3" />
          <div className="h-3 w-32 bg-white/10 rounded mb-2 animate-pulse" />
        </li>
      ))}
    </ul>
  );
}

function JugadoresSkeleton() {
  return (
    <ul className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <li key={i} className="py-3 px-3 bg-white/5 rounded-xl border border-white/10">
          <div className="w-14 h-14 rounded-full bg-white/10 animate-pulse mb-3" />
          <div className="h-3 w-32 bg-white/10 rounded mb-2 animate-pulse" />
          <div className="h-3 w-20 bg-white/10 rounded animate-pulse" />
        </li>
      ))}
    </ul>
  );
}

function JugadorCard({
  jugador,
  dict,
  lang,
  compact = false,
}: {
  jugador: JugadorLite;
  dict: any;
  lang: string;
  compact?: boolean;
}) {
  const nombre = jugador.apodo || jugador.nombre;
  // Usar slug si está disponible, sino usar ID
  const href = `/${lang}/jugadores/${jugador.slug || jugador.id}`;

  return (
    <a
      href={href}
      className={`block py-3 px-3 bg-white/5 rounded-xl border border-white/10 hover:border-white/30 hover:bg-white/10 transition`}
      aria-label={`${dict?.jugadores_page?.see_more || "ver jugador"}: ${nombre}`}
      rel="prefetch"
    >
      <div className="flex flex-col items-center gap-3">
        <div className="w-14 h-14 rounded-full bg-[#111] border border-[var(--color-card)] flex items-center justify-center overflow-hidden">
          {jugador.foto_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={jugador.foto_url}
              alt={nombre}
              className="w-full h-full object-cover"
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
          {jugador.club_nombre ? (
            <span className="text-xs text-white/60">{jugador.club_nombre}</span>
          ) : null}
          {jugador.posicion_principal ? (
            <span className="text-xs text-white/50">{jugador.posicion_principal}</span>
          ) : null}
        </div>

        {/* Mini-stats */}
        {(jugador.goles != null || jugador.partidos_jugados != null || jugador.edad_display != null) && (
          <div
            className={`flex flex-wrap items-center justify-center gap-2 ${
              compact ? "text-[10px]" : "text-[11px]"
            } text-white/80`}
          >
            {jugador.edad_display != null && (
              <Chip label={dict?.jugadores_page?.age || "EDAD"} value={jugador.edad_display} />
            )}
            {jugador.goles != null && jugador.goles > 0 && (
              <Chip label={dict?.jugadores_page?.goals || "GOLES"} value={jugador.goles} />
            )}
            {jugador.partidos_jugados != null && jugador.partidos_jugados > 0 && (
              <Chip label={dict?.jugadores_page?.matches || "PJ"} value={jugador.partidos_jugados} />
            )}
          </div>
        )}

        {/* CTA */}
        <div className="text-[0.65rem] uppercase tracking-wide text-brand-accent hover:underline">
          {dict?.jugadores_page?.see_more || "ver jugador"}
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


