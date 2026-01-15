// /app/[lang]/clubes/page.tsx
// @ts-nocheck
import { getDictionary } from "../../../lib/i18n";
import ClubsPageClient from "./ClubsPageClient";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.clubes?.title || "Clubes de Fútbol Sala — Directorio Completo";
  const description = dict?.seo?.clubes?.description || "Explora todos los clubes de fútbol sala amateur en España. Perfiles, plantillas, estadísticas y resultados de cada club.";
  
  return generateMetadataWithAlternates(
    lang,
    "/clubes",
    title,
    description,
    undefined,
    dict
  );
}

async function fetchFilterContext() {
  const URL = "https://pcfutsal.es/api/nucleo/filter-context/";
  try {
    const res = await fetch(URL, {
      method: "GET",
      cache: "no-store",
      next: { revalidate: 0 },
    });
    if (!res.ok) {
      console.error("SSR filter-context clubes: HTTP", res.status);
      return null;
    }
    const json = await res.json();
    return json;
  } catch (err) {
    console.error("SSR filter-context clubes: ERROR", err);
    return null;
  }
}

export default async function ClubsPage({ params }) {
  const dict = await getDictionary(params.lang);
  const filterData = await fetchFilterContext();

  return (
    <ClubsPageClient
      lang={params.lang}
      dict={dict}
      // 👇 se lo pasamos
      filterData={filterData}
    />
  );
}
