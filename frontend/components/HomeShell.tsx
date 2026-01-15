// /frontend/components/HomeShell.tsx
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

// 👇 componentes GLOBAL
import GlobalMVPCard from "../home_components/GlobalMVPCard";
import GlobalTeamCard from "../home_components/GlobalTeamCard";
import GlobalTopScorerCard from "../home_components/GlobalTopScorerCard";
import GlobalGoalkeepersList from "../home_components/GlobalGoalkeepersList";
import GlobalWeekSelector from "../home_components/GlobalWeekSelector";
import GlobalTopMatches from "../home_components/GlobalTopMatches";

export default function HomeShell({ dict, filterData, lang = "es" }: any) {
  const [scope, setScope] = React.useState<"GLOBAL" | "COMPETICIONES">("GLOBAL");

  const [selectedCompeticionId, setSelectedCompeticionId] =
    React.useState<number | null>(null);
  const [selectedGrupoId, setSelectedGrupoId] =
    React.useState<number | null>(null);

  const [selectedJornada, setSelectedJornada] = React.useState<number | null>(null);

  // Valores por defecto: Tercera División (ID: 4) y Grupo XV (ID: 1)
  const DEFAULT_COMPETICION_ID = 4; // Tercera División
  const DEFAULT_GRUPO_ID = 1; // Grupo XV

  // Ref para rastrear si ya se establecieron los valores por defecto
  const hasDefaultSetRef = React.useRef<boolean>(false);

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
      hasDefaultSetRef.current = false; // Reset para permitir establecer valores por defecto de nuevo
    }
  }, [scope, filterData, selectedGrupoId]);

  // Semana seleccionada (YYYY-MM-DD) — valor por defecto: martes de la semana más reciente disponible
  const [selectedWeekend, setSelectedWeekend] = React.useState<string>(() => {
    // Calcular el martes por defecto (semana más reciente disponible)
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const dayOfWeek = today.getDay();
    
    // Función auxiliar para obtener el miércoles de una semana
    const getWednesdayOfWeek = (date: Date): Date => {
      const d = new Date(date);
      d.setHours(0, 0, 0, 0);
      const dow = d.getDay();
      let daysToSubtract;
      if (dow === 3) {
        daysToSubtract = 0;
      } else if (dow > 3 || dow === 0) {
        daysToSubtract = dow === 0 ? 4 : dow - 3;
      } else {
        daysToSubtract = dow + 4;
      }
      d.setDate(d.getDate() - daysToSubtract);
      return d;
    };
    
    const currentWeekWed = getWednesdayOfWeek(today);
    let defaultTuesday: Date;
    
    if (dayOfWeek < 3) {
      // Hoy es domingo, lunes o martes -> semana pasada
      const prevWeekWed = new Date(currentWeekWed);
      prevWeekWed.setDate(prevWeekWed.getDate() - 7);
      defaultTuesday = new Date(prevWeekWed);
      defaultTuesday.setDate(prevWeekWed.getDate() + 6);
    } else {
      // Hoy es miércoles o después -> la semana actual ya ha comenzado, usar su martes
      defaultTuesday = new Date(currentWeekWed);
      defaultTuesday.setDate(currentWeekWed.getDate() + 6);
    }
    
    return defaultTuesday.toISOString().slice(0, 10);
  });

  // ————————————————————————————————————————
  // Contexto activo (global / competición / grupo)
  // ————————————————————————————————————————
  const activeContext = React.useMemo(() => {
    if (scope === "GLOBAL") {
      return { tipo: "GLOBAL" as const };
    }
    if (scope === "COMPETICIONES" && selectedCompeticionId && !selectedGrupoId) {
      return {
        tipo: "COMPETICION" as const,
        competicion_id: selectedCompeticionId,
      };
    }
    if (scope === "COMPETICIONES" && selectedCompeticionId && selectedGrupoId) {
      return {
        tipo: "GRUPO" as const,
        grupo_id: selectedGrupoId,
      };
    }
    return { tipo: "NONE" as const };
  }, [scope, selectedCompeticionId, selectedGrupoId]);

  const grupoIdForFetch =
    activeContext.tipo === "GRUPO" ? activeContext.grupo_id : null;

  // ————————————————————————————————————————
  // Temporada activa (para GLOBAL)
  // ————————————————————————————————————————
  const temporadaId: number | null =
    filterData?.temporada_activa?.id ??
    filterData?.data?.temporada_activa?.id ??
    null;

  // ————————————————————————————————————————
  // Mini clasificación (cuando hay grupo)
  // ————————————————————————————————————————
  const {
    data: clasifData,
    loading: clasifLoading,
    error: clasifError,
  } = useMiniClasificacion(grupoIdForFetch || null);

  // ————————————————————————————————————————
  // BLOQUE GLOBAL
  // ————————————————————————————————————————
  const GlobalGrid = (
    <>
      {/* Selector arriba a la derecha (solo global) */}
      <div className="max-w-7xl mx-auto px-4 pt-6 w-full flex justify-end">
        <GlobalWeekSelector selected={selectedWeekend} onChange={setSelectedWeekend} dict={dict} lang={lang} />
      </div>

      {/* Top 3 partidos de la semana (global) */}
      <div className="max-w-7xl mx-auto px-4 pb-4 w-full">
        <HomeSectionCard
          title={dict.home?.star_matches_of_the_week || "Partidos destacados de la semana"}
          description={
            dict.home?.star_matches_of_the_week_desc ||
            "Los 3 partidos más interesantes entre todas las divisiones"
          }
        >
          <GlobalTopMatches
            key={`gtm-${temporadaId}-${selectedWeekend}`}
            temporadaId={temporadaId}
            dict={dict}
            weekend={selectedWeekend}
            top={3}
            lang={lang}
          />
        </HomeSectionCard>
      </div>

      {/* Grid principal con MVP/Goleador/Equipo/Porteros */}
      <section className="grid gap-6 md:grid-cols-3 text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-6 w-full">
        {/* Columna 1: MVP GLOBAL */}
        <HomeSectionCard
          title={dict.home?.player_of_the_week}
          description={dict.home?.player_of_the_week_desc}
        >
          <GlobalMVPCard
            key={`gmvp-${temporadaId}-${selectedWeekend}`}
            temporadaId={temporadaId}
            dict={dict}
            weekend={selectedWeekend}
            lang={lang}
          />
        </HomeSectionCard>

        {/* Columna 2: GOLEADOR GLOBAL */}
        <HomeSectionCard
          title={dict.home?.top_scorer_of_the_week || "Goleador de la jornada"}
          description={
            dict.home?.top_scorer_of_the_week_desc ||
            "Máximo goleador ponderado por división"
          }
        >
          <GlobalTopScorerCard
            key={`gts-${temporadaId}-${selectedWeekend}`}
            temporadaId={temporadaId}
            dict={dict}
            weekend={selectedWeekend}
            lang={lang}
          />
        </HomeSectionCard>

        {/* Columna 3: grid con dos filas → Equipo (arriba) + Porteros (abajo) */}
        <div className="flex flex-col gap-6">
          <HomeSectionCard
            title={dict.home?.team_of_the_week}
            description={dict.home?.team_of_the_week_desc}
          >
            <GlobalTeamCard
              key={`gt-${temporadaId}-${selectedWeekend}`}
              temporadaId={temporadaId}
              dict={dict}
              lang={lang}
              weekend={selectedWeekend}
            />
          </HomeSectionCard>

          <HomeSectionCard
            title={dict.home?.goalkeepers_of_the_week || "Porteros de la jornada"}
            description={
              dict.home?.goalkeeper_of_the_week_desc ||
              "Top porteros ponderado por división"
            }
          >
            <GlobalGoalkeepersList
              key={`ggk-${temporadaId}-${selectedWeekend}`}
              temporadaId={temporadaId}
              dict={dict}
              top={5}
              weekend={selectedWeekend}
              lang={lang}
            />
          </HomeSectionCard>
        </div>
      </section>
    </>
  );

  // ————————————————————————————————————————
  // BLOQUE COMPETICIONES (cuando hay grupo)
  // ————————————————————————————————————————
  const CompetitionContentGrid = (
    <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 py-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        {/* IZQUIERDA: CLASIFICACIÓN */}
        <div className="w-full">
          <HomeSectionCard>
            {grupoIdForFetch == null ? (
              <div className="text-xs text-white/60">
                {dict.home_table_labels?.hint_select_group ||
                  "Selecciona un grupo para ver la clasificación"}
              </div>
            ) : clasifLoading ? (
              <EmptyState dict={dict} type="home" variant="loading" />
            ) : clasifError ? (
              <EmptyState dict={dict} type="general" variant="error" />
            ) : !clasifData || !Array.isArray(clasifData.tabla) || clasifData.tabla.length === 0 ? (
              <EmptyState dict={dict} type="home" variant="no_classification" />
            ) : (
              <MiniClassificationTable rows={clasifData.tabla} dict={dict} />
            )}
          </HomeSectionCard>
        </div>

        {/* DERECHA: SUBGRID */}
        <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* FILA 1 → MVP y GOLEADOR */}
          <HomeSectionCard
            title={dict.home?.player_of_the_week}
            description={dict.home?.player_of_the_week_desc}
          >
            <MVPOfMatchday
              grupoId={grupoIdForFetch ?? null}
              jornada={selectedJornada}
              dict={dict}
            />
          </HomeSectionCard>

          <HomeSectionCard
            title={dict.home?.top_scorer_of_the_week}
            description={dict.home?.top_scorer_of_the_week_desc}
          >
            <TopScorerOfMatchday
              grupoId={grupoIdForFetch ?? null}
              jornada={selectedJornada}
              dict={dict}
            />
          </HomeSectionCard>

          {/* FILA 2 LAYOUT ESPECIAL */}
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
                grupoId={grupoIdForFetch ?? null}
                jornada={selectedJornada}
                dict={dict}
              />
            </HomeSectionCard>

            <HomeSectionCard
              title={dict.home?.team_of_the_week}
              description={dict.home?.team_of_the_week_desc}
            >
              <TeamOfMatchday
                grupoId={grupoIdForFetch ?? null}
                jornada={selectedJornada}
                dict={dict}
                lang={lang}
                hookData={useEquipoJornada(
                  grupoIdForFetch ?? null,
                  selectedJornada
                )}
              />
            </HomeSectionCard>
          </div>

          {/* Columna dcha: destacados */}
          <div className="h-full">
            <HomeSectionCard
              title={dict.home?.highlight_players_matchday_title}
              description={dict.home?.highlight_players_matchday_desc}
            >
              <TopPlayersOfMatchday
                grupoId={grupoIdForFetch ?? null}
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
            grupoId={grupoIdForFetch ?? null}
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
            grupoId={grupoIdForFetch ?? null}
            jornada={selectedJornada}
            dict={dict}
            lang={lang}
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
            grupoId={grupoIdForFetch ?? null}
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
          description={"Ranking acumulado por puntos de sanción."}
        >
          <JugadoresMasSancionadosCard
            grupoId={grupoIdForFetch ?? null}
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
            grupoId={grupoIdForFetch ?? null}
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
      {/* FILTRO SUPERIOR */}
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
            hasDefaultSetRef.current = false; // Reset para permitir establecer valores por defecto de nuevo
          }
        }}
        selectedCompeticionId={selectedCompeticionId}
        setSelectedCompeticionId={(compId) => {
          setSelectedCompeticionId(compId);
          if (!compId) {
            setSelectedGrupoId(null);
            hasDefaultSetRef.current = false; // Reset para permitir establecer valores por defecto de nuevo
          } else {
            hasDefaultSetRef.current = true; // Marcar como inicializado al seleccionar manualmente
          }
        }}
        selectedGrupoId={selectedGrupoId}
        setSelectedGrupoId={(gid: number | null) => {
          setSelectedGrupoId(gid);
          setSelectedJornada(null);
          if (gid) {
            hasDefaultSetRef.current = true; // Marcar como inicializado al seleccionar manualmente
          }
        }}
      />

      {/* RESULTADOS JORNADA (solo en competiciones/grupos) */}
      {scope === "COMPETICIONES" && (
        <MatchDaySection
          grupoId={grupoIdForFetch ?? null}
          divisionLogoSrc="/ligas/tercera_xv.png"
          dict={dict}
          selectedJornada={selectedJornada}
          onChangeJornada={setSelectedJornada}
          lang={lang}
        />
      )}

      {/* CONTENIDO PRINCIPAL */}
      {scope === "GLOBAL" ? (
        GlobalGrid
      ) : (
        <>
          {CompetitionContentGrid}
          <MatchdayKPIsRow
            grupoId={grupoIdForFetch ?? null}
            jornada={selectedJornada}
            dict={dict}
          />
          {CompetitionScorersAndTeamsRow}
          {DisciplineRow}
        </>
      )}

      {/* CONTENIDO EDITORIAL - HOME */}
      {scope === "GLOBAL" && dict?.editorial?.home && (
        <section className="max-w-7xl mx-auto px-4 py-8 w-full">
          <div className="bg-brand-card border border-brand-card rounded-lg p-6 space-y-4">
            <h2 className="text-2xl font-bold text-brand-text">
              {dict.editorial.home.title || "¿Qué es PC FUTSAL?"}
            </h2>
            <div className="space-y-3 text-sm text-brand-textSecondary leading-relaxed">
              <p>{dict.editorial.home.paragraph1}</p>
              <p>{dict.editorial.home.paragraph2}</p>
              <p>{dict.editorial.home.paragraph3}</p>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
