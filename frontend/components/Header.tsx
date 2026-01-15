"use client";

import React, { useState } from "react";
import { Search, Menu, X, ChevronDown, Globe } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import LanguageSwitcher from "./LanguageSwitcher";

type HeaderProps = {
  dict: {
    topbar: {
      last_update_label: string;
      info_links: {
        home: string;
        que_es: string;
        about: string;
        collaborate: string;
        request_profile: string;
        contact: string;
      };
      cta_register: string;
    };
    nav: {
      pilot_label: string;
      brand: string;
      brand_subtitle?: string;
      menu: {
        table: string;
        matches: string;
        players: string;
        clubs?: string;
        rankings: string;
        fantasy: string;
      };
      potw: string;
    };
    language_label: string;
    header?: {
      rankings_mvp?: string;
      rankings_equipos?: string;
      rankings_goleadores?: string;
      rankings_tarjetas?: string;
      logo_alt?: string;
    };
  };
  lang: "es" | "val" | "en" | "fr" | "it" | "pt" | "de";
  lastUpdate: string;
};

export default function Header({ dict, lang, lastUpdate }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [rankingsOpen, setRankingsOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  const goHome = () => {
    router.push(`/${lang}`);
    setMobileMenuOpen(false);
  };

  const goToClasificacion = () => {
    router.push(`/${lang}/clasificacion`);
    setMobileMenuOpen(false);
  };

  const goToClubes = () => {
    router.push(`/${lang}/clubes`);
    setMobileMenuOpen(false);
  };

  const goToJugadores = () => {
    router.push(`/${lang}/jugadores`);
    setMobileMenuOpen(false);
  };

  const goToRanking = (sub: string) => {
    router.push(`/${lang}/rankings/${sub}`);
    setRankingsOpen(false);
    setMobileMenuOpen(false);
  };

  return (
    <>
      <header className="w-full text-sm tracking-wide font-base text-brand-text border-b border-brand-card">
        {/* ================= TOP BAR ================= */}
        <div className="w-full bg-brand-bg text-brand-text border-b border-brand-card">
          <div className="mx-auto max-w-7xl px-4 py-2 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between lg:gap-4">
            {/* IZQUIERDA */}
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:gap-4 lg:flex-[1_1_auto] lg:min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center gap-2 rounded-full bg-brand-card/80 px-3 py-1 text-[0.7rem] font-bold leading-none text-brand-text shadow-md border border-brand-card">
                  <div className="flex items-center gap-1">
                    <span className="block h-2 w-2 rounded-full bg-brand-accent" />
                    <span className="block h-2 w-2 rounded-full bg-brand-navy" />
                  </div>
                  <span className="whitespace-nowrap">
                    {dict.topbar.last_update_label}: {lastUpdate}
                  </span>
                </div>

                {/* idioma móvil */}
                <div className="shrink-0 lg:hidden">
                  <LanguageSwitcher currentLang={lang} currentPath={pathname} />
                </div>
              </div>

              {/* PÁGINAS DE INTERÉS */}
              <nav
                className="
                  -mx-4 px-4 flex items-center gap-4 text-[0.7rem] font-medium text-brand-textSecondary
                  overflow-x-auto whitespace-nowrap no-scrollbar
                  lg:mx-0 lg:px-0 lg:overflow-visible lg:flex lg:flex-row lg:flex-wrap lg:gap-4
                "
              >
                <button
                  onClick={() => router.push(`/${lang}`)}
                  className="hover:text-brand-text whitespace-nowrap"
                >
                  {dict.topbar.info_links.home}
                </button>
                <button
                  onClick={() => router.push(`/${lang}/que-es-pc-futsal`)}
                  className="hover:text-brand-text whitespace-nowrap"
                >
                  {dict.topbar.info_links.que_es}
                </button>
                <button
                  onClick={() => router.push(`/${lang}/quienes-somos`)}
                  className="hover:text-brand-text whitespace-nowrap"
                >
                  {dict.topbar.info_links.about}
                </button>
                <button
                  onClick={() => router.push(`/${lang}/como-colaborar`)}
                  className="hover:text-brand-text whitespace-nowrap"
                >
                  {dict.topbar.info_links.collaborate}
                </button>
                <button
                  onClick={() => router.push(`/${lang}/solicitar-perfil`)}
                  className="hover:text-brand-text whitespace-nowrap"
                >
                  {dict.topbar.info_links.request_profile}
                </button>
                <button
                  onClick={() => router.push(`/${lang}/contacto`)}
                  className="hover:text-brand-text whitespace-nowrap"
                >
                  {dict.topbar.info_links.contact}
                </button>
              </nav>
            </div>

            {/* DERECHA */}
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:gap-4 lg:flex-none">
              <div className="w-full lg:w-auto">
                <button className="w-full lg:w-auto rounded-md bg-brand-accent px-3 py-1.5 text-brand-text hover:brightness-110 text-[0.7rem] font-extrabold uppercase font-title tracking-wide text-center whitespace-nowrap">
                  {dict.topbar.cta_register}
                </button>
              </div>

              {/* idioma desktop */}
              <div className="hidden lg:block shrink-0">
                <LanguageSwitcher currentLang={lang} currentPath={pathname} />
              </div>
            </div>
          </div>
        </div>

        {/* ================= NAV BAR ================= */}
        <div className="w-full bg-brand-bg text-brand-text">
          <div className="mx-auto max-w-7xl px-4 py-3 flex items-start justify-between gap-4 lg:items-center">
            {/* LOGO */}
            <div
              className="flex items-start gap-3 cursor-pointer"
              onClick={goHome}
            >
              <div className="flex items-center justify-center h-10 w-auto shrink-0">
                  <img
                  src="/logo/pcfutsal.png"
                  alt={dict?.header?.logo_alt || "PC FUTSAL Logo"}
                  className="h-10 w-auto object-contain"
                />
              </div>

              <div className="flex flex-col leading-tight">
                <span className="text-[0.65rem] font-base font-bold uppercase text-brand-textSecondary tracking-wide">
                  {dict.nav.pilot_label}
                </span>
                <span className="text-base font-title font-black uppercase text-brand-text tracking-wide">
                  {dict.nav.brand}
                </span>
                {dict.nav.brand_subtitle && (
                  <span className="text-[0.6rem] font-base font-medium text-brand-textSecondary leading-snug">
                    {dict.nav.brand_subtitle}
                  </span>
                )}
              </div>
            </div>

            {/* MENÚ DESKTOP */}
            <nav className="relative hidden lg:flex gap-6 text-[0.75rem] font-extrabold uppercase text-brand-text font-base items-center">
              <button
                onClick={goToClasificacion}
                className="hover:text-brand-accent"
              >
                {dict.nav.menu.table}
              </button>
              <button
                onClick={() => {
                  router.push(`/${lang}/partidos`);
                  setMobileMenuOpen(false);
                }}
                className="hover:text-brand-accent"
              >
                {dict.nav.menu.matches}
              </button>
              <button onClick={goToJugadores} className="hover:text-brand-accent">
                {dict.nav.menu.players}
              </button>
              <button onClick={goToClubes} className="hover:text-brand-accent">
                {dict.nav.menu.clubs || "Clubes"}
              </button>

              {/* NUEVO: DESPLEGABLE RANKINGS */}
              <div className="relative">
                <button
                  onClick={() => setRankingsOpen(!rankingsOpen)}
                  className="flex items-center gap-1 hover:text-brand-accent"
                >
                  {dict.nav.menu.rankings}
                  <ChevronDown
                    className={`h-3 w-3 transition-transform duration-200 ${
                      rankingsOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {rankingsOpen && (
                  <div className="absolute left-0 mt-2 w-48 bg-[#0D0D0D] border border-brand-card rounded-md shadow-lg z-50">
                    {[
                      { key: "mvp", label: dict?.header?.rankings_mvp || "MVP" },
                      { key: "equipos", label: dict?.header?.rankings_equipos || "Equipos" },
                      { key: "goleadores", label: dict?.header?.rankings_goleadores || "Goleadores" },
                      { key: "tarjetas", label: dict?.header?.rankings_tarjetas || "Tarjetas" },
                    ].map((item) => (
                      <button
                        key={item.key}
                        onClick={() => goToRanking(item.key)}
                        className="w-full text-left px-4 py-2 text-xs hover:bg-brand-card/60 text-brand-text"
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <button className="hover:text-brand-accent">
                {dict.nav.menu.fantasy}
              </button>
            </nav>

            {/* DERECHA */}
            <div className="flex items-center gap-3 shrink-0">
              <button className="hidden lg:flex items-center gap-2 text-[0.7rem] font-extrabold uppercase text-brand-text hover:text-brand-accent font-base">
                <span className="block h-[18px] w-[18px] rounded-sm bg-brand-warning text-[0.6rem] font-black leading-[18px] text-black shadow-[0_0_0_2px_rgba(0,0,0,0.8)] font-title tracking-wide text-center">
                  ★
                </span>
                <span>{dict.nav.potw}</span>
              </button>
              <button
                onClick={() => router.push(`/${lang}/web-club`)}
                className="hidden lg:flex items-center gap-2 text-[0.7rem] font-extrabold uppercase text-brand-text hover:text-brand-accent font-base"
              >
                <span className="flex h-[18px] w-[18px] items-center justify-center rounded-sm bg-brand-accent text-[0.6rem] font-black leading-[18px] text-black shadow-[0_0_0_2px_rgba(0,0,0,0.8)] font-title tracking-wide">
                  <Globe className="h-3 w-3 text-black" />
                </span>
                <span>{(dict?.nav as any)?.web_club || "Web para tu club"}</span>
              </button>

              <button className="flex h-8 w-8 items-center justify-center rounded-full border border-brand-card bg-brand-bg text-brand-text hover:text-brand-accent">
                <Search className="h-4 w-4" />
              </button>

              <button
                className="flex h-8 w-8 items-center justify-center rounded-md border border-brand-card bg-brand-card text-brand-text hover:text-brand-accent lg:hidden"
                onClick={() => setMobileMenuOpen(true)}
              >
                <Menu className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="flex h-1 w-full border-t border-brand-card">
            <div className="h-full flex-1 bg-brand-accent" />
            <div className="h-full flex-1 bg-brand-navy" />
          </div>
        </div>
      </header>

      {/* ================= MENÚ MÓVIL ================= */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-[9999] flex lg:hidden">
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative ml-auto h-full w-[80%] max-w-[320px] bg-brand-bg border-l border-brand-card shadow-xl flex flex-col">
            {/* encabezado móvil */}
            <div className="flex items-center justify-between px-4 py-4 border-b border-brand-card">
              <div
                className="flex items-start gap-2 cursor-pointer"
                onClick={goHome}
              >
                <div className="h-8 w-auto flex items-center">
                  <img
                    src="/logo/pcfutsal.png"
                    alt={dict?.header?.logo_alt || "PC FUTSAL Logo"}
                    className="h-8 w-auto object-contain"
                  />
                </div>
                <div className="flex flex-col leading-tight">
                  <span className="text-[0.6rem] font-base font-bold uppercase text-brand-textSecondary tracking-wide">
                    {dict.nav.pilot_label}
                  </span>
                  <span className="text-sm font-title font-black uppercase text-brand-text tracking-wide leading-none">
                    {dict.nav.brand}
                  </span>
                </div>
              </div>

              <button
                className="flex h-8 w-8 items-center justify-center rounded-md border border-brand-card bg-brand-card text-brand-text hover:text-brand-accent"
                onClick={() => setMobileMenuOpen(false)}
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <nav className="flex flex-col px-4 py-4 text-[0.9rem] font-extrabold uppercase font-base text-brand-text">
              <button
                onClick={() => router.push(`/${lang}`)}
                className="text-left w-full py-3 border-b border-brand-card hover:text-brand-accent"
              >
                {dict.topbar.info_links.home}
              </button>
              <button
                onClick={goToClasificacion}
                className="text-left w-full py-3 border-b border-brand-card hover:text-brand-accent"
              >
                {dict.nav.menu.table}
              </button>
              <button
                onClick={() => {
                  router.push(`/${lang}/partidos`);
                  setMobileMenuOpen(false);
                }}
                className="text-left w-full py-3 border-b border-brand-card hover:text-brand-accent"
              >
                {dict.nav.menu.matches}
              </button>
              <button
                onClick={goToJugadores}
                className="text-left w-full py-3 border-b border-brand-card hover:text-brand-accent"
              >
                {dict.nav.menu.players}
              </button>
              <button
                onClick={goToClubes}
                className="text-left w-full py-3 border-b border-brand-card hover:text-brand-accent"
              >
                {dict.nav.menu.clubs || "Clubes"}
              </button>

              {/* NUEVO: SUBMENÚ RANKINGS EN MÓVIL */}
              <div className="flex flex-col border-b border-brand-card">
                <button
                  onClick={() => setRankingsOpen(!rankingsOpen)}
                  className="flex items-center justify-between w-full py-3 hover:text-brand-accent"
                >
                  <span>{dict.nav.menu.rankings}</span>
                  <ChevronDown
                    className={`h-4 w-4 transition-transform ${
                      rankingsOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {rankingsOpen && (
                  <div className="flex flex-col pl-4 pb-2">
                    {[
                      { key: "mvp", label: dict?.header?.rankings_mvp || "MVP" },
                      { key: "equipos", label: dict?.header?.rankings_equipos || "Equipos" },
                      { key: "goleadores", label: dict?.header?.rankings_goleadores || "Goleadores" },
                      { key: "tarjetas", label: dict?.header?.rankings_tarjetas || "Tarjetas" },
                    ].map((item) => (
                      <button
                        key={item.key}
                        onClick={() => goToRanking(item.key)}
                        className="text-left py-2 text-sm text-brand-text hover:text-brand-accent"
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <button className="text-left w-full py-3 border-b border-brand-card hover:text-brand-accent">
                {dict.nav.menu.fantasy}
              </button>
            </nav>

            <div className="mt-auto px-4 pb-6 pt-2 border-t border-brand-card">
              <button className="w-full rounded-md bg-brand-accent px-4 py-3 text-brand-text hover:brightness-110 text-[0.8rem] font-extrabold uppercase font-title tracking-wide text-center">
                {dict.topbar.cta_register}
              </button>
            </div>

            <div className="flex h-1 w-full">
              <div className="h-full flex-1 bg-brand-accent" />
              <div className="h-full flex-1 bg-brand-navy" />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
