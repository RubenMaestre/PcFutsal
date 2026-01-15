"use client";

import React from "react";
import { useMVPClassification } from "../../../../../../hooks/useMVPClassification";
import MVPClassificationTable from "../../../../../../components/MVPClassificationTable";

type Props = {
  lang: string;
  dict: any;
  grupoId: number;
  initialJornada: number | null;
};

export default function MVPGroupPageClient({
  lang,
  dict,
  grupoId,
  initialJornada,
}: Props) {
  const [selectedJornada, setSelectedJornada] = React.useState<number | null>(
    initialJornada
  );
  const [onlyPorteros, setOnlyPorteros] = React.useState(false);

  const { data, loading, error } = useMVPClassification(grupoId, {
    jornada: selectedJornada,
    onlyPorteros,
  });

  const labels = dict?.mvp_labels || {};
  const jornadas = data?.jornadas_disponibles ?? [];
  // ✅ ya no existe data?.jornada en MVPAccumData
  const jornadaAplicada = data?.jornada_aplicada ?? null;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-6">
      {/* Filtros */}
      <div className="flex flex-wrap items-center gap-3">
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
            {labels.filter_gk || "Portero"}
          </button>

          {/* de momento desactivados */}
          <button
            disabled
            className="px-3 py-1 rounded-full text-xs bg-[#12121233] text-[#555] cursor-not-allowed"
          >
            {labels.filter_cierre || dict?.mvp_group?.filter_cierre || "Cierre"}
          </button>
          <button
            disabled
            className="px-3 py-1 rounded-full text-xs bg-[#12121233] text-[#555] cursor-not-allowed"
          >
            {labels.filter_ala || dict?.mvp_group?.filter_ala || "Ala"}
          </button>
          <button
            disabled
            className="px-3 py-1 rounded-full text-xs bg-[#12121233] text-[#555] cursor-not-allowed"
          >
            {labels.filter_ala_cierre || dict?.mvp_group?.filter_ala_cierre || "Ala-cierre"}
          </button>
          <button
            disabled
            className="px-3 py-1 rounded-full text-xs bg-[#12121233] text-[#555] cursor-not-allowed"
          >
            {labels.filter_ala_pivot || dict?.mvp_group?.filter_ala_pivot || "Ala-pívot"}
          </button>
          <button
            disabled
            className="px-3 py-1 rounded-full text-xs bg-[#12121233] text-[#555] cursor-not-allowed"
          >
            {labels.filter_pivot || dict?.mvp_group?.filter_pivot || "Pívot"}
          </button>
        </div>

        {/* Selector jornada */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-[#B3B3B3]">
            {labels.select_matchday || "Jornada"}
          </label>
          <select
            value={selectedJornada ?? jornadaAplicada ?? ""}
            onChange={(e) => {
              const v = e.target.value;
              setSelectedJornada(v ? Number(v) : null);
            }}
            className="bg-[#121212] border border-[#222] rounded-md px-3 py-1.5 text-sm"
          >
            {jornadas.length === 0 ? (
              jornadaAplicada !== null ? (
                <option value={jornadaAplicada}>
                  {labels.matchday_label
                    ? `${labels.matchday_label} ${jornadaAplicada}`
                    : `Jornada ${jornadaAplicada}`}
                </option>
              ) : (
                <option value="">
                  {labels.no_matchdays || "Sin jornadas"}
                </option>
              )
            ) : (
              jornadas.map((j) => (
                <option key={j} value={j}>
                  {labels.matchday_label
                    ? `${labels.matchday_label} ${j}`
                    : `Jornada ${j}`}
                </option>
              ))
            )}
          </select>
        </div>
      </div>

      {/* Tabla */}
      <MVPClassificationTable
        dict={dict}
        loading={loading}
        error={error}
        data={data}
        lang={lang}
      />
    </div>
  );
}



