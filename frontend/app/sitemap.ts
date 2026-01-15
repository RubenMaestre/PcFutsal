import { MetadataRoute } from "next";
import { getApiBaseUrl, getInternalApiUrl } from "../lib/seo";

const siteUrl = "https://pcfutsal.es";
const languages = ["es", "en", "de", "fr", "it", "pt", "val"];

interface SitemapEntry {
  url: string;
  lastModified: Date | string;
  changeFrequency: "always" | "hourly" | "daily" | "weekly" | "monthly" | "yearly" | "never";
  priority: number;
}

async function getFilterContext() {
  try {
    const internalUrl = getInternalApiUrl();
    const res = await fetch(`${internalUrl}/api/nucleo/filter-context/`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    return null;
  }
}

async function getAllGrupos() {
  const filterData = await getFilterContext();
  if (!filterData?.competiciones) return [];

  const grupos: Array<{ competicionSlug: string; grupoSlug: string }> = [];

  // El endpoint grupo-info necesita competicion_slug y grupo_slug
  // Por ahora, intentamos construir los slugs desde los datos disponibles
  // Si no están disponibles, los generamos desde el nombre o ID
  for (const competicion of filterData.competiciones) {
    if (competicion.grupos) {
      for (const grupo of competicion.grupos) {
        // Intentamos usar slugs si están disponibles
        const competicionSlug = competicion.slug || 
          (competicion.nombre ? competicion.nombre.toLowerCase().replace(/\s+/g, "-") : null);
        const grupoSlug = grupo.slug || 
          (grupo.nombre ? grupo.nombre.toLowerCase().replace(/\s+/g, "-") : null);
        
        if (competicionSlug && grupoSlug) {
          grupos.push({
            competicionSlug,
            grupoSlug,
          });
        }
      }
    }
  }

  return grupos;
}

async function getAllClubs() {
  try {
    const baseUrl = getApiBaseUrl();
    const res = await fetch(`${baseUrl}/api/clubes/`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data || [];
  } catch (error) {
    return [];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const entries: SitemapEntry[] = [];

  // Páginas estáticas
  const staticPages = [
    { path: "/", priority: 1.0, changeFreq: "daily" as const },
    { path: "/rankings/equipos", priority: 0.9, changeFreq: "daily" as const },
    { path: "/rankings/mvp", priority: 0.9, changeFreq: "daily" as const },
    { path: "/mvp", priority: 0.8, changeFreq: "weekly" as const },
    { path: "/clasificacion", priority: 0.8, changeFreq: "weekly" as const },
    { path: "/clubes", priority: 0.8, changeFreq: "weekly" as const },
  ];

  for (const lang of languages) {
    for (const page of staticPages) {
      entries.push({
        url: `${siteUrl}/${lang}${page.path}`,
        lastModified: new Date(),
        changeFrequency: page.changeFreq,
        priority: page.priority,
      });
    }
  }

  // Grupos (dinámicos)
  try {
    const grupos = await getAllGrupos();
    for (const lang of languages) {
      for (const grupo of grupos) {
        entries.push({
          url: `${siteUrl}/${lang}/competicion/${grupo.competicionSlug}/${grupo.grupoSlug}`,
          lastModified: new Date(),
          changeFrequency: "weekly",
          priority: 0.8,
        });
        entries.push({
          url: `${siteUrl}/${lang}/clasificacion/${grupo.competicionSlug}/${grupo.grupoSlug}`,
          lastModified: new Date(),
          changeFrequency: "weekly",
          priority: 0.7,
        });
        entries.push({
          url: `${siteUrl}/${lang}/competicion/mvp/${grupo.competicionSlug}/${grupo.grupoSlug}`,
          lastModified: new Date(),
          changeFrequency: "weekly",
          priority: 0.7,
        });
        entries.push({
          url: `${siteUrl}/${lang}/competicion/${grupo.competicionSlug}/${grupo.grupoSlug}/clasificacion`,
          lastModified: new Date(),
          changeFrequency: "weekly",
          priority: 0.7,
        });
      }
    }
  } catch (error) {
    console.error("Error generating grupo sitemap entries:", error);
  }

  // Clubs (dinámicos)
  try {
    const clubs = await getAllClubs();
    for (const lang of languages) {
      for (const club of clubs) {
        if (club.id) {
          entries.push({
            url: `${siteUrl}/${lang}/clubes/${club.id}`,
            lastModified: new Date(),
            changeFrequency: "weekly",
            priority: 0.7,
          });
        }
      }
    }
  } catch (error) {
    console.error("Error generating club sitemap entries:", error);
  }

  return entries;
}

