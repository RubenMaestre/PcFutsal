// /app/[lang]/partidos/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import React from "react";
import PartidosShell from "../../../components/PartidosShell";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.partidos?.title || dict?.partidos?.meta_title || "Partidos de Fútbol Sala — Resultados y Calendario";
  const description = dict?.seo?.partidos?.description || dict?.partidos?.meta_desc || "Consulta todos los partidos de fútbol sala amateur en España. Resultados, calendario y detalles de cada encuentro.";
  
  return generateMetadataWithAlternates(
    lang,
    "/partidos",
    title,
    description,
    undefined,
    dict
  );
}

async function getFilterContextSSR() {
  try {
    const res = await fetch(
      "http://127.0.0.1:8024/api/nucleo/filter-context/",
      {
        method: "GET",
        cache: "no-store",
      }
    );
    if (!res.ok) throw new Error("bad status");
    return await res.json();
  } catch (err) {
    return { temporada_activa: null, competiciones: [] };
  }
}

export default async function PartidosPage({ params, searchParams }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const filterData = await getFilterContextSSR();
  
  // Obtener parámetros de la URL
  const competicionId = searchParams?.competicion_id ? parseInt(searchParams.competicion_id) : null;
  const grupoId = searchParams?.grupo_id ? parseInt(searchParams.grupo_id) : null;
  const jornada = searchParams?.jornada ? parseInt(searchParams.jornada) : null;

  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      <div className="w-full">
        <PartidosShell
          dict={dict}
          filterData={filterData}
          lang={lang}
          initialCompeticionId={competicionId}
          initialGrupoId={grupoId}
          initialJornada={jornada}
        />
      </div>
    </div>
  );
}

