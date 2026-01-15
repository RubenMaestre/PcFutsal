"use client";
import { useMemo } from "react";
import React from "react";

type WeekOption = {
  num: number;
  start: Date; // Miércoles
  end: Date; // Martes siguiente
  label: string;
  value: string; // fecha del martes en formato YYYY-MM-DD
};

function formatDate(d: Date, locale: string = "es-ES") {
  return d.toLocaleDateString(locale, { day: "2-digit", month: "short" });
}

/**
 * Obtiene el miércoles más reciente que ya pasó o es hoy.
 * La semana va de miércoles a martes.
 * Si hoy es lunes/martes, devuelve el miércoles de esta semana (que ya pasó).
 * Si hoy es miércoles o después, devuelve el miércoles de esta semana.
 */
function getWednesdayOfWeek(date: Date): Date {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  const dayOfWeek = d.getDay(); // 0 = domingo, 1 = lunes, ..., 3 = miércoles, ..., 6 = sábado
  
  let daysToSubtract;
  
  if (dayOfWeek === 3) {
    // Es miércoles, quedarnos en este miércoles
    daysToSubtract = 0;
  } else if (dayOfWeek >= 4) {
    // Es jueves (4), viernes (5) o sábado (6) -> retroceder al miércoles de esta semana
    daysToSubtract = dayOfWeek - 3;
  } else if (dayOfWeek === 0) {
    // Es domingo -> retroceder 4 días al miércoles de esta semana
    daysToSubtract = 4;
  } else {
    // Es lunes (1) o martes (2)
    // El miércoles de esta semana ya pasó, retroceder al miércoles más reciente
    // lunes: 5 días atrás (para llegar al miércoles pasado)
    // martes: 6 días atrás (para llegar al miércoles pasado)
    daysToSubtract = dayOfWeek + 4;
  }
  
  const wed = new Date(d);
  wed.setDate(d.getDate() - daysToSubtract);
  wed.setHours(0, 0, 0, 0);
  return wed;
}

/**
 * Obtiene el miércoles correspondiente a una fecha de martes.
 * Útil para cuando recibimos la fecha del martes y necesitamos el miércoles de inicio.
 * Exportada para uso en otros componentes.
 */
export function getWednesdayFromTuesday(tuesdayDate: Date | string): Date {
  const tue = typeof tuesdayDate === 'string' ? new Date(tuesdayDate) : new Date(tuesdayDate);
  tue.setHours(0, 0, 0, 0);
  const wed = new Date(tue);
  wed.setDate(tue.getDate() - 6); // Martes - 6 días = Miércoles anterior
  wed.setHours(19, 0, 0, 0); // 19:00 como en el backend
  return wed;
}

/**
 * Calcula el rango completo (miércoles a martes) a partir de una fecha de martes.
 * Retorna objetos Date con las horas correctas (miércoles 19:00, martes 23:59:59).
 */
export function getWeekRangeFromTuesday(tuesdayDate: Date | string): { wed: Date; tue: Date } {
  const tue = typeof tuesdayDate === 'string' ? new Date(tuesdayDate) : new Date(tuesdayDate);
  tue.setHours(23, 59, 59, 999);
  const wed = getWednesdayFromTuesday(tue);
  return { wed, tue };
}

/**
 * Obtiene el martes siguiente al miércoles dado
 */
function getTuesdayAfter(wednesday: Date): Date {
  const tuesday = new Date(wednesday);
  tuesday.setDate(wednesday.getDate() + 6); // Miércoles + 6 días = Martes
  tuesday.setHours(23, 59, 59, 999);
  return tuesday;
}

/**
 * Obtiene el martes de la semana más reciente disponible (por defecto).
 * Siempre devuelve el martes de la semana actual (la que ya ha comenzado).
 */
export function getDefaultTuesday(): string {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const currentWeekWed = getWednesdayOfWeek(today);
  const defaultTuesday = getTuesdayAfter(currentWeekWed);
  return defaultTuesday.toISOString().slice(0, 10);
}

/**
 * Genera semanas (Miércoles → Martes siguiente) desde el inicio hasta hoy.
 * Muestra la semana actual si ya ha comenzado (desde el miércoles).
 * No muestra la semana siguiente hasta que llegue su miércoles.
 */
