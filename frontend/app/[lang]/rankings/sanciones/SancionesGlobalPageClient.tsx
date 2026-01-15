// /frontend/app/[lang]/rankings/sanciones/SancionesGlobalPageClient.tsx
"use client";

import React from "react";
import GlobalWeekSelector, { getWeekRangeFromTuesday } from "../../../../home_components/GlobalWeekSelector";
import { useSancionesGlobal } from "../../../../hooks/useSancionesGlobal";
import SancionesGlobalTable from "../../../../rankings_components/SancionesGlobalTable";
import EmptyState from "../../../../components/EmptyState";

type Props = {
  lang: string;
  dict: any;
};

// ————————————————————————————————
// Helper para generar semanas (Miércoles → Martes)
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
    const tue = new Date(wed);
    tue.setDate(wed.getDate() + 6); // martes

    weeks.push({
      num: weekNum,
      start: wed,
      end: tue,
    });

    current.setDate(current.getDate() + 7);
    weekNum++;
  }

  // Más reciente primero
  return weeks.reverse();
}

export default function SancionesGlobalPageClient({ lang, dict }: Props) {
  // Semanas y valor inicial = la más reciente
  const weeks = React.useMemo(() => generateWeeks("2025-09-10"), []);
  const [selectedWeekEnd, setSelectedWeekEnd] = React.useState<string>(() =>
    weeks.length > 0 ? weeks[0].end.toISOString().slice(0, 10) : ""
  );

  // ⚠️ Igual que en otros rankings: de momento ID fijo de temporada
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
  // - SANCIONES TOTALES: todas las sanciones de la temporada
  // - SANCIONES SEMANA: sanciones de la semana seleccionada (si hay filtro)
  // - PUNTOS TOTALES: 5*rojas + 3*dobles_amarillas + 1*amarillas (sin coeficiente)
  // ========================================
  
  // Una sola llamada al endpoint optimizado que devuelve todo
  const {
    data: rankingData,
    loading,
    error,
  } = useSancionesGlobal({
    from,  // Filtro de semana (opcional)
    to,    // Filtro de semana (opcional)
    temporadaId,
    top: 200,
  });

  const labels = dict?.sanciones_global_labels || {};

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
          {labels.title || "Ranking global de sanciones"}
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
      <SancionesGlobalTable
        dict={dict}
        loading={loading}
        error={error}
        data={rows}
        noWeekData={noWeekData}
        lang={lang}
      />

      {/* Mensajes extra */}
      {!loading && !error && rows.length === 0 && (
        <EmptyState dict={dict} type="rankings" variant="no_sanctions" />
      )}
      {error && (
        <EmptyState dict={dict} type="general" variant="error" />
      )}
    </div>
  );
}




