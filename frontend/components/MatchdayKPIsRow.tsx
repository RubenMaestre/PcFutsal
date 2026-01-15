// /frontend/components/MatchdayKPIsRow.tsx
"use client";

import React from "react";
import HomeSectionCard from "./HomeSectionCard";
import { useMatchdayKPIs } from "../hooks/useMatchdayKPIs";

export default function MatchdayKPIsRow({
  grupoId,
  jornada,
  dict,
}: {
  grupoId: number | null;
  jornada: number | null;
  dict: any;
}) {
  const { loading, error, data } = useMatchdayKPIs(grupoId, jornada);
  const labels = dict?.home_matchday_stats_labels || {};

  const renderBigNumber = (
    value: number | null | undefined,
    extraClasses?: string
  ) => (
    <div
      className={
        "text-2xl font-title font-bold leading-none " +
        (extraClasses || "")
      }
    >
      {typeof value === "number" ? value : "--"}
    </div>
  );

  // 🔄 actualizado: bloque centrado en columna
  const renderResultBlock = (
    label: string,
    value: number | null | undefined
  ) => (
    <div className="flex flex-col items-center justify-center text-center min-w-0">
      <span className="text-[11px] font-semibold uppercase tracking-wide text-[var(--color-text-secondary)]">
        {label}
      </span>
      <span
        className="text-xl font-title font-bold text-[var(--color-text)] leading-none mt-1"
        style={{
          fontFamily: "var(--font-title)",
        }}
      >
        {typeof value === "number" ? value : "--"}
      </span>
    </div>
  );

  //
  // ESTADOS ESPECIALES
  //

  // 1. Sin grupo seleccionado aún
  if (!grupoId) {
    return (
      <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 w-full">
          <HomeSectionCard
            title={labels.goals_card_title || "Goles jornada"}
            description={
              labels.goals_card_desc || "Total de goles en esta jornada"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.hint_select_group ||
                "Selecciona un grupo para ver las estadísticas de la jornada."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.yellows_card_title || "Amarillas"}
            description={
              labels.yellows_card_desc || "Tarjetas amarillas totales"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.hint_select_group ||
                "Selecciona un grupo para ver las estadísticas de la jornada."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.reds_card_title || "Rojas"}
            description={
              labels.reds_card_desc ||
              "Expulsiones directas / doble amarilla"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.hint_select_group ||
                "Selecciona un grupo para ver las estadísticas de la jornada."}
            </div>
          </HomeSectionCard>

          <div className="md:col-span-2">
            <HomeSectionCard
              title={labels.results_card_title || "Resultados jornada"}
              description={
                labels.results_card_desc ||
                "Balance local / empate / visitante"
              }
            >
              <div className="text-xs text-[var(--color-text-secondary)] font-base">
                {labels.hint_select_group ||
                  "Selecciona un grupo para ver las estadísticas de la jornada."}
              </div>
            </HomeSectionCard>
          </div>
        </div>
      </section>
    );
  }

  // 2. Cargando
  if (loading) {
    return (
      <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 w-full">
          <HomeSectionCard
            title={labels.goals_card_title || "Goles jornada"}
            description={
              labels.goals_card_desc || "Total de goles en esta jornada"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.loading || "Cargando estadísticas de la jornada..."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.yellows_card_title || "Amarillas"}
            description={
              labels.yellows_card_desc || "Tarjetas amarillas totales"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.loading || "Cargando estadísticas de la jornada..."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.reds_card_title || "Rojas"}
            description={
              labels.reds_card_desc ||
              "Expulsiones directas / doble amarilla"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.loading || "Cargando estadísticas de la jornada..."}
            </div>
          </HomeSectionCard>

          <div className="md:col-span-2">
            <HomeSectionCard
              title={labels.results_card_title || "Resultados jornada"}
              description={
                labels.results_card_desc ||
                "Balance local / empate / visitante"
              }
            >
              <div className="text-xs text-[var(--color-text-secondary)] font-base">
                {labels.loading || "Cargando estadísticas de la jornada..."}
              </div>
            </HomeSectionCard>
          </div>
        </div>
      </section>
    );
  }

  // 3. Error
  if (error) {
    return (
      <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 w-full">
          <HomeSectionCard
            title={labels.goals_card_title || "Goles jornada"}
            description={
              labels.goals_card_desc || "Total de goles en esta jornada"
            }
          >
            <div className="text-xs text-[var(--color-error,#7A0F2A)] font-base">
              {labels.error || "Error al cargar las estadísticas."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.yellows_card_title || "Amarillas"}
            description={
              labels.yellows_card_desc || "Tarjetas amarillas totales"
            }
          >
            <div className="text-xs text-[var(--color-error,#7A0F2A)] font-base">
              {labels.error || "Error al cargar las estadísticas."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.reds_card_title || "Rojas"}
            description={
              labels.reds_card_desc ||
              "Expulsiones directas / doble amarilla"
            }
          >
            <div className="text-xs text-[var(--color-error,#7A0F2A)] font-base">
              {labels.error || "Error al cargar las estadísticas."}
            </div>
          </HomeSectionCard>

          <div className="md:col-span-2">
            <HomeSectionCard
              title={labels.results_card_title || "Resultados jornada"}
              description={
                labels.results_card_desc ||
                "Balance local / empate / visitante"
              }
            >
              <div className="text-xs text-[var(--color-error,#7A0F2A)] font-base">
                {labels.error || "Error al cargar las estadísticas."}
              </div>
            </HomeSectionCard>
          </div>
        </div>
      </section>
    );
  }

  // 4. Sin datos todavía
  if (!data || !data.stats) {
    return (
      <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 w-full">
          <HomeSectionCard
            title={labels.goals_card_title || "Goles jornada"}
            description={
              labels.goals_card_desc || "Total de goles en esta jornada"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.no_data || "Sin datos de esta jornada todavía."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.yellows_card_title || "Amarillas"}
            description={
              labels.yellows_card_desc || "Tarjetas amarillas totales"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.no_data || "Sin datos de esta jornada todavía."}
            </div>
          </HomeSectionCard>

          <HomeSectionCard
            title={labels.reds_card_title || "Rojas"}
            description={
              labels.reds_card_desc ||
              "Expulsiones directas / doble amarilla"
            }
          >
            <div className="text-xs text-[var(--color-text-secondary)] font-base">
              {labels.no_data || "Sin datos de esta jornada todavía."}
            </div>
          </HomeSectionCard>

          <div className="md:col-span-2">
            <HomeSectionCard
              title={labels.results_card_title || "Resultados jornada"}
              description={
                labels.results_card_desc ||
                "Balance local / empate / visitante"
              }
            >
              <div className="text-xs text-[var(--color-text-secondary)] font-base">
                {labels.no_data || "Sin datos de esta jornada todavía."}
              </div>
            </HomeSectionCard>
          </div>
        </div>
      </section>
    );
  }

  //
  // 5. DATA OK ✅
  //
  const s = data.stats;

  return (
    <section className="w-full text-[var(--color-text)] font-base max-w-7xl mx-auto px-4 pb-6">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 w-full">
        {/* GOLES JORNADA */}
        <HomeSectionCard
          title={labels.goals_card_title || "Goles jornada"}
          description={
            labels.goals_card_desc || "Total de goles en esta jornada"
          }
        >
          {renderBigNumber(
            s.goles_totales,
            "text-[var(--color-success,#00C46A)]"
          )}
        </HomeSectionCard>

        {/* AMARILLAS */}
        <HomeSectionCard
          title={labels.yellows_card_title || "Amarillas"}
          description={
            labels.yellows_card_desc || "Tarjetas amarillas totales"
          }
        >
          {renderBigNumber(
            s.amarillas_totales,
            "text-[var(--color-warning,#FFD43B)]"
          )}
        </HomeSectionCard>

        {/* ROJAS */}
        <HomeSectionCard
          title={labels.reds_card_title || "Rojas"}
          description={
            labels.reds_card_desc ||
            "Expulsiones directas / doble amarilla"
          }
        >
          {renderBigNumber(
            s.rojas_totales,
            "text-[var(--color-error,#7A0F2A)]"
          )}
        </HomeSectionCard>

        {/* RESUMEN RESULTADOS */}
        <div className="md:col-span-2">
          <HomeSectionCard
            title={labels.results_card_title || "Resultados jornada"}
            description={
              labels.results_card_desc ||
              "Balance local / empate / visitante"
            }
          >
            {/* 🔄 aquí cambiamos el layout interno */}
            <div className="grid grid-cols-3 gap-4 text-center mt-2">
              {renderResultBlock(
                labels.home_wins_label || "Victorias local",
                s.victorias_local
              )}

              {renderResultBlock(
                labels.draws_label || "Empates",
                s.empates
              )}

              {renderResultBlock(
                labels.away_wins_label || "Victorias visitante",
                s.victorias_visitante
              )}
            </div>
          </HomeSectionCard>
        </div>
      </div>
    </section>
  );
}
