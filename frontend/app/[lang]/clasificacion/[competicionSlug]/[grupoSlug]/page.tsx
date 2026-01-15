// /app/[lang]/clasificacion/[competicionSlug]/[grupoSlug]/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../../../lib/i18n";
import React from "react";
import ClasificacionShell from "../../../../../components/ClasificacionShell";
import { generateMetadataWithAlternates, getApiBaseUrl, replaceTemplate } from "../../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

async function getGrupoInfo(competicionSlug: string, grupoSlug: string) {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/estadisticas/grupo-info/?competicion_slug=${competicionSlug}&grupo_slug=${grupoSlug}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Error al cargar datos del grupo");
  }
  return res.json();
}

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang, competicionSlug, grupoSlug } = params;
  const dict = await getDictionary(lang);
  
  try {
    const data = await getGrupoInfo(competicionSlug, grupoSlug);
    const meta = data.meta;
    const competicion = meta.grupo.competicion;
    const grupo = meta.grupo.nombre;
    const temporada = meta.grupo.temporada;
    
    // Usar template de competición pero adaptado para clasificación
    const titleTemplate = dict?.seo?.competicion?.title_template || "{competicion} · {grupo} · {temporada} — Resultados y Clasificación";
    const title = replaceTemplate(titleTemplate, { competicion, grupo, temporada }).replace("Resultados y Clasificación", "Clasificación");
    const description = `Clasificación completa del ${grupo} de ${competicion} en ${temporada}. Posiciones, puntos, goles y estadísticas en tiempo real.`;
    const path = `/clasificacion/${competicionSlug}/${grupoSlug}`;
    
    return generateMetadataWithAlternates(lang, path, title, description, undefined, dict);
  } catch (error) {
    // Fallback metadata
    const path = `/clasificacion/${competicionSlug}/${grupoSlug}`;
    const fallbackTitle = dict?.seo?.clasificacion?.title || dict?.clasificacion?.fallback_title || "Clasificación — Resultados y Posiciones";
    const fallbackDesc = dict?.seo?.clasificacion?.description || dict?.clasificacion?.fallback_desc || "Clasificación completa con posiciones, puntos, goles y estadísticas.";
    
    return generateMetadataWithAlternates(
      lang,
      path,
      fallbackTitle,
      fallbackDesc,
      undefined,
      dict
    );
  }
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

export default async function ClasificacionGrupoPage({ params }) {
  const { lang, competicionSlug, grupoSlug } = params;
  const dict = await getDictionary(lang);

  const data = await getGrupoInfo(competicionSlug, grupoSlug);
  const meta = data.meta;
  const grupo = meta.grupo;

  const initialGrupoId = grupo.id;
  const initialCompeticionId = grupo.competicion_id ?? null;

  const filterData = await getFilterContextSSR();

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <h1 className="text-2xl font-bold mb-2">
          {grupo.competicion} – {grupo.nombre} ({grupo.temporada})
        </h1>
      </div>

      <ClasificacionShell
        dict={dict}
        initialCompeticionId={initialCompeticionId}
        initialGrupoId={initialGrupoId}
        filterData={filterData} // 👈 lo pasamos ya
      />
    </>
  );
}
