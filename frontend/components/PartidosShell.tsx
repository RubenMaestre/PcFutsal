// /components/PartidosShell.tsx
"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";
import CompetitionFilter from "./CompetitionFilter";
import PartidosList from "./PartidosList";
import GlobalWeekSelector, { getDefaultTuesday } from "../home_components/GlobalWeekSelector";
import { usePartidosList } from "../hooks/usePartidosList";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es";

type PartidosShellProps = {
  dict: any;
  initialCompeticionId?: number | null;
  initialGrupoId?: number | null;
  initialJornada?: number | null;
  filterData?: any | null;
  lang?: string;
};

export default function PartidosShell({
  dict,
  initialCompeticionId = null,
  initialGrupoId = null,
  initialJornada = null,
  filterData: filterDataFromSSR = null,
  lang = "es",
}: PartidosShellProps) {
  const router = useRouter();
  const pathname = usePathname();

  const [scope, setScope] = React.useState<"GLOBAL" | "COMPETICIONES">(
    "GLOBAL"
  );

  const [filterData, setFilterData] = React.useState<any>(
    filterDataFromSSR ?? null
  );

  const [selectedCompeticionId, setSelectedCompeticionId] =
    React.useState<number | null>(initialCompeticionId);
  const [selectedGrupoId, setSelectedGrupoId] =
    React.useState<number | null>(initialGrupoId);
  const [selectedJornada, setSelectedJornada] = React.useState<number | null>(
    initialJornada
  );
  
  // Estado para jornadas disponibles
  const [jornadasDisponibles, setJornadasDisponibles] = React.useState<number[]>([]);
  
  // Estado para semana seleccionada (GLOBAL) - por defecto la semana actual
  const [selectedWeek, setSelectedWeek] = React.useState<string>(getDefaultTuesday());

  // Valores por defecto: Tercera División (ID: 4) y Grupo XV (ID: 1)
  const DEFAULT_COMPETICION_ID = 4; // Tercera División
  const DEFAULT_GRUPO_ID = 1; // Grupo XV

  // Ref para rastrear si ya se establecieron los valores por defecto
  const hasDefaultSetRef = React.useRef<boolean>(false);
  
  // Obtener la última semana con resultados disponibles
  React.useEffect(() => {
    if (scope === "GLOBAL") {
      let cancelled = false;
      
      async function fetchLastWeek() {
        try {
          // Obtener partidos de la última semana para determinar qué semana tiene resultados
          const res = await fetch(
            `/api/partidos/lista/?scope=GLOBAL&random=true&limit=100`,
            { cache: "no-store" }
          );
          
          if (!res.ok) throw new Error("HTTP " + res.status);
          
          const json = await res.json();
          
          if (!cancelled && json.partidos && json.partidos.length > 0) {
            // Obtener la fecha más reciente de los partidos
            const fechas = json.partidos
              .map((p: any) => p.fecha_hora)
              .filter(Boolean)
              .map((f: string) => new Date(f))
              .sort((a: Date, b: Date) => b.getTime() - a.getTime());
            
            if (fechas.length > 0) {
              const fechaMasReciente = fechas[0];
              
              // Calcular el martes de esa semana usando la misma lógica que GlobalWeekSelector
              const getWednesdayOfWeek = (date: Date): Date => {
                const d = new Date(date);
                d.setHours(0, 0, 0, 0);
                const day = d.getDay();
                let daysToSubtract;
                
                if (day === 3) {
                  daysToSubtract = 0;
                } else if (day >= 4) {
                  daysToSubtract = day - 3;
                } else if (day === 0) {
                  daysToSubtract = 4;
                } else {
                  daysToSubtract = day + 4;
                }
                
                const wed = new Date(d);
                wed.setDate(d.getDate() - daysToSubtract);
                wed.setHours(0, 0, 0, 0);
                return wed;
              };
              
              const getTuesdayAfter = (wednesday: Date): Date => {
                const tuesday = new Date(wednesday);
                tuesday.setDate(wednesday.getDate() + 6);
                tuesday.setHours(23, 59, 59, 999);
                return tuesday;
              };
              
              const weekWed = getWednesdayOfWeek(fechaMasReciente);
              const tuesday = getTuesdayAfter(weekWed);
              
              if (!cancelled) {
                setSelectedWeek(tuesday.toISOString().slice(0, 10));
              }
            }
          }
        } catch (err) {
          // Si hay error, mantener el valor por defecto
          console.error("Error obteniendo última semana:", err);
        }
      }
      
      fetchLastWeek();
      return () => {
        cancelled = true;
      };
    }
  }, [scope]);


  // Cargar filter data si no viene de SSR y establecer valores por defecto
  React.useEffect(() => {
    if (filterDataFromSSR) {
      setFilterData(filterDataFromSSR);
      
      // Si no hay grupoId inicial y no hay selección, establecer valores por defecto (solo una vez)
      if (!initialGrupoId && !selectedCompeticionId && !selectedGrupoId && !hasDefaultSetRef.current && filterDataFromSSR?.competiciones?.length) {
        const tercera = filterDataFromSSR.competiciones.find((c: any) => c.id === DEFAULT_COMPETICION_ID);
        if (tercera) {
          const grupoXV = tercera.grupos?.find((g: any) => g.id === DEFAULT_GRUPO_ID);
          if (grupoXV) {
            setSelectedCompeticionId(DEFAULT_COMPETICION_ID);
            setSelectedGrupoId(DEFAULT_GRUPO_ID);
            hasDefaultSetRef.current = true;
          }
        }
      }
      return;
    }
    
    let cancelled = false;

    async function loadFilter() {
      try {
        const res = await fetch(`${API_BASE}/api/nucleo/filter-context/`, {
          method: "GET",
          cache: "no-store",
        });
        const json = await res.json();
        if (cancelled) return;
        setFilterData(json);

        // Si no hay grupoId inicial y no hay selección, establecer valores por defecto (solo una vez)
        if (!initialGrupoId && !selectedCompeticionId && !selectedGrupoId && !hasDefaultSetRef.current && json?.competiciones?.length) {
          const tercera = json.competiciones.find((c: any) => c.id === DEFAULT_COMPETICION_ID);
          if (tercera) {
            const grupoXV = tercera.grupos?.find((g: any) => g.id === DEFAULT_GRUPO_ID);
            if (grupoXV) {
              setSelectedCompeticionId(DEFAULT_COMPETICION_ID);
              setSelectedGrupoId(DEFAULT_GRUPO_ID);
              hasDefaultSetRef.current = true;
            }
          }
        }
      } catch (err) {
        if (!cancelled) {
          setFilterData({ temporada_activa: null, competiciones: [] });
        }
      }
    }

    loadFilter();
    return () => {
      cancelled = true;
    };
  }, [filterDataFromSSR, initialGrupoId]);

  // Obtener jornadas disponibles cuando se selecciona un grupo
  React.useEffect(() => {
    if (scope === "COMPETICIONES" && selectedGrupoId) {
      let cancelled = false;
      
      async function fetchJornadas() {
        try {
          const res = await fetch(
            `/api/estadisticas/resultados-jornada/?grupo_id=${selectedGrupoId}`,
            { cache: "no-store" }
          );
          if (!res.ok) throw new Error("HTTP " + res.status);
          
          const json = await res.json();
          if (!cancelled) {
            const jornadas = json.jornadas_disponibles || [];
            setJornadasDisponibles(jornadas);
            
            // Si no hay jornada seleccionada, usar la última jornada con resultados
            if (!selectedJornada && json.jornada !== null) {
              setSelectedJornada(json.jornada);
            }
          }
        } catch (err) {
          if (!cancelled) {
            setJornadasDisponibles([]);
          }
        }
      }
      
      fetchJornadas();
      return () => {
        cancelled = true;
      };
    } else {
      setJornadasDisponibles([]);
    }
  }, [scope, selectedGrupoId, selectedJornada]);

  // Establecer valores por defecto cuando se cambia a COMPETICIONES sin grupo
  React.useEffect(() => {
    if (scope === "COMPETICIONES" && !selectedGrupoId && filterData?.competiciones && filterData.competiciones.length > 0 && !hasDefaultSetRef.current) {
      // Buscar Tercera División y Grupo XV
      const tercera = filterData.competiciones.find((c: any) => c.id === DEFAULT_COMPETICION_ID);
      if (tercera) {
        const grupoXV = tercera.grupos?.find((g: any) => g.id === DEFAULT_GRUPO_ID);
        if (grupoXV) {
          setSelectedCompeticionId(DEFAULT_COMPETICION_ID);
          setSelectedGrupoId(DEFAULT_GRUPO_ID);
          hasDefaultSetRef.current = true;
        }
      }
    } else if (scope === "GLOBAL") {
      setSelectedCompeticionId(null);
      setSelectedGrupoId(null);
      setSelectedJornada(null);
      hasDefaultSetRef.current = false; // Reset para permitir establecer valores por defecto de nuevo
    }
  }, [scope, filterData, selectedGrupoId]);

  // Hook para obtener lista de partidos
  const { data, loading, error } = usePartidosList(
    scope,
    scope === "COMPETICIONES" ? selectedCompeticionId : null,
    scope === "COMPETICIONES" ? selectedGrupoId : null,
    scope === "COMPETICIONES" ? selectedJornada : null,
    scope === "GLOBAL" ? true : false, // random solo para GLOBAL
    12,
    scope === "GLOBAL" ? selectedWeek : null // semana para GLOBAL
  );

  const handleCompeticionChange = (compId: number | null) => {
    setSelectedCompeticionId(compId);
    if (!compId) {
      setSelectedGrupoId(null);
      setSelectedJornada(null);
      hasDefaultSetRef.current = false; // Reset para permitir establecer valores por defecto de nuevo
    } else {
      hasDefaultSetRef.current = true; // Marcar como inicializado al seleccionar manualmente
    }
  };

  const handleGrupoChange = (grupoId: number | null) => {
    setSelectedGrupoId(grupoId);
    // No resetear jornada aquí, se establecerá automáticamente cuando se carguen las jornadas disponibles
    if (grupoId) {
      hasDefaultSetRef.current = true; // Marcar como inicializado al seleccionar manualmente
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-6">
      {/* Filtros */}
      <div className="mb-6">
        <CompetitionFilter
          dict={dict}
          data={filterData}
          scope={scope}
          setScope={(newScope) => {
            setScope(newScope);
            // Cuando se cambia a GLOBAL, limpiar selecciones
            if (newScope === "GLOBAL") {
              setSelectedCompeticionId(null);
              setSelectedGrupoId(null);
              setSelectedJornada(null);
              hasDefaultSetRef.current = false; // Reset para permitir establecer valores por defecto de nuevo
            } else if (newScope === "COMPETICIONES") {
              // Cuando se cambia a COMPETICIONES, establecer valores por defecto si no hay selección
              if (!selectedCompeticionId && !selectedGrupoId && !hasDefaultSetRef.current && filterData?.competiciones?.length) {
                const tercera = filterData.competiciones.find((c: any) => c.id === DEFAULT_COMPETICION_ID);
                if (tercera) {
                  const grupoXV = tercera.grupos?.find((g: any) => g.id === DEFAULT_GRUPO_ID);
                  if (grupoXV) {
                    setSelectedCompeticionId(DEFAULT_COMPETICION_ID);
                    setSelectedGrupoId(DEFAULT_GRUPO_ID);
                    hasDefaultSetRef.current = true;
                  }
                }
              }
            }
          }}
          selectedCompeticionId={selectedCompeticionId}
          setSelectedCompeticionId={handleCompeticionChange}
          selectedGrupoId={selectedGrupoId}
          setSelectedGrupoId={handleGrupoChange}
          disableNavigation={true}
        />
        
        {/* Selector de semana para GLOBAL */}
        {scope === "GLOBAL" && selectedWeek && (
          <div className="mt-4">
            <GlobalWeekSelector
              selected={selectedWeek}
              onChange={setSelectedWeek}
              dict={dict}
              lang={lang}
            />
          </div>
        )}

        {/* Selector de jornada si hay grupo seleccionado */}
        {scope === "COMPETICIONES" && selectedGrupoId && filterData && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-white/60 mb-2">
              {dict?.filters?.jornada || "Jornada"}
            </label>
            <select
              value={selectedJornada || ""}
              onChange={(e) => {
                const jornada = e.target.value ? parseInt(e.target.value) : null;
                setSelectedJornada(jornada);
              }}
              className="w-full md:w-auto px-4 py-2 border border-[var(--color-accent)] rounded-md bg-brand-card text-white focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
            >
              <option value="">{dict?.filters?.todas_jornadas || "Todas las jornadas"}</option>
              {jornadasDisponibles.length > 0 ? (
                jornadasDisponibles.map((num) => (
                  <option key={num} value={num}>
                    {dict?.filters?.jornada || "Jornada"} {num}
                  </option>
                ))
              ) : (
                // Fallback si no hay jornadas disponibles todavía
                Array.from({ length: 30 }, (_, i) => i + 1).map((num) => (
                  <option key={num} value={num}>
                    {dict?.filters?.jornada || "Jornada"} {num}
                  </option>
                ))
              )}
            </select>
          </div>
        )}

      </div>

      {/* Lista de partidos */}
      <PartidosList
        partidos={data?.partidos || []}
        dict={dict}
        lang={lang}
        loading={loading}
        error={error}
      />
    </div>
  );
}

