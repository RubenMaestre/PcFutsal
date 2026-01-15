// /frontend/app/[lang]/rankings/goleadores/GoleadoresGlobalPageClient.tsx
"use client";

import React from "react";
import GlobalWeekSelector, { getWeekRangeFromTuesday } from "../../../../home_components/GlobalWeekSelector";
import { useGoleadoresGlobal } from "../../../../hooks/useGoleadoresGlobal";
import GoleadoresGlobalTable from "../../../../rankings_components/GoleadoresGlobalTable";
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

export default function GoleadoresGlobalPageClient({ lang, dict }: Props) {
  // Semanas y valor inicial = la más reciente
  const weeks = React.useMemo(() => generateWeeks("2025-09-10"), []);
  const [selectedWeekEnd, setSelectedWeekEnd] = React.useState<string>(() =>
    weeks.length > 0 ? weeks[0].end.toISOString().slice(0, 10) : ""
  );

  // ⚠️ Igual que en MVPGlobalPageClient: de momento ID fijo de temporada
  const temporadaId = 4; // cambia si tu temporada activa es otra

  // selectedWeekEnd es la fecha del MARTES (del GlobalWeekSelector)
  // Calculamos el rango completo miércoles 19:00 → martes 23:59:59
  const { from, to } = React.useMemo(() => {
    if (!selectedWeekEnd) {
      return { from: undefined, to: undefined };
    }

    // Usar la función helper que calcula correctamente miércoles-martes
    const { wed, tue } = getWeekRangeFromTuesday(selectedWeekEnd);

    // Formato YYYY-MM-DD para el backend (incluye toda la semana hasta el final del martes)
    const isoStart = wed.toISOString().slice(0, 10);
    const isoEnd = tue.toISOString().slice(0, 10);

    return { from: isoStart, to: isoEnd };
  }, [selectedWeekEnd]);

  // ========================================
  // LÓGICA OPTIMIZADA:
  // - GOLES TOTALES: todos los goles de la temporada
  // - GOLES SEMANA: goles de la semana seleccionada (si hay filtro)
  // - PUNTOS TOTALES: goles_total * coef_division * 3.1416 (redondeado)
  // ========================================
  
  // Una sola llamada al endpoint optimizado que devuelve todo
  const {
    data: rankingData,
    loading,
    error,
  } = useGoleadoresGlobal({
    from,  // Filtro de semana (opcional)
    to,    // Filtro de semana (opcional)
    temporadaId,
    top: 200,
  });

  const labels = dict?.goleadores_global_labels || {};

  // El endpoint optimizado ya devuelve todo fusionado y ordenado por puntos_total
  const rows = rankingData?.ranking_global ?? [];
  
  // Verificar si hay datos de semana para mostrar "—" cuando no hay
  const hasWeekData = !!from && (rankingData?.window?.matched_games ?? 0) > 0;
  const noWeekData = !!from && !hasWeekData;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-6">
      {/* FILTROS */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm font-semibold text-[var(--color-text-primary)]">
          {labels.title || "Ranking global de goleadores"}
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
      <GoleadoresGlobalTable
        dict={dict}
        loading={loading}
        error={error}
        data={rows}
        noWeekData={noWeekData}
        lang={lang}
      />

      {/* Mensajes extra */}
      {!loading && !error && rows.length === 0 && (
        <EmptyState dict={dict} type="rankings" variant="no_goals" />
      )}
      {error && (
        <EmptyState dict={dict} type="general" variant="error" />
      )}
    </div>
  );
}

