// components/ClasificacionShell.tsx
"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";
import CompetitionFilter from "./CompetitionFilter";
import HomeSectionCard from "./HomeSectionCard";
// este es tu componente que pinta la tabla con racha debajo
import FullClassificationTable from "./FullClassificationShell";
import ClasificacionEvolucionChart from "./ClasificacionEvolucionChart";
import { useClasificacionMultiScope } from "../hooks/useClasificacionMultiScope";

// 👇 añadimos esto para no depender de la ruta relativa
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es";

type ClasificacionShellProps = {
  dict: any;
  initialCompeticionId?: number | null;
  initialGrupoId?: number | null;
  // si viene del servidor, no hacemos fetch en cliente
  filterData?: any | null;
};

export default function ClasificacionShell({
  dict,
  initialCompeticionId = null,
  initialGrupoId = null,
  filterData: filterDataFromSSR = null,
}: ClasificacionShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const langFromPath =
    pathname?.split("/")[1] && pathname.split("/")[1].length <= 3
      ? pathname.split("/")[1]
      : "es";

  const [scope, setScope] = React.useState<"GLOBAL" | "COMPETICIONES">(
    "COMPETICIONES"
  );

  const [filterData, setFilterData] = React.useState<any>(
    filterDataFromSSR ?? null
  );

  const [selectedCompeticionId, setSelectedCompeticionId] =
    React.useState<number | null>(initialCompeticionId);
  const [selectedGrupoId, setSelectedGrupoId] =
    React.useState<number | null>(initialGrupoId);

  const [selectedJornada, setSelectedJornada] = React.useState<number | null>(
    null
  );

  // Estado para favorito y selección aleatoria
  const [isFavorite, setIsFavorite] = React.useState<boolean>(false);
  const [isRandom, setIsRandom] = React.useState<boolean>(false);

  // aquí guardamos las clasificaciones de la jornada anterior (para las flechas)
  const [prevDataByScope, setPrevDataByScope] = React.useState<{
    overall: any | null;
    home: any | null;
    away: any | null;
  }>({
    overall: null,
    home: null,
    away: null,
  });

  // Función para obtener favorito de localStorage
  const getFavoriteFromStorage = React.useCallback((): {
    competicionId: number;
    grupoId: number;
  } | null => {
    if (typeof window === "undefined") return null;
    try {
      const stored = localStorage.getItem("pcfutsal_clasificacion_favorite");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.competicionId && parsed.grupoId) {
          return {
            competicionId: parsed.competicionId,
            grupoId: parsed.grupoId,
          };
        }
      }
    } catch (e) {
      console.error("Error reading favorite from localStorage:", e);
    }
    return null;
  }, []);

  // Función para guardar favorito en localStorage
  const saveFavoriteToStorage = React.useCallback(
    (competicionId: number | null, grupoId: number | null) => {
      if (typeof window === "undefined") return;
      try {
        if (competicionId && grupoId) {
          localStorage.setItem(
            "pcfutsal_clasificacion_favorite",
            JSON.stringify({ competicionId, grupoId })
          );
          setIsFavorite(true);
          setIsRandom(false);
        } else {
          localStorage.removeItem("pcfutsal_clasificacion_favorite");
          setIsFavorite(false);
        }
      } catch (e) {
        console.error("Error saving favorite to localStorage:", e);
      }
    },
    []
  );

  // Función para seleccionar una clasificación aleatoria
  const selectRandomClassification = React.useCallback(() => {
    if (!filterData?.competiciones || filterData.competiciones.length === 0) {
      return;
    }

    // Recopilar todos los grupos disponibles
    const allGroups: Array<{ competicionId: number; grupoId: number }> = [];
    filterData.competiciones.forEach((comp: any) => {
      if (comp.grupos && Array.isArray(comp.grupos)) {
        comp.grupos.forEach((grupo: any) => {
          if (grupo.id) {
            allGroups.push({
              competicionId: comp.id,
              grupoId: grupo.id,
            });
          }
        });
      }
    });

    if (allGroups.length > 0) {
      const randomIndex = Math.floor(Math.random() * allGroups.length);
      const random = allGroups[randomIndex];
      setSelectedCompeticionId(random.competicionId);
      setSelectedGrupoId(random.grupoId);
      setIsRandom(true);
      setIsFavorite(false);
    }
  }, [filterData]);

  // Cargar favorito al inicio si no hay selección inicial
  React.useEffect(() => {
    if (initialGrupoId || initialCompeticionId) {
      // Si hay selección inicial, verificar si es favorito
      const favorite = getFavoriteFromStorage();
      if (
        favorite &&
        favorite.competicionId === initialCompeticionId &&
        favorite.grupoId === initialGrupoId
      ) {
        setIsFavorite(true);
        setIsRandom(false);
      } else {
        setIsFavorite(false);
        setIsRandom(false);
      }
      return;
    }

    // Si no hay selección inicial, intentar cargar favorito
    const favorite = getFavoriteFromStorage();
    if (favorite) {
      setSelectedCompeticionId(favorite.competicionId);
      setSelectedGrupoId(favorite.grupoId);
      setIsFavorite(true);
      setIsRandom(false);
    } else if (filterData?.competiciones) {
      // Si no hay favorito, seleccionar aleatoria
      selectRandomClassification();
    }
  }, [
    initialGrupoId,
    initialCompeticionId,
    getFavoriteFromStorage,
    selectRandomClassification,
    filterData,
  ]);

  // Actualizar estado de favorito cuando cambia la selección
  React.useEffect(() => {
    if (!selectedCompeticionId || !selectedGrupoId) {
      setIsFavorite(false);
      return;
    }

    const favorite = getFavoriteFromStorage();
    if (
      favorite &&
      favorite.competicionId === selectedCompeticionId &&
      favorite.grupoId === selectedGrupoId
    ) {
      setIsFavorite(true);
      setIsRandom(false);
    } else if (!isRandom) {
      setIsFavorite(false);
    }
  }, [selectedCompeticionId, selectedGrupoId, getFavoriteFromStorage, isRandom]);

  // ⬇️ SOLO si NO viene desde SSR, intentamos cargarlo en cliente
  React.useEffect(() => {
    if (filterDataFromSSR) return;
    let cancelled = false;

    async function loadFilter() {
      try {
        // 👇 aquí estaba el problema: antes era "/api/nucleo/filter-context/"
        const res = await fetch(
          `${API_BASE}/api/nucleo/filter-context/`,
          {
            cache: "no-store",
          }
        );
        const json = await res.json();
        if (!cancelled) setFilterData(json);
      } catch (err) {
        if (!cancelled)
          setFilterData({ temporada_activa: null, competiciones: [] });
      }
    }
    loadFilter();
    return () => {
      cancelled = true;
    };
  }, [filterDataFromSSR]);

  // traemos las 3 clasificaciones (overall, home, away)
  const {
    dataByScope,
    loadingScope,
    error,
    fetchScope,
    fetchSingleScope,
  } = useClasificacionMultiScope(selectedGrupoId, selectedJornada);

  const [tableScope, setTableScope] = React.useState<
    "overall" | "home" | "away"
  >("overall");

  // si cambia de grupo, reseteamos
  React.useEffect(() => {
    setSelectedJornada(null);
    setPrevDataByScope({ overall: null, home: null, away: null });
  }, [selectedGrupoId]);

  // si la API nos dice la jornada aplicada y nosotros no tenemos ninguna, la fijamos
  React.useEffect(() => {
    const overall = dataByScope["overall"];
    if (
      overall &&
      overall.jornada_aplicada &&
      (selectedJornada === null || selectedJornada === undefined)
    ) {
      setSelectedJornada(overall.jornada_aplicada);
    }
  }, [dataByScope, selectedJornada]);

  // traer también la jornada anterior para las flechitas
  React.useEffect(() => {
    (async () => {
      if (!selectedGrupoId) {
        setPrevDataByScope({ overall: null, home: null, away: null });
        return;
      }

      const currentOverall = dataByScope["overall"];
      if (
        currentOverall &&
        currentOverall.jornadas_disponibles &&
        currentOverall.jornada_aplicada
      ) {
        const actual = currentOverall.jornada_aplicada as number;
        const jornadas: number[] = currentOverall.jornadas_disponibles;
        const anterior = jornadas
          .filter((j) => j < actual)
          .sort((a, b) => b - a)[0];

        if (anterior) {
          const [prevOverall, prevHome, prevAway] = await Promise.all([
            fetchSingleScope("overall", anterior),
            fetchSingleScope("home", anterior),
            fetchSingleScope("away", anterior),
          ]);
          setPrevDataByScope({
            overall: prevOverall,
            home: prevHome,
            away: prevAway,
          });
        } else {
          setPrevDataByScope({ overall: null, home: null, away: null });
        }
      } else {
        setPrevDataByScope({ overall: null, home: null, away: null });
      }
    })();
  }, [dataByScope, selectedGrupoId, fetchSingleScope]);

  const handleTableScopeChange = (next: "overall" | "home" | "away") => {
    setTableScope(next);
    fetchScope(next, selectedJornada);
  };

  // ⬇️ datos actuales de la tabla (los del scope elegido)
  const currentData = dataByScope[tableScope];
  const prevData = prevDataByScope[tableScope];

  // ⬇️ normalización de racha (esto lo dejamos tal cual lo tenías ✅)
  const normalizedCurrentRows = React.useMemo(() => {
    if (!currentData || !Array.isArray(currentData.tabla)) return [];
    return currentData.tabla.map((row: any) => {
      const rawRacha =
        row.racha ||
        row.form ||
        row.streak ||
        row.ultimos_partidos ||
        row.ultimas_jornadas ||
        null;

      let finalRacha: string[] = [];

      if (Array.isArray(rawRacha)) {
        finalRacha = rawRacha.map((x) => String(x).toUpperCase());
      } else if (typeof rawRacha === "string" && rawRacha.trim() !== "") {
        finalRacha = rawRacha.trim().toUpperCase().split("");
      } else {
        finalRacha = [];
      }

      return {
        ...row,
        racha: finalRacha,
      };
    });
  }, [currentData]);

  const normalizedPrevRows = React.useMemo(() => {
    if (!prevData || !Array.isArray(prevData.tabla)) return null;
    return prevData.tabla.map((row: any) => {
      const rawRacha =
        row.racha ||
        row.form ||
        row.streak ||
        row.ultimos_partidos ||
        row.ultimas_jornadas ||
        null;

      let finalRacha: string[] = [];

      if (Array.isArray(rawRacha)) {
        finalRacha = rawRacha.map((x) => String(x).toUpperCase());
      } else if (typeof rawRacha === "string" && rawRacha.trim() !== "") {
        finalRacha = rawRacha.trim().toUpperCase().split("");
      } else {
        finalRacha = [];
      }

      return {
        ...row,
        racha: finalRacha,
      };
    });
  }, [prevData]);

  const handleFilterSelectionCompleted = (
    competicionSlug: string,
    grupoSlug: string
  ) => {
    router.push(
      `/${langFromPath}/clasificacion/${competicionSlug}/${grupoSlug}`
    );
  };

  // Handler para toggle de favorito
  const handleToggleFavorite = () => {
    if (isFavorite) {
      saveFavoriteToStorage(null, null);
    } else if (selectedCompeticionId && selectedGrupoId) {
      saveFavoriteToStorage(selectedCompeticionId, selectedGrupoId);
    }
  };

  return (
    <main className="flex flex-col w-full text-[var(--color-text)] font-base">
      <CompetitionFilter
        dict={dict}
        data={filterData}
        scope={scope}
        setScope={setScope}
        selectedCompeticionId={selectedCompeticionId}
        setSelectedCompeticionId={(compId) => {
          setSelectedCompeticionId(compId);
          setSelectedGrupoId(null);
          setIsRandom(false);
        }}
        selectedGrupoId={selectedGrupoId}
        setSelectedGrupoId={(gid) => {
          setSelectedGrupoId(gid);
          setTableScope("overall");
          setIsRandom(false);
        }}
        disableNavigation={true}
        onSelectionCompleted={handleFilterSelectionCompleted}
      />

      <div className="max-w-7xl mx-auto px-4 py-6 w-full">
        <HomeSectionCard
          title={dict?.home_table_labels?.title_full || "Clasificación completa"}
          description={
            dict?.home_table_labels?.desc_full ||
            "Todos los equipos del grupo con puntos, goles y racha."
          }
        >
          {/* Indicador de estado (aleatoria/favorita) y botón de favorito */}
          {selectedGrupoId && (
            <div className="mb-4 flex items-center justify-between gap-2 flex-wrap">
              <div className="flex items-center gap-2">
                {isRandom && (
                  <span className="text-xs text-white/60 italic">
                    {dict?.clasificacion?.random_selected ||
                      "Clasificación seleccionada aleatoriamente"}
                  </span>
                )}
                {isFavorite && !isRandom && (
                  <span className="text-xs text-white/60 italic">
                    {dict?.clasificacion?.favorite_selected ||
                      "Clasificación favorita"}
                  </span>
                )}
              </div>
              <button
                onClick={handleToggleFavorite}
                className={`
                  text-xs px-3 py-1.5 rounded-md transition-colors
                  ${
                    isFavorite
                      ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/30"
                      : "bg-brand-card text-white/60 border border-[var(--color-card)] hover:bg-brand-card/80"
                  }
                `}
                title={
                  isFavorite
                    ? dict?.clasificacion?.remove_favorite ||
                      "Quitar de favoritos"
                    : dict?.clasificacion?.set_as_favorite ||
                      "Marcar como favorita"
                }
              >
                {isFavorite ? "★" : "☆"}{" "}
                {isFavorite
                  ? dict?.clasificacion?.remove_favorite || "Quitar favorito"
                  : dict?.clasificacion?.set_as_favorite || "Marcar favorito"}
              </button>
            </div>
          )}
          {selectedGrupoId == null ? (
            <div className="text-xs text-white/60">
              {dict.home_table_labels?.hint_select_group ||
                "Selecciona una competición y un grupo para ver la clasificación."}
            </div>
          ) : error ? (
            <div className="text-xs text-[var(--color-error)]">
              {dict.home_table_labels?.error ||
                "Error al cargar la clasificación."}
            </div>
          ) : (
            <FullClassificationTable
              rows={normalizedCurrentRows}
              dict={dict}
              loading={loadingScope !== null && !currentData}
              scope={tableScope}
              setScope={handleTableScopeChange}
              jornadasDisponibles={currentData?.jornadas_disponibles || []}
              jornadaAplicada={currentData?.jornada_aplicada || null}
              selectedJornada={selectedJornada}
              onChangeJornada={(j) => {
                setSelectedJornada(j);
                fetchScope(tableScope, j);
              }}
              prevRows={normalizedPrevRows}
              lang={langFromPath}
            />
          )}
        </HomeSectionCard>

        {/* Gráfica de evolución de posiciones */}
        {selectedGrupoId && (
          <div className="mt-6">
            <ClasificacionEvolucionChart
              grupoId={selectedGrupoId}
              dict={dict}
              lang={langFromPath}
            />
          </div>
        )}
      </div>
    </main>
  );
}
