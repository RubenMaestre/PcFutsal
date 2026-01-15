// /app/[lang]/rankings/tarjetas/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../../lib/i18n";
import React from "react";
import SancionesGlobalPageClient from "../sanciones/SancionesGlobalPageClient";
import { generateMetadataWithAlternates } from "../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.rankings?.tarjetas?.title || dict?.tarjetas_global_labels?.meta_title || "Ranking Global de Tarjetas — Jugadores Más Sancionados de Fútbol Sala";
  const description = dict?.seo?.rankings?.tarjetas?.description || dict?.tarjetas_global_labels?.meta_desc || "Ranking global de los jugadores más sancionados de fútbol sala amateur en España. Compara tarjetas (amarillas, rojas) de todas las competiciones y categorías.";
  
  return generateMetadataWithAlternates(
    lang,
    "/rankings/tarjetas",
    title,
    description,
    undefined,
    dict
  );
}

export default async function TarjetasGlobalPage({ params }) {
  const { lang } = params;
  const dict = await getDictionary(lang);

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <h1 className="text-2xl font-bold mb-2">
          {dict.tarjetas_global_labels?.global_title ||
            dict.sanciones_global_labels?.global_title ||
            "Ranking Global de Tarjetas"}
        </h1>

        <p className="text-sm text-white/60">
          {dict.tarjetas_global_labels?.global_desc ||
            dict.sanciones_global_labels?.global_desc ||
            "Clasificación global de los jugadores más sancionados con sistema de puntos de disciplina."}
        </p>
      </div>

      <SancionesGlobalPageClient lang={lang} dict={dict} />

      {/* CONTENIDO EDITORIAL - RANKINGS */}
      {dict?.editorial?.rankings && (
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="bg-brand-card border border-brand-card rounded-lg p-6 space-y-4">
            <h2 className="text-xl font-bold text-brand-text">
              {dict.editorial.rankings.title || "Cómo Funcionan los Rankings"}
            </h2>
            <div className="space-y-3 text-sm text-brand-textSecondary leading-relaxed">
              <p>{dict.editorial.rankings.paragraph1}</p>
              <p>{dict.editorial.rankings.paragraph2}</p>
              <p>{dict.editorial.rankings.paragraph3}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}




