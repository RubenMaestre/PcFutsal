// @ts-nocheck

import { getDictionary } from "../../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.legal?.cookies?.meta_title || "Política de Cookies — PC FUTSAL";
  const description = dict?.legal?.cookies?.meta_desc || "Política de cookies de PC FUTSAL. Información sobre el uso de cookies técnicas y analíticas en el sitio.";
  
  return generateMetadataWithAlternates(
    lang,
    "/legal/cookies",
    title,
    description,
    undefined,
    dict
  );
}

export default async function CookiesPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const cookies = dict?.legal?.cookies;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        {cookies?.title || "Política de Cookies"}
      </h1>

      <div className="prose prose-invert max-w-none space-y-6 text-sm leading-relaxed">
        <p>
          {cookies?.intro || "PC FUTSAL utiliza cookies propias y de terceros para un correcto funcionamiento técnico y para analizar el uso del sitio."}
        </p>

        <section>
          <h2 className="text-xl font-semibold mb-3">{cookies?.section1_title || "1. ¿Qué cookies usamos?"}</h2>
          
          <h3 className="text-lg font-medium mb-2 mt-4">{cookies?.section1_technical_title || "Cookies técnicas (obligatorias)"}</h3>
          <p>
            {cookies?.section1_technical_text || "Garantizan el funcionamiento del sitio y no requieren consentimiento."}
          </p>

          <h3 className="text-lg font-medium mb-2 mt-4">{cookies?.section1_analytical_title || "Cookies analíticas"}</h3>
          <p>
            {cookies?.section1_analytical_text || "Permiten conocer cómo se utiliza la web. Usamos cookies de análisis (Google Analytics o equivalentes) anonimizadas."}
          </p>

          <h3 className="text-lg font-medium mb-2 mt-4">{cookies?.section1_personalization_title || "Cookies de personalización (si existieran)"}</h3>
          <p>
            {cookies?.section1_personalization_text || "Permiten recordar preferencias como idioma o configuración visual."}
          </p>

          <p className="mt-3">
            <strong>{cookies?.section1_no_ads || "No usamos cookies de publicidad ni de segmentación."}</strong>
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{cookies?.section2_title || "2. Gestión de cookies"}</h2>
          <p>
            {cookies?.section2_text || "Puedes aceptar o rechazar las cookies analíticas desde el banner inicial o desde la configuración de tu navegador."}
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{cookies?.section3_title || "3. Cómo desactivar las cookies"}</h2>
          <p>{cookies?.section3_intro || "Desde los ajustes de:"}</p>
          <ul className="list-disc pl-6 space-y-1 mt-2">
            <li>{cookies?.section3_item1 || "Chrome"}</li>
            <li>{cookies?.section3_item2 || "Firefox"}</li>
            <li>{cookies?.section3_item3 || "Safari"}</li>
            <li>{cookies?.section3_item4 || "Microsoft Edge"}</li>
            <li>{cookies?.section3_item5 || "Android o iOS"}</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
