"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import MatchCard, { MatchData } from "./MatchCard";

export default function MatchCarousel({
  matches,
  divisionLogoSrc,
  dict,
  // 👇 nuevo
  starMatchId = null,
  lang = "es",
}: {
  matches: MatchData[];
  divisionLogoSrc: string;
  dict: any;
  starMatchId?: string | number | null;
  lang?: string;
}) {
  const trackRef = React.useRef<HTMLDivElement | null>(null);

  // === AUTO-SLIDE CADA 7s (sin hacer scroll vertical en la página) ===
  React.useEffect(() => {
    const track = trackRef.current;
    if (!track || !matches?.length) return;

    let index = 0;

    const interval = setInterval(() => {
      if (!track) return;
      const slides = track.children;
      if (!slides.length) return;

      index = (index + 1) % slides.length;
      const next = slides[index] as HTMLElement;
      if (!next) return;

      // scroll horizontal suave solo dentro del carrusel
      const offsetLeft = next.offsetLeft;
      track.scrollTo({
        left: offsetLeft,
        behavior: "smooth",
      });
    }, 7000);

    return () => clearInterval(interval);
  }, [matches]);

  // === SCROLL MANUAL CON FLECHAS (solo desktop) ===
  const scrollByAmount = (dir: "left" | "right") => {
    const track = trackRef.current;
    if (!track) return;
    const scrollWidth = track.clientWidth * 0.9; // avanza aprox. 3 cards en desktop
    track.scrollBy({
      left: dir === "left" ? -scrollWidth : scrollWidth,
      behavior: "smooth",
    });
  };

  if (!matches || matches.length === 0) return null;

  return (
    <div className="relative">
      {/* Flecha izquierda (desktop) */}
      <button
        onClick={() => scrollByAmount("left")}
        className="
          hidden lg:flex
          absolute left-0 top-1/2 -translate-y-1/2 z-10
          w-10 h-10 rounded-full bg-black/50 hover:bg-black/70
          items-center justify-center text-white
          transition
        "
      >
        <ChevronLeft size={22} />
      </button>

      {/* Flecha derecha (desktop) */}
      <button
        onClick={() => scrollByAmount("right")}
        className="
          hidden lg:flex
          absolute right-0 top-1/2 -translate-y-1/2 z-10
          w-10 h-10 rounded-full bg-black/50 hover:bg-black/70
          items-center justify-center text-white
          transition
        "
      >
        <ChevronRight size={22} />
      </button>

      {/* Track del carrusel */}
      <div
        ref={trackRef}
        className="
          flex gap-4 overflow-x-auto pb-6 no-scrollbar
          snap-x snap-mandatory scroll-smooth scroll-pl-4
        "
        style={{ WebkitOverflowScrolling: "touch" }}
      >
        {matches.map((m) => {
          // 👇 calculamos si este partido es el estrella
          const isStar =
            starMatchId !== null &&
            (String(starMatchId) === String(m.id) ||
              (m.identificador_federacion &&
                String(starMatchId) === String(m.identificador_federacion)));

          return (
            <div
              key={m.id}
              className="
                snap-start flex-shrink-0
                w-[90%] sm:w-[60%] lg:w-[33.333%] max-w-[400px]
              "
            >
              <MatchCard
                match={m}
                divisionLogoSrc={divisionLogoSrc}
                dict={dict}
                /* 👇 lo forzamos a boolean para que TS no llore */
                isStar={Boolean(isStar)}
                lang={lang}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
