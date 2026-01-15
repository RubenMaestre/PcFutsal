// app/layout.tsx
// @ts-nocheck
import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PC FUTSAL & DATA",
  description: "Donde los goles valen… y los datos también.",
  icons: {
    icon: "/logo/favicon.ico", // <- favicon global
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        {/* Fallback meta tags in case metadata.icons doesn’t render */}
        <link rel="icon" href="/logo/favicon.ico" sizes="any" />
        <title>PC FUTSAL & DATA</title>
      </head>
      <body className="bg-neutral-950 text-neutral-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
