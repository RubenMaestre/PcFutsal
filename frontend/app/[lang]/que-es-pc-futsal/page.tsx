// /app/[lang]/que-es-pc-futsal/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.que_es_pc_futsal?.meta_title || "¿Qué es PC FUTSAL? — La Plataforma del Fútbol Sala Amateur";
  const description = dict?.que_es_pc_futsal?.meta_description || "PC FUTSAL es la plataforma donde el fútbol sala amateur deja de ser invisible. Datos, rankings, fantasy, narrativa y un poquito de mala leche bien entendida.";
  
  return generateMetadataWithAlternates(
    lang,
    "/que-es-pc-futsal",
    title,
    description,
    undefined,
    dict
  );
}

export default async function QueEsPCFutsalPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const Q = dict?.que_es_pc_futsal || {};

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-3 text-brand-text">
          {Q.title || "¿Qué es PC FUTSAL?"}
        </h1>
        <p className="text-lg text-brand-textSecondary italic">
          {Q.subtitle || "La explicación que te daría un míster en un pabellón a las 21:45, pero con datos."}
        </p>
      </div>

      {/* Intro */}
      <div className="mb-8 text-brand-textSecondary leading-relaxed">
        <p className="text-lg">{Q.intro}</p>
      </div>

      {/* Sección: Futsal Real */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {Q.section_real_futsal?.title || "Es futsal real, del de siempre:"}
        </h2>
        <ul className="space-y-2 text-brand-textSecondary mb-4">
          <li>{Q.section_real_futsal?.item1}</li>
          <li>{Q.section_real_futsal?.item2}</li>
          <li>{Q.section_real_futsal?.item3}</li>
          <li>{Q.section_real_futsal?.item4}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {Q.section_real_futsal?.footer}
        </p>
      </section>

      {/* Sección: Ecosistema */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {Q.section_ecosistema?.title || "Un ecosistema completo (sí, has leído bien: ecosistema)"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {Q.section_ecosistema?.subtitle || "PC FUTSAL es tres cosas al mismo tiempo:"}
        </p>
        
        <div className="space-y-6">
          {/* Base de datos */}
          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              {Q.section_ecosistema?.database?.title}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_ecosistema?.database?.content}
            </p>
          </div>

          {/* FIFA */}
          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              {Q.section_ecosistema?.fifa?.title}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_ecosistema?.fifa?.content}
            </p>
          </div>

          {/* Fantasy */}
          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              {Q.section_ecosistema?.fantasy?.title}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_ecosistema?.fantasy?.content}
            </p>
          </div>
        </div>
      </section>

      {/* Sección: Por qué */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {Q.section_por_que?.title || "¿Por qué existe PC FUTSAL?"}
        </h2>
        <div className="space-y-3 text-brand-textSecondary leading-relaxed">
          <p className="text-lg font-semibold">{Q.section_por_que?.paragraph1}</p>
          <p>{Q.section_por_que?.paragraph2}</p>
          <p>{Q.section_por_que?.paragraph3}</p>
        </div>
      </section>

      {/* Sección: Lo que encontrarás */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-6 text-brand-accent">
          {Q.section_que_encontraras?.title || "Lo que encontrarás dentro"}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-brand-card border border-brand-card rounded-lg p-5">
            <h3 className="text-lg font-bold mb-2 text-brand-text">
              {Q.section_que_encontraras?.clasificaciones?.title}
            </h3>
            <p className="text-sm text-brand-textSecondary">
              {Q.section_que_encontraras?.clasificaciones?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-5">
            <h3 className="text-lg font-bold mb-2 text-brand-text">
              {Q.section_que_encontraras?.perfiles?.title}
            </h3>
            <p className="text-sm text-brand-textSecondary">
              {Q.section_que_encontraras?.perfiles?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-5">
            <h3 className="text-lg font-bold mb-2 text-brand-text">
              {Q.section_que_encontraras?.rankings?.title}
            </h3>
            <p className="text-sm text-brand-textSecondary">
              {Q.section_que_encontraras?.rankings?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-5">
            <h3 className="text-lg font-bold mb-2 text-brand-text">
              {Q.section_que_encontraras?.fantasy?.title}
            </h3>
            <p className="text-sm text-brand-textSecondary">
              {Q.section_que_encontraras?.fantasy?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-5">
            <h3 className="text-lg font-bold mb-2 text-brand-text">
              {Q.section_que_encontraras?.verificaciones?.title}
            </h3>
            <p className="text-sm text-brand-textSecondary">
              {Q.section_que_encontraras?.verificaciones?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-5">
            <h3 className="text-lg font-bold mb-2 text-brand-text">
              {Q.section_que_encontraras?.memoria?.title}
            </h3>
            <p className="text-sm text-brand-textSecondary">
              {Q.section_que_encontraras?.memoria?.content}
            </p>
          </div>
        </div>
      </section>

      {/* Sección: Tono */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {Q.section_tono?.title || "Nuestro tono (importante)"}
        </h2>
        <div className="space-y-3 text-brand-textSecondary leading-relaxed">
          <p>{Q.section_tono?.paragraph1}</p>
          <p>{Q.section_tono?.paragraph2}</p>
          <p>{Q.section_tono?.paragraph3}</p>
          <p className="text-lg font-bold text-brand-text">{Q.section_tono?.paragraph4}</p>
          <p className="text-lg font-bold text-brand-text">{Q.section_tono?.paragraph5}</p>
          <p>{Q.section_tono?.paragraph6}</p>
        </div>
      </section>

      {/* Sección: Futuro */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {Q.section_futuro?.title || "¿Y hacia dónde vamos?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {Q.section_futuro?.subtitle || "A convertir PC FUTSAL en:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {Q.section_futuro?.item1}</li>
          <li>• {Q.section_futuro?.item2}</li>
          <li>• {Q.section_futuro?.item3}</li>
          <li>• {Q.section_futuro?.item4}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {Q.section_futuro?.footer}
        </p>
      </section>

      {/* Footer */}
      <div className="mt-12 pt-8 border-t border-brand-card text-center">
        <h2 className="text-3xl font-bold mb-2 text-brand-accent">
          {Q.footer?.title || "PC FUTSAL"}
        </h2>
        <p className="text-lg text-brand-textSecondary italic">
          {Q.footer?.subtitle || "Donde los goles valen… y los datos también."}
        </p>
      </div>
    </div>
  );
}















