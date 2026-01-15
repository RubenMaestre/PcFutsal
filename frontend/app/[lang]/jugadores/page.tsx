// /app/[lang]/jugadores/page.tsx
// @ts-nocheck
import { getDictionary } from "../../../lib/i18n";
import JugadoresPageClient from "./JugadoresPageClient";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.jugadores?.title || "Jugadores de Fútbol Sala — Directorio Completo";
  const description = dict?.seo?.jugadores?.description || "Explora todos los jugadores de fútbol sala amateur en España. Perfiles, estadísticas y trayectoria de cada jugador.";
  
  return generateMetadataWithAlternates(
    lang,
    "/jugadores",
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
      console.error("SSR filter-context jugadores: HTTP", res.status);
      return null;
    }
    const json = await res.json();
    return json;
  } catch (err) {
    console.error("SSR filter-context jugadores: ERROR", err);
    return null;
  }
}

export default async function JugadoresPage({ params }) {
  const dict = await getDictionary(params.lang);
  const filterData = await fetchFilterContext();

  return (
    <JugadoresPageClient
      lang={params.lang}
      dict={dict}
      filterData={filterData}
    />
  );
}












