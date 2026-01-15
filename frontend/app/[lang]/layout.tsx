// app/[lang]/layout.tsx
// @ts-nocheck

import "../globals.css";
import type { Metadata } from "next";
import { Cabin, Orbitron } from "next/font/google";
import { getDictionary } from "../../lib/i18n";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import AnimatedShell from "../../components/AnimatedShell";
import { generateOrganizationSchema } from "../../lib/schema";
import { getDefaultOgImage, getDefaultOgTitle, getDefaultOgDescription } from "../../lib/seo";

const cabin = Cabin({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
  variable: "--font-cabin",
});

const orbitron = Orbitron({
  subsets: ["latin"],
  weight: ["500", "700", "900"],
  display: "swap",
  variable: "--font-orbitron",
});

const siteUrl = "https://pcfutsal.es";
const ogImage = getDefaultOgImage();

export const metadata: Metadata = {
  title: "PC FUTSAL",
  description: "El fútbol sala como nunca te lo habían puntuado.",
  openGraph: {
    title: getDefaultOgTitle(),
    description: getDefaultOgDescription(),
    url: siteUrl,
    siteName: "PC FUTSAL",
    images: [
      {
        url: ogImage,
        width: 1200,
        height: 630,
        alt: "PC FUTSAL – Plataforma de datos y Fantasy de fútbol sala",
      },
    ],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: getDefaultOgTitle(),
    description: getDefaultOgDescription(),
    images: [ogImage],
  },
};

export function generateStaticParams() {
  return [
    { lang: "es" },
    { lang: "val" },
    { lang: "en" },
    { lang: "fr" },
    { lang: "it" },
    { lang: "pt" },
    { lang: "de" },
  ];
}

async function getLastUpdateFromAPI() {
  try {
    const res = await fetch("https://pcfutsal.es/api/status/last_update/", {
      method: "GET",
      next: { revalidate: 300 },
    });

    if (!res.ok) {
      return "—";
    }

    const data = await res.json();
    if (data && data.last_update_display) {
      return data.last_update_display;
    }
    return "—";
  } catch (err) {
    return "—";
  }
}

export default async function LangLayout({ children, params }: any) {
  const { lang } = await params;
  const dict = await getDictionary(lang);
  const lastUpdate = await getLastUpdateFromAPI();
  const organizationSchema = generateOrganizationSchema();

  return (
    <html lang={lang} className={`${cabin.variable} ${orbitron.variable}`}>
      <head>
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9121651028519630"
          crossOrigin="anonymous"
        />

        {/* Schema.org Organization */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
      </head>
      <body className={`bg-brand-bg text-brand-text min-h-screen antialiased font-base flex flex-col ${cabin.className}`}>
        <Header dict={dict} lang={lang} lastUpdate={lastUpdate} />
        <main className="flex-1 w-full">
          <div className="max-w-7xl mx-auto w-full px-4 py-4">
            <AnimatedShell>{children}</AnimatedShell>
          </div>
        </main>
        <Footer dict={dict} lang={lang} />
      </body>
    </html>
  );
}
