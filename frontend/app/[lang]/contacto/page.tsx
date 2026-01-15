// /app/[lang]/contacto/page.tsx
// @ts-nocheck

import { getDictionary } from "../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.legal?.contacto?.meta_title || "Contacto — PC FUTSAL";
  const description = dict?.legal?.contacto?.meta_desc || "Contacta con PC FUTSAL. Información de contacto, email y datos de la empresa para consultas, sugerencias y colaboraciones.";
  
  return generateMetadataWithAlternates(
    lang,
    "/contacto",
    title,
    description,
    undefined,
    dict
  );
}

export default async function ContactoPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const C = dict?.legal?.contacto || {};

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-3 text-brand-text">
          {C.title || "Contacto"}
        </h1>
        <p className="text-lg text-brand-textSecondary italic">
          {C.subtitle || "(o cómo enviarnos un mensaje sin tener que gritar desde la grada)"}
        </p>
      </div>

      {/* Intro */}
      <div className="mb-8 space-y-4 text-brand-textSecondary leading-relaxed">
        <p className="text-lg">{C.intro || "Si has llegado a esta página es porque:"}</p>
        <ul className="space-y-2 ml-4">
          <li>• {C.reasons?.reclamar}</li>
          <li>• {C.reasons?.valorar}</li>
          <li>• {C.reasons?.fotos}</li>
          <li>• {C.reasons?.corregir}</li>
          <li>• {C.reasons?.colaborar}</li>
          <li>• {C.reasons?.intensidad}</li>
        </ul>
        <p className="text-lg font-semibold">{C.bienvenido || "Sea lo que sea… bienvenido/a."}</p>
        <p className="text-lg">{C.descripcion}</p>
      </div>

      {/* Motivos */}
      <div className="mb-8">
        <p className="text-lg font-semibold mb-4 text-brand-textSecondary">
          {C.puedes_escribir || "Puedes escribirnos para:"}
        </p>
        <ul className="space-y-3 text-brand-textSecondary">
          <li className="flex items-start">
            <span className="text-brand-accent mr-2">🟥</span>
            <span>{C.motivos?.reclamar}</span>
          </li>
          <li className="flex items-start">
            <span className="text-brand-accent mr-2">🟦</span>
            <span>{C.motivos?.aportar}</span>
          </li>
          <li className="flex items-start">
            <span className="text-brand-accent mr-2">🟩</span>
            <span>{C.motivos?.mejoras}</span>
          </li>
          <li className="flex items-start">
            <span className="text-brand-accent mr-2">🟧</span>
            <span>{C.motivos?.errores}</span>
          </li>
          <li className="flex items-start">
            <span className="text-brand-accent mr-2">🟫</span>
            <span>{C.motivos?.colaborar}</span>
          </li>
          <li className="flex items-start">
            <span className="text-brand-accent mr-2">🟪</span>
            <span>{C.motivos?.goat}</span>
          </li>
        </ul>
        <p className="text-lg font-semibold mt-4 text-brand-textSecondary">
          {C.estamos_aqui || "Estamos al otro lado para ayudarte."}
        </p>
      </div>

      {/* Email de contacto */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {C.section_email?.title || "Email de contacto"}
        </h2>
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 mb-4">
          <p className="text-xl mb-2">
            <a 
              href={`mailto:${C.section_email?.email || "contacto@pcfutsal.es"}`}
              className="text-brand-accent hover:underline font-medium"
            >
              📧 {C.section_email?.email || "contacto@pcfutsal.es"}
            </a>
          </p>
        </div>
        <div className="space-y-2 text-brand-textSecondary">
          <p>{C.section_email?.respondo}</p>
          <p>{C.section_email?.prometo}</p>
        </div>
      </section>

      {/* Información del proyecto */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {C.section_proyecto?.title || "Información del proyecto"}
        </h2>
        <div className="space-y-3 text-brand-textSecondary">
          <p>{C.section_proyecto?.descripcion}</p>
          <p className="font-semibold">{C.section_proyecto?.footer}</p>
        </div>
      </section>

      {/* Información de la empresa */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {C.section_empresa?.title || "Información de la empresa"}
        </h2>
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 space-y-2 text-brand-textSecondary">
          <p><strong>{C.section_empresa?.company_name}</strong></p>
          <p>{C.section_empresa?.commercial_name}</p>
          <p>{C.section_empresa?.project}</p>
          <p>{C.section_empresa?.address}</p>
          <p>{C.section_empresa?.city}</p>
          <p>
            <a 
              href={`mailto:${C.section_empresa?.email_general?.split(": ")[1] || "contact@rumaza.io"}`}
              className="text-brand-accent hover:underline"
            >
              {C.section_empresa?.email_general}
            </a>
          </p>
        </div>
      </section>

      {/* ¿Quieres colaborar? */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4 text-brand-accent">
          {C.section_colaborar?.title || "¿Quieres colaborar?"}
        </h2>
        <div className="space-y-3 text-brand-textSecondary">
          <p>{C.section_colaborar?.descripcion}</p>
          <p className="font-semibold">{C.section_colaborar?.footer}</p>
        </div>
      </section>
    </div>
  );
}
