// components/ClubsGrid.tsx
"use client";

import React from "react";

type ClubLite = {
  id: number;
  nombre_oficial: string;
  nombre_corto?: string;
  localidad?: string;
  escudo_url?: string;
};

type Props = {
  clubs: ClubLite[];
  dict?: any;
  onSelectClub?: (clubId: number) => void; // por si lo quieres en modal o en ruta
  lang?: string;
};

export default function ClubsGrid({ clubs, dict, onSelectClub, lang }: Props) {
  if (!clubs || clubs.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        {dict?.clubs_page?.no_results || "No hay clubes en esta competición."}
      </div>
    );
  }

  return (
    <div
      className="
        grid gap-4
        grid-cols-2
        sm:grid-cols-3
        lg:grid-cols-4
      "
    >
      {clubs.map((club) => {
        // Prioridad: nombre_corto (más legible) > nombre_oficial (más formal)
        const nombre = club.nombre_corto || club.nombre_oficial;
        // Construir URL con idioma si está disponible, sino usar hash fallback
        const href =
          lang && club.id
            ? `/${lang}/clubes/${club.id}`
            : `#/clubes/${club.id}`;

        const cardContent = (
          <div className="flex flex-col items-center gap-2 bg-white/5 rounded-xl border border-white/10 p-3 hover:border-white/30 hover:bg-white/10 transition">
            {/* Mostrar escudo si está disponible, sino mostrar iniciales como fallback */}
            {club.escudo_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={club.escudo_url}
                alt={nombre}
                className="w-16 h-16 object-contain"
              />
            ) : (
              // Fallback: mostrar las dos primeras letras del nombre en un círculo
              <div className="w-16 h-16 rounded-full bg-slate-700/40 flex items-center justify-center text-sm">
                {nombre?.slice(0, 2)?.toUpperCase()}
              </div>
            )}

            <div className="text-center">
              <div className="text-sm font-semibold text-white">{nombre}</div>
              {club.localidad ? (
                <div className="text-[11px] text-slate-200/70">
                  {club.localidad}
                </div>
              ) : null}
            </div>
          </div>
        );

        // Si se pasa onSelectClub, el componente actúa como botón (útil para modales o selección).
        // Si no, actúa como enlace normal (navegación a la página del club).
        // Esto permite reutilizar el componente en diferentes contextos.
        if (onSelectClub) {
          return (
            <button
              key={club.id}
              onClick={() => onSelectClub(club.id)}
              className="text-left"
            >
              {cardContent}
            </button>
          );
        }

        // Enlace normal para navegación a la página del club
        return (
          <a key={club.id} href={href} className="block">
            {cardContent}
          </a>
        );
      })}
    </div>
  );
}
