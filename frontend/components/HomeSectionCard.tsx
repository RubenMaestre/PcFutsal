// components/HomeSectionCard.tsx
"use client";

import React from "react";

type Props = {
  title?: string;
  description?: string;
  children?: React.ReactNode;
};

export default function HomeSectionCard({ title, description, children }: Props) {
  return (
    <div className="col-span-1 rounded-xl border border-brand-card bg-brand-card p-2 sm:p-4">
      {/* Header del card (opcional) */}
      {title ? (
        <header className="mb-3">
          <h2 className="text-sm text-brand-textSecondary font-title font-semibold uppercase tracking-wide">
            {title}
          </h2>

          {description && (
            <p className="mt-1 text-brand-textSecondary text-xs font-base leading-snug">
              {description}
            </p>
          )}
        </header>
      ) : null}

      {/* Contenido libre dentro del card */}
      <div>{children}</div>
    </div>
  );
}
