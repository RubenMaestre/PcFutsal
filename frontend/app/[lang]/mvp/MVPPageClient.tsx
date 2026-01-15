// app/[lang]/mvp/MVPPageClient.tsx
"use client";

import React from "react";
import { useRouter } from "next/navigation";
import CompetitionFilter from "../../../components/CompetitionFilter";

type Props = {
  lang: string;
  dict: any;
  initialFilterData: any;
};

export default function MVPPageClient({
  lang,
  dict,
  initialFilterData,
}: Props) {
  const router = useRouter();

  const [scope, setScope] = React.useState<"GLOBAL" | "COMPETICIONES">(
    "COMPETICIONES"
  );
  const [selectedCompeticionId, setSelectedCompeticionId] =
    React.useState<number | null>(null);
  const [selectedGrupoId, setSelectedGrupoId] = React.useState<number | null>(
    null
  );

  return (
    <div className="w-full">
      <CompetitionFilter
        dict={dict}
        data={initialFilterData}
        scope={scope}
        setScope={setScope}
        selectedCompeticionId={selectedCompeticionId}
        setSelectedCompeticionId={setSelectedCompeticionId}
        selectedGrupoId={selectedGrupoId}
        setSelectedGrupoId={setSelectedGrupoId}
        disableNavigation={false}
        onSelectionCompleted={(competicionSlug, grupoSlug) => {
          // 👇 ahora sí, la ruta que tú quieres
          router.push(
            `/${lang}/competicion/mvp/${competicionSlug}/${grupoSlug}`
          );
        }}
      />

      <div className="max-w-7xl mx-auto px-4 py-8 text-sm text-white/50">
        {selectedGrupoId
          ? (dict?.mvp_labels?.loading || "Cargando clasificación MVP…")
          : (dict?.mvp_labels?.select_group || "Selecciona competición y grupo para ver la clasificación MVP.")}
      </div>
    </div>
  );
}
