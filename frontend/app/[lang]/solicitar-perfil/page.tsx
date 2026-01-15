// /app/[lang]/solicitar-perfil/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.solicitar_perfil?.meta_title || "¿Cómo solicitar mi perfil en PC FUTSAL? — Reclama tu Tarjeta FIFA";
  const description = dict?.solicitar_perfil?.meta_description || "Descubre cómo solicitar y verificar tu perfil en PC FUTSAL. Reclama tu tarjeta FIFA personalizada, mejora tus estadísticas y participa en la mayor base de datos del futsal amateur.";
  
  return generateMetadataWithAlternates(
    lang,
    "/solicitar-perfil",
    title,
    description,
    undefined,
    dict
  );
}

export default async function SolicitarPerfilPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const S = dict?.solicitar_perfil || {};

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-3 text-brand-text">
          {S.title || "¿Cómo solicitar mi perfil en PC FUTSAL?"}
        </h1>
        <p className="text-lg text-brand-textSecondary italic">
          {S.subtitle || "(o cómo conseguir tu propia tarjeta FIFA sin tener que fichar por el Barça)"}
        </p>
      </div>

      {/* Intro */}
      <div className="mb-8 space-y-4 text-brand-textSecondary leading-relaxed">
        <p className="text-lg">{S.intro}</p>
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 italic">
          <p className="text-lg font-semibold text-brand-text mb-2">
            {S.quote || "\"¿Cómo que tengo 72 de regate? ¿Quién ha puesto esto?\""}
          </p>
          <p className="text-sm">
            {S.quote_author || "— Un ala cualquiera indignado"}
          </p>
        </div>
        <p className="text-lg font-semibold">{S.tranquilo}</p>
        <p className="text-lg font-semibold">{S.respira}</p>
        <p className="text-lg">{S.intro_footer}</p>
        <p className="text-lg font-semibold">{S.vamos}</p>
      </div>

      {/* Sección: ¿Qué es? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {S.section_que_es?.title || "1) ¿Qué es \"solicitar mi perfil\"?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {S.section_que_es?.intro || "Solicitar tu perfil significa:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {S.section_que_es?.items?.confirmar}</li>
          <li>• {S.section_que_es?.items?.modificar}</li>
          <li>• {S.section_que_es?.items?.peso}</li>
          <li>• {S.section_que_es?.items?.acceder}</li>
          <li>• {S.section_que_es?.items?.participar}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {S.section_que_es?.footer}
        </p>
      </section>

      {/* Sección: ¿Por qué? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {S.section_por_que?.title || "2) ¿Por qué reclamar mi perfil en PC FUTSAL?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {S.section_por_que?.intro}
        </p>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {S.section_por_que?.subtitle || "Y entonces pasan cosas como:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {S.section_por_que?.ejemplos?.asistencias}</li>
          <li>• {S.section_por_que?.ejemplos?.goles}</li>
          <li>• {S.section_por_que?.ejemplos?.intensidad}</li>
          <li>• {S.section_por_que?.ejemplos?.ranking}</li>
        </ul>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {S.section_por_que?.subtitle2 || "Solicitar tu perfil te permite:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>✔ {S.section_por_que?.items?.tarjeta}</li>
          <li>✔ {S.section_por_que?.items?.rankings}</li>
          <li>✔ {S.section_por_que?.items?.valoracion}</li>
          <li>✔ {S.section_por_que?.items?.fantasy}</li>
          <li>✔ {S.section_por_que?.items?.archivo}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {S.section_por_que?.footer}
        </p>
      </section>

      {/* Sección: ¿Cómo? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {S.section_como?.title || "3) ¿Cómo solicitar tu perfil? (modo simple)"}
        </h2>
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 mb-6">
          <p className="font-semibold mb-2 text-brand-text">
            📧 {S.section_como?.email_label || "Envíanos un email:"}
          </p>
          <p className="text-xl">
            <a 
              href={`mailto:${S.section_como?.email || "contacto@pcfutsal.es"}`}
              className="text-brand-accent hover:underline font-medium"
            >
              👉 {S.section_como?.email || "contacto@pcfutsal.es"}
            </a>
          </p>
        </div>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {S.section_como?.subtitle || "Con esta info:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {S.section_como?.items?.nombre}</li>
          <li>• {S.section_como?.items?.equipo}</li>
          <li>• {S.section_como?.items?.posicion}</li>
          <li>• {S.section_como?.items?.dorsal}</li>
          <li>• {S.section_como?.items?.enlace}</li>
          <li>• {S.section_como?.items?.foto}</li>
          <li>• {S.section_como?.items?.palmares}</li>
        </ul>
        <div className="space-y-2 text-brand-textSecondary">
          <p>{S.section_como?.footer1}</p>
          <p>{S.section_como?.footer2}</p>
          <p className="font-semibold">{S.section_como?.footer3}</p>
        </div>
      </section>

      {/* Sección: ¿Qué pasa? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {S.section_que_pasa?.title || "4) ¿Qué pasa cuando solicitas tu perfil?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {S.section_que_pasa?.intro || "Muy sencillo:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {S.section_que_pasa?.items?.revisamos}</li>
          <li>• {S.section_que_pasa?.items?.marcamos}</li>
          <li>• {S.section_que_pasa?.items?.voto}</li>
          <li>• {S.section_que_pasa?.items?.correcciones}</li>
          <li>• {S.section_que_pasa?.items?.mejorar}</li>
          <li>• {S.section_que_pasa?.items?.oficial}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {S.section_que_pasa?.footer}
        </p>
      </section>

      {/* Sección: Errores */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {S.section_errores?.title || "5) ¿Y si veo errores en mi perfil?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary font-semibold">
          {S.section_errores?.intro || "¡Perfecto!"}
        </p>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {S.section_errores?.subtitle || "Estás invitado oficialmente a:"}
        </p>
        <ul className="space-y-2 mb-4 text-brand-textSecondary">
          <li>• {S.section_errores?.items?.correcciones}</li>
          <li>• {S.section_errores?.items?.temporadas}</li>
          <li>• {S.section_errores?.items?.goles}</li>
          <li>• {S.section_errores?.items?.fotos}</li>
          <li>• {S.section_errores?.items?.historial}</li>
        </ul>
        <p className="text-brand-textSecondary font-semibold">
          {S.section_errores?.footer}
        </p>
      </section>

      {/* Sección: ¿Cuesta dinero? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {S.section_cuesta?.title || "6) ¿Cuesta dinero solicitar mi perfil?"}
        </h2>
        <p className="text-2xl mb-2 text-brand-accent font-bold">
          {S.section_cuesta?.answer || "JAJAJAJAJAJAJA."}
        </p>
        <p className="text-lg mb-2 text-brand-textSecondary font-semibold">
          {S.section_cuesta?.no || "No, amigo."}
        </p>
        <p className="text-lg mb-2 text-brand-textSecondary">
          {S.section_cuesta?.intro || "Esto es futsal."}
        </p>
        <p className="text-brand-textSecondary">
          {S.section_cuesta?.footer1}
        </p>
        <p className="text-brand-textSecondary">
          {S.section_cuesta?.footer2}
        </p>
      </section>

      {/* Sección: ¿Puedo ayudar? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-2 text-brand-accent">
          {S.section_ayudar?.title || "7) ¿Y puedo ayudar en más cosas?"}
        </h2>
        <p className="text-lg mb-4 text-brand-textSecondary">
          {S.section_ayudar?.intro || "Claro."}
        </p>
        <p className="font-semibold mb-3 text-brand-textSecondary">
          {S.section_ayudar?.subtitle || "Siempre necesitamos ayuda con:"}
        </p>
        <ul className="space-y-2 text-brand-textSecondary">
          <li>• {S.section_ayudar?.items?.fotos}</li>
          <li>• {S.section_ayudar?.items?.datos}</li>
          <li>• {S.section_ayudar?.items?.estadisticas}</li>
          <li>• {S.section_ayudar?.items?.informacion}</li>
          <li>• {S.section_ayudar?.items?.correcciones}</li>
          <li>• {S.section_ayudar?.items?.valoraciones}</li>
          <li>• {S.section_ayudar?.items?.goat}</li>
        </ul>
      </section>

      {/* Sección Final */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {S.section_final?.title || "Solicita tu perfil y entra en el universo PC FUTSAL"}
        </h2>
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 mb-6">
          <p className="font-semibold mb-2 text-brand-text">
            {S.section_final?.email_label || "Escríbenos:"}
          </p>
          <p className="text-xl">
            <a 
              href={`mailto:${S.section_final?.email || "contacto@pcfutsal.es"}`}
              className="text-brand-accent hover:underline font-medium"
            >
              👉 {S.section_final?.email || "contacto@pcfutsal.es"}
            </a>
          </p>
        </div>
        <div className="space-y-2 text-brand-textSecondary">
          <p className="font-semibold">{S.section_final?.footer1}</p>
          <p className="font-semibold">{S.section_final?.footer2}</p>
          <p className="font-semibold">{S.section_final?.footer3}</p>
        </div>
      </section>
    </div>
  );
}















