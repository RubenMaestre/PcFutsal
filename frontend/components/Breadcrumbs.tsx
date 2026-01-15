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
  // Generate schema.org breadcrumb
  const schema = generateBreadcrumbSchema(items);

  return (
    <>
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
                {index > 0 && (
                  <ChevronRight className="w-4 h-4 text-white/40" />
                )}
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




