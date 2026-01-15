// app/[lang]/mvp/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.mvp?.title || "Clasificación MVP — Mejores Jugadores por Jornada";
  const description = dict?.seo?.mvp?.description || "Sistema de valoración tipo FIFA para jugadores de fútbol sala. Descubre los mejores jugadores de cada jornada y competición.";
  
  return generateMetadataWithAlternates(
    lang,
    "/mvp",
    title,
    description,
    undefined,
    dict
  );
}

async function getFilterContext() {
  // mismo truco que en la home
  try {
    const res = await fetch(
      "http://127.0.0.1:8024/api/nucleo/filter-context/",
      {
        method: "GET",
        cache: "no-store",
      }
    );
    if (!res.ok) {
      throw new Error("Bad status " + res.status);
    }
    return await res.json();
  } catch (err) {
    // devolvemos algo mínimo para que el client no casque
    return {
      temporada_activa: null,
      competiciones: [],
    };
  }
}

export default async function MVPPage({ params }) {
  const dict = await getDictionary(params.lang);
  const filterData = await getFilterContext();

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <h1 className="text-2xl font-bold mb-2">
          {dict?.mvp_labels?.page_title || "Clasificación MVP PC FUTSAL"}
        </h1>
        <p className="text-sm text-white/60 mb-4">
          {dict?.mvp_labels?.page_desc ||
            "Elige competición y grupo para ver la clasificación MVP por jornada."}
        </p>
      </div>

      {/* cliente */}
      <MVPPageClient
        lang={params.lang}
        dict={dict}
        initialFilterData={filterData}
      />
    </>
  );
}

// 👇 IMPORTANTE: hay que importar el client después para que Next lo resuelva
import MVPPageClient from "./MVPPageClient";
