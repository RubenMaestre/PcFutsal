import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const baseUrl = "https://pcfutsal.es";

  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/api/",
          "/admin/",
          "/backend/",
          "/_next/",
          "/static/",
          "/*?*", // Bloquear parámetros de query para evitar duplicados
          "/*&*",
        ],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}




