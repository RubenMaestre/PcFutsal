// /app/[lang]/partidos/[id]/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../../lib/i18n";
import React from "react";
import PartidoDetailClient from "./PartidoDetailClient";
import { generateMetadataWithAlternates } from "../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang, id } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.partidos?.detail_title || `Partido ${id} — PC FUTSAL`;
  const description = dict?.seo?.partidos?.detail_description || `Detalle completo del partido ${id} con eventos, alineaciones y estadísticas.`;
  
  return generateMetadataWithAlternates(
    lang,
    `/partidos/${id}`,
    title,
    description,
    undefined,
    dict
  );
}

export default async function PartidoDetailPage({ params }: any) {
  const { lang, id } = params;
  const dict = await getDictionary(lang);

  // Convertir id a número si es posible, mantener como string si no
  const partidoId = id ? (isNaN(Number(id)) ? id : Number(id)) : null;

  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      <PartidoDetailClient partidoId={partidoId} dict={dict} lang={lang} />
    </div>
  );
}




