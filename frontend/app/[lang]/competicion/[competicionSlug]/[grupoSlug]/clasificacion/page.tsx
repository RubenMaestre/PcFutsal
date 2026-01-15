// @ts-nocheck
import { getDictionary } from "../../../../../../lib/i18n";
import React from "react";
import FullClassificationShell from "../../../../../../components/FullClassificationShell";
import { generateMetadataWithAlternates, getApiBaseUrl, replaceTemplate } from "../../../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

async function getGrupoInfo(competicionSlug, grupoSlug) {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/estadisticas/grupo-info/?competicion_slug=${competicionSlug}&grupo_slug=${grupoSlug}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Error al cargar datos del grupo");
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
    const path = `/competicion/${competicionSlug}/${grupoSlug}/clasificacion`;
    
    return generateMetadataWithAlternates(lang, path, title, description, undefined, dict);
  } catch (error) {
    // Fallback metadata
    const path = `/competicion/${competicionSlug}/${grupoSlug}/clasificacion`;
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

export default async function ClasificacionPage({ params }) {
  const { lang, competicionSlug, grupoSlug } = params;
  const dict = await getDictionary(lang);
  const data = await getGrupoInfo(competicionSlug, grupoSlug);
  const meta = data.meta;

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <h1 className="text-2xl font-bold mb-2">
          {meta.grupo.competicion} – {meta.grupo.nombre} ({meta.grupo.temporada})
        </h1>
      </div>

      <FullClassificationShell dict={dict} grupoId={meta.grupo.id} />
    </>
  );
}
