// /app/[lang]/jugadores/[id]/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../../lib/i18n";
import JugadorDetailClient from "./JugadorDetailClient";
import { generateMetadataWithAlternates, getApiBaseUrl, replaceTemplate } from "../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

async function getJugadorData(jugadorId: string) {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/jugadores/full/?jugador_id=${jugadorId}`;
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
    const data = await getJugadorData(id);
    if (data?.jugador) {
      const nombre = data.jugador.nombre || data.jugador.apodo || "Jugador";
      const titleTemplate = dict?.seo?.jugador?.title_template || "{nombre} — Estadísticas y Media Tipo FIFA | PC FUTSAL";
      const descriptionTemplate = dict?.seo?.jugador?.description_template || "Ficha completa de {nombre} con estadísticas, valoraciones FIFA, historial y más en PC FUTSAL.";
      
      const title = replaceTemplate(titleTemplate, { nombre });
      const description = replaceTemplate(descriptionTemplate, { nombre });
      // Usar slug si está disponible, sino usar el ID de la URL
      const path = `/jugadores/${data.jugador.slug || id}`;
      
      // Usar foto del jugador si está disponible
      const ogImage = data.jugador.foto_url || undefined;
      
      return generateMetadataWithAlternates(lang, path, title, description, ogImage, dict);
    }
  } catch (error) {
    // Fallback
  }
  
  // Fallback metadata
  const path = `/jugadores/${id}`;
  const fallbackTitle = dict?.seo?.jugador?.fallback_title || "Jugador — Estadísticas y Media Tipo FIFA | PC FUTSAL";
  const fallbackDesc = dict?.seo?.jugador?.fallback_desc || "Ficha completa del jugador con estadísticas, valoraciones FIFA, historial y más en PC FUTSAL.";
  
  return generateMetadataWithAlternates(
    lang,
    path,
    fallbackTitle,
    fallbackDesc,
    undefined,
    dict
  );
}

export default async function JugadorDetailPage({ params }) {
  const dict = await getDictionary(params.lang);

  return (
    <JugadorDetailClient
      lang={params.lang}
      jugadorId={params.id}
      dict={dict}
    />
  );
}
