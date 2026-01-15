// app/[lang]/page.tsx
// @ts-nocheck

import { getDictionary } from "../../lib/i18n";
import HomeShell from "../../components/HomeShell";
import { generateMetadataWithAlternates } from "../../lib/seo";
import type { Metadata } from "next";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.seo?.home?.title || "PC FUTSAL — Resultados, Estadísticas y Rankings de Fútbol Sala en España";
  const description = dict?.seo?.home?.description || "Resultados oficiales, clasificaciones, jugadores, clubes y rankings tipo FIFA del fútbol sala amateur en España. Datos actualizados y Fantasy semanal.";
  
  return generateMetadataWithAlternates(
    lang,
    "/",
    title,
    description,
    undefined,
    dict
  );
}

export default async function HomePage({ params }: any) {
  const dict = await getDictionary(params.lang);

  // Vamos a intentar leer el contexto de filtros desde Django directamente
  // usando el puerto interno de Gunicorn (127.0.0.1:8024)
  let filterData;

  try {
    const res = await fetch(
      "http://127.0.0.1:8024/api/nucleo/filter-context/",
      {
        method: "GET",
        cache: "no-store", // no cachear para SSR/render
      }
    );

    if (!res.ok) {
      throw new Error("Bad status " + res.status);
    }

    filterData = await res.json();
  } catch (err) {
    // Fallback seguro para que la home renderice aunque la API falle
    filterData = {
      temporada_activa: null,
      competiciones: [],
    };
  }

  return <HomeShell dict={dict} filterData={filterData} lang={params.lang} />;
}
