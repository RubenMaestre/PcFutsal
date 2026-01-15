"use client";

import React from "react";
import Link from "next/link";
import { useSancionesJornada } from "../hooks/useSancionesJornada";

export default function SancionesJornadaCard({ grupoId, jornada, dict, lang = "es" }: any) {
  const { loading, error, sancionados } = useSancionesJornada(grupoId, jornada);

  if (!grupoId)
    return <p className="text-xs text-[var(--color-text-secondary)]">{dict?.hint_select_group}</p>;
  if (loading)
    return <p className="text-xs text-[var(--color-text-secondary)]">Cargando sancionados...</p>;
  if (error)
    return <p className="text-xs text-[var(--color-error)]">{error}</p>;
  if (!sancionados.length)
    return <p className="text-xs text-[var(--color-text-secondary)]">Sin sancionados esta jornada.</p>;

  return (
    <ul className="flex flex-col gap-2 text-[13px] leading-tight">
      {sancionados.map((s, idx) => (
        <li key={idx} className="flex items-center gap-3 bg-[var(--color-card)] border border-[var(--color-card)] rounded-lg px-3 py-2">
          <Link
            href={`/${lang}/jugadores/${(s as any).slug || s.jugador_id}`}
            className="flex items-center gap-3 flex-1 min-w-0 hover:text-brand-accent transition-colors"
          >
            <div className="w-9 h-9 rounded-lg overflow-hidden bg-[#1c1c1c] border border-[var(--color-card)] flex-shrink-0 flex items-center justify-center">
              {s.foto ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={s.foto} alt={s.nombre} className="w-full h-full object-cover" />
              ) : (
                <div className="text-[10px] text-[var(--color-text-secondary)]">-</div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="font-semibold truncate">{s.apodo || s.nombre}</div>
              <Link
                href={(s as any).club_slug ? `/${lang}/clubes/${(s as any).club_slug}` : `/${lang}/clubes/${s.club_id}`}
                className="text-[11px] text-[var(--color-text-secondary)] truncate hover:text-brand-accent transition-colors"
                onClick={(e) => e.stopPropagation()}
              >
                {s.club_nombre}
              </Link>
            </div>
          </Link>

          <div className="flex items-center gap-2 flex-shrink-0">
            {s.rojas > 0 && (
              <div className="flex items-center gap-1">
                <img src="/iconos/roja.png" alt="roja" className="w-4 h-4" /> <span>{s.rojas}</span>
              </div>
            )}
            {s.dobles_amarillas > 0 && (
              <div className="flex items-center gap-1">
                <img src="/iconos/doble_amarilla.png" alt="doble amarilla" className="w-4 h-4" /> <span>{s.dobles_amarillas}</span>
              </div>
            )}
            {s.amarillas > 0 && (
              <div className="flex items-center gap-1">
                <img src="/iconos/amarilla.png" alt="amarilla" className="w-4 h-4" /> <span>{s.amarillas}</span>
              </div>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
