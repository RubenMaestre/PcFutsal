"use client";

import React from "react";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { generateBreadcrumbSchema } from "../lib/schema";

type BreadcrumbItem = {
  name: string;
  url: string;
};

type Props = {
  items: BreadcrumbItem[];
  lang: string;
};

export default function Breadcrumbs({ items, lang }: Props) {
  // Generar schema.org breadcrumb para SEO.
  // Esto ayuda a los motores de búsqueda a entender la estructura de navegación del sitio.
  const schema = generateBreadcrumbSchema(items);

  return (
    <>
      {/* Schema.org JSON-LD para SEO. Los motores de búsqueda usan esto
          para mostrar breadcrumbs en los resultados de búsqueda. */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      <nav aria-label="Breadcrumb" className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-white/70 flex-wrap">
          {items.map((item, index) => {
            const isLast = index === items.length - 1;
            return (
              <li key={index} className="flex items-center gap-2">
                {/* Separador entre items (no se muestra antes del primer item) */}
                {index > 0 && (
                  <ChevronRight className="w-4 h-4 text-white/40" />
                )}
                {/* El último item no es un enlace, solo texto (página actual) */}
                {isLast ? (
                  <span className="text-white font-medium" aria-current="page">
                    {item.name}
                  </span>
                ) : (
                  <Link
                    href={item.url}
                    className="hover:text-white transition-colors"
                  >
                    {item.name}
                  </Link>
                )}
              </li>
            );
          })}
        </ol>
      </nav>
    </>
  );
}




