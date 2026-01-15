// /frontend/rankings_components/MVPPodium.tsx
"use client";

import React from "react";
import Link from "next/link";

type MVPTop3Row = {
  jugador_id: number;
  nombre: string;
  slug?: string | null;
  foto: string;
  club_id: number | null;
  club_nombre: string;
  club_escudo: string;
  puntos: number | null;
  puntos_semana?: number | null;
  puntos_global: number;
  coef_division: number;
  goles_jornada?: number;
  grupo_id: number;
  grupo_nombre: string;
  competicion_id: number;
  competicion_nombre: string;
};

type Props = {
  top3: MVPTop3Row[];
  lang: string;
  dict: any;
};

export default function MVPPodium({ top3, lang, dict }: Props) {
  if (!top3 || top3.length === 0) {
    return null;
  }

  // Ordenar: 1º, 2º, 3º
  const [first, second, third] = top3;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-end justify-center gap-4 relative">
        {/* 2º LUGAR (IZQUIERDA) */}
        {second && (
          <div className="flex flex-col items-center gap-4 flex-1 max-w-[280px]">
            {/* Foto del jugador */}
            <div className="relative w-28 h-28 rounded-full overflow-hidden border-4 border-[var(--color-podium-silver)] bg-brand-card">
              {second.foto ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={second.foto}
                  alt={second.nombre}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-brand-card flex items-center justify-center text-white/40 text-xs">
                  ?
                </div>
              )}
            </div>
            
            {/* Número 2º - Plata */}
            <div className="px-8 py-4 rounded-lg font-bold min-w-[100px] text-center shadow-lg" style={{ backgroundColor: '#C0C0C0', color: '#000000', fontSize: '2.5rem', fontWeight: '900' }}>
              2º
            </div>
            
            {/* Nombre del jugador */}
            <div className="text-center">
              <Link
                href={`/${lang}/jugadores/${second.jugador_id}${second.slug ? `/${second.slug}` : ""}`}
                className="text-white font-semibold text-lg hover:text-brand-primary transition-colors block"
              >
                {second.nombre}
              </Link>
            </div>
            
            {/* Escudo y nombre del club */}
            <div className="flex items-center gap-2">
              {second.club_escudo && (
                <div className="relative w-8 h-8">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={second.club_escudo}
                    alt={second.club_nombre || ""}
                    className="w-full h-full object-contain"
                  />
                </div>
              )}
              {second.club_nombre && (
                <div className="text-white/80 text-sm font-medium">{second.club_nombre}</div>
              )}
            </div>
            
            {/* Competición + Grupo */}
            {second.competicion_nombre && (
              <div className="text-center">
                <div className="text-white/60 text-xs">{second.competicion_nombre}</div>
                {second.grupo_nombre && (
                  <div className="text-white/50 text-xs">{second.grupo_nombre}</div>
                )}
              </div>
            )}
            
            {/* Puntos */}
            <div className="bg-brand-card border border-brand-card rounded-lg p-3 w-full text-center">
              <div className="text-white/60 text-xs">PTS Totales</div>
              <div className="text-white font-bold text-lg">{second.puntos_global}</div>
              {second.puntos_semana !== null && second.puntos_semana !== undefined && (
                <>
                  <div className="text-white/60 text-xs mt-2">PTS Semana</div>
                  <div className="text-white font-semibold">{second.puntos_semana}</div>
                </>
              )}
            </div>
          </div>
        )}

        {/* 1º LUGAR (CENTRO - MÁS ALTO) */}
        {first && (
          <div className="flex flex-col items-center gap-4 flex-1 max-w-[280px] relative z-10">
            {/* Foto del jugador */}
            <div className="relative w-36 h-36 rounded-full overflow-hidden border-4 border-[var(--color-podium-gold)] bg-brand-card shadow-lg">
              {first.foto ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={first.foto}
                  alt={first.nombre}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-brand-card flex items-center justify-center text-white/40 text-xs">
                  ?
                </div>
              )}
            </div>
            
            {/* Número 1º - Dorado */}
            <div className="px-10 py-5 rounded-lg font-bold min-w-[120px] text-center shadow-lg" style={{ backgroundColor: '#FFD700', color: '#000000', fontSize: '3.5rem', fontWeight: '900' }}>
              1º
            </div>
            
            {/* Nombre del jugador */}
            <div className="text-center">
              <Link
                href={`/${lang}/jugadores/${first.jugador_id}${first.slug ? `/${first.slug}` : ""}`}
                className="text-white font-bold text-xl hover:text-brand-primary transition-colors block"
              >
                {first.nombre}
              </Link>
            </div>
            
            {/* Escudo y nombre del club */}
            <div className="flex items-center gap-2">
              {first.club_escudo && (
                <div className="relative w-10 h-10">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={first.club_escudo}
                    alt={first.club_nombre || ""}
                    className="w-full h-full object-contain"
                  />
                </div>
              )}
              {first.club_nombre && (
                <div className="text-white/80 text-base font-medium">{first.club_nombre}</div>
              )}
            </div>
            
            {/* Competición + Grupo */}
            {first.competicion_nombre && (
              <div className="text-center">
                <div className="text-white/60 text-sm">{first.competicion_nombre}</div>
                {first.grupo_nombre && (
                  <div className="text-white/50 text-xs">{first.grupo_nombre}</div>
                )}
              </div>
            )}
            
            {/* Puntos */}
            <div className="bg-brand-card border border-brand-card rounded-lg p-4 w-full text-center shadow-lg">
              <div className="text-white/60 text-xs">PTS Totales</div>
              <div className="text-white font-bold text-2xl">{first.puntos_global}</div>
              {first.puntos_semana !== null && first.puntos_semana !== undefined && (
                <>
                  <div className="text-white/60 text-xs mt-2">PTS Semana</div>
                  <div className="text-white font-semibold text-lg">{first.puntos_semana}</div>
                </>
              )}
            </div>
          </div>
        )}

        {/* 3º LUGAR (DERECHA) */}
        {third && (
          <div className="flex flex-col items-center gap-4 flex-1 max-w-[280px]">
            {/* Foto del jugador */}
            <div className="relative w-28 h-28 rounded-full overflow-hidden border-4 border-[var(--color-podium-bronze)] bg-brand-card">
              {third.foto ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={third.foto}
                  alt={third.nombre}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-brand-card flex items-center justify-center text-white/40 text-xs">
                  ?
                </div>
              )}
            </div>
            
            {/* Número 3º - Bronce */}
            <div className="px-8 py-4 rounded-lg font-bold min-w-[100px] text-center shadow-lg" style={{ backgroundColor: '#CD7F32', color: '#FFFFFF', fontSize: '2.5rem', fontWeight: '900' }}>
              3º
            </div>
            
            {/* Nombre del jugador */}
            <div className="text-center">
              <Link
                href={`/${lang}/jugadores/${third.jugador_id}${third.slug ? `/${third.slug}` : ""}`}
                className="text-white font-semibold text-lg hover:text-brand-primary transition-colors block"
              >
                {third.nombre}
              </Link>
            </div>
            
            {/* Escudo y nombre del club */}
            <div className="flex items-center gap-2">
              {third.club_escudo && (
                <div className="relative w-8 h-8">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={third.club_escudo}
                    alt={third.club_nombre || ""}
                    className="w-full h-full object-contain"
                  />
                </div>
              )}
              {third.club_nombre && (
                <div className="text-white/80 text-sm font-medium">{third.club_nombre}</div>
              )}
            </div>
            
            {/* Competición + Grupo */}
            {third.competicion_nombre && (
              <div className="text-center">
                <div className="text-white/60 text-xs">{third.competicion_nombre}</div>
                {third.grupo_nombre && (
                  <div className="text-white/50 text-xs">{third.grupo_nombre}</div>
                )}
              </div>
            )}
            
            {/* Puntos */}
            <div className="bg-brand-card border border-brand-card rounded-lg p-3 w-full text-center">
              <div className="text-white/60 text-xs">PTS Totales</div>
              <div className="text-white font-bold text-lg">{third.puntos_global}</div>
              {third.puntos_semana !== null && third.puntos_semana !== undefined && (
                <>
                  <div className="text-white/60 text-xs mt-2">PTS Semana</div>
                  <div className="text-white font-semibold">{third.puntos_semana}</div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

