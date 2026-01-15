// /app/[lang]/clasificacion/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import React from "react";
import ClasificacionShell from "../../../components/ClasificacionShell";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.clasificacion?.title || dict?.clasificacion?.meta_title || "Clasificaciones de Fútbol Sala — Resultados y Posiciones";
  const description = dict?.seo?.clasificacion?.description || dict?.clasificacion?.meta_desc || "Consulta las clasificaciones de todas las competiciones de fútbol sala amateur en España. Resultados, posiciones y estadísticas en tiempo real.";
  
  return generateMetadataWithAlternates(
    lang,
    "/clasificacion",
    title,
    description,
    undefined,
    dict
  );
}

async function getFilterContextSSR() {
  // aquí usamos el puerto interno porque estamos en el SERVIDOR
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

export default async function ClasificacionPage({ params }) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const filterData = await getFilterContextSSR();

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <h1 className="text-2xl font-bold mb-2">
          {dict?.nav?.menu?.table || "Clasificación"}
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          {dict?.home_table_labels?.hint_select_group ||
            "Selecciona una competición y un grupo para ver la clasificación."}
        </p>
      </div>

      {/* CONTENIDO EDITORIAL - CLASIFICACIÓN */}
      {dict?.editorial?.clasificacion && (
        <div className="max-w-7xl mx-auto px-4 py-6">
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

      {/* 💡 ahora le pasamos el filtro ya cargado */}
      <ClasificacionShell dict={dict} filterData={filterData} />
    </>
  );
}
