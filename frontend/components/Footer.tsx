"use client";

import React from "react";
import { useRouter } from "next/navigation";

type FooterProps = {
  dict: any;
  lang: "es" | "val" | "en" | "fr" | "it" | "pt" | "de";
};

export default function Footer({ dict, lang }: FooterProps) {
  const router = useRouter();
  const currentYear = new Date().getFullYear();

  const goTo = (slug: string) => {
    router.push(`/${lang}/${slug}`);
  };

  return (
    <footer className="w-full text-sm text-brand-text bg-brand-bg border-t border-brand-card mt-10">
      {/* CONTENIDO PRINCIPAL */}
      <div className="mx-auto max-w-7xl px-4 py-8 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        {/* IZQUIERDA */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-auto flex items-center justify-center">
            <img src="/logo/pcfutsal.png" alt={dict?.header?.logo_alt || "PC FUTSAL Logo"} className="h-10 w-auto object-contain" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-base font-title font-black uppercase tracking-wide text-brand-text">
              {dict?.nav?.brand || "PC FUTSAL"}
            </span>
            {dict?.nav?.brand_subtitle ? (
              <span className="text-[0.7rem] text-brand-textSecondary">{dict.nav.brand_subtitle}</span>
            ) : null}
          </div>
        </div>

        {/* CENTRO */}
        <nav className="flex flex-wrap gap-x-5 gap-y-2 text-[0.7rem] font-medium text-brand-textSecondary">
          <button onClick={() => router.push(`/${lang}`)} className="hover:text-brand-text transition-colors">
            {dict?.topbar?.info_links?.home || "Inicio"}
          </button>
          <span className="hidden md:inline text-brand-textSecondary/40">|</span>

          <button onClick={() => goTo("que-es-pc-futsal")} className="hover:text-brand-text transition-colors">
            {dict?.topbar?.info_links?.que_es}
          </button>
          <span className="hidden md:inline text-brand-textSecondary/40">|</span>

          <button onClick={() => goTo("quienes-somos")} className="hover:text-brand-text transition-colors">
            {dict?.topbar?.info_links?.about}
          </button>
          <span className="hidden md:inline text-brand-textSecondary/40">|</span>

          <button onClick={() => goTo("como-colaborar")} className="hover:text-brand-text transition-colors">
            {dict?.topbar?.info_links?.collaborate}
          </button>
          <span className="hidden md:inline text-brand-textSecondary/40">|</span>

          <button onClick={() => goTo("solicitar-perfil")} className="hover:text-brand-text transition-colors">
            {dict?.topbar?.info_links?.request_profile}
          </button>
          <span className="hidden md:inline text-brand-textSecondary/40">|</span>

          <button onClick={() => goTo("contacto")} className="hover:text-brand-text transition-colors">
            {dict?.topbar?.info_links?.contact}
          </button>
        </nav>

        {/* DERECHA */}
        <div className="text-[0.65rem] text-brand-textSecondary text-right md:text-left">
          <span className="font-semibold text-brand-text">
            {dict?.footer?.copyright || "© PC FUTSAL"} {currentYear}
          </span>{" "}
          — {dict?.footer?.claim || "Donde los goles valen… y los datos también."}
        </div>
      </div>

      {/* BARRA DOBLE */}
      <div className="flex h-1 w-full">
        <div className="h-full flex-1 bg-brand-accent" />
        <div className="h-full flex-1 bg-brand-navy" />
      </div>

      {/* SUBFOOTER */}
      <div className="w-full bg-[#04050a] border-t border-brand-card/40">
        <div className="mx-auto max-w-7xl px-4 py-4">
          {/* ENLACES LEGALES */}
          <div className="flex flex-wrap gap-x-4 gap-y-2 text-[0.65rem] text-brand-textSecondary mb-3 pb-3 border-b border-brand-card/20">
            <button 
              onClick={() => goTo("legal/aviso-legal")} 
              className="hover:text-brand-text transition-colors"
            >
              {dict?.legal?.footer_links?.aviso_legal || "Aviso Legal"}
            </button>
            <span className="text-brand-textSecondary/40">|</span>
            <button 
              onClick={() => goTo("legal/privacidad")} 
              className="hover:text-brand-text transition-colors"
            >
              {dict?.legal?.footer_links?.privacidad || "Privacidad"}
            </button>
            <span className="text-brand-textSecondary/40">|</span>
            <button 
              onClick={() => goTo("legal/cookies")} 
              className="hover:text-brand-text transition-colors"
            >
              {dict?.legal?.footer_links?.cookies || "Cookies"}
            </button>
            <span className="text-brand-textSecondary/40">|</span>
            <button 
              onClick={() => goTo("contacto")} 
              className="hover:text-brand-text transition-colors"
            >
              {dict?.legal?.footer_links?.contacto || "Contacto"}
            </button>
          </div>
          
          {/* AUTOR Y CRÉDITOS */}
          <div className="text-[0.65rem] text-brand-textSecondary flex flex-col gap-2">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
              <p className="leading-snug">
                {dict?.footer?.author_line || "Diseñado y creado por"}{" "}
                <a
                  href="https://digital.rubenmaestre.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-brand-text hover:text-brand-accent font-semibold"
                >
                  {dict?.footer?.cta_author || "Rubén Maestre"}
                </a>{" "}
                –{" "}
                {dict?.footer?.author_role ||
                  "Científico y Analista de Datos, Inteligencia Artificial, Python – Proyectos Digitales"}
              </p>
              <p className="text-[0.6rem] text-brand-textSecondary/70">
                {dict?.footer?.made_with || "Hecho con futsal real, datos y un poco de mala leche deportiva."}
              </p>
            </div>
            <p className="text-[0.65rem] text-brand-textSecondary/80 mt-1">
              <a
                href="https://www.rumaza.io"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-brand-accent transition-colors"
              >
                {dict?.footer?.company_info || "RUMAZA SYSTEMS S.L. - RUMAZA STUDIO - www.rumaza.io"}
              </a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