function generateWeeks(
  startSeason: string = "2025-09-10", // primera jornada (aprox)
  endSeason: string = new Date().toISOString().slice(0, 10),
  weekPrefix: string = "Semana"
): WeekOption[] {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todayTime = today.getTime();
  
  const weeks: WeekOption[] = [];
  
  // Comenzar desde el miércoles de la primera semana
  let currentWed = getWednesdayOfWeek(new Date(startSeason));
  currentWed.setHours(0, 0, 0, 0);
  
  // Determinar hasta qué semana mostrar
  // La semana actual (si ya ha comenzado su miércoles) SÍ debe aparecer
  // La semana siguiente NO debe aparecer hasta que llegue su miércoles
  
  // Obtener el miércoles de la semana actual (el más reciente que ya pasó o es hoy)
  const currentWeekWed = getWednesdayOfWeek(today);
  currentWeekWed.setHours(0, 0, 0, 0);
  
  // Calcular el martes de la semana actual
  const thisWeekTuesday = getTuesdayAfter(currentWeekWed);
  thisWeekTuesday.setHours(23, 59, 59, 999);
  
  // El martes máximo es el de la semana actual
  // La semana siguiente (que empieza el próximo miércoles) no se incluye
  const maxTuesday = thisWeekTuesday;
  
  // Normalizar maxTuesday para comparación (solo fecha)
  maxTuesday.setHours(0, 0, 0, 0);
  
  let weekNum = 1;
  
  // Generar semanas desde el inicio hasta maxTuesday (incluyendo la semana actual si aplica)
  // maxTuesday ya está normalizado (solo fecha, sin hora)
  
  while (true) {
    const tue = getTuesdayAfter(currentWed);
    const tueNormalized = new Date(tue);
    tueNormalized.setHours(0, 0, 0, 0);
    
    // Si el martes de esta semana está después del martes máximo, parar
    // Esto significa que esta semana aún no ha comenzado (es una semana futura)
    if (tueNormalized.getTime() > maxTuesday.getTime()) {
      break;
    }
    
    // Incluir esta semana (su martes es <= maxTuesday)
    weeks.push({
      num: weekNum,
      start: new Date(currentWed),
      end: new Date(tue),
      label: `${weekPrefix} ${weekNum} — ${formatDate(currentWed, "es-ES")} · ${formatDate(tue, "es-ES")}`, // Se formateará después con el locale correcto en useMemo
      value: tue.toISOString().slice(0, 10), // Fecha del martes en formato YYYY-MM-DD
    });
    
    // Siguiente semana: avanzar al siguiente miércoles
    const nextWed = new Date(currentWed);
    nextWed.setDate(currentWed.getDate() + 7);
    currentWed = nextWed;
    weekNum++;
    
    // Seguridad: evitar loops infinitos
    if (weekNum > 100) break;
  }
  
  return weeks.reverse(); // más reciente primero
}

export default function GlobalWeekSelector({
  selected,
  onChange,
  dict,
  lang,
}: {
  selected: string;
  onChange: (v: string) => void;
  dict?: any;
  lang?: string;
}) {
  // Mapeo de idiomas a locales
  const localeMap: Record<string, string> = {
    es: "es-ES",
    en: "en-US",
    val: "ca-ES",
    fr: "fr-FR",
    it: "it-IT",
    pt: "pt-PT",
    de: "de-DE",
  };
  const detectedLang = lang || (dict?.language_label === "Idioma" ? "es" : dict?.language_label === "Language" ? "en" : "es");
  const locale = localeMap[detectedLang] || "es-ES";
  
  const weekPrefix = dict?.week_selector?.week_prefix || "Semana";
  const weeks = useMemo(() => {
    const weeksList = generateWeeks("2025-09-10", new Date().toISOString().slice(0, 10), weekPrefix);
    // Actualizar labels con el locale correcto
    return weeksList.map(w => ({
      ...w,
      label: `${weekPrefix} ${w.num} — ${formatDate(w.start, locale)} · ${formatDate(w.end, locale)}`,
    }));
  }, [weekPrefix, locale]);
  
  // Asegurar que el valor seleccionado existe en las semanas disponibles
  // Si no existe o está vacío, usar el primero (más reciente)
  const validSelected = useMemo(() => {
    if (!selected || !weeks.length) {
      return weeks.length > 0 ? weeks[0].value : "";
    }
    const exists = weeks.some(w => w.value === selected);
    return exists ? selected : (weeks.length > 0 ? weeks[0].value : "");
  }, [selected, weeks]);
  
  // Si el valor seleccionado no es válido, corregirlo una vez al montar
  React.useEffect(() => {
    if (validSelected && validSelected !== selected && weeks.length > 0) {
      onChange(validSelected);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Solo ejecutar al montar

  return (
    // Fila de control alineada a la derecha
    <div className="w-full flex items-center justify-end gap-2 mb-4">
      <label className="font-semibold text-sm text-[var(--color-text-secondary)]">
        {dict?.week_selector?.label || "Selecciona semana:"}
      </label>

      <select
        value={validSelected}
        onChange={(e) => onChange(e.target.value)}
        className="
          rounded-md px-3 py-1 text-sm
          bg-[var(--color-accent)] text-white
          border border-[var(--color-accent)]
          outline-none
          focus:ring-2 focus:ring-[var(--color-accent)] focus:border-[var(--color-accent)]
          hover:bg-[var(--color-accent)]/90
          transition-colors
          font-semibold
        "
      >
        {weeks.map((w) => (
          <option key={w.num} value={w.value}>
            {w.label}
          </option>
        ))}
      </select>
    </div>
  );
}
