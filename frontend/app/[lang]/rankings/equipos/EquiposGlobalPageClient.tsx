// /frontend/app/[lang]/rankings/equipos/EquiposGlobalPageClient.tsx
"use client";

import React from "react";
import GlobalWeekSelector from "../../../../home_components/GlobalWeekSelector";
import { useEquipoGlobal } from "../../../../hooks/useEquipoGlobal";
import EquipoGlobalTable from "../../../../rankings_components/EquipoGlobalTable";
import EmptyState from "../../../../components/EmptyState";

type Props = {
  lang: string;
  dict: any;
};

// ————————————————————————————————
// Helper para generar semanas (Miércoles → Domingo)
// ————————————————————————————————
type WeekOption = {
  num: number;
  start: Date;
  end: Date;
};

function generateWeeks(
  startSeason: string = "2025-09-10", // primera jornada (aprox)
  endSeason: string = new Date().toISOString().slice(0, 10)
): WeekOption[] {
  const start = new Date(startSeason);
  const end = new Date(endSeason);
  const weeks: WeekOption[] = [];
  let current = new Date(start);
  let weekNum = 1;

  while (current < end) {
    const wed = new Date(current);
    wed.setDate(current.getDate() + ((3 - current.getDay() + 7) % 7)); // miércoles
    const sun = new Date(wed);
    sun.setDate(wed.getDate() + 4); // domingo

    weeks.push({
      num: weekNum,
      start: wed,
      end: sun,
    });

    current.setDate(current.getDate() + 7);
    weekNum++;
  }

  // Más reciente primero
  return weeks.reverse();
}

export default function EquiposGlobalPageClient({ lang, dict }: Props) {
  // Semanas y valor inicial = la más reciente
  const weeks = React.useMemo(() => generateWeeks("2025-09-10"), []);
  const [selectedWeekEnd, setSelectedWeekEnd] = React.useState<string>(() =>
    weeks.length > 0 ? weeks[0].end.toISOString().slice(0, 10) : ""
  );

  // ⚠️ Igual que en MVPGlobalPageClient: de momento ID fijo de temporada
  const temporadaId = 4; // cambia si tu temporada activa es otra

  // A partir del "end" (domingo) calculamos "from" (miércoles)
  const { from, to } = React.useMemo(() => {
    if (!selectedWeekEnd) {
      return { from: undefined, to: undefined };
    }

    const endDate = new Date(selectedWeekEnd);
    const startDate = new Date(endDate);
    startDate.setDate(endDate.getDate() - 4); // miércoles = domingo - 4

    const isoStart = startDate.toISOString().slice(0, 10);
    const isoEnd = endDate.toISOString().slice(0, 10);

    return { from: isoStart, to: isoEnd };
  }, [selectedWeekEnd]);

  // ========================================
  // LÓGICA OPTIMIZADA:
  // - PTS TOTALES: siempre del sumatorio (endpoint optimizado lee de PuntosEquipoTotal)
  // - PTS SEMANA: de la semana seleccionada (endpoint optimizado lee de PuntosEquipoJornada)
  // ========================================
  
  // Una sola llamada al endpoint optimizado que devuelve:
  // - Puntos totales del sumatorio (siempre)
  // - Puntos semanales de la semana seleccionada (si hay filtro)
  const {
    data: rankingData,
    loading,
    error,
  } = useEquipoGlobal({
    from,  // Filtro de semana (opcional)
    to,    // Filtro de semana (opcional)
    temporadaId,
    top: 200,
    strict: !!from,
  });

  const labels = dict?.team_global_labels || {};

  // El endpoint optimizado ya devuelve todo fusionado:
  // - score_global: puntos totales del sumatorio (ACUMULADOS de todas las semanas)
  // - score/score_semana: puntos de la semana seleccionada (si hay filtro) o null
  const rows = rankingData?.ranking_global ?? [];
  
  // Verificar si hay datos de semana para mostrar "—" cuando no hay
  const hasWeekData = !!from && (rankingData?.window?.matched_games ?? 0) > 0;
  const noWeekData = !!from && !hasWeekData;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-6">
      {/* FILTROS */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm font-semibold text-[var(--color-text-primary)]">
          {labels.title || "Ranking global de equipos"}
        </div>

        {/* Selector de semana */}
        <GlobalWeekSelector
          selected={selectedWeekEnd}
          onChange={(v: string) => setSelectedWeekEnd(v)}
          dict={dict}
          lang={lang}
        />
      </div>

      {/* TABLA */}
      <EquipoGlobalTable
        dict={dict}
        loading={loading}
        error={error}
        data={rows}
        noWeekData={noWeekData}
      />

      {/* Mensajes extra */}
      {!loading && !error && rows.length === 0 && (
        <EmptyState dict={dict} type="rankings" variant="no_teams" />
      )}
      {error && (
        <EmptyState dict={dict} type="general" variant="error" />
      )}
    </div>
  );
}
