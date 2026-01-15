// app/[lang]/rankings/mvp/MVPGlobalPageClient.tsx
"use client";

import React from "react";
import { useMVPGlobal } from "../../../../hooks/useMVPGlobal";
import { useMVPTop3 } from "../../../../hooks/useMVPTop3";
import MVPGlobalTable from "../../../../rankings_components/MVPGlobalTable";
import MVPPodium from "../../../../rankings_components/MVPPodium";
import GlobalWeekSelector from "../../../../home_components/GlobalWeekSelector";

type Props = {
  lang: string;
  dict: any;
};

// ————————————————————————————————
// Helper interno para generar semanas
// (misma lógica que en GlobalWeekSelector: Miércoles → Domingo)
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

  // más reciente primero
  return weeks.reverse();
}

export default function MVPGlobalPageClient({ lang, dict }: Props) {
  const [onlyPorteros, setOnlyPorteros] = React.useState(false);

  // Semanas y valor inicial = la más reciente
  const weeks = React.useMemo(() => generateWeeks("2025-09-10"), []);
  const [selectedWeekEnd, setSelectedWeekEnd] = React.useState<string>(() =>
    weeks.length > 0 ? weeks[0].end.toISOString().slice(0, 10) : ""
  );

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
  // - TOP 3: endpoint separado para los 3 primeros (más rápido)
  // - RESTO: endpoint normal empezando desde el 4º (offset=3)
  // ========================================
  
  // Top 3 para el podio
  const {
    data: top3Data,
    loading: loadingTop3,
    error: errorTop3,
  } = useMVPTop3({
    from,
    to,
    temporadaId: 4,
    onlyPorteros,
  });
  
  // Resto del ranking (desde el 4º en adelante)
  const {
    data: rankingData,
    loading,
    error,
  } = useMVPGlobal({
    from,
    to,
    temporadaId: 4,
    onlyPorteros,
    top: 100,
    strict: !!from,
    offset: 3, // Empezar desde el 4º jugador
  });

  const labels = dict?.mvp_labels || {};

  // El endpoint optimizado ya devuelve todo fusionado:
  // - puntos_global: puntos totales del sumatorio
  // - puntos/puntos_semana: puntos de la semana (si hay filtro) o null
  const rows = rankingData?.ranking_global ?? [];
  
  // Verificar si hay datos de semana para mostrar "—" cuando no hay
  const hasWeekData = !!from && (rankingData?.window?.matched_games ?? 0) > 0;
  const noWeekData = !!from && !hasWeekData;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-6">
      {/* FILTROS */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Filtro porteros */}
        <div className="flex gap-2">
          <button
            onClick={() => setOnlyPorteros(false)}
            className={`px-3 py-1 rounded-full text-xs ${
              !onlyPorteros
                ? "bg-[#A51B3D] text-white"
                : "bg-[#121212] text-[#B3B3B3]"
            }`}
          >
            {labels.filter_all || "Todos"}
          </button>
          <button
            onClick={() => setOnlyPorteros(true)}
            className={`px-3 py-1 rounded-full text-xs ${
              onlyPorteros
                ? "bg-[#A51B3D] text-white"
                : "bg-[#121212] text-[#B3B3B3]"
            }`}
          >
            {labels.filter_gk || "Porteros"}
          </button>
        </div>

        {/* Selector de semana */}
        <GlobalWeekSelector
          selected={selectedWeekEnd}
          onChange={(v: string) => setSelectedWeekEnd(v)}
          dict={dict}
          lang={lang}
        />
      </div>

      {/* PODIO - TOP 3 */}
      <MVPPodium
        top3={top3Data?.top3 || []}
        lang={lang}
        dict={dict}
      />

      {/* TABLA - DESDE EL 4º */}
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Resto del Ranking</h2>
        <MVPGlobalTable
          dict={dict}
          loading={loading}
          error={error}
          data={rows}
          noWeekData={noWeekData}
          lang={lang}
        />
      </div>

      {/* Info ventana: siempre mostramos la de la semana seleccionada */}
      {rankingData?.window && (
        <p className="text-xs text-white/50">
          {rankingData.window.effective_start
            ? `Ventana efectiva: ${rankingData.window.effective_start} → ${rankingData.window.effective_end}`
            : ""}
        </p>
      )}

      {/* Mensajes extra */}
      {!loading && !error && rows.length === 0 && (
        <div className="text-xs text-white/60">
          {labels.no_data || "No hay datos disponibles."}
        </div>
      )}
      {error && (
        <div className="text-xs text-red-500">
          {labels.error || "Error al cargar los datos."}
        </div>
      )}
    </div>
  );
}
