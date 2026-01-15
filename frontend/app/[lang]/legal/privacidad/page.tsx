// @ts-nocheck

import { getDictionary } from "../../../../lib/i18n";
import { generateMetadataWithAlternates } from "../../../../lib/seo";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const { lang } = params;
  const dict = await getDictionary(lang);
  
  const title = dict?.legal?.privacidad?.meta_title || "Política de Privacidad — PC FUTSAL";
  const description = dict?.legal?.privacidad?.meta_desc || "Política de privacidad de PC FUTSAL. Información sobre el tratamiento de datos personales según RGPD y LOPDGDD.";
  
  return generateMetadataWithAlternates(
    lang,
    "/legal/privacidad",
    title,
    description,
    undefined,
    dict
  );
}

export default async function PrivacidadPage({ params }: any) {
  const { lang } = params;
  const dict = await getDictionary(lang);
  const privacy = dict?.legal?.privacidad;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        {privacy?.title || "Política de Privacidad"}
      </h1>

      <div className="prose prose-invert max-w-none space-y-6 text-sm leading-relaxed">
        <p className="text-brand-textSecondary">
          {privacy?.intro || "En cumplimiento del RGPD (Reglamento UE 2016/679) y la LOPDGDD, se informa lo siguiente:"}
        </p>

        <section>
          <h2 className="text-xl font-semibold mb-3">{privacy?.section1_title || "1. Responsable del tratamiento"}</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>{privacy?.section1_company || "RUMAZA SYSTEMS S.L."}</li>
            <li>{privacy?.section1_commercial || "Nombre comercial: RUMAZA STUDIO"}</li>
            <li>{privacy?.section1_project || "Proyecto: PC FUTSAL"}</li>
            <li>{privacy?.section1_address || "Domicilio: C/ Antonio Moya Albadalejo nº13 bajo, 03204, Elche (Alicante)"}</li>
            <li>{privacy?.section1_email || "Email:"} <a href="mailto:contact@rumaza.io" className="text-brand-accent hover:underline">contact@rumaza.io</a></li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{privacy?.section2_title || "2. Qué datos recopilamos"}</h2>
          
          <h3 className="text-lg font-medium mb-2 mt-4">{privacy?.section2_voluntary_title || "Datos proporcionados voluntariamente"}</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>{privacy?.section2_voluntary_item1 || "Nombre"}</li>
            <li>{privacy?.section2_voluntary_item2 || "Email"}</li>
            <li>{privacy?.section2_voluntary_item3 || "Información enviada por formularios o registro (si existiera)"}</li>
          </ul>

          <h3 className="text-lg font-medium mb-2 mt-4">{privacy?.section2_technical_title || "Datos técnicos (no identificativos)"}</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>{privacy?.section2_technical_item1 || "Cookies técnicas"}</li>
            <li>{privacy?.section2_technical_item2 || "Datos analíticos"}</li>
            <li>{privacy?.section2_technical_item3 || "IP anonimizadas (cuando sea posible)"}</li>
            <li>{privacy?.section2_technical_item4 || "Uso y navegación"}</li>
          </ul>

          <h3 className="text-lg font-medium mb-2 mt-4">{privacy?.section2_scraping_title || "Datos provenientes de scraping (no personales)"}</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>{privacy?.section2_scraping_item1 || "Clasificaciones"}</li>
            <li>{privacy?.section2_scraping_item2 || "Resultados"}</li>
            <li>{privacy?.section2_scraping_item3 || "Datos deportivos públicos"}</li>
            <li>{privacy?.section2_scraping_item4 || "Datos de jugadores publicados por federaciones (no datos sensibles)"}</li>
            <li>{privacy?.section2_scraping_item5 || "Listas públicas y estadísticas"}</li>
          </ul>
          
          <p className="mt-3">
            <strong>{privacy?.section2_never || "Nunca recogemos datos privados no publicados oficialmente."}</strong>
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{privacy?.section3_title || "3. Finalidad del tratamiento"}</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>{privacy?.section3_item1 || "Gestionar consultas enviadas a través del sitio"}</li>
            <li>{privacy?.section3_item2 || "Mejorar el funcionamiento técnico de la plataforma"}</li>
            <li>{privacy?.section3_item3 || "Realizar análisis estadísticos agregados"}</li>
            <li>{privacy?.section3_item4 || "Mostrar información deportiva pública"}</li>
            <li>{privacy?.section3_item5 || "Generar contenido lúdico (fantasy, rankings, datos visuales)"}</li>
          </ul>
          <p className="mt-3">
            {privacy?.section3_footer || "Los datos deportivos públicos no se asocian a usuarios ni se utilizan para segmentación o publicidad."}
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{privacy?.section4_title || "4. Legitimación"}</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>{privacy?.section4_item1 || "Consentimiento del usuario"}</li>
            <li>{privacy?.section4_item2 || "Interés legítimo para la gestión técnica y analítica del sitio"}</li>
            <li>{privacy?.section4_item3 || "Información pública accesible libremente"}</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{privacy?.section5_title || "5. Destinatarios"}</h2>
          <p>
            {privacy?.section5_text || "No se ceden datos personales a terceros salvo obligación legal. Los proveedores tecnológicos (hosting, analítica) operan como encargados de tratamiento con contrato regulado."}
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{privacy?.section6_title || "6. Conservación de datos"}</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>{privacy?.section6_item1 || "Datos enviados por el usuario: hasta solicitar su eliminación."}</li>
            <li>{privacy?.section6_item2 || "Datos técnicos: según configuración de cookies."}</li>
            <li>{privacy?.section6_item3 || "Datos de scraping: pueden mantenerse indefinidamente con fines estadísticos e informativos."}</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">{privacy?.section7_title || "7. Derechos del usuario"}</h2>
          <p>{privacy?.section7_intro || "Puedes ejercer tus derechos de:"}</p>
          <ul className="list-disc pl-6 space-y-1 mt-2">
            <li>{privacy?.section7_item1 || "Acceso"}</li>
            <li>{privacy?.section7_item2 || "Rectificación"}</li>
            <li>{privacy?.section7_item3 || "Supresión"}</li>
            <li>{privacy?.section7_item4 || "Oposición"}</li>
            <li>{privacy?.section7_item5 || "Limitación"}</li>
            <li>{privacy?.section7_item6 || "Portabilidad"}</li>
          </ul>
          <p className="mt-3">
            {privacy?.section7_email || "Enviando un email a:"} <a href="mailto:contact@rumaza.io" className="text-brand-accent hover:underline">contact@rumaza.io</a>
          </p>
          <p className="mt-2">
            {privacy?.section7_aepd || "Si lo deseas, puedes reclamar ante la AEPD."}
          </p>
        </section>
      </div>
    </div>
  );
}
