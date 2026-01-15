// Parche temporal para Next.js 15.5.x con React 18
// Evita errores de tipos en build (ResolvingMetadata / ResolvingViewport)

declare module "next/types.js" {
  export type ResolvingMetadata = unknown;
  export type ResolvingViewport = unknown;
}
