"use client";

import React from "react";

import CompetitionFilter from "./CompetitionFilter";
import HomeSectionCard from "./HomeSectionCard";
import MiniClassificationTable from "./MiniClassificationTable";
import MatchDaySection from "./MatchDaySection";
import TopScorerOfMatchday from "./TopScorerOfMatchday";
import SeasonTopScorersImpact from "./SeasonTopScorersImpact";
import MatchdayKPIsRow from "./MatchdayKPIsRow";
import TeamGoalsTable from "./TeamGoalsTable";

import SancionesJornadaCard from "./SancionesJornadaCard";
import JugadoresMasSancionadosCard from "./JugadoresMasSancionadosCard";
import FairPlayEquiposCard from "./FairPlayEquiposCard";

import { useMiniClasificacion } from "../hooks/useMiniClasificacion";
import { useEquipoJornada } from "../hooks/useEquipoJornada";

import TeamOfMatchday from "./TeamOfMatchday";
import MVPOfMatchday from "./MVPOfMatchday";
import GoalkeeperOfMatchday from "./GoalkeeperOfMatchday";
import TopPlayersOfMatchday from "./TopPlayersOfMatchday";
import EmptyState from "./EmptyState";

export default function GroupShell({
  dict,
  grupoId,
  initialJornada = null,
  filterData: filterDataFromSSR = null,
  lang = "es",
}: {
  dict: any;
  grupoId: number;
  initialJornada?: number | null;
  filterData?: any | null;
  lang?: string;
}) {
  const [scope, setScope] = React.useState<"GLOBAL" | "COMPETICIONES">(
    "COMPETICIONES"
  );
  const [filterData, setFilterData] = React.useState<any>(
    filterDataFromSSR ?? null
  );

  // Valores por defecto: Tercera División (ID: 4) y Grupo XV (ID: 1)
  const DEFAULT_COMPETICION_ID = 4; // Tercera División
  const DEFAULT_GRUPO_ID = 1; // Grupo XV

  const [selectedCompeticionId, setSelectedCompeticionId] =
    React.useState<number | null>(null);
  const [selectedGrupoId, setSelectedGrupoId] =
    React.useState<number | null>(grupoId);
  const [selectedJornada, setSelectedJornada] = React.useState<number | null>(
    initialJornada
  );
  
  // Ref para rastrear si ya se establecieron los valores por defecto
  const hasDefaultSetRef = React.useRef<boolean>(false);

  // si no viene SSR pedimos el filter
  React.useEffect(() => {
    if (filterDataFromSSR) {
      setFilterData(filterDataFromSSR);
      
      // Si tenemos grupoId inicial, buscar la competición correspondiente
      if (grupoId && !selectedCompeticionId && filterDataFromSSR?.competiciones?.length) {
        for (const comp of filterDataFromSSR.competiciones) {
          const g = comp.grupos?.find((gg: any) => gg.id === grupoId);
          if (g) {
            setSelectedCompeticionId(comp.id);
            setSelectedGrupoId(g.id);
            return;
          }
        }
      }
      
      // Si no hay grupoId inicial y no hay selección, establecer valores por defecto (solo una vez)
      if (!grupoId && !selectedCompeticionId && !selectedGrupoId && !hasDefaultSetRef.current && filterDataFromSSR?.competiciones?.length) {
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
        const res = await fetch(`/api/nucleo/filter-context/`, {
          method: "GET",
          cache: "no-store",
        });
        const json = await res.json();
        if (cancelled) return;
        setFilterData(json);

        if (json?.competiciones?.length) {
          // Si tenemos grupoId inicial, buscar la competición correspondiente
          if (grupoId && !selectedCompeticionId) {
            for (const comp of json.competiciones) {
              const g = comp.grupos?.find((gg: any) => gg.id === grupoId);
              if (g) {
                setSelectedCompeticionId(comp.id);
                setSelectedGrupoId(g.id);
                return;
              }
            }
          }
          
          // Si no hay grupoId inicial y no hay selección, establecer valores por defecto (solo una vez)
          if (!grupoId && !selectedCompeticionId && !selectedGrupoId && !hasDefaultSetRef.current) {
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
  }, [filterDataFromSSR, grupoId]);

  // mini clasificación
  const {
    data: clasifData,
    loading: clasifLoading,
    error: clasifError,
  } = useMiniClasificacion(selectedGrupoId || grupoId);

  // equipo de la jornada
  const {
    data: equipoJornadaData,
    loading: equipoJornadaLoading,
    error: equipoJornadaError,
  } = useEquipoJornada(selectedGrupoId ?? grupoId, selectedJornada);

  const CompetitionContentGrid = (
    <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 py-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        {/* COLUMNA IZQUIERDA */}
        <div className="w-full">
          <HomeSectionCard>
            {clasifLoading ? (
              <EmptyState dict={dict} type="competicion" variant="loading" />
            ) : clasifError ? (
              <EmptyState dict={dict} type="general" variant="error" />
            ) : !clasifData || !Array.isArray(clasifData.tabla) || clasifData.tabla.length === 0 ? (
              <EmptyState dict={dict} type="competicion" variant="no_classification" />
            ) : (
              <MiniClassificationTable rows={clasifData.tabla} dict={dict} />
            )}
          </HomeSectionCard>
        </div>

        {/* COLUMNA DERECHA: SUBGRID */}
        <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* FILA 1 */}
          <HomeSectionCard
            title={dict.home?.player_of_the_week}
            description={dict.home?.player_of_the_week_desc}
          >
            <MVPOfMatchday
              grupoId={selectedGrupoId ?? grupoId}
              jornada={selectedJornada}
              dict={dict}
            />
          </HomeSectionCard>

          <HomeSectionCard
            title={dict.home?.top_scorer_of_the_week}
            description={dict.home?.top_scorer_of_the_week_desc}
          >
            <TopScorerOfMatchday
              grupoId={selectedGrupoId ?? grupoId}
              jornada={selectedJornada}
              dict={dict}
            />
          </HomeSectionCard>

          {/* FILA 2 → layout especial */}
          {/* Columna izq: portero + equipo */}
          <div className="flex flex-col gap-6 h-full">
            <HomeSectionCard
              title={
                dict.home?.goalkeeper_of_the_week || "Portero de la jornada"
              }
              description={
                dict.home?.goalkeeper_of_the_week_desc ||
                "Ni el WiFi pasa por su portería."
              }
            >
              <GoalkeeperOfMatchday
                grupoId={selectedGrupoId ?? grupoId}
                jornada={selectedJornada}
                dict={dict}
                lang={lang}
              />
            </HomeSectionCard>

            <HomeSectionCard
              title={dict.home?.team_of_the_week}
              description={dict.home?.team_of_the_week_desc}
            >
              <TeamOfMatchday
                grupoId={selectedGrupoId ?? grupoId}
                jornada={selectedJornada}
                dict={dict}
                hookData={{
                  data: equipoJornadaData,
                  loading: equipoJornadaLoading,
                  error: equipoJornadaError,
                }}
              />
            </HomeSectionCard>
          </div>

          {/* Columna dcha: destacados → ocupa toda la altura */}
          <div className="h-full">
            <HomeSectionCard
              title={dict.home?.highlight_players_matchday_title}
              description={dict.home?.highlight_players_matchday_desc}
            >
              <TopPlayersOfMatchday
                grupoId={selectedGrupoId ?? grupoId}
                jornada={selectedJornada}
                dict={dict}
                lang={dict?.lang || "es"}
              />
            </HomeSectionCard>
          </div>
        </div>
      </div>
    </section>
  );

  const CompetitionScorersAndTeamsRow = (
    <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        <HomeSectionCard
          title={dict.home?.goalscorers_title}
          description={dict.home?.goalscorers_desc}
        >
          <SeasonTopScorersImpact
            grupoId={selectedGrupoId ?? grupoId}
            dict={dict}
            lang={lang}
          />
        </HomeSectionCard>

        <HomeSectionCard
          title={dict.home?.team_goals_title || "Goles por equipo"}
          description={
            dict.home?.team_goals_desc || "Producción ofensiva total por club"
          }
        >
          <TeamGoalsTable
            grupoId={selectedGrupoId ?? grupoId}
            jornada={selectedJornada}
            dict={dict}
          />
        </HomeSectionCard>
      </div>
    </section>
  );

  const DisciplineRow = (
    <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        <HomeSectionCard
          title={dict.home?.suspended_title || "Sanciones jornada"}
          description={
            dict.home?.suspended_desc ||
            "Bajas por tarjeta roja o acumulación para la próxima jornada."
          }
        >
          <SancionesJornadaCard
            grupoId={selectedGrupoId ?? grupoId}
            jornada={selectedJornada}
            dict={{
              hint_select_group:
                dict.home_matchday_stats_labels?.hint_select_group ||
                "Selecciona un grupo para ver las estadísticas de la jornada.",
            }}
          />
        </HomeSectionCard>

        <HomeSectionCard
          title={dict?.most_booked?.title || "Jugadores más sancionados"}
          description={dict?.most_booked?.desc || "Ranking acumulado por puntos de sanción."}
        >
          <JugadoresMasSancionadosCard
            grupoId={selectedGrupoId ?? grupoId}
            dict={{
              hint_select_group:
                dict.home_matchday_stats_labels?.hint_select_group ||
                "Selecciona un grupo para ver las estadísticas de la jornada.",
            }}
            lang={lang}
          />
        </HomeSectionCard>

        <HomeSectionCard
          title={dict.home?.fair_play_title || "Deportividad equipos"}
          description={
            dict.home?.fair_play_desc ||
            "Fair play, disciplina, control emocional."
          }
        >
          <FairPlayEquiposCard
            grupoId={selectedGrupoId ?? grupoId}
            dict={{
              hint_select_group:
                dict.home_matchday_stats_labels?.hint_select_group ||
                "Selecciona un grupo para ver las estadísticas de la jornada.",
            }}
          />
        </HomeSectionCard>
      </div>
    </section>
  );

  return (
    <main className="flex flex-col w-full text-[var(--color-text)] font-base">
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
          }
        }}
        selectedCompeticionId={selectedCompeticionId}
        setSelectedCompeticionId={(compId) => {
          setSelectedCompeticionId(compId);
          if (!compId) {
            setSelectedGrupoId(null);
          }
        }}
        selectedGrupoId={selectedGrupoId}
        setSelectedGrupoId={(gid: number | null) => {
          setSelectedGrupoId(gid);
          setSelectedJornada(null);
        }}
      />

      <MatchDaySection
        grupoId={selectedGrupoId ?? grupoId}
        divisionLogoSrc="/ligas/tercera_xv.png"
        dict={dict}
        selectedJornada={selectedJornada}
        onChangeJornada={setSelectedJornada}
        lang={lang}
      />

      <>
        {CompetitionContentGrid}
        <MatchdayKPIsRow
          grupoId={selectedGrupoId ?? grupoId}
          jornada={selectedJornada}
          dict={dict}
        />
        {CompetitionScorersAndTeamsRow}
        {DisciplineRow}
      </>
    </main>
  );
}
