// /app/[lang]/clubes/[id]/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../../lib/i18n";
import ClubDetailClient from "./ClubDetailClient";
import { generateMetadataWithAlternates, getApiBaseUrl, replaceTemplate } from "../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

async function getClubData(clubId: string) {
  const baseUrl = getApiBaseUrl();
  // Determinar si es ID numérico o slug
  const isNumeric = /^\d+$/.test(clubId.trim());
  const paramName = isNumeric ? "club_id" : "slug";
  const url = `${baseUrl}/api/clubes/full/?${paramName}=${encodeURIComponent(clubId)}`;
  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    return null;
  }
}

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang, id } = params;
  const dict = await getDictionary(lang);
  
  try {
    const data = await getClubData(id);
    if (data?.club) {
      const nombre = data.club.nombre_oficial || data.club.nombre_corto || "Club";
      const titleTemplate = dict?.seo?.club?.title_template || "{nombre} — Resultados, Plantilla y Estadísticas";
      const descriptionTemplate = dict?.seo?.club?.description_template || "Plantilla completa, últimos resultados, clasificación, racha y estadísticas del {nombre}.";
      
      const title = replaceTemplate(titleTemplate, { nombre });
      const description = replaceTemplate(descriptionTemplate, { nombre });
      // Usar slug si está disponible, sino usar ID
      const clubSlug = data.club?.slug;
      const path = clubSlug ? `/clubes/${clubSlug}` : `/clubes/${id}`;
      
      return generateMetadataWithAlternates(lang, path, title, description, undefined, dict);
    }
  } catch (error) {
    // Fallback
  }
  
  // Fallback metadata
  const path = `/clubes/${id}`;
  const fallbackTitle = dict?.seo?.club?.fallback_title || "Club — Resultados, Plantilla y Estadísticas";
  const fallbackDesc = dict?.seo?.club?.fallback_desc || "Plantilla completa, últimos resultados, clasificación, racha y estadísticas del club.";
  
  return generateMetadataWithAlternates(
    lang,
    path,
    fallbackTitle,
    fallbackDesc,
    undefined,
    dict
  );
}

export default async function ClubDetailPage({ params }) {
  const dict = await getDictionary(params.lang);

  return (
    <ClubDetailClient
      lang={params.lang}
      clubId={params.id}
      dict={dict}
    />
  );
}
