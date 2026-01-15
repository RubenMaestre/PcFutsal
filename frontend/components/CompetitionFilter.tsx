// /components/CompetitionFilter.tsx
"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";

type GrupoInfo = {
  id: number;
  nombre: string;
  slug?: string;
};

type CompeticionInfo = {
  id: number;
  nombre: string;
  slug?: string;
  tiene_grupos: boolean;
  grupos: GrupoInfo[];
};

type FilterData = {
  temporada_activa: {
    id: number;
    nombre: string;
  } | null;
  competiciones: CompeticionInfo[];
};

type CompetitionFilterProps = {
  dict: any;
  data: any;
  scope: "GLOBAL" | "COMPETICIONES";
  setScope: (v: "GLOBAL" | "COMPETICIONES") => void;
  selectedCompeticionId: number | null;
  setSelectedCompeticionId: (v: number | null) => void;
  selectedGrupoId: number | null;
  setSelectedGrupoId: (v: number | null) => void;
  disableNavigation?: boolean;
  onSelectionCompleted?: (competicionSlug: string, grupoSlug: string) => void;
};

export default function CompetitionFilter({
  dict,
  data,
  scope,
  setScope,
  selectedCompeticionId,
  setSelectedCompeticionId,
  selectedGrupoId,
  setSelectedGrupoId,
  disableNavigation = false,
  onSelectionCompleted,
}: CompetitionFilterProps) {
  const router = useRouter();
  const pathname = usePathname();

  // /es/... → lang = es
  const lang = React.useMemo(() => {
    const parts = pathname.split("/").filter(Boolean);
    return parts[0] || "es";
  }, [pathname]);

  // estamos en /es/clasificacion...
  const isClassificationPage = React.useMemo(() => {
    const parts = pathname.split("/").filter(Boolean);
    return parts[1] === "clasificacion";
  }, [pathname]);

  // 👇 nuevo: estamos en /es/mvp o en /es/competicion/mvp/...
  const isMVPPage = React.useMemo(() => {
    const parts = pathname.split("/").filter(Boolean);
    // casos:
    // /es/mvp              → parts = ["es","mvp"]
    // /es/competicion/mvp  → parts = ["es","competicion","mvp",...]
    if (parts[1] === "mvp") return true;
    if (parts[1] === "competicion" && parts[2] === "mvp") return true;
    return false;
  }, [pathname]);

  const f = dict?.filters || {};

  // 👇 si el padre me pasa algo, NO fetch
  const [internalData, setInternalData] = React.useState<any>(null);
  const [internalLoading, setInternalLoading] = React.useState(false);

  const extractRaw = (src: any) => {
    if (!src) return null;
    if (src.data) return src.data;
    return src;
  };

  const rawFromProp = extractRaw(data);

  React.useEffect(() => {
    if (rawFromProp) return;

    let cancelled = false;

    async function fetchFilter() {
      try {
        setInternalLoading(true);
        const res = await fetch("/api/nucleo/filter-context/", {
          cache: "no-store",
        });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const json = await res.json();
        if (!cancelled) setInternalData(json);
      } catch (err) {
        if (!cancelled) {
          setInternalData({
            temporada_activa: null,
            competiciones: [],
          });
        }
      } finally {
        if (!cancelled) setInternalLoading(false);
      }
    }

    fetchFilter();
    return () => {
      cancelled = true;
    };
  }, [rawFromProp]);

  const effectiveData = rawFromProp ?? extractRaw(internalData);

  const normalizedCompetitions: CompeticionInfo[] = React.useMemo(() => {
    if (!effectiveData) return [];
    if (Array.isArray(effectiveData.competiciones))
      return effectiveData.competiciones;
    if (Array.isArray(effectiveData.competitions))
      return effectiveData.competitions;
    if (Array.isArray(effectiveData.results)) return effectiveData.results;
    return [];
  }, [effectiveData]);

  const safeData: FilterData = {
    temporada_activa: effectiveData?.temporada_activa ?? null,
    competiciones: normalizedCompetitions,
  };

  const loading = internalLoading || !effectiveData;
  const hasCompetitions = safeData.competiciones.length > 0;

  const currentCompeticion = React.useMemo(() => {
    if (!hasCompetitions) return null;
    return (
      safeData.competiciones.find(
        (c) => c.id === selectedCompeticionId
      ) || null
    );
  }, [hasCompetitions, safeData, selectedCompeticionId]);

  // ───────────────────────────
  // handlers
  // ───────────────────────────
  const handleScopeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as "GLOBAL" | "COMPETICIONES";
    setScope(value);

    if (value === "GLOBAL") {
      setSelectedCompeticionId(null);
      setSelectedGrupoId(null);

      if (!disableNavigation) {
        if (isClassificationPage) {
          router.push(`/${lang}/clasificacion`);
        } else if (isMVPPage) {
          router.push(`/${lang}/mvp`);
        } else {
          router.push(`/${lang}`);
        }
      }
    }
  };

  const handleCompeticionChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const compId = e.target.value === "" ? null : Number(e.target.value);
    setSelectedCompeticionId(compId);
    setSelectedGrupoId(null);

    if (loading || !compId) return;

    const comp = safeData.competiciones.find((c) => c.id === compId);
    if (!comp) return;

    // 📍 caso CLASIFICACIÓN
    if (isClassificationPage && comp.slug && !disableNavigation) {
      router.push(`/${lang}/clasificacion/${comp.slug}`);
      return;
    }

    // 📍 caso MVP → NO vamos a la competición normal, esperamos al grupo
    if (isMVPPage) {
      // aquí no navegamos todavía, porque en MVP siempre queremos grupo
      return;
    }

    // 📍 caso normal (home / competicion)
    if (!comp.tiene_grupos && comp.slug && !disableNavigation) {
      router.push(`/${lang}/competicion/${comp.slug}`);
    }
  };

  const handleGrupoChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const grupoId = e.target.value === "" ? null : Number(e.target.value);
    setSelectedGrupoId(grupoId);

    if (!grupoId) return;
    if (!currentCompeticion) return;

    const grupo = currentCompeticion.grupos.find((g) => g.id === grupoId);
    if (!grupo?.slug || !currentCompeticion.slug) return;

    // 📍 caso CLASIFICACIÓN
    if (isClassificationPage && !disableNavigation) {
      router.push(
        `/${lang}/clasificacion/${currentCompeticion.slug}/${grupo.slug}`
      );
    }

    // 📍 caso MVP
    if (isMVPPage && !disableNavigation) {
      // primero avisamos al padre, por si quiere hacer algo
      if (onSelectionCompleted) {
        onSelectionCompleted(currentCompeticion.slug!, grupo.slug!);
      }
      // y luego navegamos a la ruta de MVP que definimos
      router.push(
        `/${lang}/competicion/mvp/${currentCompeticion.slug}/${grupo.slug}`
      );
      return;
    }

    // 📍 caso normal
    if (!isClassificationPage && !disableNavigation) {
      router.push(
        `/${lang}/competicion/${currentCompeticion.slug}/${grupo.slug}`
      );
    }

    // y aun así avisamos al padre
    if (onSelectionCompleted) {
      onSelectionCompleted(currentCompeticion.slug!, grupo.slug!);
    }
  };

  // ───────────────────────────
  // render
  // ───────────────────────────
  return (
    <section className="w-full bg-brand-bg border-b border-brand-card text-brand-text">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col gap-3 md:flex-row md:items-end md:justify-start">
        {/* IZQUIERDA */}
        <div className="flex flex-col gap-2">
          <div className="text-xs text-brand-dim uppercase tracking-wide">
            {(f.season_label || "Temporada") + " "}
            {safeData.temporada_activa?.nombre ?? ""}
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center gap-2">
            <label className="text-xs text-brand-dim sm:mr-2">
              {f.scope_label || "Ámbito"}
            </label>
            <select
              className="bg-brand-card text-brand-text px-3 py-2 rounded-md border border-brand-card focus:outline-none focus:ring-2 focus:ring-brand-accent text-sm"
              value={scope}
              onChange={handleScopeChange}
            >
              <option value="GLOBAL">{f.scope_global || "GLOBAL"}</option>
              <option value="COMPETICIONES">
                {f.scope_competitions || "COMPETICIONES"}
              </option>
            </select>
          </div>
        </div>

        {/* DERECHA */}
        <div className="flex flex-col md:flex-row md:items-end gap-3">
          {scope === "COMPETICIONES" && (
            <>
              {/* COMPETICIÓN */}
              <div className="flex flex-col gap-1">
                <label className="text-xs text-brand-dim">
                  {f.competition_label || "Competición"}
                </label>
                <select
                  className="bg-brand-card text-brand-text px-3 py-2 rounded-md border border-brand-card focus:outline-none focus:ring-2 focus:ring-brand-accent text-sm min-w-[200px]"
                  value={loading ? "" : selectedCompeticionId ?? ""}
                  onChange={handleCompeticionChange}
                  disabled={loading}
                >
                  {loading ? (
                    <option value="">
                      {f.loading_competitions || "Cargando competiciones..."}
                    </option>
                  ) : hasCompetitions ? (
                    <>
                      <option value="">
                        {f.placeholder_competition ||
                          "-- Selecciona competición --"}
                      </option>
                      {safeData.competiciones.map((comp) => (
                        <option key={comp.id} value={comp.id}>
                          {comp.nombre}
                        </option>
                      ))}
                    </>
                  ) : (
                    <option value="">
                      {f.no_competitions || "No hay competiciones"}
                    </option>
                  )}
                </select>
              </div>

              {/* GRUPO */}
              {!loading && currentCompeticion?.tiene_grupos && (
                <div className="flex flex-col gap-1">
                  <label className="text-xs text-brand-dim">
                    {f.group_label || "Grupo"}
                  </label>
                  <select
                    className="bg-brand-card text-brand-text px-3 py-2 rounded-md border border-brand-card focus:outline-none focus:ring-2 focus:ring-brand-accent text-sm min-w-[180px]"
                    value={selectedGrupoId ?? ""}
                    onChange={handleGrupoChange}
                  >
                    <option value="">
                      {f.placeholder_group || "-- Selecciona grupo --"}
                    </option>
                    {currentCompeticion.grupos.map((g) => (
                      <option key={g.id} value={g.id}>
                        {g.nombre}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </section>
  );
}
