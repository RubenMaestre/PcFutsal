// /app/[lang]/quienes-somos/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.quienes_somos?.meta_title || "¿Quiénes somos? — PC FUTSAL";
  const description = dict?.quienes_somos?.meta_description || "Conoce al equipo detrás de PC FUTSAL. Un proyecto nacido para dar visibilidad al futsal amateur con datos, rankings, fantasy y comunidad.";
  
  return generateMetadataWithAlternates(
    lang,
    "/quienes-somos",
    title,
    description,
    undefined,
    dict
  );
}

export default async function QuienesSomosPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const Q = dict?.quienes_somos || {};

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-3 text-brand-text">
          {Q.title || "Quiénes somos"}
        </h1>
        <p className="text-lg text-brand-textSecondary italic mb-4">
          {Q.spoiler || "(spoiler: ahora mismo somos menos gente que en un entrenamiento de viernes antes de un puente)"}
        </p>
      </div>

      {/* Intro */}
      <div className="mb-8 space-y-4 text-brand-textSecondary leading-relaxed">
        <p className="text-lg">{Q.intro}</p>
        <p className="text-lg font-semibold">{Q.presentation}</p>
        <p className="text-lg">{Q.alone}</p>
        <p className="text-sm italic">{Q.emoji_note}</p>
        <p className="text-lg">{Q.why_born}</p>
        <p>{Q.why_born_detail}</p>
        <p className="text-lg font-semibold">{Q.alone_ecosystem}</p>
        <p>{Q.alone_ecosystem_detail}</p>
      </div>

      {/* Sección: ¿Qué buscamos? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {Q.section_que_buscamos?.title || "¿Qué buscamos?"}
        </h2>
        <p className="text-lg mb-6 text-brand-textSecondary">
          {Q.section_que_buscamos?.subtitle || "Gente del futsal que quiera aportar:"}
        </p>
        
        <div className="space-y-6">
          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              ✔ {Q.section_que_buscamos?.entrenadores?.title || "Entrenadores"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_que_buscamos?.entrenadores?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              ✔ {Q.section_que_buscamos?.jugadores?.title || "Jugadores"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_que_buscamos?.jugadores?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              ✔ {Q.section_que_buscamos?.directores?.title || "Directores deportivos"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_que_buscamos?.directores?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              ✔ {Q.section_que_buscamos?.aficionados?.title || "Aficionados frikis del futsal"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_que_buscamos?.aficionados?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-2 text-brand-text">
              ✔ {Q.section_que_buscamos?.cualquiera?.title || "Y cualquiera que quiera ayudar"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_que_buscamos?.cualquiera?.content}
            </p>
          </div>
        </div>
      </section>

      {/* Sección: ¿Para qué queremos ayuda? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-6 text-brand-accent">
          {Q.section_para_que?.title || "¿Para qué queremos ayuda?"}
        </h2>
        
        <div className="space-y-6">
          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-3 text-brand-text">
              🏆 {Q.section_para_que?.fifa?.title || "Para poner notas tipo FIFA a todos"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_para_que?.fifa?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-3 text-brand-text">
              🖼️ {Q.section_para_que?.fotos?.title || "Para mejorar perfiles y fotos"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_para_que?.fotos?.content}
            </p>
          </div>

          <div className="bg-brand-card border border-brand-card rounded-lg p-6">
            <h3 className="text-xl font-bold mb-3 text-brand-text">
              📚 {Q.section_para_que?.database?.title || "Para construir la mayor base de datos del futsal"}
            </h3>
            <p className="text-brand-textSecondary leading-relaxed">
              {Q.section_para_que?.database?.content}
            </p>
          </div>
        </div>
      </section>

      {/* Sección: ¿Qué ofrecemos a cambio? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {Q.section_que_ofrecemos?.title || "¿Qué ofrecemos a cambio?"}
        </h2>
        <div className="space-y-4 text-brand-textSecondary leading-relaxed">
          <p className="text-lg">{Q.section_que_ofrecemos?.intro}</p>
          <p className="text-lg font-semibold">💸 {Q.section_que_ofrecemos?.no_dinero}</p>
          <p>{Q.section_que_ofrecemos?.no_enganamos}</p>
          <p className="text-lg font-semibold">{Q.section_que_ofrecemos?.lo_que_ofrecemos}</p>
          <ul className="space-y-2 ml-4">
            <li>🎖️ {Q.section_que_ofrecemos?.items?.colaborador}</li>
            <li>🤝 {Q.section_que_ofrecemos?.items?.ecosistema}</li>
            <li>🔥 {Q.section_que_ofrecemos?.items?.influencia}</li>
            <li>😎 {Q.section_que_ofrecemos?.items?.orgullo}</li>
          </ul>
        </div>
      </section>

      {/* Sección: Invitación */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {Q.section_invitacion?.title || "Si quieres ayudar, estás invitado"}
        </h2>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {Q.section_invitacion?.items?.reclamar}</li>
          <li>• {Q.section_invitacion?.items?.verificar}</li>
          <li>• {Q.section_invitacion?.items?.aportar}</li>
          <li>• {Q.section_invitacion?.items?.subir}</li>
          <li>• {Q.section_invitacion?.items?.proponer}</li>
          <li>• {Q.section_invitacion?.items?.mensaje}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold leading-relaxed">
          {Q.section_invitacion?.footer}
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















