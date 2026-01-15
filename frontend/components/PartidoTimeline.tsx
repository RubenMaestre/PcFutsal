// /components/PartidoTimeline.tsx
"use client";

import React from "react";
import Link from "next/link";

type Evento = {
  id: number;
  minuto: number | null;
  tipo_evento: "gol" | "gol_pp" | "amarilla" | "doble_amarilla" | "roja" | "mvp";
  parte: "primera" | "segunda" | "prorroga" | "desconocida";
  jugador: {
    id: number;
    nombre: string;
    slug: string | null;
    foto: string;
  } | null;
  club: {
    id: number;
    nombre: string;
    slug: string | null;
    lado: "local" | "visitante" | null;
  } | null;
  nota: string;
};

type PartidoTimelineProps = {
  eventos: Evento[];
  local: {
    id: number;
    nombre: string;
    escudo: string;
    slug: string | null;
  };
  visitante: {
    id: number;
    nombre: string;
    escudo: string;
    slug: string | null;
  };
  dict: any;
  lang: string;
};

// Mapea el tipo de evento a un color CSS variable.
// Los colores se definen en el tema global, permitiendo cambiar la paleta fácilmente.
function getEventoColor(tipo: string) {
  switch (tipo) {
    case "gol":
    case "gol_pp":
      return "bg-[var(--color-success)]"; // Verde para goles (positivo)
    case "amarilla":
      return "bg-[var(--color-warning)]"; // Amarillo para tarjetas (advertencia)
    case "doble_amarilla":
      return "bg-[var(--color-warning)]"; // Mismo color que amarilla simple
    case "roja":
      return "bg-[var(--color-error)]"; // Rojo para tarjetas rojas (negativo)
    case "mvp":
      return "bg-[var(--color-gold)]"; // Dorado para MVP (destacado)
    default:
      return "bg-[var(--color-text-secondary)]"; // Gris para eventos desconocidos
  }
}

// Mapea el tipo de evento a un emoji/icono para mejor identificación visual.
// Los emojis son universales y no requieren carga de iconos externos.
function getEventoIcon(tipo: string) {
  switch (tipo) {
    case "gol":
    case "gol_pp":
      return "⚽"; // Balón para goles
    case "amarilla":
      return "🟨"; // Cuadrado amarillo para tarjeta amarilla
    case "doble_amarilla":
      return "🟨🟨"; // Dos cuadrados para doble amarilla
    case "roja":
      return "🟥"; // Cuadrado rojo para tarjeta roja
    case "mvp":
      return "⭐"; // Estrella para MVP
    default:
      return "•"; // Punto genérico para eventos desconocidos
  }
}

