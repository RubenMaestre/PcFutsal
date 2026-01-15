"use client";

import React, { useState, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useClasificacionEvolucion, EquipoEvolucion } from "../hooks/useClasificacionEvolucion";
import Image from "next/image";

type Props = {
  grupoId: number | string | null;
  dict: any;
  lang?: string;
};

// Función para generar colores únicos para cada equipo
function getColorForTeam(index: number, total: number): string {
  const hues = Array.from({ length: total }, (_, i) => (i * 360) / total);
  const hue = hues[index % total];
  const saturation = 60 + (index % 3) * 10; // 60-80%
  const lightness = 50 + (index % 2) * 5; // 50-55%
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

// Componente personalizado para mostrar el escudo en lugar de círculos
function CustomDotWithShield({
  cx,
  cy,
  payload,
  clubId,
  escudo,
  color,
}: {
  cx?: number;
  cy?: number;
  payload?: any;
  clubId: number;
  escudo: string;
  color: string;
}) {
  if (cx === undefined || cy === undefined) return null;
  if (payload === null || payload === undefined) return null;
  if (!escudo) return null;

  const size = 20; // Tamaño del escudo en píxeles
  const offset = size / 2;
  const radius = size / 2;

  return (
    <g>
      {/* Círculo de fondo con el color del equipo */}
      <circle cx={cx} cy={cy} r={radius + 3} fill={color} opacity={0.15} />
      <circle cx={cx} cy={cy} r={radius + 2} fill="var(--color-card)" stroke={color} strokeWidth={1.5} />
      {/* ClipPath para hacer el escudo circular */}
      <defs>
        <clipPath id={`shield-clip-${clubId}-${payload.jornada}`}>
          <circle cx={cx} cy={cy} r={radius} />
        </clipPath>
      </defs>
      {/* Escudo del equipo como imagen SVG */}
      <image
        x={cx - offset}
        y={cy - offset}
        width={size}
        height={size}
        href={escudo}
        clipPath={`url(#shield-clip-${clubId}-${payload.jornada})`}
        preserveAspectRatio="xMidYMid meet"
      />
    </g>
  );
}

// Componente para el dot activo (hover) más grande
function CustomActiveDot({
  cx,
  cy,
  payload,
  clubId,
  escudo,
  color,
}: {
  cx?: number;
  cy?: number;
  payload?: any;
  clubId: number;
  escudo: string;
  color: string;
}) {
  if (cx === undefined || cy === undefined) return null;
  if (payload === null || payload === undefined) return null;
  if (!escudo) return null;

  const size = 28; // Tamaño más grande para el dot activo
  const offset = size / 2;
  const radius = size / 2;

  return (
    <g>
      {/* Círculo de fondo más grande */}
      <circle cx={cx} cy={cy} r={radius + 4} fill={color} opacity={0.25} />
      <circle cx={cx} cy={cy} r={radius + 3} fill="var(--color-card)" stroke={color} strokeWidth={2} />
      {/* ClipPath para hacer el escudo circular */}
      <defs>
        <clipPath id={`shield-clip-active-${clubId}-${payload.jornada}`}>
          <circle cx={cx} cy={cy} r={radius} />
        </clipPath>
      </defs>
      {/* Escudo del equipo como imagen SVG */}
      <image
        x={cx - offset}
        y={cy - offset}
        width={size}
        height={size}
        href={escudo}
        clipPath={`url(#shield-clip-active-${clubId}-${payload.jornada})`}
        preserveAspectRatio="xMidYMid meet"
      />
    </g>
  );
}

// Función para preparar los datos para Recharts
function prepareChartData(
  equipos: EquipoEvolucion[],
  jornadas: number[],
  enabledTeams: Set<number>
) {
  const chartData: Array<{ [key: string]: number | string | null }> = [];

  // Inicializar estructura base con jornadas
  jornadas.forEach((jornada) => {
    const dataPoint: { [key: string]: number | string | null } = {
      jornada: jornada,
    };

    // Para cada equipo habilitado, añadir su posición en esa jornada
    equipos.forEach((equipo) => {
      if (enabledTeams.has(equipo.club_id)) {
        const evo = equipo.evolucion.find((e) => e.jornada === jornada);
        dataPoint[`pos_${equipo.club_id}`] = evo?.posicion ?? null;
        dataPoint[`nombre_${equipo.club_id}`] = equipo.nombre;
      }
    });

    chartData.push(dataPoint);
  });

  return chartData;
}

export default function ClasificacionEvolucionChart({
  grupoId,
  dict,
  lang = "es",
}: Props) {
  const { data, loading, error } = useClasificacionEvolucion(grupoId, !!grupoId);
  const [enabledTeams, setEnabledTeams] = useState<Set<number>>(new Set());

  const labels = dict?.clasificacion_evolucion || {};

  // Inicializar equipos habilitados cuando lleguen los datos
  React.useEffect(() => {
    if (data && data.equipos.length > 0 && enabledTeams.size === 0) {
      // Por defecto, habilitar los primeros 8 equipos para no sobrecargar la gráfica
      const initialTeams = new Set(
        data.equipos.slice(0, 8).map((e) => e.club_id)
      );
      setEnabledTeams(initialTeams);
    }
  }, [data, enabledTeams.size]);

  const chartData = useMemo(() => {
    if (!data) return [];
    return prepareChartData(data.equipos, data.jornadas, enabledTeams);
  }, [data, enabledTeams]);

  const maxPosition = useMemo(() => {
    if (!data || !data.equipos.length) return 16;
    const maxPos = Math.max(
      ...data.equipos.flatMap((e) =>
        e.evolucion.map((ev) => ev.posicion ?? 0).filter((p) => p > 0)
      )
    );
    return Math.max(maxPos, 16);
  }, [data]);

  if (!grupoId) {
    return null;
  }

  if (loading) {
    return (
      <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
        <div className="text-center text-sm text-white/60">
          {labels.loading || "Cargando evolución de clasificación..."}
        </div>
      </div>
    );
  }

  // Si hay error, mostrar mensaje de error
  if (error) {
    return (
      <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
        <div className="text-center text-sm text-[var(--color-error)]">
          {labels.error || "Error al cargar la evolución de clasificación"}
        </div>
      </div>
    );
  }

  // Si no hay datos o no hay jornadas, mostrar mensaje informativo
  if (!data || !data.jornadas || data.jornadas.length === 0) {
    return (
      <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
        <div className="space-y-2">
          <h3 className="text-xl font-bold text-[var(--color-text)] mb-1">
            {labels.title || "Evolución de Posiciones"}
          </h3>
          <div className="text-center text-sm text-white/60">
            {labels.no_data || "No hay datos históricos de evolución disponibles para este grupo. La gráfica aparecerá cuando se generen los datos históricos de posiciones por jornada."}
          </div>
        </div>
      </div>
    );
  }

  // Si hay datos pero no equipos, también mostrar mensaje
  if (!data.equipos || data.equipos.length === 0) {
    return (
      <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
        <div className="text-center text-sm text-white/60">
          {labels.no_data || "No hay equipos disponibles para mostrar en la gráfica."}
        </div>
      </div>
    );
  }

  const toggleTeam = (clubId: number) => {
    setEnabledTeams((prev) => {
      const next = new Set(prev);
      if (next.has(clubId)) {
        next.delete(clubId);
      } else {
        next.add(clubId);
      }
      return next;
    });
  };

  const enabledEquipos = data.equipos.filter((e) => enabledTeams.has(e.club_id));

  return (
    <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6 space-y-4">
      <div>
        <h3 className="text-xl font-bold text-[var(--color-text)] mb-1">
          {labels.title || "Evolución de Posiciones"}
        </h3>
        <p className="text-sm text-white/60">
          {labels.subtitle ||
            "Seguimiento de la posición en la clasificación jornada a jornada"}
        </p>
      </div>

      {/* Selector de equipos */}
      <div className="flex flex-wrap gap-2 mb-4">
        {data.equipos.map((equipo, idx) => {
          const isEnabled = enabledTeams.has(equipo.club_id);
          const color = getColorForTeam(idx, data.equipos.length);
          return (
            <button
              key={equipo.club_id}
              onClick={() => toggleTeam(equipo.club_id)}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-semibold transition-all
                flex items-center gap-2
                ${
                  isEnabled
                    ? "bg-opacity-20 border-2"
                    : "bg-opacity-5 border border-[var(--color-navy)] opacity-50"
                }
              `}
              style={{
                backgroundColor: isEnabled ? `${color}20` : "transparent",
                borderColor: isEnabled ? color : "var(--color-navy)",
                color: isEnabled ? color : "var(--color-text-secondary)",
              }}
            >
              {equipo.escudo && (
                <img
                  src={equipo.escudo}
                  alt={equipo.nombre}
                  className="w-4 h-4 object-contain"
                />
              )}
              <span>{equipo.nombre}</span>
            </button>
          );
        })}
      </div>

      {/* Gráfica */}
      <div className="w-full" style={{ height: "720px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 30, right: 30, left: 40, bottom: 30 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--color-navy)"
              opacity={0.3}
            />
            <XAxis
              dataKey="jornada"
              stroke="var(--color-text-secondary)"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              label={{
                value: labels.jornada_label || "Jornada",
                position: "insideBottom",
                offset: -5,
                fill: "var(--color-text-secondary)",
                style: { textAnchor: "middle" },
              }}
            />
            <YAxis
              domain={[maxPosition, 1]}
              reversed
              stroke="var(--color-text-secondary)"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              label={{
                value: labels.posicion_label || "Posición",
                angle: -90,
                position: "insideLeft",
                fill: "var(--color-text-secondary)",
                style: { textAnchor: "middle" },
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--color-card)",
                border: "1px solid var(--color-navy)",
                borderRadius: "8px",
                color: "var(--color-text)",
              }}
              formatter={(value: any, name: string) => {
                if (value === null || value === undefined) return "—";
                const clubId = parseInt(name.replace("pos_", ""));
                const equipo = data.equipos.find((e) => e.club_id === clubId);
                return [
                  `${value}º`,
                  equipo?.nombre || name,
                ];
              }}
              labelFormatter={(label) => `${labels.jornada || "J"} ${label}`}
            />
            <Legend
              wrapperStyle={{
                paddingTop: "20px",
              }}
              formatter={(value: string) => {
                const clubId = parseInt(value.replace("pos_", ""));
                const equipo = data.equipos.find((e) => e.club_id === clubId);
                return equipo?.nombre || value;
              }}
            />
            {enabledEquipos.map((equipo, idx) => {
              const color = getColorForTeam(
                data.equipos.findIndex((e) => e.club_id === equipo.club_id),
                data.equipos.length
              );
              return (
                <Line
                  key={equipo.club_id}
                  type="monotone"
                  dataKey={`pos_${equipo.club_id}`}
                  stroke={color}
                  strokeWidth={2}
                  dot={(props: any) => {
                    // Solo mostrar dot si hay posición válida
                    if (props.payload && props.payload[`pos_${equipo.club_id}`] !== null && props.payload[`pos_${equipo.club_id}`] !== undefined) {
                      return (
                        <CustomDotWithShield
                          {...props}
                          clubId={equipo.club_id}
                          escudo={equipo.escudo || ""}
                          color={color}
                        />
                      );
                    }
                    return null;
                  }}
                  activeDot={(props: any) => {
                    if (props.payload && props.payload[`pos_${equipo.club_id}`] !== null && props.payload[`pos_${equipo.club_id}`] !== undefined) {
                      return (
                        <CustomActiveDot
                          {...props}
                          clubId={equipo.club_id}
                          escudo={equipo.escudo || ""}
                          color={color}
                        />
                      );
                    }
                    return null;
                  }}
                  name={`pos_${equipo.club_id}`}
                  connectNulls={false}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Nota informativa */}
      <p className="text-xs text-white/60 text-center">
        {labels.note ||
          "Haz clic en los equipos arriba para activar o desactivar sus líneas en la gráfica"}
      </p>
    </div>
  );
}

