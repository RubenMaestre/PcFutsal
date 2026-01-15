// /app/[lang]/web-club/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.web_club?.meta_title || "¿Quieres una web para tu club? — Diseño Web para Clubes de Futsal";
  const description = dict?.web_club?.meta_description || "Crea una web moderna y automática para tu club de futsal. Diseño profesional, datos en tiempo real, tarjetas FIFA y contenido automático. Presupuesto claro y adaptado.";
  
  return generateMetadataWithAlternates(
    lang,
    "/web-club",
    title,
    description,
    undefined,
    dict
  );
}

export default async function WebClubPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const W = dict?.web_club || {};

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-3 text-brand-text">
          {W.title || "¿Quieres una web para tu club?"}
        </h1>
        <p className="text-lg text-brand-textSecondary italic">
          {W.subtitle || "(Porque seguir usando el cartel del pabellón como \"página oficial\" ya no cuela)"}
        </p>
      </div>

      {/* Intro */}
      <div className="mb-8 space-y-4 text-brand-textSecondary leading-relaxed">
        <p className="text-lg">{W.intro}</p>
        <p className="text-lg">{W.intro2}</p>
        <p className="text-lg">{W.intro3}</p>
        <p className="text-lg font-semibold">{W.intro4}</p>
      </div>

      {/* Sección: ¿Por qué? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {W.section_por_que?.title || "¿Por qué tu club necesita una web de verdad?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {W.section_por_que?.intro}
        </p>

        {/* Ventaja 1 */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2 text-brand-text">
            ⭐ {W.section_por_que?.ventaja1?.title}
          </h3>
          <div className="space-y-2 text-brand-textSecondary">
            <p>{W.section_por_que?.ventaja1?.desc1}</p>
            <p>{W.section_por_que?.ventaja1?.desc2}</p>
            <p>{W.section_por_que?.ventaja1?.desc3}</p>
            <p className="font-semibold">{W.section_por_que?.ventaja1?.desc4}</p>
          </div>
        </div>

        {/* Ventaja 2 */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2 text-brand-text">
            ⭐ {W.section_por_que?.ventaja2?.title}
          </h3>
          <div className="space-y-2 text-brand-textSecondary">
            <p>{W.section_por_que?.ventaja2?.desc1}</p>
            <p>{W.section_por_que?.ventaja2?.desc2}</p>
            <p className="font-semibold">{W.section_por_que?.ventaja2?.desc3}</p>
          </div>
        </div>

        {/* Ventaja 3 */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2 text-brand-text">
            ⭐ {W.section_por_que?.ventaja3?.title}
          </h3>
          <div className="space-y-2 text-brand-textSecondary">
            <p>{W.section_por_que?.ventaja3?.desc1}</p>
            <p className="font-semibold">{W.section_por_que?.ventaja3?.desc2}</p>
          </div>
        </div>

        {/* Ventaja 4 */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2 text-brand-text">
            ⭐ {W.section_por_que?.ventaja4?.title}
          </h3>
          <div className="space-y-2 text-brand-textSecondary">
            <p>{W.section_por_que?.ventaja4?.desc1}</p>
            <ul className="ml-4 space-y-1">
              <li>{W.section_por_que?.ventaja4?.items?.item1}</li>
              <li>{W.section_por_que?.ventaja4?.items?.item2}</li>
              <li>{W.section_por_que?.ventaja4?.items?.item3}</li>
              <li>{W.section_por_que?.ventaja4?.items?.item4}</li>
              <li>{W.section_por_que?.ventaja4?.items?.item5}</li>
            </ul>
            <p className="font-semibold">{W.section_por_que?.ventaja4?.desc2}</p>
          </div>
        </div>

        {/* Ventaja 5 */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2 text-brand-text">
            ⭐ {W.section_por_que?.ventaja5?.title}
          </h3>
          <div className="space-y-2 text-brand-textSecondary">
            <p>{W.section_por_que?.ventaja5?.desc1}</p>
            <p className="font-semibold">{W.section_por_que?.ventaja5?.desc2}</p>
          </div>
        </div>
      </section>

      {/* Sección: Lo que incluye */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {W.section_incluye?.title || "Lo que incluye tu web"}
        </h2>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>✔ {W.section_incluye?.items?.item1}</li>
          <li>✔ {W.section_incluye?.items?.item2}</li>
          <li>✔ {W.section_incluye?.items?.item3}</li>
          <li>✔ {W.section_incluye?.items?.item4}</li>
          <li>✔ {W.section_incluye?.items?.item5}</li>
          <li>✔ {W.section_incluye?.items?.item6}</li>
          <li>✔ {W.section_incluye?.items?.item7}</li>
          <li>✔ {W.section_incluye?.items?.item8}</li>
          <li>✔ {W.section_incluye?.items?.item9}</li>
          <li>✔ {W.section_incluye?.items?.item10}</li>
          <li>✔ {W.section_incluye?.items?.item11}</li>
        </ul>
        <div className="space-y-2 text-brand-textSecondary">
          <p className="font-semibold">{W.section_incluye?.footer}</p>
          <p className="font-semibold text-brand-accent">{W.section_incluye?.footer2}</p>
        </div>
      </section>

      {/* Sección: Estilos */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {W.section_estilos?.title || "¿Qué estilos puedes elegir?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {W.section_estilos?.intro}
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-4 text-brand-textSecondary">
          <p>• {W.section_estilos?.estilos?.estilo1}</p>
          <p>• {W.section_estilos?.estilos?.estilo2}</p>
          <p>• {W.section_estilos?.estilos?.estilo3}</p>
          <p>• {W.section_estilos?.estilos?.estilo4}</p>
          <p>• {W.section_estilos?.estilos?.estilo5}</p>
          <p>• {W.section_estilos?.estilos?.estilo6}</p>
          <p>• {W.section_estilos?.estilos?.estilo7}</p>
          <p>• {W.section_estilos?.estilos?.estilo8}</p>
          <p>• {W.section_estilos?.estilos?.estilo9}</p>
        </div>
        <p className="text-brand-textSecondary font-semibold">
          {W.section_estilos?.footer}
        </p>
      </section>

      {/* Sección: ¿Cuánto cuesta? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {W.section_cuanto?.title || "¿Cuánto cuesta?"}
        </h2>
        <div className="space-y-2 text-brand-textSecondary">
          <p className="text-lg">{W.section_cuanto?.desc1}</p>
          <p>{W.section_cuanto?.desc2}</p>
          <p className="font-semibold">{W.section_cuanto?.desc3}</p>
        </div>
      </section>

      {/* Sección: ¿Quieres más información? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {W.section_info?.title || "¿Quieres más información?"}
        </h2>
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 mb-6">
          <p className="font-semibold mb-2 text-brand-text">
            📧 {W.section_info?.email_label || "Envíanos:"}
          </p>
          <p className="text-xl">
            <a 
              href={`mailto:${W.section_info?.email || "contact@rumaza.io"}`}
              className="text-brand-accent hover:underline font-medium"
            >
              {W.section_info?.email || "contact@rumaza.io"}
            </a>
          </p>
        </div>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {W.section_info?.email_label || "Envíanos:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {W.section_info?.items?.item1}</li>
          <li>• {W.section_info?.items?.item2}</li>
          <li>• {W.section_info?.items?.item3}</li>
          <li>• {W.section_info?.items?.item4}</li>
          <li>• {W.section_info?.items?.item5}</li>
          <li>• {W.section_info?.items?.item6}</li>
        </ul>
        <div className="space-y-2 text-brand-textSecondary">
          <p className="font-semibold">{W.section_info?.footer}</p>
          <p className="font-semibold">{W.section_info?.footer2}</p>
        </div>
      </section>

      {/* Sección Final */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {W.section_final?.title || "Tu club merece una web que esté a la altura."}
        </h2>
        <p className="text-lg font-semibold text-brand-textSecondary">
          {W.section_final?.subtitle || "Nosotros te la hacemos."}
        </p>
      </section>
    </div>
  );
}