function TimelineParte({
  eventosParte,
  minInicio,
  minFin,
  titulo,
  local,
  visitante,
  dict,
  lang,
}: {
  eventosParte: Evento[];
  minInicio: number;
  minFin: number;
  titulo: string;
  local: { nombre: string };
  visitante: { nombre: string };
  dict: any;
  lang: string;
}) {
  const eventosFiltrados = eventosParte.filter((e) => e.minuto !== null);
  
  if (eventosFiltrados.length === 0) return null;

  const anchoTotal = minFin - minInicio; // 20 minutos para cada parte

  return (
    <div className="mb-8">
      <div className="text-lg font-bold text-white mb-4 pb-2 border-b-2 border-[var(--color-accent)]">
        {titulo}
      </div>
      
      {/* Línea temporal */}
      <div className="relative bg-brand-navy rounded-lg p-3 md:p-6 border border-[var(--color-navy)]/50 overflow-x-auto">
        {/* Área de la línea temporal - mínimo ancho para que funcione bien */}
        <div className="relative h-48 min-w-[600px] md:min-w-0">
          {/* Nombre del equipo LOCAL arriba */}
          <div className="absolute left-0 top-2 z-20 max-w-[40%] md:max-w-none">
            <div className="text-[10px] md:text-xs font-bold text-white bg-brand-card px-2 md:px-3 py-1 md:py-1.5 rounded border border-[var(--color-accent)]/50 truncate">
              {local.nombre}
            </div>
          </div>
          
          {/* Nombre del equipo VISITANTE abajo */}
          <div className="absolute left-0 bottom-2 z-20 max-w-[40%] md:max-w-none">
            <div className="text-[10px] md:text-xs font-bold text-white bg-brand-card px-2 md:px-3 py-1 md:py-1.5 rounded border border-[var(--color-accent)]/50 truncate">
              {visitante.nombre}
            </div>
          </div>
          
          {/* Línea central temporal */}
          <div className="absolute left-0 right-0 top-1/2 h-1 bg-white/60 transform -translate-y-1/2 rounded-full" />
          
          {/* Marcadores de minutos */}
          {Array.from({ length: Math.floor(anchoTotal / 5) + 1 }, (_, i) => {
            const minuto = minInicio + i * 5;
            if (minuto > minFin) return null;
            const porcentaje = ((minuto - minInicio) / anchoTotal) * 100;
            return (
              <div
                key={minuto}
                className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2"
                style={{ left: `${porcentaje}%` }}
              >
                {/* Marcador vertical */}
                <div className="w-0.5 h-6 bg-white/50" />
                {/* Etiqueta del minuto */}
                <div className="absolute top-8 left-1/2 transform -translate-x-1/2 text-[10px] md:text-[11px] text-white font-bold bg-brand-card px-1 md:px-1.5 py-0.5 rounded whitespace-nowrap">
                  {minuto}'
                </div>
              </div>
            );
          })}

          {/* Eventos - Local arriba, Visitante abajo */}
          {eventosFiltrados.map((evento) => {
            if (evento.minuto === null) return null;
            const porcentaje = ((evento.minuto - minInicio) / anchoTotal) * 100;
            const esLocal = evento.club?.lado === "local";
            
            return (
              <div
                key={evento.id}
                className="absolute transform -translate-x-1/2 z-10"
                style={{
                  left: `${porcentaje}%`,
                  top: esLocal ? "25%" : "65%",
                }}
              >
                {/* Línea vertical conectando con la línea temporal */}
                <div
                  className="absolute left-1/2 transform -translate-x-1/2 w-0.5 bg-[var(--color-accent)]/60"
                  style={{
                    top: esLocal ? "0%" : "50%",
                    bottom: esLocal ? "50%" : "0%",
                    height: esLocal ? "25%" : "15%",
                  }}
                />
                
                {/* Icono del evento */}
                <div
                  className={`relative ${getEventoColor(evento.tipo_evento)} rounded-full w-10 h-10 md:w-12 md:h-12 flex items-center justify-center shadow-xl border-2 border-brand-card cursor-pointer hover:scale-125 active:scale-125 transition-transform group touch-manipulation`}
                  title={`${evento.minuto}' - ${evento.jugador?.nombre || evento.nota || evento.tipo_evento}`}
                >
                  <span className="text-lg md:text-xl">{getEventoIcon(evento.tipo_evento)}</span>
                  
                  {/* Tooltip - visible en hover y touch */}
                  <div className={`absolute left-1/2 transform -translate-x-1/2 ${
                    esLocal ? "bottom-full mb-2 md:mb-3" : "top-full mt-2 md:mt-3"
                  } opacity-0 group-hover:opacity-100 group-active:opacity-100 transition-opacity pointer-events-none z-20`}>
                    <div className="bg-brand-card border-2 border-[var(--color-accent)] rounded-lg p-2 md:p-3 shadow-2xl whitespace-nowrap max-w-[200px]">
                      <div className="text-[10px] md:text-xs font-bold text-white mb-1">
                        {evento.minuto}'
                      </div>
                      {evento.jugador ? (
                        <Link
                          href={
                            evento.jugador.slug
                              ? `/${lang}/jugadores/${evento.jugador.slug}`
                              : `/${lang}/jugadores/${evento.jugador.id}`
                          }
                          className="text-[10px] md:text-xs text-[var(--color-accent)] hover:underline font-semibold"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {evento.jugador.nombre}
                        </Link>
                      ) : (
                        <div className="text-[10px] md:text-xs text-white/60">
                          {evento.nota || evento.tipo_evento}
                        </div>
                      )}
                      {evento.nota && evento.jugador && (
                        <div className="text-[9px] md:text-[10px] text-white/60 mt-1">
                          {evento.nota}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function PartidoTimeline({
  eventos,
  local,
  visitante,
  dict,
  lang,
}: PartidoTimelineProps) {
  const eventosPrimera = eventos.filter((e) => e.parte === "primera");
  const eventosSegunda = eventos.filter((e) => e.parte === "segunda");
  const eventosProrroga = eventos.filter((e) => e.parte === "prorroga");

  return (
    <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-4 md:p-6">
      <h2 className="text-xl md:text-2xl font-bold text-white mb-4 md:mb-6 font-[var(--font-title)]">
        {dict?.partidos?.timeline_title || "Línea del Tiempo"}
      </h2>

      {/* Primera Parte */}
      <TimelineParte
        eventosParte={eventosPrimera}
        minInicio={0}
        minFin={20}
        titulo={dict?.partidos?.primera_parte || "Primera Parte (0-20 min)"}
        local={local}
        visitante={visitante}
        dict={dict}
        lang={lang}
      />

      {/* Segunda Parte */}
      <TimelineParte
        eventosParte={eventosSegunda}
        minInicio={20}
        minFin={40}
        titulo={dict?.partidos?.segunda_parte || "Segunda Parte (20:01-40 min)"}
        local={local}
        visitante={visitante}
        dict={dict}
        lang={lang}
      />

      {/* Prórroga */}
      {eventosProrroga.length > 0 && (
        <div className="mb-6">
          <div className="text-lg font-bold text-white mb-4 pb-2 border-b-2 border-[var(--color-accent)]">
            {dict?.partidos?.prorroga || "Prórroga"}
          </div>
          <div className="bg-brand-navy rounded-lg p-4 border border-[var(--color-navy)]/50">
            <div className="space-y-2">
              {eventosProrroga.map((evento) => (
                <div
                  key={evento.id}
                  className="flex items-center gap-3 p-2 bg-brand-card rounded-lg"
                >
                  <div className={`${getEventoColor(evento.tipo_evento)} rounded-full w-8 h-8 flex items-center justify-center`}>
                    <span className="text-sm">{getEventoIcon(evento.tipo_evento)}</span>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-white">
                      {evento.minuto !== null ? `${evento.minuto}'` : ""}
                    </div>
                    {evento.jugador ? (
                      <Link
                        href={
                          evento.jugador.slug
                            ? `/${lang}/jugadores/${evento.jugador.slug}`
                            : `/${lang}/jugadores/${evento.jugador.id}`
                        }
                        className="text-sm text-[var(--color-accent)] hover:underline"
                      >
                        {evento.jugador.nombre}
                      </Link>
                    ) : (
                      <div className="text-sm text-white/60">
                        {evento.nota || evento.tipo_evento}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {eventos.length === 0 && (
        <div className="text-center text-white/60 py-12 bg-brand-navy rounded-lg border border-[var(--color-navy)]/50">
          {dict?.partidos?.no_eventos || "No hay eventos registrados"}
        </div>
      )}
    </div>
  );
}
