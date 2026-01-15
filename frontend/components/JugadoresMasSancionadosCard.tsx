"use client";

import React from "react";
import Link from "next/link";
import { useSancionesJugadores } from "../hooks/useSancionesJugadores";

export default function JugadoresMasSancionadosCard({ grupoId, dict, lang = "es" }: any) {
  const { loading, error, jugadores } = useSancionesJugadores(grupoId);

  if (!grupoId)
    return <p className="text-xs text-[var(--color-text-secondary)]">{dict?.hint_select_group}</p>;
  if (loading)
    return <p className="text-xs text-[var(--color-text-secondary)]">Cargando jugadores...</p>;
  if (error)
    return <p className="text-xs text-[var(--color-error)]">{error}</p>;
  if (!jugadores.length)
    return <p className="text-xs text-[var(--color-text-secondary)]">Sin datos todavía.</p>;

  return (
    <ul className="flex flex-col gap-2 text-[13px] leading-tight">
      {jugadores.map((j, idx) => (
        <li key={idx} className="flex items-center gap-3 bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg px-3 py-2">
          <Link
            href={`/${lang}/jugadores/${j.slug || j.jugador_id}`}
            className="flex items-center gap-3 flex-1 min-w-0 hover:text-brand-accent transition-colors"
          >
            <div className="w-9 h-9 rounded-lg overflow-hidden bg-[#1c1c1c] border border-[var(--color-card)] flex-shrink-0 flex items-center justify-center">
              {j.foto ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={j.foto} alt={j.nombre} className="w-full h-full object-cover" />
              ) : (
                <div className="text-[10px] text-[var(--color-text-secondary)]">-</div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="font-semibold truncate">{j.apodo || j.nombre}</div>
              <Link
                href={j.club_slug ? `/${lang}/clubes/${j.club_slug}` : `/${lang}/clubes/${j.club_id}`}
                className="text-[11px] text-[var(--color-text-secondary)] truncate hover:text-brand-accent transition-colors"
                onClick={(e) => e.stopPropagation()}
              >
                {j.club_nombre}
              </Link>
            </div>
          </Link>

          <div className="flex items-center gap-2 flex-shrink-0">
            {j.rojas > 0 && <img src="/iconos/roja.png" alt="roja" className="w-4 h-4" />}
            {j.dobles_amarillas > 0 && <img src="/iconos/doble_amarilla.png" alt="doble" className="w-4 h-4" />}
            {j.amarillas > 0 && <img src="/iconos/amarilla.png" alt="amarilla" className="w-4 h-4" />}
            <span className="text-[12px] font-semibold">{j.puntos_disciplina}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}
