// @ts-nocheck
import { getDictionary } from "../../../../../../lib/i18n";
import React from "react";
import MVPGroupPageClient from "./MVPGroupPageClient";
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
    
    // Usar template de competición pero adaptado para MVP
    const titleTemplate = dict?.seo?.competicion?.title_template || "{competicion} · {grupo} · {temporada} — Resultados y Clasificación";
    const title = replaceTemplate(titleTemplate, { competicion, grupo, temporada }).replace("Resultados y Clasificación", "MVP");
    const description = `Clasificación MVP del ${grupo} de ${competicion} en ${temporada}. Mejores jugadores por jornada con valoraciones tipo FIFA.`;
    const path = `/competicion/mvp/${competicionSlug}/${grupoSlug}`;
    
    return generateMetadataWithAlternates(lang, path, title, description, undefined, dict);
  } catch (error) {
    // Fallback metadata
    const path = `/competicion/mvp/${competicionSlug}/${grupoSlug}`;
    const fallbackTitle = dict?.seo?.mvp?.title || dict?.mvp_page?.fallback_title || "MVP — Mejores Jugadores por Jornada";
    const fallbackDesc = dict?.seo?.mvp?.description || dict?.mvp_page?.fallback_desc || "Clasificación MVP con los mejores jugadores por jornada.";
    
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

export default async function MVPGroupPage({ params }) {
  const { lang, competicionSlug, grupoSlug } = params;
  const dict = await getDictionary(lang);
  const data = await getGrupoInfo(competicionSlug, grupoSlug);
  const meta = data.meta;
  const d = data.data;

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <h1 className="text-2xl font-bold mb-2">
          {meta.grupo.competicion} – {meta.grupo.nombre} ({meta.grupo.temporada})
        </h1>
        <p className="text-sm text-white/60">
          {dict?.mvp_page?.page_group_desc ||
            "Clasificación MVP de la jornada para este grupo."}
        </p>
      </div>

      <MVPGroupPageClient
        lang={lang}
        dict={dict}
        grupoId={meta.grupo.id}
        initialJornada={d?.resultados_jornada?.jornada || null}
      />
    </>
  );
}
