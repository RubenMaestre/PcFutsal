"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";

type LangOption = {
  code: string; // "es", "val", "en", ...
  label: string; // "Español", "Valencià", ...
  flag: string; // "/flags/spain.png"
};

type Props = {
  currentLang: string; // idioma actual (ej: "es")
  currentPath: string; // ruta actual (ej: "/es/competicion/tercera-division/grupo-xv")
};

export default function LanguageSwitcher({ currentLang, currentPath }: Props) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Lista de idiomas disponibles en el orden solicitado
  const LANGS: LangOption[] = [
    { code: "es", label: "Español", flag: "/flags/spain.png" },
    { code: "val", label: "Valencià", flag: "/flags/valenciana.png" },
    { code: "en", label: "English", flag: "/flags/ingles.png" },
    { code: "fr", label: "Français", flag: "/flags/frances.png" },
    { code: "it", label: "Italiano", flag: "/flags/italiano.png" },
    { code: "pt", label: "Português", flag: "/flags/portugues.png" },
    { code: "de", label: "Deutsch", flag: "/flags/aleman.png" },
  ];

  // Idioma activo
  const active = LANGS.find((l) => l.code === currentLang) ?? LANGS[0];

  // Cerrar el desplegable automáticamente al hacer click fuera del componente.
  // Esto mejora la UX al evitar que el menú se quede abierto cuando el usuario
  // hace click en otra parte de la página.
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    // Solo añadir el listener cuando el desplegable está abierto para optimizar rendimiento
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [open]);

  // Genera la URL con el nuevo idioma manteniendo la estructura de la ruta actual.
  // Si la URL ya tiene un idioma como primer segmento (ej: /es/...), lo sustituye.
  // Si no, lo añade al principio. Esto permite cambiar de idioma sin perder la navegación.
  const getLangUrl = (newLang: string) => {
    if (!currentPath) return `/${newLang}`;
    const parts = currentPath.split("/");
    // Si la URL tiene idioma como primer segmento (ej: /es/...),
    // lo sustituimos; si no, lo añadimos.
    if (parts.length > 1 && LANGS.some((l) => l.code === parts[1])) {
      parts[1] = newLang;
    } else {
      parts.splice(1, 0, newLang);
    }
    return parts.join("/") || `/${newLang}`;
  };

  return (
    <div className="relative" ref={containerRef}>
      {/* BOTÓN PRINCIPAL */}
      <button
        onClick={() => setOpen(!open)}
        className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-card border border-brand-card hover:bg-brand-navy overflow-hidden"
        title={active.label}
        aria-label="Cambiar idioma"
      >
        <Image
          src={active.flag}
          alt={active.label}
          width={24}
          height={24}
          className="object-cover"
        />
      </button>

      {/* DESPLEGABLE */}
      {open && (
        <div className="absolute right-0 mt-2 w-44 rounded-md border border-brand-card bg-brand-bg shadow-xl z-50">
          <ul className="py-1 text-[0.8rem] font-base text-brand-text">
            {LANGS.map((lang) => {
              const targetUrl = getLangUrl(lang.code);
              return (
                <li key={lang.code}>
                  <Link
                    href={targetUrl}
                    className={`flex items-center gap-2 px-3 py-2 hover:bg-brand-card ${
                      lang.code === currentLang
                        ? "text-brand-accent font-semibold"
                        : "text-brand-text"
                    }`}
                    onClick={() => setOpen(false)}
                  >
                    {/* bandera */}
                    <span className="flex h-5 w-5 items-center justify-center rounded-full overflow-hidden border border-brand-card bg-brand-card">
                      <Image
                        src={lang.flag}
                        alt={lang.label}
                        width={20}
                        height={20}
                        className="object-cover"
                      />
                    </span>
                    {/* nombre idioma */}
                    <span className="leading-none">{lang.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
