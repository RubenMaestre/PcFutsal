// @ts-nocheck

import { getDictionary } from "../../../../../lib/i18n";
import React from "react";
import GroupShell from "../../../../../components/GroupShell";
import { generateMetadataWithAlternates, getApiBaseUrl, replaceTemplate } from "../../../../../lib/seo";
import { generateSportsOrganizationSchema } from "../../../../../lib/schema";
import Breadcrumbs from "../../../../../components/Breadcrumbs";
import LanguageSwitcher from "../../../../../components/LanguageSwitcher";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

async function getGrupoInfo(competicionSlug, grupoSlug) {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/estadisticas/grupo-info/?competicion_slug=${competicionSlug}&grupo_slug=${grupoSlug}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Error al cargar datos del grupo"); // Este error se maneja en el catch
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
    
    const titleTemplate = dict?.seo?.competicion?.title_template || "{competicion} · {grupo} · {temporada} — Resultados y Clasificación";
    const descriptionTemplate = dict?.seo?.competicion?.description_template || "Jornadas, resultados, clasificación, clubs, goleadores y ranking de jugadores del {grupo} de {competicion} en {temporada}.";
    
    const title = replaceTemplate(titleTemplate, { competicion, grupo, temporada });
    const description = replaceTemplate(descriptionTemplate, { competicion, grupo, temporada });
    const path = `/competicion/${competicionSlug}/${grupoSlug}`;
    
    return generateMetadataWithAlternates(lang, path, title, description, undefined, dict);
  } catch (error) {
    // Fallback metadata if API fails
    const path = `/competicion/${competicionSlug}/${grupoSlug}`;
    const fallbackTitle = dict?.seo?.competicion?.fallback_title || dict?.competicion?.fallback_title || "Competición — Resultados y Clasificación";
    const fallbackDesc = dict?.seo?.competicion?.fallback_desc || dict?.competicion?.fallback_desc || "Jornadas, resultados, clasificación, clubs, goleadores y ranking de jugadores.";
    
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

export default async function GrupoPage({ params }) {
  const { lang, competicionSlug, grupoSlug } = params;
  const dict = await getDictionary(lang);

  const data = await getGrupoInfo(competicionSlug, grupoSlug);
  const meta = data.meta;
  const d = data.data;

  // Generate breadcrumbs
  const breadcrumbs = [
    { name: dict?.competicion?.breadcrumb_home || "Home", url: `/${lang}` },
    { name: meta.grupo.competicion, url: `/${lang}/competicion/${competicionSlug}/${grupoSlug}` },
    { name: meta.grupo.nombre, url: `/${lang}/competicion/${competicionSlug}/${grupoSlug}` },
  ];

  // Generate SportsOrganization schema
  const sportsOrgSchema = generateSportsOrganizationSchema({
    competicion: meta.grupo.competicion,
    nombre: meta.grupo.nombre,
    temporada: meta.grupo.temporada,
  });

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(sportsOrgSchema) }}
      />
      {/* título arriba (SSR) */}
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <Breadcrumbs items={breadcrumbs} lang={lang} />
        <h1 className="text-2xl font-bold mb-2">
          {meta.grupo.competicion} – {meta.grupo.nombre} ({meta.grupo.temporada})
        </h1>
      </div>

      {/* todo lo interactivo abajo (CLIENT) */}
      <GroupShell
        dict={dict}
        grupoId={meta.grupo.id}
        initialJornada={d?.resultados_jornada?.jornada || null}
      />

      {/* CONTENIDO EDITORIAL - COMPETICIÓN (antes del footer) */}
      {dict?.editorial?.clasificacion && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-brand-card border border-brand-card rounded-lg p-6 space-y-4">
            <h2 className="text-xl font-bold text-brand-text">
              {dict.editorial.clasificacion.title || "Sobre las Clasificaciones"}
            </h2>
            <div className="space-y-3 text-sm text-brand-textSecondary leading-relaxed">
              <p>{dict.editorial.clasificacion.paragraph1}</p>
              <p>{dict.editorial.clasificacion.paragraph2}</p>
              <p>{dict.editorial.clasificacion.paragraph3}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
