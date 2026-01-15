// /app/[lang]/como-colaborar/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.como_colaborar?.meta_title || "Cómo colaborar con PC FUTSAL — Únete al Proyecto";
  const description = dict?.como_colaborar?.meta_description || "Descubre cómo colaborar con PC FUTSAL. Reclama tu perfil, verifica tu cuenta, aporta datos, fotos y ayuda a construir la mayor base de datos del futsal amateur.";
  
  return generateMetadataWithAlternates(
    lang,
    "/como-colaborar",
    title,
    description,
    undefined,
    dict
  );
}

export default async function ComoColaborarPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const C = dict?.como_colaborar || {};

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-3 text-brand-text">
          {C.title || "Cómo colaborar con PC FUTSAL"}
        </h1>
        <p className="text-lg text-brand-textSecondary italic">
          {C.subtitle || "(o cómo convertirte en parte del mayor proyecto de futsal del país sin sudar una gota… literalmente)"}
        </p>
      </div>

      {/* Intro */}
      <div className="mb-8 space-y-4 text-brand-textSecondary leading-relaxed">
        <p className="text-lg">{C.intro}</p>
        <p>{C.intro_items}</p>
        <p className="font-semibold">{C.intro_footer}</p>
        <p className="text-lg">{C.but}</p>
        <p>{C.ruben}</p>
        <p className="text-lg font-semibold">{C.so}</p>
      </div>

      {/* Sección: Bienvenido */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_bienvenido?.title || "¿Quieres ayudar? Bienvenido/a al equipo (sin pagar ficha)."}
        </h2>
        <p className="text-lg mb-6 text-brand-textSecondary">
          {C.section_bienvenido?.subtitle || "Aquí puedes colaborar de muchas maneras. Todas igual de importantes."}
        </p>
      </section>

      {/* Sección: Jugador */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_jugador?.title || "1) Reclama tu perfil de jugador"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {C.section_jugador?.intro}
        </p>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {C.section_jugador?.subtitle || "Así podrás:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {C.section_jugador?.items?.foto}</li>
          <li>• {C.section_jugador?.items?.datos}</li>
          <li>• {C.section_jugador?.items?.temporadas}</li>
          <li>• {C.section_jugador?.items?.votar}</li>
          <li>• {C.section_jugador?.items?.archivo}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {C.section_jugador?.footer}
        </p>
      </section>

      {/* Sección: Entrenador */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_entrenador?.title || "2) Si eres entrenador, únete como verificado"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {C.section_entrenador?.intro}
        </p>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {C.section_entrenador?.subtitle || "Podéis:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {C.section_entrenador?.items?.mvp}</li>
          <li>• {C.section_entrenador?.items?.puntuacion}</li>
          <li>• {C.section_entrenador?.items?.fotos_club}</li>
          <li>• {C.section_entrenador?.items?.validar}</li>
          <li>• {C.section_entrenador?.items?.decidir}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {C.section_entrenador?.footer}
        </p>
      </section>

      {/* Sección: Aficionado */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_aficionado?.title || "3) Aficionados del futsal: también sois importantes"}
        </h2>
        <div className="mb-4 text-brand-textSecondary">
          <p>{C.section_aficionado?.intro}</p>
          <p>{C.section_aficionado?.intro2}</p>
          <p>{C.section_aficionado?.intro3}</p>
        </div>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {C.section_aficionado?.subtitle || "Entonces aquí puedes:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {C.section_aficionado?.items?.votar}</li>
          <li>• {C.section_aficionado?.items?.rankings}</li>
          <li>• {C.section_aficionado?.items?.fantasy}</li>
          <li>• {C.section_aficionado?.items?.corregir}</li>
          <li>• {C.section_aficionado?.items?.fotos}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {C.section_aficionado?.footer}
        </p>
      </section>

      {/* Sección: Fotos */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_fotos?.title || "4) Ayuda con fotos, datos y contenido"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {C.section_fotos?.intro}
        </p>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {C.section_fotos?.subtitle || "Si puedes aportar:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {C.section_fotos?.items?.fotos_equipos}</li>
          <li>• {C.section_fotos?.items?.fotos_jugadores}</li>
          <li>• {C.section_fotos?.items?.historicos}</li>
          <li>• {C.section_fotos?.items?.trayectorias}</li>
          <li>• {C.section_fotos?.items?.pabellones}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold leading-relaxed">
          {C.section_fotos?.footer}
        </p>
      </section>

      {/* Sección: Correcciones */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_correcciones?.title || "5) Correcciones y aportes de temporadas antiguas"}
        </h2>
        <p className="text-lg mb-2 text-brand-textSecondary">
          {C.section_correcciones?.intro}
        </p>
        <p className="font-semibold mb-2 text-brand-textSecondary">
          {C.section_correcciones?.subtitle}
        </p>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {C.section_correcciones?.subtitle2 || "Puedes mandarnos:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {C.section_correcciones?.items?.temporadas}</li>
          <li>• {C.section_correcciones?.items?.estadisticas}</li>
          <li>• {C.section_correcciones?.items?.goles}</li>
          <li>• {C.section_correcciones?.items?.datos}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {C.section_correcciones?.footer}
        </p>
      </section>

      {/* Sección: Compartir */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_compartir?.title || "6) Comparte, difunde, pica a tus colegas"}
        </h2>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {C.section_compartir?.items?.tarjeta}</li>
          <li>• {C.section_compartir?.items?.fantasy}</li>
          <li>• {C.section_compartir?.items?.medalla}</li>
          <li>• {C.section_compartir?.items?.ranking}</li>
          <li>• {C.section_compartir?.items?.cualquier}</li>
        </ul>
        <div className="space-y-2 text-brand-textSecondary">
          <p>{C.section_compartir?.footer1}</p>
          <p>{C.section_compartir?.footer2}</p>
          <p className="font-semibold">{C.section_compartir?.footer3}</p>
        </div>
      </section>

      {/* Sección: Cómo empezar */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {C.section_como_empezar?.title || "¿Cómo empezar?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {C.section_como_empezar?.subtitle || "Muy fácil:"}
        </p>
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 mb-6">
          <p className="font-semibold mb-2 text-brand-text">
            📧 {C.section_como_empezar?.email_label || "Escríbenos aquí:"}
          </p>
          <p className="text-xl">
            <a 
              href={`mailto:${C.section_como_empezar?.email || "contacto@pcfutsal.es"}`}
              className="text-brand-accent hover:underline font-medium"
            >
              👉 {C.section_como_empezar?.email || "contacto@pcfutsal.es"}
            </a>
          </p>
        </div>
        <p className="text-lg mb-4 text-brand-textSecondary font-semibold">
          {C.section_como_empezar?.or || "O simplemente:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {C.section_como_empezar?.items?.reclamar}</li>
          <li>• {C.section_como_empezar?.items?.verificar}</li>
          <li>• {C.section_como_empezar?.items?.actualizar}</li>
          <li>• {C.section_como_empezar?.items?.aportar}</li>
          <li>• {C.section_como_empezar?.items?.fantasy}</li>
          <li>• {C.section_como_empezar?.items?.votar}</li>
          <li>• {C.section_como_empezar?.items?.goat}</li>
        </ul>
        <div className="space-y-2 text-brand-textSecondary">
          <p className="font-semibold">{C.section_como_empezar?.footer1}</p>
          <p className="font-semibold">{C.section_como_empezar?.footer2}</p>
        </div>
      </section>

      {/* Footer */}
      <div className="mt-12 pt-8 border-t border-brand-card text-center">
        <h2 className="text-3xl font-bold mb-2 text-brand-accent">
          {C.footer?.title || "PC FUTSAL"}
        </h2>
        <p className="text-lg text-brand-textSecondary italic">
          {C.footer?.subtitle || "Donde los goles valen… y los datos también."}
        </p>
      </div>
    </div>
  );
}















