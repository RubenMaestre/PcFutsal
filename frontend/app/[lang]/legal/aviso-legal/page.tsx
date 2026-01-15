// @ts-nocheck

import { getDictionary } from "../../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.legal?.aviso_legal?.meta_title || "Aviso Legal — PC FUTSAL";
  const description = dict?.legal?.aviso_legal?.meta_desc || "Aviso legal de PC FUTSAL. Información sobre el titular, objeto del sitio, propiedad intelectual y responsabilidades.";
  
  return generateMetadataWithAlternates(
    lang,
    "/legal/aviso-legal",
    title,
    description,
    undefined,
    dict
  );
}

export default async function AvisoLegalPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const legal = dict?.legal?.aviso_legal;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        {legal?.title || "Aviso Legal"}
      </h1>

      <div className="prose prose-invert max-w-none space-y-6 text-sm leading-relaxed">
        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section1_title || "1. AVISO LEGAL — PC FUTSAL (pcfutsal.es)"}</h2>
          
          <div className="space-y-3">
            <p><strong>{legal?.section1_titular || "Titular del sitio web:"}</strong></p>
            <ul className="list-disc pl-6 space-y-1">
              <li>{legal?.section1_company || "RUMAZA SYSTEMS S.L."}</li>
              <li>{legal?.section1_commercial || "Nombre comercial: RUMAZA STUDIO"}</li>
              <li>{legal?.section1_project || "Proyecto: PC FUTSAL"}</li>
              <li>{legal?.section1_address || "Domicilio: C/ Antonio Moya Albadalejo nº13 bajo, 03204, Elche (Alicante), España"}</li>
              <li>{legal?.section1_email || "Email de contacto:"} <a href="mailto:contact@rumaza.io" className="text-brand-accent hover:underline">contact@rumaza.io</a></li>
            </ul>
            
            <p className="mt-4">
              {legal?.section1_acceptance || "El acceso y uso del sitio web pcfutsal.es atribuye la condición de usuario e implica la aceptación plena de este Aviso Legal."}
            </p>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section2_title || "2. Objeto del sitio web"}</h2>
          <p>
            {legal?.section2_intro || "El proyecto PC FUTSAL es una plataforma desarrollada por RUMAZA SYSTEMS S.L. cuyo propósito es:"}
          </p>
          <ul className="list-disc pl-6 space-y-1 mt-2">
            <li>{legal?.section2_item1 || "Mostrar información pública sobre resultados, clasificaciones y datos deportivos."}</li>
            <li>{legal?.section2_item2 || "Generar estadísticas, visualizaciones y contenido analítico."}</li>
            <li>{legal?.section2_item3 || "Crear juegos de entretenimiento como \"fantasy futsal\" basados en datos públicos."}</li>
            <li>{legal?.section2_item4 || "Producir rankings, tarjetas de jugadores y contenido deportivo informativo."}</li>
          </ul>
          <p className="mt-3">
            {legal?.section2_footer || "El sitio pcfutsal.es no es oficial ni está vinculado a ninguna federación deportiva, y utiliza exclusivamente información pública disponible en fuentes oficiales."}
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section3_title || "3. Obtención de datos (Scraping)"}</h2>
          <p>{legal?.section3_intro || "PC FUTSAL recopila información deportiva exclusivamente pública procedente de:"}</p>
          <ul className="list-disc pl-6 space-y-1 mt-2">
            <li>{legal?.section3_item1 || "Webs oficiales de federaciones deportivas."}</li>
            <li>{legal?.section3_item2 || "Páginas con resultados, clasificaciones y datos públicos sobre partidos y jugadores."}</li>
          </ul>
          <p className="mt-3">
            {legal?.section3_purpose || "El scraping se realiza solo con fines informativos, estadísticos y recreativos, incluyendo visualizaciones, rankings, tarjetas tipo \"FIFA\" y juegos fantasy."}
          </p>
          <p className="mt-2">
            {legal?.section3_no_commercial || "No utilizamos los datos para fines comerciales, segmentación publicitaria o creación de perfiles personales con efecto legal."}
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section4_title || "4. Propiedad intelectual e industrial"}</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>{legal?.section4_item1 || "Todos los contenidos propios (diseño, visualizaciones, textos, código, gráficos, rankings, logos y materiales creados) pertenecen a RUMAZA SYSTEMS S.L."}</li>
            <li>{legal?.section4_item2 || "Los datos públicos extraídos pertenecen a sus respectivas fuentes oficiales."}</li>
            <li>{legal?.section4_item3 || "Está prohibido reproducir, distribuir o modificar contenidos sin autorización previa."}</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section5_title || "5. Responsabilidad del usuario"}</h2>
          <p>{legal?.section5_intro || "El usuario se compromete a:"}</p>
          <ul className="list-disc pl-6 space-y-1 mt-2">
            <li>{legal?.section5_item1 || "Hacer un uso adecuado y lícito del sitio."}</li>
            <li>{legal?.section5_item2 || "No realizar actividades que afecten al funcionamiento de la web."}</li>
            <li>{legal?.section5_item3 || "No manipular ni extraer los contenidos de forma masiva."}</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section6_title || "6. Enlaces externos"}</h2>
          <p>
            {legal?.section6_text || "PC FUTSAL puede incluir enlaces a webs de terceros. RUMAZA SYSTEMS S.L. no se responsabiliza del contenido o funcionamiento de dichas webs."}
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section7_title || "7. Protección de datos"}</h2>
          <p>
            {legal?.section7_text || "El tratamiento de datos personales se detalla en la"} <a href={`/${lang}/legal/privacidad`} className="text-brand-accent hover:underline">{legal?.section7_link || "Política de Privacidad"}</a>.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{legal?.section8_title || "8. Legislación aplicable"}</h2>
          <p>
            {legal?.section8_text || "Este sitio se rige por la legislación española. Las partes renuncian a cualquier otro fuero y someten sus conflictos a los Juzgados y Tribunales de Elche (Alicante)."}
          </p>
        </section>
      </div>
    </div>
  );
}
